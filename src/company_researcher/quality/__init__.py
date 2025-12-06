"""
Quality assurance module for Company Researcher.

Phase 2: Basic quality checking
Phase 5: Source tracking, multi-factor scoring, confidence assessment
Phase 10: Fact extraction, contradiction detection, Logic Critic
"""

from .quality_checker import check_research_quality
from .models import (
    Source,
    ResearchFact,
    QualityReport,
    SourceQuality,
    ConfidenceLevel
)
from .source_assessor import SourceQualityAssessor, get_quality_tier_info
from .source_tracker import SourceTracker

# Phase 10: Fact extraction and contradiction detection
from .fact_extractor import (
    FactExtractor,
    ExtractedFact,
    ExtractionResult,
    FactCategory,
    ClaimType,
    extract_facts,
    extract_from_all_agents
)
from .contradiction_detector import (
    ContradictionDetector,
    Contradiction,
    ContradictionReport,
    ContradictionSeverity,
    ResolutionStrategy,
    detect_contradictions,
    quick_contradiction_check
)

__all__ = [
    # Phase 2
    "check_research_quality",
    # Phase 5
    "Source",
    "ResearchFact",
    "QualityReport",
    "SourceQuality",
    "ConfidenceLevel",
    "SourceQualityAssessor",
    "SourceTracker",
    "get_quality_tier_info",
    # Phase 10: Fact extraction
    "FactExtractor",
    "ExtractedFact",
    "ExtractionResult",
    "FactCategory",
    "ClaimType",
    "extract_facts",
    "extract_from_all_agents",
    # Phase 10: Contradiction detection
    "ContradictionDetector",
    "Contradiction",
    "ContradictionReport",
    "ContradictionSeverity",
    "ResolutionStrategy",
    "detect_contradictions",
    "quick_contradiction_check",
]
