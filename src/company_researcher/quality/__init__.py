"""
Quality Assurance Module for Company Researcher.

This module is organized into subdirectories:
- validation/: Cross-source validation, contradiction detection, quality checking
- tracking/: Source tracking, freshness tracking, audit trail
- scoring/: Confidence scoring, source assessment
- extraction/: Fact extraction, source attribution

New code should import from subdirectories:
    from company_researcher.quality.validation import ContradictionDetector
    from company_researcher.quality.tracking import AuditTrail

This file maintains backward compatibility with existing imports.

Phase History:
- Phase 2: Basic quality checking
- Phase 5: Source tracking, multi-factor scoring, confidence assessment
- Phase 10: Fact extraction, contradiction detection, Logic Critic
- Phase 21: Cross-source validation, source attribution
"""

# Core models (shared across modules)
from .models import (
    Source,
    ResearchFact,
    QualityReport,
    SourceQuality,
    ConfidenceLevel
)

# ============================================================================
# Validation Module
# ============================================================================

from .quality_checker import check_research_quality

from .contradiction_detector import (
    ContradictionDetector,
    Contradiction,
    ContradictionReport,
    ContradictionSeverity,
    ResolutionStrategy,
    detect_contradictions,
    quick_contradiction_check
)

from .cross_source_validator import (
    CrossSourceValidator,
    SourceInfo,
    SourceTier,
    Fact,
    Conflict,
    ConflictType,
    ValidationResult,
    validate_research_data,
)

# ============================================================================
# Tracking Module
# ============================================================================

from .source_tracker import SourceTracker

from .freshness_tracker import (
    FreshnessTracker,
    FreshnessAssessment,
    FreshnessLevel,
    FreshnessThreshold,
    DataType,
    DateExtractor,
    create_freshness_tracker,
    assess_data_freshness,
)

from .audit_trail import (
    ResearchAuditTrail,
    AuditEvent,
    AuditEventType,
    SourceReference,
    ClaimProvenance,
    AgentExecution,
    create_audit_trail,
)

# ============================================================================
# Scoring Module
# ============================================================================

from .source_assessor import SourceQualityAssessor, get_quality_tier_info

from .confidence_scorer import (
    ConfidenceScorer,
    ScoredFact,
    ConfidenceFactors,
    SourceInfo as ConfidenceSourceInfo,
    SourceType,
    ConfidenceLevel as ScorerConfidenceLevel,
    score_facts,
    create_confidence_scorer,
)

# ============================================================================
# Extraction Module
# ============================================================================

from .fact_extractor import (
    FactExtractor,
    ExtractedFact,
    ExtractionResult,
    FactCategory,
    ClaimType,
    extract_facts,
    extract_from_all_agents
)

from .source_attribution import (
    SourceTracker as AttributionTracker,
    SourceDocument,
    Evidence,
    EvidenceChain,
    EvidenceType,
    Citation,
    CitationStyle,
    create_tracker_for_research,
)

# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Core Models
    "Source",
    "ResearchFact",
    "QualityReport",
    "SourceQuality",
    "ConfidenceLevel",

    # Validation
    "check_research_quality",
    "ContradictionDetector",
    "Contradiction",
    "ContradictionReport",
    "ContradictionSeverity",
    "ResolutionStrategy",
    "detect_contradictions",
    "quick_contradiction_check",
    "CrossSourceValidator",
    "SourceInfo",
    "SourceTier",
    "Fact",
    "Conflict",
    "ConflictType",
    "ValidationResult",
    "validate_research_data",

    # Tracking
    "SourceTracker",
    "FreshnessTracker",
    "FreshnessAssessment",
    "FreshnessLevel",
    "FreshnessThreshold",
    "DataType",
    "DateExtractor",
    "create_freshness_tracker",
    "assess_data_freshness",
    "ResearchAuditTrail",
    "AuditEvent",
    "AuditEventType",
    "SourceReference",
    "ClaimProvenance",
    "AgentExecution",
    "create_audit_trail",

    # Scoring
    "SourceQualityAssessor",
    "get_quality_tier_info",
    "ConfidenceScorer",
    "ScoredFact",
    "ConfidenceFactors",
    "ConfidenceSourceInfo",
    "SourceType",
    "ScorerConfidenceLevel",
    "score_facts",
    "create_confidence_scorer",

    # Extraction
    "FactExtractor",
    "ExtractedFact",
    "ExtractionResult",
    "FactCategory",
    "ClaimType",
    "extract_facts",
    "extract_from_all_agents",
    "AttributionTracker",
    "SourceDocument",
    "Evidence",
    "EvidenceChain",
    "EvidenceType",
    "Citation",
    "CitationStyle",
    "create_tracker_for_research",
]
