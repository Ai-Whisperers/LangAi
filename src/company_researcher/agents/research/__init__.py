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

from .deep_research import (
    DeepResearchAgent,
    deep_research_agent_node,
    create_deep_research_agent,
    ResearchDepth,
    ResearchIteration,
)
from .reasoning import (
    ReasoningAgent,
    reasoning_agent_node,
    create_reasoning_agent,
    ReasoningType,
    Hypothesis,
)
from .trend_analyst import (
    TrendAnalystAgent,
    trend_analyst_agent_node,
    create_trend_analyst,
    TrendDirection,
    TrendStrength,
    Trend,
    Forecast,
    TrendAnalysis,
)
from .enhanced_researcher import (
    EnhancedResearcherAgent,
    enhanced_researcher_node,
    create_enhanced_researcher_agent,
)
# Re-export from consolidated research/ version (agents/research/ version deleted)
from ...research.metrics_validator import (
    MetricsValidator,
    ValidationReport as ValidationResult,  # Alias for backward compatibility
    DataCategory,
    CompanyType,
    create_metrics_validator,
)
from .data_threshold import (
    DataThresholdChecker,
    ThresholdResult,
    RetryStrategy,
    create_threshold_checker,
)
from .quality_enforcer import (
    QualityEnforcer,
    QualityGateResult,
    ReportStatus,
    BlockReason,
    create_quality_enforcer,
)
from .multilingual_search import (
    MultilingualSearchGenerator,
    MultilingualQuery,
    Language,
    Region,
    create_multilingual_generator,
)
from .competitive_matrix import (
    CompetitiveMatrixGenerator,
    CompetitiveMatrix,
    CompetitorProfile,
    MatrixDimension,
    CompetitivePosition,
    create_competitive_matrix,
)
from .risk_quantifier import (
    RiskQuantifier,
    RiskAssessment,
    Risk,
    RiskCategory,
    RiskLevel,
    RiskProbability,
    create_risk_quantifier,
)
from .investment_thesis import (
    InvestmentThesisGenerator,
    InvestmentThesis,
    InvestmentRecommendation,
    InvestmentHorizon,
    InvestorProfile,
    BullCase,
    BearCase,
    ValuationMetrics,
    create_thesis_generator,
)
# AI-powered sentiment analysis (replaces legacy news_sentiment)
from ...ai.sentiment import (
    AISentimentAnalyzer as NewsSentimentAnalyzer,  # Alias for backward compatibility
    SentimentAnalysisResult as NewsSentimentProfile,  # Alias for backward compatibility
    SentimentLevel,
    NewsCategory,
    get_sentiment_analyzer as create_sentiment_analyzer,  # Alias for backward compatibility
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
