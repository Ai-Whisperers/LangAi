"""
Search Result Formatting - Centralized utilities for formatting search results.

This module consolidates the various search result formatting patterns used
across agents into reusable components:
- Basic formatting (title, URL, content)
- Keyword-based relevance scoring
- Domain-specific formatters (market, competitor, financial, etc.)

Usage:
    # As a standalone function
    from company_researcher.agents.base import format_search_results
    formatted = format_search_results(results, max_sources=15)

    # With keyword scoring
    from company_researcher.agents.base import SearchResultFormatter
    formatter = SearchResultFormatter(
        keywords=["market", "TAM", "growth"],
        boost_keywords=["market share"],
        relevance_label="Market"
    )
    formatted = formatter.format(results)

    # Using predefined formatters
    from company_researcher.agents.base import (
        MarketSearchFormatter,
        CompetitorSearchFormatter,
        FinancialSearchFormatter
    )
    formatted = MarketSearchFormatter().format(results)

    # As a mixin in an agent class
    class MyAgent(SearchResultMixin, BaseSpecialistAgent):
        search_keywords = ["revenue", "profit"]
        ...
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class FormatterConfig:
    """Configuration for search result formatting."""
    max_sources: int = 15
    content_length: int = 500
    show_relevance: bool = False
    relevance_label: str = "Relevance"
    empty_message: str = "No search results available."


class SearchResultFormatter:
    """
    Flexible search result formatter with keyword-based relevance scoring.

    Attributes:
        keywords: List of keywords to match for relevance scoring
        boost_keywords: Keywords that get extra weight
        boost_amount: Extra points for boost keywords
        config: Formatting configuration
    """

    def __init__(
        self,
        keywords: Optional[List[str]] = None,
        boost_keywords: Optional[List[str]] = None,
        boost_amount: int = 3,
        config: Optional[FormatterConfig] = None
    ):
        self.keywords = keywords or []
        self.boost_keywords = boost_keywords or []
        self.boost_amount = boost_amount
        self.config = config or FormatterConfig()

    def calculate_relevance(self, result: Dict[str, Any]) -> int:
        """
        Calculate relevance score for a search result.

        Args:
            result: Search result dictionary with 'title' and 'content'

        Returns:
            Integer relevance score (higher = more relevant)
        """
        content = result.get("content", "").lower()
        title = result.get("title", "").lower()

        # Base score from keyword matches
        score = sum(
            1 for keyword in self.keywords
            if keyword.lower() in content or keyword.lower() in title
        )

        # Boost for high-priority keywords
        for keyword in self.boost_keywords:
            if keyword.lower() in content or keyword.lower() in title:
                score += self.boost_amount

        return score

    def sort_by_relevance(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Tuple[int, Dict[str, Any]]]:
        """
        Sort results by relevance score (descending).

        Args:
            results: List of search result dictionaries

        Returns:
            List of (score, result) tuples sorted by score descending
        """
        if not self.keywords and not self.boost_keywords:
            # No scoring - return original order with score 0
            return [(0, r) for r in results]

        scored = [(self.calculate_relevance(r), r) for r in results]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

    def format_single(
        self,
        result: Dict[str, Any],
        index: int,
        score: Optional[int] = None
    ) -> str:
        """
        Format a single search result.

        Args:
            result: Search result dictionary
            index: Source index (1-based)
            score: Optional relevance score to display

        Returns:
            Formatted result string
        """
        title = result.get("title", "N/A")
        url = result.get("url", "N/A")
        content = result.get("content", "N/A")

        # Truncate content
        if isinstance(content, str) and len(content) > self.config.content_length:
            content = content[:self.config.content_length] + "..."

        # Build header
        if self.config.show_relevance and score is not None:
            header = f"Source {index} [{self.config.relevance_label}: {score}]: {title}"
        else:
            header = f"Source {index}: {title}"

        return f"{header}\nURL: {url}\nContent: {content}"

    def format(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results for LLM consumption.

        Args:
            results: List of search result dictionaries

        Returns:
            Formatted string with all results
        """
        if not results:
            return self.config.empty_message

        # Sort by relevance if keywords provided
        scored_results = self.sort_by_relevance(results)

        # Format top results
        formatted = []
        for i, (score, result) in enumerate(scored_results[:self.config.max_sources], 1):
            formatted.append(self.format_single(result, i, score))

        return "\n\n".join(formatted)


