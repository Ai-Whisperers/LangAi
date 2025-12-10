"""
Contradiction Detection Module (Phase 10).

Detects conflicting information across research sources and agent outputs.

Features:
- Fact grouping by topic
- LLM-based contradiction detection
- Severity assessment
- Resolution suggestions
- Priority ranking
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
from anthropic import Anthropic

from ..config import get_config
from ..llm.client_factory import safe_extract_text
from ..types import ContradictionSeverity, ResolutionStrategy  # Centralized enums
# AI models for extraction
from ..ai.extraction import ExtractedFact, FactCategory


# ============================================================================
# Enumerations
# ============================================================================
# Note: ContradictionSeverity, ResolutionStrategy imported from types.py


# ============================================================================
# Data Models
# ============================================================================

class Contradiction(BaseModel):
    """A detected contradiction between facts."""
    id: str
    topic: str
    severity: ContradictionSeverity
    fact_a: str
    fact_b: str
    source_a: Optional[str] = None
    source_b: Optional[str] = None
    agent_a: str = "unknown"
    agent_b: str = "unknown"
    explanation: str
    resolution_strategy: ResolutionStrategy = ResolutionStrategy.INVESTIGATE
    resolution_suggestion: str = ""
    detected_at: datetime = Field(default_factory=datetime.now)

    def to_markdown(self) -> str:
        """Format contradiction as markdown."""
        severity_icon = {
            ContradictionSeverity.CRITICAL: "🔴",
            ContradictionSeverity.HIGH: "🟠",
            ContradictionSeverity.MEDIUM: "🟡",
            ContradictionSeverity.LOW: "🟢"
        }.get(self.severity, "⚪")

        return f"""
{severity_icon} **Contradiction #{self.id}** ({self.severity})

**Topic:** {self.topic}

**Fact A** ({self.agent_a}):
> {self.fact_a}

**Fact B** ({self.agent_b}):
> {self.fact_b}

**Explanation:** {self.explanation}

**Resolution:** {self.resolution_strategy.value}
{self.resolution_suggestion if self.resolution_suggestion else ""}
"""


class ContradictionReport(BaseModel):
    """Report of all detected contradictions."""
    contradictions: List[Contradiction] = Field(default_factory=list)
    total_facts_analyzed: int = 0
    topics_analyzed: int = 0
    analysis_time_ms: float = 0.0
    generated_at: datetime = Field(default_factory=datetime.now)

    @property
    def critical_count(self) -> int:
        return sum(1 for c in self.contradictions if c.severity == ContradictionSeverity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for c in self.contradictions if c.severity == ContradictionSeverity.HIGH)

    @property
    def total_count(self) -> int:
        return len(self.contradictions)

    @property
    def has_critical(self) -> bool:
        return self.critical_count > 0

    def get_by_severity(self, severity: ContradictionSeverity) -> List[Contradiction]:
        return [c for c in self.contradictions if c.severity == severity]

    def to_markdown(self) -> str:
        """Format report as markdown."""
        if not self.contradictions:
            return """
## Contradiction Analysis

✅ **No contradictions detected**

- Facts analyzed: {self.total_facts_analyzed}
- Topics reviewed: {self.topics_analyzed}
""".format(self=self)

        severity_summary = f"""
- 🔴 Critical: {self.critical_count}
- 🟠 High: {self.high_count}
- 🟡 Medium: {sum(1 for c in self.contradictions if c.severity == ContradictionSeverity.MEDIUM)}
- 🟢 Low: {sum(1 for c in self.contradictions if c.severity == ContradictionSeverity.LOW)}
"""

        contradictions_md = "\n".join(c.to_markdown() for c in self.contradictions)

        return f"""
## Contradiction Analysis

**Total Contradictions:** {self.total_count}
{severity_summary}

### Detected Contradictions

{contradictions_md}

