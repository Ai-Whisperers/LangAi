"""
Semantic Gap Detection Module.

Replaces regex-based gap detection with multi-signal semantic analysis.
Detects real gaps even when LLM doesn't explicitly say "data not available".

Key improvements over pattern-based detection:
1. Keyword presence vs substance check
2. Source authority validation
3. Cross-agent consistency
4. Coverage level assessment (not just binary)
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class GapConfidence(Enum):
    """Confidence level that a gap exists."""
    CONFIRMED = "confirmed"      # Definitely missing - multiple signals
    LIKELY = "likely"            # Probably missing - strong signals
    POSSIBLE = "possible"        # Might be missing - some signals
    COVERED = "covered"          # Information appears present


class CoverageLevel(Enum):
    """Level of coverage for a field."""
    COMPREHENSIVE = "comprehensive"  # Multiple specific data points
    ADEQUATE = "adequate"            # Basic information present
    PARTIAL = "partial"              # Mentioned but incomplete
    ABSENT = "absent"                # Not covered at all
    NEGATIVE = "negative"            # Explicitly stated as unavailable


@dataclass
class GapAssessment:
    """Assessment of a gap in research coverage."""
    category: str
    field: str
    confidence: GapConfidence
    coverage_level: CoverageLevel
    signals: List[str]
    evidence: List[str]
    recommendation: str
    priority: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category,
            "field": self.field,
            "confidence": self.confidence.value,
            "coverage_level": self.coverage_level.value,
            "signals": self.signals,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "priority": self.priority
        }


@dataclass
class CoverageAssessment:
    """Detailed coverage assessment for a field."""
    level: CoverageLevel
    evidence: List[str]
    specific_mentions: int
    has_authoritative_source: bool = False


# Field requirements with patterns for substantive coverage
FIELD_REQUIREMENTS = {
    "financial": {
        "revenue": {
            "keywords": ["revenue", "sales", "annual revenue", "quarterly revenue"],
            "required_patterns": [
                r"revenue\s+(?:of|was|reached|totaled)\s+\$?[\d,.]+",
                r"\$[\d,.]+(?:B|M|billion|million)\s+(?:in\s+)?revenue",
            ],
            "negative_patterns": [
                r"revenue\s+(?:not|isn't|wasn't)\s+(?:available|disclosed|reported)",
                r"(?:no|undisclosed)\s+revenue\s+(?:data|information|figures)",
                r"revenue.*data not available",
            ],
            "min_specific_mentions": 2,
            "priority": 10,
            "authoritative_domains": ["sec.gov", "investor.", "ir.", "10-K", "10-Q"]
        },
        "profit_margin": {
            "keywords": ["profit margin", "gross margin", "operating margin", "net margin"],
            "required_patterns": [
                r"(?:profit|gross|operating|net)\s+margin\s+(?:of|was|at)\s+[\d,.]+%",
                r"[\d,.]+%\s+(?:profit|gross|operating|net)\s+margin",
            ],
            "negative_patterns": [
                r"margin\s+(?:not|isn't)\s+(?:available|disclosed)",
            ],
            "min_specific_mentions": 1,
            "priority": 8,
            "authoritative_domains": ["sec.gov", "investor.", "yahoo"]
        },
        "market_cap": {
            "keywords": ["market cap", "market capitalization", "valuation"],
            "required_patterns": [
                r"market\s+cap(?:italization)?\s+(?:of|is|was|at)\s+\$?[\d,.]+",
                r"\$[\d,.]+(?:T|B|M|trillion|billion|million)\s+(?:market\s+)?(?:cap|valuation)",
            ],
            "negative_patterns": [
                r"market\s+cap(?:italization)?\s+(?:not|isn't)\s+(?:available|disclosed)",
            ],
            "min_specific_mentions": 1,
            "priority": 9,
            "authoritative_domains": ["yahoo", "bloomberg", "reuters"]
        },
        "pe_ratio": {
            "keywords": ["p/e ratio", "pe ratio", "price to earnings", "price-to-earnings"],
            "required_patterns": [
                r"(?:P/?E|price[- ]?(?:to[- ])?earnings)\s+(?:ratio\s+)?(?:of|is|at)\s*[\d.]+",
            ],
            "negative_patterns": [
                r"P/?E\s+(?:ratio\s+)?(?:not|isn't)\s+(?:available|applicable)",
            ],
            "min_specific_mentions": 1,
            "priority": 7,
            "authoritative_domains": ["yahoo", "bloomberg"]
        }
    },
    "market": {
        "market_share": {
            "keywords": ["market share", "share of market", "market position"],
            "required_patterns": [
                r"market\s+share\s+(?:of|at|around)\s+[\d,.]+%",
                r"[\d,.]+%\s+(?:of\s+the\s+)?market",
                r"(?:holds?|commands?|captures?)\s+[\d,.]+%",
            ],
            "negative_patterns": [
                r"market\s+share\s+(?:not|isn't)\s+(?:known|available|disclosed)",
            ],
            "min_specific_mentions": 1,
            "priority": 8,
            "authoritative_domains": ["statista", "ibisworld", "gartner"]
        },
        "market_size": {
            "keywords": ["market size", "TAM", "total addressable market", "industry size"],
            "required_patterns": [
                r"(?:market|industry)\s+size\s+(?:of|is|was|estimated\s+at)\s+\$?[\d,.]+",
                r"(?:TAM|total\s+addressable\s+market)\s+(?:of|is)\s+\$?[\d,.]+",
            ],
            "negative_patterns": [
                r"market\s+size\s+(?:not|isn't)\s+(?:known|available)",
            ],
            "min_specific_mentions": 1,
            "priority": 7,
            "authoritative_domains": ["statista", "grandviewresearch", "marketsandmarkets"]
        },
        "competitors": {
            "keywords": ["competitor", "competition", "rival", "competitive landscape"],
            "required_patterns": [
                r"(?:main|key|primary|major)\s+competitors?\s+(?:include|are|is)",
                r"competes?\s+(?:with|against)",
            ],
            "negative_patterns": [
                r"competitors?\s+(?:not|aren't)\s+(?:known|identified)",
            ],
            "min_specific_mentions": 2,
            "priority": 6,
            "authoritative_domains": []
        }
    },
    "company": {
        "employees": {
            "keywords": ["employee", "staff", "workforce", "headcount"],
            "required_patterns": [
                r"[\d,]+\s*(?:full[- ]?time\s+)?employees",
                r"(?:employs?|workforce\s+of|headcount\s+of)\s*[\d,]+",
            ],
            "negative_patterns": [
                r"employee\s+(?:count|number)\s+(?:not|isn't)\s+(?:known|available)",
            ],
            "min_specific_mentions": 1,
            "priority": 5,
            "authoritative_domains": ["linkedin", "yahoo"]
        },
        "headquarters": {
            "keywords": ["headquarters", "HQ", "based in", "headquartered"],
            "required_patterns": [
                r"(?:headquarters?|HQ|based)\s+(?:in|at)\s+[A-Z][a-z]+",
                r"headquartered\s+in\s+[A-Z][a-z]+",
            ],
            "negative_patterns": [],
            "min_specific_mentions": 1,
            "priority": 4,
            "authoritative_domains": []
        },
        "founded": {
            "keywords": ["founded", "established", "started", "inception"],
            "required_patterns": [
                r"(?:founded|established|started)\s+(?:in\s+)?\d{4}",
            ],
            "negative_patterns": [],
            "min_specific_mentions": 1,
            "priority": 3,
            "authoritative_domains": []
        },
        "ceo": {
            "keywords": ["CEO", "chief executive", "founder", "leader"],
            "required_patterns": [
                r"CEO\s+(?:is|was)?\s*[A-Z][a-z]+\s+[A-Z][a-z]+",
                r"[A-Z][a-z]+\s+[A-Z][a-z]+\s+(?:is\s+(?:the\s+)?)?CEO",
            ],
            "negative_patterns": [],
            "min_specific_mentions": 1,
            "priority": 6,
            "authoritative_domains": ["linkedin", "bloomberg"]
        }
    },
    "product": {
        "products": {
            "keywords": ["product", "service", "offering", "solution"],
            "required_patterns": [
                r"(?:main|key|primary|flagship)\s+products?\s+(?:include|are|is)",
                r"offers?\s+(?:a\s+)?(?:range|variety|suite)\s+of",
            ],
            "negative_patterns": [
                r"products?\s+(?:not|aren't)\s+(?:known|detailed)",
            ],
            "min_specific_mentions": 2,
            "priority": 7,
            "authoritative_domains": []
        },
        "technology": {
            "keywords": ["technology", "tech stack", "platform", "infrastructure"],
            "required_patterns": [
                r"(?:built|powered|developed)\s+(?:on|with|using)",
                r"technology\s+(?:stack|platform)\s+(?:includes?|consists?)",
            ],
            "negative_patterns": [],
            "min_specific_mentions": 1,
            "priority": 5,
            "authoritative_domains": []
        }
    }
}


class SemanticGapDetector:
    """
    Multi-signal gap detection using semantic analysis.

    Key detection signals:
    1. Explicit gap patterns ("data not available")
    2. Keyword without substance (mentions "revenue" but no actual figures)
    3. No authoritative source
    4. Cross-agent inconsistency
    5. Pattern match failure

    Usage:
        detector = SemanticGapDetector()
        gaps = detector.detect_gaps(report_text, sources, agent_outputs)
    """

    def __init__(self, llm_client: Any = None):
        """
        Initialize detector.

        Args:
            llm_client: Optional LLM client for semantic verification
        """
        self.llm_client = llm_client
        self._compiled_patterns: Dict[str, Dict] = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for efficiency."""
        for section, fields in FIELD_REQUIREMENTS.items():
            self._compiled_patterns[section] = {}
            for field_name, config in fields.items():
                self._compiled_patterns[section][field_name] = {
                    "required": [re.compile(p, re.IGNORECASE) for p in config["required_patterns"]],
                    "negative": [re.compile(p, re.IGNORECASE) for p in config["negative_patterns"]]
                }

    def detect_gaps(
        self,
        report_text: str,
        sources: List[Dict],
        agent_outputs: Dict[str, Any]
    ) -> List[GapAssessment]:
        """
        Detect gaps using multiple signals.

        Args:
            report_text: Generated report text
            sources: List of source dictionaries
            agent_outputs: Output from each agent

        Returns:
            List of gap assessments, sorted by priority
        """
        gaps = []

        # Combine all text for analysis
        all_text = self._combine_text(report_text, agent_outputs)

        for section, fields in FIELD_REQUIREMENTS.items():
            for field_name, config in fields.items():
                signals = []
                evidence = []

                # Signal 1: Check for explicit "not available" patterns
                has_explicit_gap = self._check_explicit_gap_patterns(
                    all_text, field_name, section
                )
                if has_explicit_gap:
                    signals.append("explicit_gap_phrase")
                    evidence.append("Found explicit 'not available' statement")

                # Signal 2: Check keyword presence vs substance
                coverage = self._assess_field_coverage(
                    all_text, field_name, section
                )

                if coverage.level == CoverageLevel.NEGATIVE:
                    signals.append("explicit_unavailable")
                    evidence.extend(coverage.evidence)
                elif coverage.level == CoverageLevel.ABSENT:
                    signals.append("no_keyword_mention")
                    evidence.append(f"No mention of {field_name}")
                elif coverage.level == CoverageLevel.PARTIAL:
                    signals.append("keyword_without_data")
                    evidence.append(f"Mentioned {field_name} without specific data")
                    evidence.extend(coverage.evidence)

                # Signal 3: Check source authority
                has_authoritative = self._check_source_authority(
                    sources, config.get("authoritative_domains", [])
                )
                if not has_authoritative and config.get("authoritative_domains"):
                    signals.append("no_authoritative_source")
                    evidence.append("No authoritative source found")

                # Signal 4: Cross-agent consistency
                agent_gap = self._check_agent_coverage(
                    agent_outputs, field_name, section
                )
                if agent_gap:
                    signals.append("agent_gap")
                    evidence.append(agent_gap)

                # Determine confidence and coverage from signals
                confidence = self._calculate_confidence(signals)
                final_coverage = coverage.level

                if confidence != GapConfidence.COVERED:
                    gaps.append(GapAssessment(
                        category=section,
                        field=field_name,
                        confidence=confidence,
                        coverage_level=final_coverage,
                        signals=signals,
                        evidence=evidence,
                        recommendation=self._generate_recommendation(field_name, section, signals),
                        priority=self._calculate_priority(config["priority"], confidence)
                    ))

        return sorted(gaps, key=lambda g: g.priority, reverse=True)

    def _combine_text(self, report_text: str, agent_outputs: Dict[str, Any]) -> str:
        """Combine all text sources for analysis."""
        parts = [report_text]

        for agent_name, output in agent_outputs.items():
            if isinstance(output, dict):
                for key in ['analysis', 'content', 'company_overview',
                           'financial_analysis', 'market_analysis']:
                    if key in output and isinstance(output[key], str):
                        parts.append(output[key])
            elif isinstance(output, str):
                parts.append(output)

        return "\n\n".join(parts)

    def _check_explicit_gap_patterns(
        self,
        text: str,
        field_name: str,
        section: str
    ) -> bool:
        """Check for explicit 'not available' patterns."""
        patterns = self._compiled_patterns.get(section, {}).get(field_name, {})
        negative_patterns = patterns.get("negative", [])

        for pattern in negative_patterns:
            if pattern.search(text):
                return True

        return False

    def _assess_field_coverage(
        self,
        text: str,
        field_name: str,
        section: str
    ) -> CoverageAssessment:
        """Assess coverage level for a specific field."""
        config = FIELD_REQUIREMENTS[section][field_name]
        patterns = self._compiled_patterns[section][field_name]

        evidence = []

        # Check for negative patterns first (explicit "not available")
        for pattern in patterns["negative"]:
            match = pattern.search(text)
            if match:
                evidence.append(f"Negative: '{match.group()}'")
                return CoverageAssessment(
                    level=CoverageLevel.NEGATIVE,
                    evidence=evidence,
                    specific_mentions=0
                )

        # Check keyword presence
        text_lower = text.lower()
        keyword_found = any(kw.lower() in text_lower for kw in config["keywords"])

        # Count specific mentions (pattern matches)
        specific_mentions = 0
        for pattern in patterns["required"]:
            matches = pattern.findall(text)
            for match in matches:
                specific_mentions += 1
                if isinstance(match, tuple):
                    match = match[0]
                evidence.append(f"Found: '{match[:50]}...'")

        # Determine coverage level
        min_required = config["min_specific_mentions"]

        if specific_mentions >= min_required * 2:
            level = CoverageLevel.COMPREHENSIVE
        elif specific_mentions >= min_required:
            level = CoverageLevel.ADEQUATE
        elif specific_mentions > 0 or keyword_found:
            level = CoverageLevel.PARTIAL
        else:
            level = CoverageLevel.ABSENT

        return CoverageAssessment(
            level=level,
            evidence=evidence,
            specific_mentions=specific_mentions
        )

    def _check_source_authority(
        self,
        sources: List[Dict],
        authoritative_domains: List[str]
    ) -> bool:
        """Check if any source is from authoritative domain."""
        if not authoritative_domains:
            return True  # No authority requirement

        for source in sources:
            url = source.get("url", "").lower()
            for domain in authoritative_domains:
                if domain.lower() in url:
                    return True

        return False

    def _check_agent_coverage(
        self,
        agent_outputs: Dict[str, Any],
        field_name: str,
        section: str
    ) -> Optional[str]:
        """Check for cross-agent coverage issues."""
        # Map sections to expected agents
        section_agents = {
            "financial": ["financial", "synthesizer"],
            "market": ["market", "competitor", "synthesizer"],
            "company": ["researcher", "synthesizer"],
            "product": ["product", "synthesizer"]
        }

        expected_agents = section_agents.get(section, [])
        found_in = []

        for agent in expected_agents:
            output = agent_outputs.get(agent, {})
            if isinstance(output, dict):
                # Check if field-related content exists
                for key, value in output.items():
                    if isinstance(value, str) and field_name.lower() in value.lower():
                        found_in.append(agent)
                        break

        if not found_in and expected_agents:
            return f"Expected in {expected_agents} agents, found in none"

        return None

    def _calculate_confidence(self, signals: List[str]) -> GapConfidence:
        """Calculate gap confidence from signals."""
        critical_signals = {"explicit_gap_phrase", "explicit_unavailable", "no_keyword_mention"}
        warning_signals = {"keyword_without_data", "no_authoritative_source", "agent_gap"}

        critical_count = len(set(signals) & critical_signals)
        warning_count = len(set(signals) & warning_signals)

        if critical_count >= 1:
            return GapConfidence.CONFIRMED
        elif warning_count >= 2:
            return GapConfidence.LIKELY
        elif warning_count >= 1:
            return GapConfidence.POSSIBLE
        return GapConfidence.COVERED

    def _calculate_priority(self, base_priority: int, confidence: GapConfidence) -> int:
        """Calculate final priority based on base and confidence."""
        confidence_multiplier = {
            GapConfidence.CONFIRMED: 1.0,
            GapConfidence.LIKELY: 0.8,
            GapConfidence.POSSIBLE: 0.5,
            GapConfidence.COVERED: 0.0
        }
        return int(base_priority * confidence_multiplier[confidence])

    def _generate_recommendation(
        self,
        field_name: str,
        section: str,
        signals: List[str]
    ) -> str:
        """Generate recommendation for addressing the gap."""
        config = FIELD_REQUIREMENTS[section][field_name]

        if "explicit_gap_phrase" in signals or "explicit_unavailable" in signals:
            return f"Search for {field_name} data from {', '.join(config.get('authoritative_domains', ['authoritative sources']))}"

        if "no_keyword_mention" in signals:
            return f"Add search queries specifically for {field_name}"

        if "keyword_without_data" in signals:
            return f"Found mention of {field_name} but no specific data. Verify and add concrete numbers/facts."

        if "no_authoritative_source" in signals:
            domains = config.get('authoritative_domains', [])
            if domains:
                return f"Add authoritative source from: {', '.join(domains)}"

        return f"Review {field_name} coverage in {section} section"

    def get_gap_summary(self, gaps: List[GapAssessment]) -> Dict[str, Any]:
        """Generate summary of all gaps."""
        confirmed = [g for g in gaps if g.confidence == GapConfidence.CONFIRMED]
        likely = [g for g in gaps if g.confidence == GapConfidence.LIKELY]
        possible = [g for g in gaps if g.confidence == GapConfidence.POSSIBLE]

        return {
            "total_gaps": len(gaps),
            "confirmed_count": len(confirmed),
            "likely_count": len(likely),
            "possible_count": len(possible),
            "high_priority_gaps": [g.field for g in gaps if g.priority >= 7],
            "by_section": self._group_by_section(gaps),
            "top_recommendations": [g.recommendation for g in gaps[:5]]
        }

    def _group_by_section(self, gaps: List[GapAssessment]) -> Dict[str, List[str]]:
        """Group gaps by section."""
        result = {}
        for gap in gaps:
            if gap.category not in result:
                result[gap.category] = []
            result[gap.category].append(gap.field)
        return result
