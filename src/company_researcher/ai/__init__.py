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

from .base import AIComponent, AIComponentRegistry, get_ai_registry
from .config import AIComponentConfig, AIConfig, get_ai_config, reset_ai_config, set_ai_config
from .exceptions import (
    AIClassificationError,
    AIComponentError,
    AICostLimitExceeded,
    AIExtractionError,
    AIFallbackTriggered,
    AIParsingError,
    AIQualityAssessmentError,
    AIQueryGenerationError,
    AISentimentError,
    AITimeoutError,
)

# Workstream 4: Data Extraction (completed)
from .extraction import (
    AIDataExtractor,
    CompanyClassification,
    CompanyType,
    ContradictionAnalysis,
    ContradictionSeverity,
    CountryDetectionResult,
    ExtractedFact,
    ExtractionResult,
    FactCategory,
    FactType,
    FinancialData,
    get_data_extractor,
    reset_data_extractor,
)
from .fallback import FallbackHandler, FallbackRegistry, get_fallback_registry, with_fallback

# Workstream 6: Integration & Migration (completed)
from .integration import AIIntegrationLayer, get_ai_integration, reset_ai_integration
from .migration import (
    ComparisonResult,
    MigrationRegistry,
    MigrationValidator,
    get_migration_registry,
    gradual_rollout,
    reset_migration_registry,
)

# Workstream 3: Quality Assessment (completed)
from .quality import (
    AIQualityAssessor,
    ConfidenceAssessment,
    ContentQualityAssessment,
    OverallQualityReport,
    QualityLevel,
    SectionRequirements,
    SourceQualityAssessment,
    SourceType,
    get_quality_assessor,
    reset_quality_assessor,
)

# Workstream 2: Query Generation (completed)
from .query import (
    AIQueryGenerator,
    CompanyContext,
    GeneratedQuery,
    QueryGenerationResult,
    QueryPurpose,
    QueryRefinementResult,
    get_query_generator,
)

# Workstream 1: Sentiment Analysis (completed)
from .sentiment import (
    AISentimentAnalyzer,
    EntitySentiment,
    NewsCategorization,
    NewsCategory,
    SentimentAggregation,
    SentimentAnalysisResult,
    SentimentLevel,
    get_sentiment_analyzer,
)
from .utils import (
    CostTracker,
    extract_json_from_text,
    format_for_prompt,
    merge_results,
    normalize_confidence,
    safe_parse_model,
    truncate_text,
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