---
*Analysis completed at {self.generated_at.strftime("%Y-%m-%d %H:%M:%S")}*
*Facts analyzed: {self.total_facts_analyzed} | Topics: {self.topics_analyzed}*
"""


# ============================================================================
# Topic Extraction
# ============================================================================

# Topic keywords for grouping facts
TOPIC_KEYWORDS = {
    "revenue": ["revenue", "sales", "income", "turnover"],
    "profit": ["profit", "margin", "net income", "EBITDA", "earnings"],
    "market_share": ["market share", "share of market", "market position"],
    "market_size": ["market size", "TAM", "SAM", "SOM", "addressable market"],
    "employees": ["employees", "staff", "workforce", "headcount", "team size"],
    "funding": ["funding", "raised", "valuation", "investment", "series"],
    "founded": ["founded", "established", "started", "began", "inception"],
    "growth": ["growth", "grew", "increase", "CAGR", "year-over-year"],
    "headquarters": ["headquarters", "HQ", "based in", "headquartered"],
    "ceo": ["CEO", "chief executive", "founder", "leader"],
    "products": ["products", "offerings", "services", "solutions"],
    "competitors": ["competitors", "rivals", "competition", "versus"],
}


def extract_topics(facts: List[ExtractedFact]) -> Dict[str, List[ExtractedFact]]:
    """
    Group facts by topic.

    Args:
        facts: List of extracted facts

    Returns:
        Dict mapping topic names to facts
    """
    topics = {}

    for fact in facts:
        fact_lower = fact.source_text.lower()

        # Check each topic
        for topic, keywords in TOPIC_KEYWORDS.items():
            if any(kw in fact_lower for kw in keywords):
                if topic not in topics:
                    topics[topic] = []
                topics[topic].append(fact)
                break
        else:
            # Use category as fallback topic
            topic = fact.category.value
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(fact)

    return topics


# ============================================================================
# Contradiction Detector
# ============================================================================

class ContradictionDetector:
    """
    Detect contradictions across research facts.

    Uses a combination of:
    1. Rule-based detection for numerical contradictions
    2. LLM-based detection for semantic contradictions

    Usage:
        detector = ContradictionDetector()
        report = detector.detect(facts)
    """

    def __init__(self, use_llm: bool = True):
        """
        Initialize contradiction detector.

        Args:
            use_llm: Whether to use LLM for semantic analysis
        """
        self.use_llm = use_llm
        self._config = get_config()
        self._contradiction_count = 0

    def detect(self, facts: List[ExtractedFact]) -> ContradictionReport:
        """
        Detect contradictions in a list of facts.

        Args:
            facts: List of extracted facts to analyze

        Returns:
            ContradictionReport with detected contradictions
        """
        start_time = datetime.now()
        self._contradiction_count = 0

        # Group facts by topic
        topics = extract_topics(facts)

        contradictions = []

        # Analyze each topic for contradictions
        for topic, topic_facts in topics.items():
            if len(topic_facts) < 2:
                continue

            # Rule-based detection for numerical facts
            numerical_contradictions = self._detect_numerical_contradictions(
                topic, topic_facts
            )
            contradictions.extend(numerical_contradictions)

            # LLM-based detection for semantic contradictions
            if self.use_llm and len(topic_facts) >= 2:
                semantic_contradictions = self._detect_semantic_contradictions(
                    topic, topic_facts
                )
                contradictions.extend(semantic_contradictions)

        analysis_time = (datetime.now() - start_time).total_seconds() * 1000

        return ContradictionReport(
            contradictions=contradictions,
            total_facts_analyzed=len(facts),
            topics_analyzed=len(topics),
            analysis_time_ms=analysis_time
        )

    def detect_from_agent_outputs(
        self,
        agent_outputs: Dict[str, Dict[str, Any]]
    ) -> ContradictionReport:
        """
        Detect contradictions across all agent outputs.

        Args:
            agent_outputs: Dict mapping agent names to outputs

        Returns:
            ContradictionReport
        """
        # Use the extraction function from logic_critic
        from ..agents.quality.logic_critic import extract_facts_from_agent_output

        all_facts = []
        for agent_name, output in agent_outputs.items():
            facts = extract_facts_from_agent_output(output, agent_name)
            all_facts.extend(facts)

        return self.detect(all_facts)

    def _detect_numerical_contradictions(
        self,
        topic: str,
        facts: List[ExtractedFact]
    ) -> List[Contradiction]:
        """
        Detect contradictions in numerical facts.

        Looks for facts about the same metric with different values.
        """
        contradictions = []

        # Extract numerical values from facts
        numerical_facts = []
        for fact in facts:
            numbers = self._extract_numbers(fact.source_text)
            if numbers:
                numerical_facts.append((fact, numbers))

        # Compare pairs
        for i, (fact_a, nums_a) in enumerate(numerical_facts):
            for j, (fact_b, nums_b) in enumerate(numerical_facts[i+1:], i+1):
                # Check if facts are about similar things
                if self._facts_are_comparable(fact_a.source_text, fact_b.source_text):
                    # Check for numerical disagreement
                    disagreement = self._check_numerical_disagreement(nums_a, nums_b)
                    if disagreement:
                        self._contradiction_count += 1
                        # Get source URL or use "unknown" for agent tracking
                        source_a = fact_a.source_url or "unknown"
                        source_b = fact_b.source_url or "unknown"
                        contradictions.append(Contradiction(
                            id=f"NUM-{self._contradiction_count}",
                            topic=topic,
                            severity=self._assess_numerical_severity(
                                disagreement['diff_pct']
                            ),
                            fact_a=fact_a.source_text,
                            fact_b=fact_b.source_text,
                            agent_a=source_a,
                            agent_b=source_b,
                            explanation=f"Numerical disagreement: {disagreement['value_a']} vs {disagreement['value_b']} ({disagreement['diff_pct']:.1f}% difference)",
                            resolution_strategy=self._suggest_numerical_resolution(fact_a, fact_b),
                            resolution_suggestion=f"Consider using the value from the more authoritative source"
                        ))

        return contradictions

    def _detect_semantic_contradictions(
        self,
        topic: str,
        facts: List[ExtractedFact]
    ) -> List[Contradiction]:
        """
        Detect semantic contradictions using LLM.
        """
        contradictions = []

        # Prepare facts for analysis
        facts_text = "\n".join([
            f"[{i+1}] ({fact.source_url or 'unknown'}): {fact.source_text}"
            for i, fact in enumerate(facts)
        ])

        prompt = f"""Analyze these facts about "{topic}" for contradictions or conflicts:

{facts_text}

Identify any contradicting or conflicting statements. For each contradiction found, provide:
1. The two conflicting fact numbers
2. Brief explanation of the contradiction
3. Severity (CRITICAL/HIGH/MEDIUM/LOW)

If there are no contradictions, respond with "NO CONTRADICTIONS".

Format each contradiction as:
CONTRADICTION: [fact_num_1] vs [fact_num_2]
EXPLANATION: [explanation]
SEVERITY: [level]
---"""

        try:
            client = Anthropic(api_key=self._config.anthropic_api_key)
            response = client.messages.create(
                model=self._config.llm_model,
                max_tokens=500,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = safe_extract_text(response, default="", agent_name="contradiction_detector")

            if "NO CONTRADICTIONS" in result_text.upper():
                return []

            # Parse response
            contradiction_blocks = result_text.split("---")
            for block in contradiction_blocks:
                if "CONTRADICTION:" not in block:
                    continue

                parsed = self._parse_llm_contradiction(block, facts)
                if parsed:
                    self._contradiction_count += 1
                    parsed.id = f"SEM-{self._contradiction_count}"
                    parsed.topic = topic
                    contradictions.append(parsed)

        except Exception as e:
            # Log error but don't fail
            print(f"[ContradictionDetector] LLM analysis error: {e}")

        return contradictions

    def _extract_numbers(self, text: str) -> List[Tuple[float, str]]:
        """Extract numerical values from text."""
        numbers = []

        # Currency patterns
        currency_pattern = r'\$?([\d,]+(?:\.\d+)?)\s*([BMK])?(?:illion)?'
        for match in re.finditer(currency_pattern, text):
            value = float(match.group(1).replace(',', ''))
            multiplier = match.group(2)
            if multiplier:
                if multiplier.upper() == 'B':
                    value *= 1_000_000_000
                elif multiplier.upper() == 'M':
                    value *= 1_000_000
                elif multiplier.upper() == 'K':
                    value *= 1_000
            numbers.append((value, match.group(0)))

        # Percentage patterns
        pct_pattern = r'([\d,]+(?:\.\d+)?)\s*%'
        for match in re.finditer(pct_pattern, text):
            value = float(match.group(1).replace(',', ''))
            numbers.append((value, match.group(0)))

        return numbers

    def _facts_are_comparable(self, fact_a: str, fact_b: str) -> bool:
        """Check if two facts are about comparable things."""
        # Simple keyword overlap check
        words_a = set(fact_a.lower().split())
        words_b = set(fact_b.lower().split())

        # Remove common words
        stopwords = {'the', 'a', 'an', 'is', 'was', 'are', 'were', 'to', 'of', 'and', 'in'}
        words_a -= stopwords
        words_b -= stopwords

        # Check overlap
        overlap = len(words_a & words_b)
        return overlap >= 3

    def _check_numerical_disagreement(
        self,
        nums_a: List[Tuple[float, str]],
        nums_b: List[Tuple[float, str]]
    ) -> Optional[Dict[str, Any]]:
        """Check for significant numerical disagreement."""
        if not nums_a or not nums_b:
            return None

        # Compare first numbers (simplified)
        val_a, str_a = nums_a[0]
        val_b, str_b = nums_b[0]

        if val_a == 0 and val_b == 0:
            return None

        max_val = max(abs(val_a), abs(val_b))
        diff_pct = abs(val_a - val_b) / max_val * 100 if max_val > 0 else 0

        # Significant if >15% difference
        if diff_pct > 15:
            return {
                'value_a': str_a,
                'value_b': str_b,
                'diff_pct': diff_pct
            }

        return None

    def _assess_numerical_severity(self, diff_pct: float) -> ContradictionSeverity:
        """Assess severity based on percentage difference."""
        if diff_pct > 50:
            return ContradictionSeverity.CRITICAL
        elif diff_pct > 30:
            return ContradictionSeverity.HIGH
        elif diff_pct > 20:
            return ContradictionSeverity.MEDIUM
        else:
            return ContradictionSeverity.LOW

    def _suggest_numerical_resolution(
        self,
        fact_a: ExtractedFact,
        fact_b: ExtractedFact
    ) -> ResolutionStrategy:
        """Suggest resolution strategy for numerical contradiction."""
        # Check for official source indicators
        official_keywords = ['official', 'SEC', '10-K', '10-Q', 'annual report', 'investor relations']

        a_is_official = any(kw in fact_a.source_text.lower() for kw in official_keywords)
        b_is_official = any(kw in fact_b.source_text.lower() for kw in official_keywords)

        if a_is_official and not b_is_official:
            return ResolutionStrategy.USE_OFFICIAL
        elif b_is_official and not a_is_official:
            return ResolutionStrategy.USE_OFFICIAL

        return ResolutionStrategy.INVESTIGATE

    def _parse_llm_contradiction(
        self,
        block: str,
        facts: List[ExtractedFact]
    ) -> Optional[Contradiction]:
        """Parse LLM contradiction output."""
        try:
            lines = block.strip().split('\n')

            fact_nums = None
            explanation = ""
            severity = ContradictionSeverity.MEDIUM

            for line in lines:
                line = line.strip()
                if line.startswith('CONTRADICTION:'):
                    # Extract fact numbers
                    nums = re.findall(r'\[(\d+)\]', line)
                    if len(nums) >= 2:
                        fact_nums = (int(nums[0]) - 1, int(nums[1]) - 1)
                elif line.startswith('EXPLANATION:'):
                    explanation = line.replace('EXPLANATION:', '').strip()
                elif line.startswith('SEVERITY:'):
                    sev_str = line.replace('SEVERITY:', '').strip().upper()
                    try:
                        severity = ContradictionSeverity(sev_str)
                    except ValueError:
                        pass

            if fact_nums and 0 <= fact_nums[0] < len(facts) and 0 <= fact_nums[1] < len(facts):
                fact_a = facts[fact_nums[0]]
                fact_b = facts[fact_nums[1]]

                return Contradiction(
                    id="",  # Will be set by caller
                    topic="",  # Will be set by caller
                    severity=severity,
                    fact_a=fact_a.source_text,
                    fact_b=fact_b.source_text,
                    agent_a=fact_a.source_url or "unknown",
                    agent_b=fact_b.source_url or "unknown",
                    explanation=explanation,
                    resolution_strategy=ResolutionStrategy.INVESTIGATE
                )

        except Exception as e:
            print(f"[ContradictionDetector] Parse error: {e}")

        return None


# ============================================================================
# Convenience Functions
# ============================================================================

def detect_contradictions(
    facts: List[ExtractedFact],
    use_llm: bool = True
) -> ContradictionReport:
    """
    Detect contradictions in facts.

    Args:
        facts: List of facts to analyze
        use_llm: Whether to use LLM for semantic analysis

    Returns:
        ContradictionReport
    """
    detector = ContradictionDetector(use_llm=use_llm)
    return detector.detect(facts)


def quick_contradiction_check(
    agent_outputs: Dict[str, Dict[str, Any]]
) -> Tuple[int, int]:
    """
    Quick check for contradictions (no LLM).

    Args:
        agent_outputs: Agent outputs to check

    Returns:
        Tuple of (total_contradictions, critical_count)
    """
    detector = ContradictionDetector(use_llm=False)
    report = detector.detect_from_agent_outputs(agent_outputs)
    return report.total_count, report.critical_count
