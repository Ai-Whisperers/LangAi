"""
Deep Research Agent (Phase 13.1).

Advanced research capabilities:
- Multi-source data aggregation
- Iterative query refinement
- Research gap identification
- Source cross-validation
- Comprehensive data extraction

This agent performs deep, multi-iteration research to gather
comprehensive information about a company.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from anthropic import Anthropic

from ..config import get_config
from ..state import OverallState


# ============================================================================
# Data Models
# ============================================================================

class ResearchDepth(str, Enum):
    """Depth levels for research."""
    SURFACE = "surface"      # Quick overview
    STANDARD = "standard"    # Normal research
    DEEP = "deep"           # Comprehensive
    EXHAUSTIVE = "exhaustive"  # Maximum depth


class DataQuality(str, Enum):
    """Quality levels for extracted data."""
    VERIFIED = "verified"      # Cross-validated
    HIGH = "high"             # Single reliable source
    MEDIUM = "medium"         # Somewhat reliable
    LOW = "low"               # Uncertain
    UNVERIFIED = "unverified"  # Not validated


@dataclass
class ResearchQuery:
    """A research query with metadata."""
    query: str
    priority: int  # 1-10
    category: str
    answered: bool = False
    answer: str = ""
    sources: List[str] = field(default_factory=list)
    quality: DataQuality = DataQuality.UNVERIFIED


@dataclass
class ExtractedFact:
    """A fact extracted during research."""
    content: str
    category: str
    source: str
    confidence: float  # 0-1
    supporting_sources: List[str] = field(default_factory=list)
    quality: DataQuality = DataQuality.MEDIUM

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "category": self.category,
            "source": self.source,
            "confidence": self.confidence,
            "quality": self.quality.value
        }


@dataclass
class ResearchState:
    """State tracking for deep research."""
    company_name: str
    queries: List[ResearchQuery] = field(default_factory=list)
    facts: List[ExtractedFact] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    iterations: int = 0
    max_iterations: int = 3
    total_sources: int = 0

    def add_query(self, query: str, priority: int, category: str) -> None:
        """Add a research query."""
        self.queries.append(ResearchQuery(
            query=query,
            priority=priority,
            category=category
        ))

    def add_fact(self, fact: ExtractedFact) -> None:
        """Add an extracted fact."""
        self.facts.append(fact)

    def get_unanswered_queries(self) -> List[ResearchQuery]:
        """Get queries that haven't been answered."""
        return [q for q in self.queries if not q.answered]

    def get_facts_by_category(self, category: str) -> List[ExtractedFact]:
        """Get facts for a category."""
        return [f for f in self.facts if f.category == category]


# ============================================================================
# Prompts
# ============================================================================

DEEP_RESEARCH_PROMPT = """You are an expert research analyst conducting deep research on {company_name}.

**RESEARCH DEPTH:** {depth}
**ITERATION:** {iteration}/{max_iterations}

**CURRENT SEARCH RESULTS:**
{search_results}

**FACTS ALREADY GATHERED:**
{existing_facts}

**IDENTIFIED GAPS:**
{gaps}

**TASK:**
Perform comprehensive research analysis. Extract ALL verifiable facts and identify gaps.

**STRUCTURE YOUR ANALYSIS:**

### 1. Key Facts Extracted
For each fact, provide:
- **Fact:** [The factual statement]
- **Category:** [financial/market/product/operational/strategic]
- **Confidence:** [HIGH/MEDIUM/LOW]
- **Source:** [Where this fact comes from]

Extract at least 10-15 distinct facts.

### 2. Data Cross-Validation
Identify which facts are supported by multiple sources:
- [Fact] - Supported by: [Source 1], [Source 2]

### 3. Research Gaps
List information that is still missing or unclear:
1. [Gap 1]: What specific data is needed
2. [Gap 2]: What specific data is needed
...

### 4. Follow-up Queries
Suggest specific queries to fill the gaps:
1. "[Specific search query]" - To find [what information]
2. "[Specific search query]" - To find [what information]
...

### 5. Confidence Assessment
Rate overall data completeness:
- **Financial Data:** [COMPLETE/PARTIAL/MINIMAL]
- **Market Data:** [COMPLETE/PARTIAL/MINIMAL]
- **Product Data:** [COMPLETE/PARTIAL/MINIMAL]
- **Competitive Data:** [COMPLETE/PARTIAL/MINIMAL]

### 6. Key Findings Summary
Summarize the most important discoveries (3-5 bullet points).

**REQUIREMENTS:**
- Be thorough and extract ALL available data
- Clearly distinguish facts from speculation
- Cite sources for each fact
- Identify contradictions if any exist
- Suggest specific follow-up research

Begin your deep research analysis:"""


