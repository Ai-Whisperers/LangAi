"""
Shared modules for the Company Researcher system.

These modules provide unified implementations used across different parts
of the system to ensure consistency and reduce code duplication.

Primary Entry Point:
    from company_researcher.shared import EnhancedResearchPipeline

    pipeline = EnhancedResearchPipeline("Apple Inc.", ticker="AAPL")
    result = pipeline.run_full_analysis(research_output)

Individual Components:
    from company_researcher.shared import (
        run_quality_pipeline,
        run_gap_detection,
        run_contradiction_analysis,
        get_optimized_queries,
        select_best_sources
    )
"""

from .quality import UnifiedQualityScorer, QualityResult, DimensionScore, QualityDimension
from .gaps import SemanticGapDetector, GapAssessment, GapConfidence, CoverageLevel
from .search import RobustSearchClient, SearchResult, ProviderHealth, QueryDiversifier

# Integration pipelines
from .integration import (
    # Main pipeline
    EnhancedResearchPipeline,
    EnhancedAnalysisResult,

    # Component pipelines
    QualityPipeline,
    GapDetectionPipeline,
    ContradictionPipeline,
    SearchOptimizationPipeline,

    # Convenience functions
    run_quality_pipeline,
    run_gap_detection,
    run_contradiction_analysis,
    get_optimized_queries,
    select_best_sources,
)

__all__ = [
    # Quality
    "UnifiedQualityScorer",
    "QualityResult",
    "DimensionScore",
    "QualityDimension",
    # Gaps
    "SemanticGapDetector",
    "GapAssessment",
    "GapConfidence",
    "CoverageLevel",
    # Search
    "RobustSearchClient",
    "SearchResult",
    "ProviderHealth",
    "QueryDiversifier",
    # Integration - Main
    "EnhancedResearchPipeline",
    "EnhancedAnalysisResult",
    # Integration - Pipelines
    "QualityPipeline",
    "GapDetectionPipeline",
    "ContradictionPipeline",
    "SearchOptimizationPipeline",
    # Integration - Convenience
    "run_quality_pipeline",
    "run_gap_detection",
    "run_contradiction_analysis",
    "get_optimized_queries",
    "select_best_sources",
]
