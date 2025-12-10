"""
Helper functions for formatting data in prompts.

This module contains utility functions used to format search results,
sources, and other data for inclusion in prompt templates.
"""


def format_search_results_for_analysis(results: list) -> str:
    """
    Format search results for the analysis prompt.

    Args:
        results: List of search result dictionaries

    Returns:
        Formatted string of search results
    """
    formatted = []
    for i, result in enumerate(results, 1):
        formatted.append(f"""
Result {i}:
Title: {result.get('title', 'N/A')}
URL: {result.get('url', 'N/A')}
Content: {result.get('content', 'N/A')}
Score: {result.get('score', 0):.0%}
---
""")
    return "\n".join(formatted)


def format_sources_for_extraction(sources: list) -> str:
    """
    Format sources for the extraction prompt.

    Args:
        sources: List of source dictionaries

    Returns:
        Formatted string of sources
    """
    formatted = []
    for i, source in enumerate(sources, 1):
        formatted.append(
            f"{i}. [{source.get('title', 'N/A')}]({source.get('url', 'N/A')}) "
            f"(Relevance: {source.get('score', 0):.0%})"
        )
    return "\n".join(formatted)


def format_sources_for_report(sources: list) -> str:
    """
    Format sources for the final report.

    Args:
        sources: List of source dictionaries

    Returns:
        Formatted markdown list of sources
    """
    formatted = []
    for i, source in enumerate(sources, 1):
        formatted.append(
            f"{i}. [{source.get('title', 'N/A')}]({source.get('url', 'N/A')})"
        )
    return "\n".join(formatted)
