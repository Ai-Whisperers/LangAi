"""
Prompt Management System.

Addresses Issue #10: LLM Usage Patterns.

Provides versioned, testable prompts with:
1. Central prompt registry
2. Version tracking for A/B testing
3. Template interpolation with validation
4. Prompt evaluation metrics
5. Easy prompt iteration without code changes

Usage:
    registry = get_prompt_registry()

    # Get current prompt for a task
    prompt = registry.get_prompt("financial_analysis")

    # Use specific version
    prompt_v2 = registry.get_prompt("financial_analysis", version="2.0")

    # Register custom prompt
    registry.register_prompt(
        "my_prompt",
        "Analyze {company} focusing on {aspect}",
        version="1.0"
    )
"""

import re
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class PromptCategory(Enum):
    """Categories of prompts."""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    QUALITY = "quality"
    EXTRACTION = "extraction"
    FORMATTING = "formatting"


@dataclass
class PromptMetrics:
    """Metrics for evaluating prompt performance."""
    total_uses: int = 0
    avg_response_quality: float = 0.0
    avg_tokens_used: int = 0
    avg_latency_ms: float = 0.0
    success_rate: float = 1.0
    last_used: Optional[datetime] = None

    def record_use(
        self,
        quality_score: float = 1.0,
        tokens_used: int = 0,
        latency_ms: float = 0.0,
        success: bool = True
    ):
        """Record a prompt use."""
        self.total_uses += 1
        self.last_used = datetime.now()

        # Running averages
        n = self.total_uses
        self.avg_response_quality = (
            (self.avg_response_quality * (n - 1) + quality_score) / n
        )
        self.avg_tokens_used = int(
            (self.avg_tokens_used * (n - 1) + tokens_used) / n
        )
        self.avg_latency_ms = (
            (self.avg_latency_ms * (n - 1) + latency_ms) / n
        )

        # Success rate
        if not success:
            self.success_rate = (
                (self.success_rate * (n - 1) + 0) / n
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_uses": self.total_uses,
            "avg_response_quality": round(self.avg_response_quality, 3),
            "avg_tokens_used": self.avg_tokens_used,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "success_rate": round(self.success_rate, 3),
            "last_used": self.last_used.isoformat() if self.last_used else None
        }


@dataclass
class PromptVersion:
    """A versioned prompt template."""
    name: str
    template: str
    version: str
    category: PromptCategory = PromptCategory.RESEARCH
    description: str = ""
    required_vars: List[str] = field(default_factory=list)
    optional_vars: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    metrics: PromptMetrics = field(default_factory=PromptMetrics)

    def __post_init__(self):
        """Extract required variables from template."""
        if not self.required_vars:
            self.required_vars = self._extract_variables(self.template)

    @staticmethod
    def _extract_variables(template: str) -> List[str]:
        """Extract variable names from template."""
        # Match {variable} patterns but not {{escaped}}
        pattern = r'(?<!\{)\{([^{}]+)\}(?!\})'
        matches = re.findall(pattern, template)
        return list(set(matches))

    def render(self, **kwargs) -> str:
        """
        Render the prompt template with provided variables.

        Args:
            **kwargs: Variable values to substitute

        Returns:
            Rendered prompt string

        Raises:
            ValueError: If required variables are missing
        """
        # Check required variables
        missing = [v for v in self.required_vars if v not in kwargs]
        if missing:
            raise ValueError(f"Missing required variables: {missing}")

        # Merge with defaults
        all_vars = {**self.optional_vars, **kwargs}

        # Render template
        try:
            return self.template.format(**all_vars)
        except KeyError as e:
            raise ValueError(f"Unknown variable in template: {e}")

    def validate(self, **kwargs) -> Tuple[bool, List[str]]:
        """
        Validate that all required variables are provided.

        Returns:
            Tuple of (is_valid, list of missing variables)
        """
        missing = [v for v in self.required_vars if v not in kwargs]
        return (len(missing) == 0, missing)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "category": self.category.value,
            "description": self.description,
            "template": self.template,
            "required_vars": self.required_vars,
            "optional_vars": self.optional_vars,
            "is_active": self.is_active,
            "metrics": self.metrics.to_dict()
        }