QUERY_GENERATION_PROMPT = """Based on the research gaps identified for {company_name}:

**GAPS:**
{gaps}

**ALREADY SEARCHED:**
{previous_queries}

Generate 5-7 specific, targeted search queries to fill these gaps.

Format each query on its own line:
1. [query] | Priority: [1-10] | Category: [financial/market/product/competitive]
2. ...

Focus on queries that will yield specific, verifiable data."""


# ============================================================================
# Deep Research Agent
# ============================================================================

class DeepResearchAgent:
    """
    Deep Research Agent for comprehensive company research.

    Performs iterative research:
    1. Initial broad research
    2. Gap identification
    3. Targeted follow-up queries
    4. Cross-validation of facts
    5. Quality assessment

    Usage:
        agent = DeepResearchAgent()
        result = agent.research(
            company_name="Tesla",
            search_results=initial_results,
            depth=ResearchDepth.DEEP
        )
    """

    def __init__(self, config=None):
        """Initialize agent."""
        self._config = config or get_config()
        self._client = Anthropic(api_key=self._config.anthropic_api_key)

    def research(
        self,
        company_name: str,
        search_results: List[Dict[str, Any]],
        depth: ResearchDepth = ResearchDepth.STANDARD,
        max_iterations: int = 2
    ) -> Dict[str, Any]:
        """
        Perform deep research on a company.

        Args:
            company_name: Company to research
            search_results: Initial search results
            depth: Research depth level
            max_iterations: Maximum research iterations

        Returns:
            Research results dictionary
        """
        # Initialize research state
        state = ResearchState(
            company_name=company_name,
            max_iterations=max_iterations,
            total_sources=len(search_results)
        )

        total_cost = 0.0
        total_tokens = {"input": 0, "output": 0}

        # Iteration loop
        while state.iterations < state.max_iterations:
            state.iterations += 1
            print(f"\n[DeepResearch] Iteration {state.iterations}/{state.max_iterations}")

            # Perform research iteration
            result = self._research_iteration(
                state=state,
                search_results=search_results,
                depth=depth
            )

            total_cost += result["cost"]
            total_tokens["input"] += result["tokens"]["input"]
            total_tokens["output"] += result["tokens"]["output"]

            # Extract facts from result
            self._extract_facts_from_analysis(state, result["analysis"])

            # Check if we have enough data
            if self._is_research_complete(state, depth):
                print("[DeepResearch] Research complete - sufficient data gathered")
                break

            # Generate follow-up queries if more iterations
            if state.iterations < state.max_iterations:
                new_queries = self._generate_follow_up_queries(state)
                state.queries.extend(new_queries)

        # Compile final results
        return {
            "company_name": company_name,
            "facts": [f.to_dict() for f in state.facts],
            "gaps": state.gaps,
            "iterations": state.iterations,
            "total_sources": state.total_sources,
            "data_quality": self._assess_overall_quality(state),
            "summary": self._generate_summary(state),
            "cost": total_cost,
            "tokens": total_tokens
        }

    def _research_iteration(
        self,
        state: ResearchState,
        search_results: List[Dict[str, Any]],
        depth: ResearchDepth
    ) -> Dict[str, Any]:
        """Perform single research iteration."""
        # Format existing facts
        existing_facts = self._format_existing_facts(state.facts)

        # Format gaps
        gaps = "\n".join(f"- {gap}" for gap in state.gaps) if state.gaps else "None identified yet"

        # Format search results
        formatted_results = self._format_search_results(search_results)

        prompt = DEEP_RESEARCH_PROMPT.format(
            company_name=state.company_name,
            depth=depth.value.upper(),
            iteration=state.iterations,
            max_iterations=state.max_iterations,
            search_results=formatted_results,
            existing_facts=existing_facts,
            gaps=gaps
        )

        # Call LLM
        response = self._client.messages.create(
            model=self._config.llm_model,
            max_tokens=2000,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}]
        )

        cost = self._config.calculate_llm_cost(
            response.usage.input_tokens,
            response.usage.output_tokens
        )

        return {
            "analysis": response.content[0].text,
            "cost": cost,
            "tokens": {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens
            }
        }

    def _extract_facts_from_analysis(
        self,
        state: ResearchState,
        analysis: str
    ) -> None:
        """Extract structured facts from analysis text."""
        lines = analysis.split("\n")
        current_category = "general"

        for line in lines:
            line = line.strip()

            # Detect category
            if "financial" in line.lower():
                current_category = "financial"
            elif "market" in line.lower():
                current_category = "market"
            elif "product" in line.lower():
                current_category = "product"
            elif "competitive" in line.lower():
                current_category = "competitive"

            # Extract facts (look for "Fact:" pattern)
            if line.startswith("- **Fact:**") or line.startswith("**Fact:**"):
                fact_content = line.replace("- **Fact:**", "").replace("**Fact:**", "").strip()

                # Determine confidence
                confidence = 0.7  # Default
                if "HIGH" in analysis[analysis.find(fact_content):analysis.find(fact_content)+200]:
                    confidence = 0.9
                elif "LOW" in analysis[analysis.find(fact_content):analysis.find(fact_content)+200]:
                    confidence = 0.5

                state.add_fact(ExtractedFact(
                    content=fact_content,
                    category=current_category,
                    source="deep_research",
                    confidence=confidence
                ))

            # Extract gaps
            if "Gap" in line or "missing" in line.lower() or "unclear" in line.lower():
                # Look for gap descriptions
                if ":" in line:
                    gap = line.split(":", 1)[1].strip()
                    if gap and len(gap) > 10 and gap not in state.gaps:
                        state.gaps.append(gap)

    def _generate_follow_up_queries(self, state: ResearchState) -> List[ResearchQuery]:
        """Generate follow-up queries based on gaps."""
        if not state.gaps:
            return []

        # Format previous queries
        prev = "\n".join(q.query for q in state.queries)

        prompt = QUERY_GENERATION_PROMPT.format(
            company_name=state.company_name,
            gaps="\n".join(f"- {g}" for g in state.gaps[:5]),
            previous_queries=prev or "None"
        )

        response = self._client.messages.create(
            model=self._config.llm_model,
            max_tokens=500,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse queries from response
        queries = []
        for line in response.content[0].text.split("\n"):
            if "|" in line and "Priority" in line:
                parts = line.split("|")
                if len(parts) >= 2:
                    query_text = parts[0].strip().lstrip("0123456789. ")
                    priority = 5  # Default
                    category = "general"

                    for part in parts[1:]:
                        if "Priority" in part:
                            try:
                                priority = int(part.split(":")[1].strip())
                            except (ValueError, IndexError):
                                pass
                        if "Category" in part:
                            category = part.split(":")[1].strip().lower()

                    queries.append(ResearchQuery(
                        query=query_text,
                        priority=priority,
                        category=category
                    ))

        return queries[:5]  # Limit queries

    def _format_existing_facts(self, facts: List[ExtractedFact]) -> str:
        """Format facts for prompt."""
        if not facts:
            return "No facts gathered yet"

        by_category = {}
        for fact in facts:
            if fact.category not in by_category:
                by_category[fact.category] = []
            by_category[fact.category].append(fact)

        lines = []
        for category, cat_facts in by_category.items():
            lines.append(f"\n**{category.upper()}:**")
            for f in cat_facts[:5]:  # Limit per category
                lines.append(f"- {f.content} (Confidence: {f.confidence:.0%})")

        return "\n".join(lines)

    def _format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for prompt."""
        if not results:
            return "No search results available"

        formatted = []
        for i, r in enumerate(results[:15], 1):
            formatted.append(
                f"Source {i}: {r.get('title', 'N/A')}\n"
                f"URL: {r.get('url', 'N/A')}\n"
                f"Content: {r.get('content', '')[:500]}...\n"
            )

        return "\n".join(formatted)

    def _is_research_complete(self, state: ResearchState, depth: ResearchDepth) -> bool:
        """Check if research is sufficiently complete."""
        min_facts = {
            ResearchDepth.SURFACE: 5,
            ResearchDepth.STANDARD: 10,
            ResearchDepth.DEEP: 20,
            ResearchDepth.EXHAUSTIVE: 30
        }

        return len(state.facts) >= min_facts.get(depth, 10)

    def _assess_overall_quality(self, state: ResearchState) -> Dict[str, str]:
        """Assess data quality by category."""
        categories = ["financial", "market", "product", "competitive"]
        quality = {}

        for cat in categories:
            cat_facts = state.get_facts_by_category(cat)
            if len(cat_facts) >= 5:
                quality[cat] = "COMPLETE"
            elif len(cat_facts) >= 2:
                quality[cat] = "PARTIAL"
            else:
                quality[cat] = "MINIMAL"

        return quality

    def _generate_summary(self, state: ResearchState) -> str:
        """Generate research summary."""
        summary_parts = [
            f"Deep research completed for {state.company_name}.",
            f"Iterations: {state.iterations}",
            f"Facts extracted: {len(state.facts)}",
            f"Data gaps remaining: {len(state.gaps)}"
        ]

        # Add top facts
        top_facts = sorted(state.facts, key=lambda f: f.confidence, reverse=True)[:3]
        if top_facts:
            summary_parts.append("\nKey findings:")
            for f in top_facts:
                summary_parts.append(f"- {f.content}")

        return "\n".join(summary_parts)


# ============================================================================
# Agent Node Function
# ============================================================================

def deep_research_agent_node(state: OverallState) -> Dict[str, Any]:
    """
    Deep Research Agent Node for workflow integration.

    Args:
        state: Current workflow state

    Returns:
        State update with deep research results
    """
    print("\n" + "=" * 70)
    print("[AGENT: Deep Research] Comprehensive research analysis...")
    print("=" * 70)

    company_name = state["company_name"]
    search_results = state.get("search_results", [])

    if not search_results:
        print("[DeepResearch] WARNING: No search results available!")
        return {
            "agent_outputs": {
                "deep_research": {
                    "analysis": "No search results available",
                    "facts": [],
                    "cost": 0.0
                }
            }
        }

    # Determine depth from config or default
    depth = ResearchDepth.STANDARD

    # Run deep research
    agent = DeepResearchAgent()
    result = agent.research(
        company_name=company_name,
        search_results=search_results,
        depth=depth,
        max_iterations=2
    )

    print(f"[DeepResearch] Extracted {len(result['facts'])} facts")
    print(f"[DeepResearch] Identified {len(result['gaps'])} gaps")
    print(f"[DeepResearch] Cost: ${result['cost']:.4f}")
    print("=" * 70)

    return {
        "agent_outputs": {"deep_research": result},
        "total_cost": result["cost"],
        "total_tokens": result["tokens"]
    }


# ============================================================================
# Factory Function
# ============================================================================

def create_deep_research_agent() -> DeepResearchAgent:
    """Create a Deep Research Agent instance."""
    return DeepResearchAgent()
