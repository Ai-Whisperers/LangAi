"""
Research Agents - Deep research and reasoning.

Agents for comprehensive research:
- DeepResearchAgent: Multi-iteration deep research
- ReasoningAgent: Strategic reasoning and hypothesis testing
- TrendAnalystAgent: Trend analysis and forecasting
- EnhancedResearcherAgent: Advanced scraping with Firecrawl/ScrapeGraph
- MetricsValidator: Data quality validation
- DataThresholdChecker: Search results quality checking
- QualityEnforcer: Report generation blocking
"""

# AI-powered sentiment analysis (replaces legacy news_sentiment)
from ...ai.sentiment import (
    AISentimentAnalyzer as NewsSentimentAnalyzer,  # Alias for backward compatibility
)
from ...ai.sentiment import NewsCategory
from ...ai.sentiment import (
    SentimentAnalysisResult as NewsSentimentProfile,  # Alias for backward compatibility
)
from ...ai.sentiment import SentimentLevel
from ...ai.sentiment import (
    get_sentiment_analyzer as create_sentiment_analyzer,  # Alias for backward compatibility
)

# Re-export from consolidated research/ version (agents/research/ version deleted)
from ...research.metrics_validator import CompanyType, DataCategory, MetricsValidator
from ...research.metrics_validator import (
    ValidationReport as ValidationResult,  # Alias for backward compatibility
)
from ...research.metrics_validator import create_metrics_validator
from .competitive_matrix import (
    CompetitiveMatrix,
    CompetitiveMatrixGenerator,
    CompetitivePosition,
    CompetitorProfile,
    MatrixDimension,
    create_competitive_matrix,
)
from .data_threshold import (
    DataThresholdChecker,
    RetryStrategy,
    ThresholdResult,
    create_threshold_checker,
)
from .deep_research import (
    DeepResearchAgent,
    ResearchDepth,
    ResearchIteration,
    create_deep_research_agent,
    deep_research_agent_node,
)
from .enhanced_researcher import (
    EnhancedResearcherAgent,
    create_enhanced_researcher_agent,
    enhanced_researcher_node,
)
from .investment_thesis import (
    BearCase,
    BullCase,
    InvestmentHorizon,
    InvestmentRecommendation,
    InvestmentThesis,
    InvestmentThesisGenerator,
    InvestorProfile,
    ValuationMetrics,
    create_thesis_generator,
)
from .multilingual_search import (
    Language,
    MultilingualQuery,
    MultilingualSearchGenerator,
    Region,
    create_multilingual_generator,
)
from .quality_enforcer import (
    BlockReason,
    QualityEnforcer,
    QualityGateResult,
    ReportStatus,
    create_quality_enforcer,
)
from .reasoning import (
    Hypothesis,
    ReasoningAgent,
    ReasoningType,
    create_reasoning_agent,
    reasoning_agent_node,
)
from .risk_quantifier import (
    Risk,
    RiskAssessment,
    RiskCategory,
    RiskLevel,
    RiskProbability,
    RiskQuantifier,
    create_risk_quantifier,
)
from .trend_analyst import (
    Forecast,
    Trend,
    TrendAnalysis,
    TrendAnalystAgent,
    TrendDirection,
    TrendStrength,
    create_trend_analyst,
    trend_analyst_agent_node,
)

__all__ = [
    # Deep Research
    "DeepResearchAgent",
    "deep_research_agent_node",
    "create_deep_research_agent",
    "ResearchDepth",
    "ResearchIteration",
    # Reasoning
    "ReasoningAgent",
    "reasoning_agent_node",
    "create_reasoning_agent",
    "ReasoningType",
    "Hypothesis",
    # Trend Analysis
    "TrendAnalystAgent",
    "trend_analyst_agent_node",
    "create_trend_analyst",
    "TrendDirection",
    "TrendStrength",
    "Trend",
    "Forecast",
    "TrendAnalysis",
    # Enhanced Researcher (Firecrawl/ScrapeGraph)
    "EnhancedResearcherAgent",
    "enhanced_researcher_node",
    "create_enhanced_researcher_agent",
    # Metrics Validation
    "MetricsValidator",
    "ValidationResult",
    "DataCategory",
    "CompanyType",
    "create_metrics_validator",
    # Data Threshold
    "DataThresholdChecker",
    "ThresholdResult",
    "RetryStrategy",
    "create_threshold_checker",
    # Quality Enforcer
    "QualityEnforcer",
    "QualityGateResult",
    "ReportStatus",
    "BlockReason",
    "create_quality_enforcer",
    # Multilingual Search
    "MultilingualSearchGenerator",
    "MultilingualQuery",
    "Language",
    "Region",
    "create_multilingual_generator",
    # Competitive Matrix
    "CompetitiveMatrixGenerator",
    "CompetitiveMatrix",
    "CompetitorProfile",
    "MatrixDimension",
    "CompetitivePosition",
    "create_competitive_matrix",
    # Risk Quantifier
    "RiskQuantifier",
    "RiskAssessment",
    "Risk",
    "RiskCategory",
    "RiskLevel",
    "RiskProbability",
    "create_risk_quantifier",
    # Investment Thesis
    "InvestmentThesisGenerator",
    "InvestmentThesis",
    "InvestmentRecommendation",
    "InvestmentHorizon",
    "InvestorProfile",
    "BullCase",
    "BearCase",
    "ValuationMetrics",
    "create_thesis_generator",
    # News Sentiment (AI-powered)
    "NewsSentimentAnalyzer",
    "NewsSentimentProfile",
    "SentimentLevel",
    "NewsCategory",
    "create_sentiment_analyzer",
]
