"""
AI-driven components for company research.

This module provides AI-powered alternatives to hardcoded logic:
- Sentiment analysis (replaces keyword-based)
- Query generation (replaces static templates)
- Quality assessment (replaces rule-based scoring)
- Data extraction (replaces regex patterns)

Usage:
    from company_researcher.ai import (
        get_sentiment_analyzer,
        get_query_generator,
        get_quality_assessor,
        get_data_extractor
    )

    # Check if AI is enabled
    from company_researcher.ai.config import get_ai_config
    config = get_ai_config()
    if config.sentiment.enabled:
        analyzer = get_sentiment_analyzer()
        result = await analyzer.analyze_sentiment(text, company_name)
"""

# Workstream 1: Sentiment Analysis (completed)
from .sentiment import (
    get_sentiment_analyzer,
    AISentimentAnalyzer,
    SentimentLevel,
    EntitySentiment,
    SentimentAnalysisResult,
    NewsCategorization,
    NewsCategory,
    SentimentAggregation,
)

# Workstream 2: Query Generation (completed)
from .query import (
    get_query_generator,
    AIQueryGenerator,
    QueryPurpose,
    CompanyContext,
    GeneratedQuery,
    QueryGenerationResult,
    QueryRefinementResult,
)

# Workstream 3: Quality Assessment (completed)
from .quality import (
    get_quality_assessor,
    reset_quality_assessor,
    AIQualityAssessor,
    QualityLevel,
    SourceType,
    ContentQualityAssessment,
    SourceQualityAssessment,
    ConfidenceAssessment,
    SectionRequirements,
    OverallQualityReport,
)

# Workstream 4: Data Extraction (completed)
from .extraction import (
    get_data_extractor,
    reset_data_extractor,
    AIDataExtractor,
    CompanyType,
    FactCategory,
    FactType,
    ContradictionSeverity,
    CompanyClassification,
    ExtractedFact,
    FinancialData,
    ContradictionAnalysis,
    ExtractionResult,
    CountryDetectionResult,
)

from .config import get_ai_config, set_ai_config, reset_ai_config, AIConfig, AIComponentConfig
from .base import AIComponent, AIComponentRegistry, get_ai_registry
from .exceptions import (
    AIComponentError,
    AIExtractionError,
    AISentimentError,
    AIQueryGenerationError,
    AIQualityAssessmentError,
    AIClassificationError,
    AIFallbackTriggered,
    AICostLimitExceeded,
    AIParsingError,
    AITimeoutError,
)
from .fallback import (
    FallbackHandler,
    FallbackRegistry,
    get_fallback_registry,
    with_fallback,
)
from .utils import (
    safe_parse_model,
    truncate_text,
    extract_json_from_text,
    normalize_confidence,
    merge_results,
    format_for_prompt,
    CostTracker,
)

# Workstream 6: Integration & Migration (completed)
from .integration import (
    AIIntegrationLayer,
    get_ai_integration,
    reset_ai_integration,
)
from .migration import (
    MigrationValidator,
    MigrationRegistry,
    ComparisonResult,
    get_migration_registry,
    reset_migration_registry,
    gradual_rollout,
)

__all__ = [
    # Sentiment Analysis (Workstream 1)
    "get_sentiment_analyzer",
    "AISentimentAnalyzer",
    "SentimentLevel",
    "EntitySentiment",
    "SentimentAnalysisResult",
    "NewsCategorization",
    "NewsCategory",
    "SentimentAggregation",
    # Query Generation (Workstream 2)
    "get_query_generator",
    "AIQueryGenerator",
    "QueryPurpose",
    "CompanyContext",
    "GeneratedQuery",
    "QueryGenerationResult",
    "QueryRefinementResult",
    # Quality Assessment (Workstream 3)
    "get_quality_assessor",
    "reset_quality_assessor",
    "AIQualityAssessor",
    "QualityLevel",
    "SourceType",
    "ContentQualityAssessment",
    "SourceQualityAssessment",
    "ConfidenceAssessment",
    "SectionRequirements",
    "OverallQualityReport",
    # Data Extraction (Workstream 4)
    "get_data_extractor",
    "reset_data_extractor",
    "AIDataExtractor",
    "CompanyType",
    "FactCategory",
    "FactType",
    "ContradictionSeverity",
    "CompanyClassification",
    "ExtractedFact",
    "FinancialData",
    "ContradictionAnalysis",
    "ExtractionResult",
    "CountryDetectionResult",
    # Config
    "get_ai_config",
    "set_ai_config",
    "reset_ai_config",
    "AIConfig",
    "AIComponentConfig",
    # Base
    "AIComponent",
    "AIComponentRegistry",
    "get_ai_registry",
    # Exceptions
    "AIComponentError",
    "AIExtractionError",
    "AISentimentError",
    "AIQueryGenerationError",
    "AIQualityAssessmentError",
    "AIClassificationError",
    "AIFallbackTriggered",
    "AICostLimitExceeded",
    "AIParsingError",
    "AITimeoutError",
    # Fallback
    "FallbackHandler",
    "FallbackRegistry",
    "get_fallback_registry",
    "with_fallback",
    # Utils
    "safe_parse_model",
    "truncate_text",
    "extract_json_from_text",
    "normalize_confidence",
    "merge_results",
    "format_for_prompt",
    "CostTracker",
    # Integration (Workstream 6)
    "AIIntegrationLayer",
    "get_ai_integration",
    "reset_ai_integration",
    # Migration (Workstream 6)
    "MigrationValidator",
    "MigrationRegistry",
    "ComparisonResult",
    "get_migration_registry",
    "reset_migration_registry",
    "gradual_rollout",
]
