"""
Quality Assurance Module for Company Researcher.

All quality modules are at root level for simplicity:
- Validation: contradiction_detector, cross_source_validator, quality_checker
- Tracking: source_tracker, freshness_tracker, audit_trail
- Scoring: confidence_scorer, source_assessor
- Extraction: fact_extractor, source_attribution

Import directly from this module:
    from company_researcher.quality import ContradictionDetector, check_research_quality

Phase History:
- Phase 2: Basic quality checking
- Phase 5: Source tracking, multi-factor scoring, confidence assessment
- Phase 10: Fact extraction, contradiction detection, Logic Critic
- Phase 21: Cross-source validation, source attribution
- Phase 22: Consolidated flat structure (removed duplicate subdirectories)
"""

# AI-powered extraction (replaces legacy fact_extractor)
from ..ai.extraction import AIDataExtractor as FactExtractor  # Alias for backward compatibility
from ..ai.extraction import ExtractedFact, ExtractionResult, FactCategory
from ..ai.extraction import FactType as ClaimType  # Alias for backward compatibility
from .audit_trail import (
    AgentExecution,
    AuditEvent,
    AuditEventType,
    ClaimProvenance,
    ResearchAuditTrail,
    SourceReference,
    create_audit_trail,
)
from .confidence_scorer import ConfidenceFactors
from .confidence_scorer import ConfidenceLevel as ScorerConfidenceLevel
from .confidence_scorer import ConfidenceScorer, ScoredFact
from .confidence_scorer import SourceInfo as ConfidenceSourceInfo
from .confidence_scorer import SourceType, create_confidence_scorer, score_facts
from .contradiction_detector import (
    Contradiction,
    ContradictionDetector,
    ContradictionReport,
    ContradictionSeverity,
    ResolutionStrategy,
    detect_contradictions,
    quick_contradiction_check,
)
from .cross_source_validator import (
    Conflict,
    ConflictType,
    CrossSourceValidator,
    Fact,
    SourceInfo,
    SourceTier,
    ValidationResult,
    validate_research_data,
)
from .enhanced_contradiction_detector import Contradiction as EnhancedContradiction
from .enhanced_contradiction_detector import ContradictionReport as EnhancedContradictionReport
from .enhanced_contradiction_detector import (
    ContradictionType,
    EnhancedContradictionDetector,
    ExtractedClaim,
)
from .freshness_tracker import (
    DataType,
    DateExtractor,
    FreshnessAssessment,
    FreshnessLevel,
    FreshnessThreshold,
    FreshnessTracker,
    assess_data_freshness,
    create_freshness_tracker,
)

# Core models (shared across modules)
from .models import ConfidenceLevel, QualityReport, ResearchFact, Source, SourceQuality
from .quality_checker import check_research_quality
from .source_assessor import SourceQualityAssessor, get_quality_tier_info
from .source_attribution import (
    Citation,
    CitationStyle,
    Evidence,
    EvidenceChain,
    EvidenceType,
    SourceDocument,
)
from .source_attribution import SourceTracker as AttributionTracker
from .source_attribution import create_tracker_for_research
from .source_tracker import SourceTracker

# ============================================================================
# Validation Module
# ============================================================================


# ============================================================================
# Tracking Module
# ============================================================================


# ============================================================================
# Scoring Module
# ============================================================================


# ============================================================================
# Extraction Module
# ============================================================================


# Note: extract_facts and extract_from_all_agents removed - use AIDataExtractor directly


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
    "EnhancedContradictionDetector",
    "ContradictionType",
    "ExtractedClaim",
    "EnhancedContradiction",
    "EnhancedContradictionReport",
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
    # Extraction (AI-powered)
    "FactExtractor",
    "ExtractedFact",
    "ExtractionResult",
    "FactCategory",
    "ClaimType",
    "AttributionTracker",
    "SourceDocument",
    "Evidence",
    "EvidenceChain",
    "EvidenceType",
    "Citation",
    "CitationStyle",
    "create_tracker_for_research",
]