# ==============================================================================
# Domain-Specific Formatters
# ==============================================================================

class MarketSearchFormatter(SearchResultFormatter):
    """Formatter optimized for market analysis."""

    def __init__(self, config: Optional[FormatterConfig] = None):
        super().__init__(
            keywords=[
                "market", "industry", "TAM", "SAM", "growth", "trend",
                "competitive", "regulation", "customer", "segment",
                "CAGR", "forecast", "projection", "share"
            ],
            boost_keywords=["market size", "market share", "TAM", "total addressable"],
            config=config or FormatterConfig(
                show_relevance=True,
                relevance_label="Market Relevance",
                empty_message="No market-specific results available."
            )
        )


class CompetitorSearchFormatter(SearchResultFormatter):
    """Formatter optimized for competitive intelligence."""

    def __init__(self, config: Optional[FormatterConfig] = None):
        super().__init__(
            keywords=[
                "competitor", "alternative", "versus", "vs", "compare",
                "rival", "competition", "market share", "similar",
                "against", "better than", "switch from"
            ],
            boost_keywords=["competitor", "alternative", "competitive analysis"],
            config=config or FormatterConfig(
                show_relevance=True,
                relevance_label="Competitor Relevance",
                empty_message="No competitor-specific results available."
            )
        )


class FinancialSearchFormatter(SearchResultFormatter):
    """Formatter optimized for financial analysis."""

    def __init__(self, config: Optional[FormatterConfig] = None):
        super().__init__(
            keywords=[
                "revenue", "profit", "margin", "growth", "earnings",
                "financial", "quarter", "fiscal", "annual", "funding",
                "valuation", "investment", "IPO", "acquisition"
            ],
            boost_keywords=["revenue", "profit margin", "earnings report", "financial results"],
            config=config or FormatterConfig(
                show_relevance=True,
                relevance_label="Financial Relevance",
                empty_message="No financial-specific results available."
            )
        )


class ProductSearchFormatter(SearchResultFormatter):
    """Formatter optimized for product analysis."""

    def __init__(self, config: Optional[FormatterConfig] = None):
        super().__init__(
            keywords=[
                "product", "feature", "service", "offering", "solution",
                "platform", "technology", "tool", "capability", "integration",
                "pricing", "plan", "tier"
            ],
            boost_keywords=["product launch", "new feature", "product roadmap"],
            config=config or FormatterConfig(
                show_relevance=True,
                relevance_label="Product Relevance",
                empty_message="No product-specific results available."
            )
        )


class SalesSearchFormatter(SearchResultFormatter):
    """Formatter optimized for sales intelligence."""

    def __init__(self, config: Optional[FormatterConfig] = None):
        super().__init__(
            keywords=[
                "customer", "client", "deal", "contract", "partnership",
                "adoption", "implementation", "case study", "testimonial",
                "buyer", "procurement", "decision maker"
            ],
            boost_keywords=["customer success", "case study", "partnership announcement"],
            config=config or FormatterConfig(
                show_relevance=True,
                relevance_label="Sales Relevance",
                empty_message="No sales-relevant results available."
            )
        )


class BrandSearchFormatter(SearchResultFormatter):
    """Formatter optimized for brand analysis."""

    def __init__(self, config: Optional[FormatterConfig] = None):
        super().__init__(
            keywords=[
                "brand", "reputation", "perception", "awareness", "sentiment",
                "review", "rating", "satisfaction", "loyalty", "trust",
                "image", "identity", "messaging"
            ],
            boost_keywords=["brand perception", "customer review", "brand reputation"],
            config=config or FormatterConfig(
                show_relevance=True,
                relevance_label="Brand Relevance",
                empty_message="No brand-relevant results available."
            )
        )


