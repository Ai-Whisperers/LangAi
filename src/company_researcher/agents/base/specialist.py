"""
Base Specialist Agent - Common functionality for specialist analysis agents.

Specialist agents differ from node functions in that they:
- Return structured dataclass results (not just analysis text)
- Have custom parsing logic for extracting data from LLM responses
- Often have multiple analysis types (brand, sales, social, etc.)

This module provides a base class that eliminates duplication across:
- SalesIntelligenceAgent
- BrandAuditorAgent
- SocialMediaAgent
- InvestmentAnalystAgent
- And other specialist agents

Usage:
    class SalesIntelligenceAgent(BaseSpecialistAgent):
        agent_name = "sales_intelligence"
        prompt_template = SALES_INTELLIGENCE_PROMPT
        result_class = SalesIntelligenceResult

        def _parse_analysis(self, company_name: str, analysis: str) -> SalesIntelligenceResult:
            # Custom parsing logic
            result = SalesIntelligenceResult(company_name=company_name)
            result.lead_score = self._extract_lead_score(analysis)
            return result
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, TypeVar

from ...config import ResearchConfig, get_config
from ...llm.client_factory import calculate_cost, get_anthropic_client, safe_extract_text
from ...utils import get_logger

logger = get_logger(__name__)

# Generic type for result dataclass
T = TypeVar("T")


@dataclass
class AnalysisMetrics:
    """Metrics from an analysis run."""

    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    sources_used: int = 0


class BaseSpecialistAgent(ABC, Generic[T]):
    """
    Base class for specialist analysis agents.

    Provides common functionality:
    - Configuration management
    - LLM client initialization
    - Search result formatting
    - Cost calculation
    - Error handling
    - Logging

    Subclasses must implement:
    - agent_name: str - unique identifier for the agent
    - _get_prompt(company_name, search_results) -> str
    - _parse_analysis(company_name, analysis) -> T

    Optional overrides:
    - _format_search_results(results) -> str - custom result formatting
    - _get_max_tokens() -> int - override config value
    - _get_temperature() -> float - override config value
    """

    agent_name: str = "base_specialist"

    def __init__(self, config: Optional[ResearchConfig] = None):
        """
        Initialize the specialist agent.

        Args:
            config: Optional configuration override. Uses global config if not provided.
        """
        self._config = config or get_config()
        self._client = get_anthropic_client()
        self._logger = logging.getLogger(f"{__name__}.{self.agent_name}")

    @abstractmethod
    def _get_prompt(self, company_name: str, formatted_results: str) -> str:
        """
        Build the analysis prompt.

        Args:
            company_name: Name of the company being analyzed
            formatted_results: Pre-formatted search results

        Returns:
            Complete prompt string for the LLM
        """

    @abstractmethod
    def _parse_analysis(self, company_name: str, analysis: str) -> T:
        """
        Parse LLM analysis into structured result.

        Args:
            company_name: Name of the company
            analysis: Raw analysis text from LLM

        Returns:
            Structured result object
        """

    def _format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results for the prompt.

        Override this method for custom formatting (e.g., prioritizing
        certain keywords).

        Args:
            results: Raw search results

        Returns:
            Formatted string for prompt
        """
        if not results:
            return "No search results available"

        max_sources = getattr(self._config, f"{self.agent_name}_max_sources", 12)
        content_length = self._config.content_truncate_length

        formatted = []
        for i, r in enumerate(results[:max_sources], 1):
            title = r.get("title", "N/A")
            content = r.get("content", "")
            if len(content) > content_length:
                content = content[:content_length] + "..."

            formatted.append(f"Source {i}: {title}\n" f"Content: {content}\n")

        return "\n".join(formatted)

    def _get_max_tokens(self) -> int:
        """Get max tokens for this agent from config."""
        return getattr(self._config, f"{self.agent_name}_max_tokens", self._config.llm_max_tokens)

    def _get_temperature(self) -> float:
        """Get temperature for this agent from config."""
        return getattr(self._config, f"{self.agent_name}_temperature", self._config.llm_temperature)

    def analyze(self, company_name: str, search_results: List[Dict[str, Any]]) -> T:
        """
        Perform analysis on a company.

        Args:
            company_name: Company to analyze
            search_results: Search results with relevant data

        Returns:
            Structured analysis result
        """
        self._logger.info(f"{self.agent_name} analyzing {company_name}")

        # Format search results
        formatted_results = self._format_search_results(search_results)

        # Build prompt
        prompt = self._get_prompt(company_name, formatted_results)

        # Call LLM
        self._logger.debug(f"Calling LLM with {len(prompt)} chars prompt")
        response = self._client.messages.create(
            model=self._config.llm_model,
            max_tokens=self._get_max_tokens(),
            temperature=self._get_temperature(),
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract and parse
        analysis = safe_extract_text(response, agent_name=self.agent_name)
        cost = calculate_cost(response.usage.input_tokens, response.usage.output_tokens)

        self._logger.info(f"{self.agent_name} complete - cost: ${cost:.4f}")

        # Parse into structured result
        result = self._parse_analysis(company_name, analysis)

        # Store analysis text and metrics if result has those attributes
        # (hasattr check ensures runtime safety; type-ignore for generic T)
        if hasattr(result, "analysis"):
            result.analysis = analysis  # type: ignore[union-attr]

        return result

    def analyze_with_metrics(
        self, company_name: str, search_results: List[Dict[str, Any]]
    ) -> tuple[T, AnalysisMetrics]:
        """
        Perform analysis and return metrics separately.

        Useful when you need detailed tracking of costs and tokens.

        Args:
            company_name: Company to analyze
            search_results: Search results

        Returns:
            Tuple of (result, metrics)
        """
        self._logger.info(f"{self.agent_name} analyzing {company_name} (with metrics)")

        # Format search results
        formatted_results = self._format_search_results(search_results)

        # Build prompt
        prompt = self._get_prompt(company_name, formatted_results)

        # Call LLM
        response = self._client.messages.create(
            model=self._config.llm_model,
            max_tokens=self._get_max_tokens(),
            temperature=self._get_temperature(),
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract and calculate
        analysis = safe_extract_text(response, agent_name=self.agent_name)
        cost = calculate_cost(response.usage.input_tokens, response.usage.output_tokens)

        metrics = AnalysisMetrics(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            cost=cost,
            sources_used=min(len(search_results), 12),
        )

        self._logger.info(f"{self.agent_name} complete - cost: ${cost:.4f}")

        # Parse into structured result
        result = self._parse_analysis(company_name, analysis)

        # (hasattr check ensures runtime safety; type-ignore for generic T)
        if hasattr(result, "analysis"):
            result.analysis = analysis  # type: ignore[union-attr]

        return result, metrics


# Common parsing utilities for specialist agents
class ParsingMixin:
    """
    Common parsing utilities for specialist agents.

    Provides reusable extraction methods for parsing LLM analysis text
    into structured data. Used by specialist agents like SalesIntelligence,
    BrandAuditor, SocialMedia, etc.

    Usage:
        class MyAgent(BaseSpecialistAgent, ParsingMixin):
            def _parse_analysis(self, company_name: str, analysis: str):
                score = self.extract_score(analysis, "Score")
                items = self.extract_list_items(analysis, "Recommendations")
                ...
    """

    @staticmethod
    def extract_section(analysis: str, keyword: str, max_length: int = 500) -> str:
        """
        Extract a section starting with a keyword.

        Args:
            analysis: Full analysis text
            keyword: Section header keyword to find
            max_length: Maximum characters to search

        Returns:
            First meaningful line from section, or empty string
        """
        if keyword in analysis:
            start = analysis.find(keyword)
            section = analysis[start : start + max_length]
            lines = section.split("\n")[1:4]
            for line in lines:
                if line.strip() and len(line.strip()) > 20:
                    return line.strip()[:200]
        return ""

    @staticmethod
    def extract_list_items(
        analysis: str,
        section_keyword: str,
        max_items: int = 5,
        min_item_length: int = 5,
        max_item_length: int = 150,
    ) -> List[str]:
        """
        Extract list items from a section.

        Args:
            analysis: Full analysis text
            section_keyword: Keyword in section header
            max_items: Maximum items to return
            min_item_length: Minimum length for valid item
            max_item_length: Maximum length before truncation

        Returns:
            List of extracted items
        """
        items = []
        lines = analysis.split("\n")

        in_section = False
        for line in lines:
            stripped = line.strip()
            # Check for section header - must START with ## or ** (not just contain them)
            is_header = stripped.startswith(("##", "**"))

            # Check if this line is a section header with our keyword
            # Important: Avoid matching key-value pairs like "**Brand Strength:** STRONG"
            # by checking if there's content after a colon on the same line
            if section_keyword.lower() in line.lower() and is_header:
                # Check if this looks like a key-value pair (has ": <content>" pattern)
                colon_idx = stripped.find(":")
                if colon_idx > 0:
                    # Check if there's significant content after the colon on same line
                    after_colon = stripped[colon_idx + 1 :].strip()
                    # If there's content after colon that's not just closing **, it's a key-value pair
                    if after_colon and after_colon not in ("**", ""):
                        # This is a key-value pair, not a section header - skip it
                        continue
                in_section = True
                continue

            if in_section:
                if stripped.startswith(
                    ("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "-", "•")
                ):
                    item = stripped.lstrip("0123456789.-•* ").strip()
                    if item and len(item) > min_item_length:
                        items.append(item[:max_item_length])
                elif is_header:
                    # New section header found, stop
                    break

        return items[:max_items]

    @staticmethod
    def extract_score(
        analysis: str, keyword: str, default: float = 50.0, max_value: float = 100.0
    ) -> float:
        """
        Extract a numeric score near a keyword.

        Args:
            analysis: Full analysis text
            keyword: Score label to find
            default: Default value if not found
            max_value: Maximum allowed value

        Returns:
            Extracted score or default
        """
        import re

        # Escape special regex characters in keyword
        escaped_keyword = re.escape(keyword)

        patterns = [
            # "Brand Score: 75" or "Brand Score:** 75"
            rf"{escaped_keyword}[:\s*]*(\d{{1,3}})",
            # "Brand Score: 75/100"
            rf"{escaped_keyword}.*?(\d{{1,3}})\s*/\s*100",
            # Table format: "| Brand Awareness | 80 |" - keyword followed by | number |
            rf"{escaped_keyword}\s*\|\s*(\d{{1,3}})",
            # Fallback: just find XX/100 pattern
            r"(\d{1,3})\s*/\s*100",
        ]

        for pattern in patterns:
            match = re.search(pattern, analysis, re.IGNORECASE)
            if match:
                score = float(match.group(1))
                return min(max_value, score)

        return default

    @staticmethod
    def extract_enum_value(
        analysis: str, keyword: str, options: List[str], default: str, context_window: int = 200
    ) -> str:
        """
        Extract an enum-like value near a keyword.

        Args:
            analysis: Full analysis text
            keyword: Label to find
            options: Valid enum options
            default: Default if not found
            context_window: Characters to search after keyword

        Returns:
            Matched option (lowercase) or default
        """
        analysis_upper = analysis.upper()

        if keyword.upper() in analysis_upper:
            start = analysis_upper.find(keyword.upper())
            context = analysis_upper[start : start + context_window]

            for option in options:
                if option.upper() in context:
                    return option.lower()

        return default.lower()

    @staticmethod
    def extract_table_rows(
        analysis: str, header_keyword: str, min_columns: int = 2, max_rows: int = 10
    ) -> List[List[str]]:
        """
        Extract rows from a markdown table.

        Args:
            analysis: Full analysis text
            header_keyword: Keyword in table header row
            min_columns: Minimum columns for valid row
            max_rows: Maximum rows to return

        Returns:
            List of rows, each row is a list of cell values
        """
        rows = []
        lines = analysis.split("\n")

        in_table = False
        for line in lines:
            if header_keyword.lower() in line.lower() and "|" in line:
                in_table = True
                continue

            if in_table:
                if "|" in line and "---" not in line:
                    cells = [c.strip() for c in line.split("|") if c.strip()]
                    if len(cells) >= min_columns:
                        rows.append(cells)
                elif not line.strip() or ("|" not in line and line.strip()):
                    break

        return rows[:max_rows]

    @staticmethod
    def extract_keyword_list(analysis: str, keyword: str, max_items: int = 5) -> List[str]:
        """
        Extract items from lines containing a keyword.

        Different from extract_list_items - this finds ANY line
        containing the keyword, not just items in a specific section.

        Args:
            analysis: Full analysis text
            keyword: Keyword to search for
            max_items: Maximum items to return

        Returns:
            List of extracted items
        """
        items = []
        lines = analysis.split("\n")

        for line in lines:
            if keyword.lower() in line.lower():
                cleaned = line.strip().lstrip("0123456789.-•* ").strip()
                if cleaned and len(cleaned) > 10:
                    items.append(cleaned[:150])

        return items[:max_items]

    @staticmethod
    def extract_metrics_table(analysis: str, metric_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Extract metric values from analysis.

        Args:
            analysis: Full analysis text
            metric_names: Names of metrics to find

        Returns:
            Dict mapping metric name to {score, trend, notes}
        """
        import re

        metrics = {}

        for name in metric_names:
            if name in analysis:
                # Find the line containing this metric
                idx = analysis.find(name)
                if idx < 0:
                    continue

                # Find the end of the line (limit context to just this line)
                line_end = analysis.find("\n", idx)
                if line_end < 0:
                    line_end = len(analysis)
                line_context = analysis[idx:line_end]

                # Find score from the line
                pattern = rf"{re.escape(name)}.*?([\d]{{1,3}})"
                match = re.search(pattern, line_context)
                score = float(match.group(1)) if match else 50.0

                # Find trend from the same line only
                trend = "stable"
                line_lower = line_context.lower()
                if "↑" in line_context or "improving" in line_lower:
                    trend = "improving"
                elif "↓" in line_context or "declining" in line_lower:
                    trend = "declining"

                metrics[name] = {"score": min(100, score), "trend": trend}

        return metrics

    @staticmethod
    def extract_count(
        analysis: str, keyword: str, multipliers: Optional[Dict[str, int]] = None
    ) -> int:
        """
        Extract a count/number with support for K/M suffixes.

        Args:
            analysis: Full analysis text
            keyword: Label to find
            multipliers: Suffix multipliers (default: K=1000, M=1000000)

        Returns:
            Extracted count or 0
        """
        import re

        if multipliers is None:
            multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}

        pattern = rf"{keyword}[:\s]*.*?([\d,]+(?:\.\d+)?)\s*([KMB]|thousand|million|billion)?"
        match = re.search(pattern, analysis, re.IGNORECASE)

        if match:
            num_str = match.group(1).replace(",", "")
            try:
                value = float(num_str)
                suffix = match.group(2)
                if suffix:
                    suffix_upper = suffix[0].upper()
                    if suffix_upper in multipliers:
                        value *= multipliers[suffix_upper]
                    elif "thousand" in suffix.lower():
                        value *= 1000
                    elif "million" in suffix.lower():
                        value *= 1000000
                    elif "billion" in suffix.lower():
                        value *= 1000000000
                return int(value)
            except ValueError:
                pass

        return 0

    @staticmethod
    def extract_sentiment(analysis: str) -> str:
        """
        Extract overall sentiment from analysis.

        Args:
            analysis: Full analysis text

        Returns:
            One of: positive, negative, neutral, mixed
        """
        import re

        analysis_lower = analysis.lower()

        # Check for explicit sentiment mentions (use word boundaries to avoid partial matches)
        # Check "mixed" first since it's most specific
        if re.search(r"\bmixed\b", analysis_lower) and "sentiment" in analysis_lower:
            return "mixed"
        elif re.search(r"\bpositive\b", analysis_lower) and "sentiment" in analysis_lower:
            return "positive"
        elif re.search(r"\bnegative\b", analysis_lower) and "sentiment" in analysis_lower:
            return "negative"

        # Fallback to word counting
        positive_words = ["strong", "excellent", "good", "growth", "success"]
        negative_words = ["weak", "poor", "declining", "risk", "concern"]

        pos_count = sum(1 for w in positive_words if w in analysis_lower)
        neg_count = sum(1 for w in negative_words if w in analysis_lower)

        if pos_count > neg_count + 2:
            return "positive"
        elif neg_count > pos_count + 2:
            return "negative"
        elif pos_count > 0 and neg_count > 0:
            return "mixed"

        return "neutral"

    @staticmethod
    def extract_boolean(
        analysis: str,
        keyword: str,
        true_indicators: Optional[List[str]] = None,
        false_indicators: Optional[List[str]] = None,
        default: bool = False,
    ) -> bool:
        """
        Extract a boolean value near a keyword.

        Args:
            analysis: Full analysis text
            keyword: Label to find
            true_indicators: Words indicating True
            false_indicators: Words indicating False
            default: Default if not determined

        Returns:
            Extracted boolean or default
        """
        if true_indicators is None:
            true_indicators = ["yes", "true", "confirmed", "present", "active"]
        if false_indicators is None:
            false_indicators = ["no", "false", "none", "absent", "inactive"]

        analysis_lower = analysis.lower()

        if keyword.lower() in analysis_lower:
            idx = analysis_lower.find(keyword.lower())
            context = analysis_lower[idx : idx + 100]

            # Check false_indicators FIRST - they take precedence over true_indicators
            # This handles cases like "Active: No" where the keyword matches a true_indicator
            for indicator in false_indicators:
                if indicator in context:
                    return False

            for indicator in true_indicators:
                if indicator in context:
                    return True

        return default

    @staticmethod
    def extract_percentage(analysis: str, keyword: str, default: float = 0.0) -> float:
        """
        Extract a percentage value near a keyword.

        Args:
            analysis: Full analysis text
            keyword: Label to find
            default: Default if not found

        Returns:
            Extracted percentage (0-100) or default
        """
        import re

        pattern = rf"{keyword}.*?([\d]+(?:\.\d+)?)\s*%"
        match = re.search(pattern, analysis, re.IGNORECASE)

        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass

        return default
