"""
Reporting Module for Company Researcher.

Provides:
- Executive summary generation
- Citation and source management
- Report formatting
- Export capabilities
"""

from .citations import (
    Citation,
    CitationManager,
    RelevanceScorer,
    Source,
    SourceClassifier,
    SourceQuality,
    SourceType,
    classify_source,
    create_citation_manager,
)
from .executive_summary import (
    ExecutiveSummary,
    ExecutiveSummaryGenerator,
    Highlight,
    KeyMetric,
    RiskOpportunity,
    SentimentType,
    SummarySection,
    create_executive_summary_generator,
    generate_executive_summary,
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
