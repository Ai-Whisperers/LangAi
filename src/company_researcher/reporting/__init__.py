"""
Reporting Module for Company Researcher.

Provides:
- Executive summary generation
- Citation and source management
- Report formatting
- Export capabilities
"""

from .executive_summary import (
    ExecutiveSummary,
    ExecutiveSummaryGenerator,
    KeyMetric,
    Highlight,
    RiskOpportunity,
    SummarySection,
    SentimentType,
    create_executive_summary_generator,
    generate_executive_summary,
)

from .citations import (
    Source,
    Citation,
    SourceType,
    SourceQuality,
    SourceClassifier,
    RelevanceScorer,
    CitationManager,
    create_citation_manager,
    classify_source,
)

__all__ = [
    # Executive Summary
    "ExecutiveSummary",
    "ExecutiveSummaryGenerator",
    "KeyMetric",
    "Highlight",
    "RiskOpportunity",
    "SummarySection",
    "SentimentType",
    "create_executive_summary_generator",
    "generate_executive_summary",
    # Citations
    "Source",
    "Citation",
    "SourceType",
    "SourceQuality",
    "SourceClassifier",
    "RelevanceScorer",
    "CitationManager",
    "create_citation_manager",
    "classify_source",
]
