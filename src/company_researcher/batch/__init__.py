"""
Batch Research Module - Research Multiple Companies in Parallel.

This module provides batch processing capabilities for company research,
allowing efficient parallel research of multiple companies with caching
and comparative analysis.
"""

from .batch_researcher import (
    BatchResearcher,
    BatchResearchResult,
    CompanyResearchResult,
    compare_companies,
    research_companies,
)

__all__ = [
    "BatchResearcher",
    "BatchResearchResult",
    "CompanyResearchResult",
    "research_companies",
    "compare_companies",
]