class PromptRegistry:
    """
    Central registry for managing prompt versions.

    Features:
    - Version management (multiple versions per prompt name)
    - Active version selection
    - Template validation
    - Usage metrics tracking
    - Serialization for persistence
    """

    def __init__(self):
        self._prompts: Dict[str, Dict[str, PromptVersion]] = {}  # name -> version -> prompt
        self._active_versions: Dict[str, str] = {}  # name -> active version
        self._load_default_prompts()

    def register_prompt(
        self,
        name: str,
        template: str,
        version: str = "1.0",
        category: PromptCategory = PromptCategory.RESEARCH,
        description: str = "",
        optional_vars: Optional[Dict[str, Any]] = None,
        set_active: bool = True
    ) -> PromptVersion:
        """
        Register a new prompt version.

        Args:
            name: Prompt identifier
            template: Prompt template with {variable} placeholders
            version: Version string
            category: Prompt category
            description: Human-readable description
            optional_vars: Default values for optional variables
            set_active: Whether to set this as the active version

        Returns:
            The created PromptVersion
        """
        prompt = PromptVersion(
            name=name,
            template=template,
            version=version,
            category=category,
            description=description,
            optional_vars=optional_vars or {}
        )

        if name not in self._prompts:
            self._prompts[name] = {}

        self._prompts[name][version] = prompt

        if set_active or name not in self._active_versions:
            self._active_versions[name] = version

        logger.info(f"Registered prompt '{name}' version {version}")
        return prompt

    def get_prompt(
        self,
        name: str,
        version: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Get a rendered prompt.

        Args:
            name: Prompt identifier
            version: Optional specific version (uses active if not specified)
            **kwargs: Variables to substitute in template

        Returns:
            Rendered prompt string
        """
        prompt_version = self.get_prompt_version(name, version)
        return prompt_version.render(**kwargs)

    def get_prompt_version(
        self,
        name: str,
        version: Optional[str] = None
    ) -> PromptVersion:
        """
        Get a PromptVersion object.

        Args:
            name: Prompt identifier
            version: Optional specific version

        Returns:
            PromptVersion object
        """
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found")

        target_version = version or self._active_versions.get(name)

        if target_version not in self._prompts[name]:
            raise KeyError(f"Version '{target_version}' not found for prompt '{name}'")

        return self._prompts[name][target_version]

    def set_active_version(self, name: str, version: str):
        """Set the active version for a prompt."""
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found")
        if version not in self._prompts[name]:
            raise KeyError(f"Version '{version}' not found for prompt '{name}'")

        self._active_versions[name] = version
        logger.info(f"Set active version for '{name}' to {version}")

    def list_prompts(self) -> List[Dict[str, Any]]:
        """List all registered prompts."""
        result = []
        for name, versions in self._prompts.items():
            active = self._active_versions.get(name)
            result.append({
                "name": name,
                "versions": list(versions.keys()),
                "active_version": active,
                "category": versions[active].category.value if active else None
            })
        return result

    def record_usage(
        self,
        name: str,
        version: Optional[str] = None,
        quality_score: float = 1.0,
        tokens_used: int = 0,
        latency_ms: float = 0.0,
        success: bool = True
    ):
        """Record usage metrics for a prompt."""
        prompt = self.get_prompt_version(name, version)
        prompt.metrics.record_use(
            quality_score=quality_score,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            success=success
        )

    def get_metrics(self, name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """Get usage metrics for a prompt."""
        prompt = self.get_prompt_version(name, version)
        return prompt.metrics.to_dict()

    def compare_versions(self, name: str) -> Dict[str, Dict[str, Any]]:
        """Compare metrics across all versions of a prompt."""
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found")

        return {
            version: prompt.metrics.to_dict()
            for version, prompt in self._prompts[name].items()
        }

    def export_prompts(self, path: Optional[Path] = None) -> Dict[str, Any]:
        """Export all prompts to JSON-serializable dict."""
        data = {
            "active_versions": self._active_versions,
            "prompts": {}
        }

        for name, versions in self._prompts.items():
            data["prompts"][name] = {
                v: p.to_dict() for v, p in versions.items()
            }

        if path:
            path.write_text(json.dumps(data, indent=2, default=str))
            logger.info(f"Exported prompts to {path}")

        return data

    def import_prompts(self, path: Path):
        """Import prompts from JSON file."""
        data = json.loads(path.read_text())

        for name, versions in data.get("prompts", {}).items():
            for version, prompt_data in versions.items():
                self.register_prompt(
                    name=prompt_data["name"],
                    template=prompt_data["template"],
                    version=prompt_data["version"],
                    category=PromptCategory(prompt_data.get("category", "research")),
                    description=prompt_data.get("description", ""),
                    optional_vars=prompt_data.get("optional_vars", {}),
                    set_active=False
                )

        # Set active versions
        for name, version in data.get("active_versions", {}).items():
            if name in self._prompts and version in self._prompts[name]:
                self._active_versions[name] = version

        logger.info(f"Imported prompts from {path}")

    def _load_default_prompts(self):
        """Load default prompts for the research system."""

        # =====================================================================
        # Research Prompts
        # =====================================================================

        self.register_prompt(
            name="financial_analysis",
            template="""Analyze the financial performance of {company_name}.

Focus on these specific metrics with exact figures:
1. Revenue (annual, with year and currency)
2. Net income and profit margins
3. Year-over-year growth rates
4. Market capitalization
5. Key financial ratios (P/E, P/S, debt/equity)

For EACH metric, you MUST:
- Provide the specific number (not ranges or estimates)
- Include the time period (fiscal year or quarter)
- Cite the source (SEC filing, earnings report, etc.)

If a metric is unavailable, explicitly state "Data not found" rather than estimating.

Company: {company_name}
{additional_context}""",
            version="1.0",
            category=PromptCategory.ANALYSIS,
            description="Financial analysis prompt requiring specific figures and citations",
            optional_vars={"additional_context": ""}
        )

        self.register_prompt(
            name="market_analysis",
            template="""Analyze the market position of {company_name}.

Research and provide:
1. Market share (with percentage and source)
2. Total addressable market size
3. Key competitors (with market positions)
4. Industry growth rate
5. Geographic presence

Requirements:
- Use specific percentages and dollar amounts
- Cite industry reports (Gartner, IDC, Statista, etc.)
- Include the date of the data
- Note any market trends affecting the company

Company: {company_name}
Industry: {industry}
{additional_context}""",
            version="1.0",
            category=PromptCategory.ANALYSIS,
            description="Market analysis prompt with specific data requirements",
            optional_vars={"industry": "Unknown", "additional_context": ""}
        )

        self.register_prompt(
            name="product_analysis",
            template="""Analyze the products and services of {company_name}.

Document:
1. Core products/services (with descriptions)
2. Revenue breakdown by product line (percentages)
3. Technology stack and innovations
4. Recent product launches (past 2 years)
5. R&D investment levels

For each product:
- Target customer segment
- Pricing model (if public)
- Competitive differentiation

Company: {company_name}
{additional_context}""",
            version="1.0",
            category=PromptCategory.ANALYSIS,
            description="Product analysis prompt",
            optional_vars={"additional_context": ""}
        )

        self.register_prompt(
            name="competitor_analysis",
            template="""Identify and analyze the main competitors of {company_name}.

For each competitor, provide:
1. Company name and brief description
2. Revenue comparison (if available)
3. Market share comparison
4. Key strengths and weaknesses
5. Head-to-head product comparison

Prioritize:
- Direct competitors (same products/markets)
- Indirect competitors (substitutes)
- Emerging competitors (startups)

Company: {company_name}
Industry: {industry}
{additional_context}""",
            version="1.0",
            category=PromptCategory.ANALYSIS,
            description="Competitor analysis prompt",
            optional_vars={"industry": "Unknown", "additional_context": ""}
        )

        # =====================================================================
        # Quality Prompts
        # =====================================================================

        self.register_prompt(
            name="gap_identification",
            template="""Review this research output and identify information gaps.

Research Output:
{research_content}

For EACH of these required fields, assess coverage:
- Revenue (annual, with year)
- Profit margins
- Employee count
- Headquarters location
- Founded year
- CEO name
- Market share
- Key competitors
- Main products

For each field, respond with:
1. FOUND: [specific value] (source)
2. MISSING: [explanation of what's needed]
3. PARTIAL: [what we have] needs [what's missing]

Company: {company_name}""",
            version="1.0",
            category=PromptCategory.QUALITY,
            description="Gap identification prompt for quality assessment"
        )

        self.register_prompt(
            name="contradiction_resolution",
            template="""Resolve conflicting information from different sources.

Conflict:
- Source A ({source_a}): {claim_a}
- Source B ({source_b}): {claim_b}

Analysis required:
1. Identify the specific discrepancy
2. Assess source authority (SEC > news > blogs)
3. Check data freshness (recent > old)
4. Recommend which value to use
5. Explain your reasoning

Provide a final recommendation with confidence level (high/medium/low).""",
            version="1.0",
            category=PromptCategory.QUALITY,
            description="Contradiction resolution prompt"
        )

        # =====================================================================
        # Synthesis Prompts
        # =====================================================================

        self.register_prompt(
            name="report_synthesis",
            template="""Synthesize research findings into a comprehensive report section.

Section: {section_name}
Company: {company_name}

Agent Findings:
{agent_outputs}

Requirements:
1. Consolidate information from all agents
2. Resolve any conflicts (prefer authoritative sources)
3. Include specific figures with citations
4. Note any remaining gaps
5. Format for readability

Output should be detailed but not redundant.""",
            version="1.0",
            category=PromptCategory.SYNTHESIS,
            description="Report synthesis prompt"
        )

        self.register_prompt(
            name="executive_summary",
            template="""Create an executive summary for {company_name}.

Full Report Content:
{report_content}

The executive summary must include:
1. Company overview (1-2 sentences)
2. Key financial highlights (revenue, growth, profitability)
3. Market position summary
4. Main products/services
5. Investment considerations or key risks

Length: 200-300 words
Tone: Professional, fact-based
Include: All specific numbers from the report""",
            version="1.0",
            category=PromptCategory.SYNTHESIS,
            description="Executive summary generation prompt"
        )

        # =====================================================================
        # Search Prompts
        # =====================================================================

        self.register_prompt(
            name="search_query_generation",
            template="""Generate search queries to research {company_name}.

Research Focus: {focus_area}

Generate {num_queries} search queries that will find:
1. Official company sources (investor relations, SEC filings)
2. Authoritative third-party data (Bloomberg, Reuters)
3. Industry analysis and reports
4. Recent news and updates

Queries should be specific and use exact company name.
Format: One query per line, no numbering.""",
            version="1.0",
            category=PromptCategory.RESEARCH,
            description="Search query generation prompt",
            optional_vars={"num_queries": 5, "focus_area": "general"}
        )


# =====================================================================
# Module-level singleton
# =====================================================================

_registry: Optional[PromptRegistry] = None


def get_prompt_registry() -> PromptRegistry:
    """Get the global prompt registry singleton."""
    global _registry
    if _registry is None:
        _registry = PromptRegistry()
    return _registry


def get_prompt(name: str, version: Optional[str] = None, **kwargs) -> str:
    """Convenience function to get a rendered prompt."""
    return get_prompt_registry().get_prompt(name, version, **kwargs)


def register_prompt(
    name: str,
    template: str,
    version: str = "1.0",
    **kwargs
) -> PromptVersion:
    """Convenience function to register a prompt."""
    return get_prompt_registry().register_prompt(name, template, version, **kwargs)
