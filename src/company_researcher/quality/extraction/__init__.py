"""
Quality Extraction Module.

Provides fact extraction and source attribution:
- Fact extraction
- Source attribution
"""

from .fact_extractor import (
    FactExtractor,
    ExtractedFact,
    FactCategory,
)

from .source_attribution import (
    SourceAttribution,
    Attribution,
    AttributionLevel,
)

__all__ = [
    # Fact extraction
    "FactExtractor",
    "ExtractedFact",
    "FactCategory",
    # Source attribution
    "SourceAttribution",
    "Attribution",
    "AttributionLevel",
]
