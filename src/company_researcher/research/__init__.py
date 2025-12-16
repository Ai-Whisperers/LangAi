"""
Research Enhancement Package

This package provides modules to improve research report quality:

1. multilingual_search - Generates multilingual search queries for regional companies
2. metrics_validator - Validates required metrics with priority levels
3. data_threshold - Pre-generation checks to prevent empty reports
4. enhanced_fact_extraction - Pattern-based fact extraction with confidence scores
5. historical_trends - Multi-year trend analysis and visualization
6. competitive_matrix - Competitive comparison matrices
7. source_tracker - Source utilization tracking and analysis
8. risk_quantifier - Quantified risk assessment
9. investment_thesis - Data-backed investment thesis generation
10. quality_enforcer - Report quality validation and enforcement
"""

from ..agents.research.multilingual_search import (
    Language,
    MultilingualSearchGenerator,
    RegionalSource,
    create_multilingual_generator,
)
from .data_threshold import (
    DataThresholdChecker,
    RetryStrategy,
    ThresholdResult,
    check_data_threshold,
    should_generate_report,
)
from .enhanced_fact_extraction import (
    Currency,
    EnhancedFactExtractor,
    ExtractedFact,
    FactType,
    extract_facts,
    extract_facts_from_sources,
)
from .historical_trends import (
    HistoricalTrendAnalyzer,
    TrendAnalysis,
    TrendDirection,
    TrendMetric,
    TrendTable,
    create_trend_analyzer,
)
from .metrics_validator import (
    CompanyType,
    DataCategory,
    MetricDefinition,
    MetricPriority,
    MetricStatus,
    MetricsValidator,
    MetricValidation,
)
from .metrics_validator import ValidationReport
from .metrics_validator import (
    ValidationReport as ValidationResult,  # Alias for backward compatibility
)
from .metrics_validator import create_metrics_validator, validate_research_metrics
from .quality_enforcer import (
    IssueSeverity,
    IssueType,
    QualityIssue,
    QualityLevel,
    QualityReport,
    ReportQualityEnforcer,
    SectionType,
    create_quality_enforcer,
)
from .source_tracker import ExtractedFact as TrackedFact
from .source_tracker import (
    ExtractionCoverage,
    FactCategory,
    SourceInfo,
    SourceType,
    SourceUtilizationTracker,
    create_source_tracker,
)

__all__ = [
    # Multilingual Search
    "MultilingualSearchGenerator",
    "Language",
    "RegionalSource",
    "create_multilingual_generator",
    # Metrics Validation
    "MetricsValidator",
    "MetricPriority",
    "CompanyType",
    "MetricDefinition",
    "ValidationReport",
    "validate_research_metrics",
    # Data Threshold
    "DataThresholdChecker",
    "RetryStrategy",
    "ThresholdResult",
    "check_data_threshold",
    "should_generate_report",
    # Fact Extraction
    "EnhancedFactExtractor",
    "FactType",
    "Currency",
    "ExtractedFact",
    "extract_facts",
    "extract_facts_from_sources",
    # Historical Trends
    "HistoricalTrendAnalyzer",
    "TrendDirection",
    "TrendMetric",
    "TrendAnalysis",
    "TrendTable",
    "create_trend_analyzer",
    # Source Tracking
    "SourceUtilizationTracker",
    "SourceType",
    "FactCategory",
    "TrackedFact",
    "SourceInfo",
    "ExtractionCoverage",
    "create_source_tracker",
    # Quality Enforcement
    "ReportQualityEnforcer",
    "QualityLevel",
    "SectionType",
    "IssueType",
    "IssueSeverity",
    "QualityIssue",
    "QualityReport",
    "create_quality_enforcer",
]