# ==============================================================================
# Mixin for Agent Classes
# ==============================================================================

class SearchResultMixin:
    """
    Mixin providing search result formatting capabilities to agent classes.

    Usage:
        class MyAgent(SearchResultMixin, BaseSpecialistAgent):
            search_keywords = ["revenue", "profit"]
            search_boost_keywords = ["earnings"]

        # Or use a predefined formatter
        class MarketAgent(SearchResultMixin, BaseSpecialistAgent):
            search_formatter_class = MarketSearchFormatter
    """

    # Override these in subclasses
    search_keywords: List[str] = []
    search_boost_keywords: List[str] = []
    search_max_sources: int = 15
    search_content_length: int = 500
    search_show_relevance: bool = False
    search_relevance_label: str = "Relevance"
    search_empty_message: str = "No search results available."

    # Or specify a formatter class
    search_formatter_class: Optional[type] = None

    def get_search_formatter(self) -> SearchResultFormatter:
        """Get the search result formatter for this agent."""
        if self.search_formatter_class:
            return self.search_formatter_class()

        config = FormatterConfig(
            max_sources=self.search_max_sources,
            content_length=self.search_content_length,
            show_relevance=self.search_show_relevance,
            relevance_label=self.search_relevance_label,
            empty_message=self.search_empty_message
        )

        return SearchResultFormatter(
            keywords=self.search_keywords,
            boost_keywords=self.search_boost_keywords,
            config=config
        )

    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results using this agent's formatter."""
        return self.get_search_formatter().format(results)


# ==============================================================================
# Convenience Functions
# ==============================================================================

def format_search_results(
    results: List[Dict[str, Any]],
    max_sources: int = 15,
    content_length: int = 500,
    keywords: Optional[List[str]] = None,
    boost_keywords: Optional[List[str]] = None,
    show_relevance: bool = False,
    relevance_label: str = "Relevance",
    empty_message: str = "No search results available."
) -> str:
    """
    Format search results for LLM analysis.

    This is a convenience function for simple use cases.
    For more control, use SearchResultFormatter directly.

    Args:
        results: List of search result dictionaries
        max_sources: Maximum number of sources to include
        content_length: Length to truncate content to
        keywords: Optional keywords for relevance scoring
        boost_keywords: Optional keywords for extra relevance weight
        show_relevance: Whether to show relevance scores in output
        relevance_label: Label for relevance scores
        empty_message: Message when no results available

    Returns:
        Formatted string of search results
    """
    config = FormatterConfig(
        max_sources=max_sources,
        content_length=content_length,
        show_relevance=show_relevance,
        relevance_label=relevance_label,
        empty_message=empty_message
    )

    formatter = SearchResultFormatter(
        keywords=keywords,
        boost_keywords=boost_keywords,
        config=config
    )

    return formatter.format(results)


def format_market_results(results: List[Dict[str, Any]]) -> str:
    """Format search results for market analysis."""
    return MarketSearchFormatter().format(results)


def format_competitor_results(results: List[Dict[str, Any]]) -> str:
    """Format search results for competitive analysis."""
    return CompetitorSearchFormatter().format(results)


def format_financial_results(results: List[Dict[str, Any]]) -> str:
    """Format search results for financial analysis."""
    return FinancialSearchFormatter().format(results)


def format_product_results(results: List[Dict[str, Any]]) -> str:
    """Format search results for product analysis."""
    return ProductSearchFormatter().format(results)


def format_sales_results(results: List[Dict[str, Any]]) -> str:
    """Format search results for sales intelligence."""
    return SalesSearchFormatter().format(results)


def format_brand_results(results: List[Dict[str, Any]]) -> str:
    """Format search results for brand analysis."""
    return BrandSearchFormatter().format(results)
