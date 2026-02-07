"""
Agents Module - Multi-agent research system.

Organized by category:
- base/: Base infrastructure (types, logging, node utilities)
- core/: Base classes and essential agents
- financial/: Financial analysis agents
- market/: Market and competitive analysis agents
- specialized/: Domain-specific agents (brand, social, sales)
- quality/: Quality assurance agents
- research/: Deep research and reasoning agents

Usage:
    from company_researcher.agents import (
        # Base Infrastructure
        AgentResult,
        AgentOutput,
        AgentLogger,
        agent_node,
        BaseAgentNode,
        # Core
        ResearcherAgent,
        AnalystAgent,
        SynthesizerAgent,
        # Financial
        FinancialAgent,
        EnhancedFinancialAgent,
        InvestmentAnalystAgent,
        # Market
        MarketAgent,
        EnhancedMarketAgent,
        CompetitorScoutAgent,
        # Specialized
        BrandAuditorAgent,
        SocialMediaAgent,
        SalesIntelligenceAgent,
        # Quality
        LogicCriticAgent,
        # Research
        DeepResearchAgent,
        ReasoningAgent,
    )
"""

# =============================================================================
# Base Agent Infrastructure
# =============================================================================
from .base import (  # Types; Logging; Node
    AgentConfig,
    AgentContext,
    AgentLogContext,
    AgentLogger,
    AgentOutput,
    AgentResult,
    AgentStatus,
    BaseAgentNode,
    NodeConfig,
    SearchResult,
    TokenUsage,
    agent_node,
    configure_agent_logging,
    create_agent_result,
    create_empty_result,
    format_search_results,
    get_agent_logger,
    merge_agent_results,
)
from .core.analyst import AnalystAgent, analyst_agent_node, create_analyst_agent

# =============================================================================
# Core Agents
# =============================================================================
from .core.base import BaseAgent
from .core.researcher import ResearcherAgent, create_researcher_agent, researcher_agent_node
from .core.synthesizer import SynthesizerAgent, create_synthesizer_agent, synthesizer_agent_node

# =============================================================================
# ESG Agent (imported directly from esg package, not deprecated esg_agent.py)
# =============================================================================
from .esg import (
    Controversy,
    ControversySeverity,
    ESGAgent,
    ESGAnalysis,
    ESGCategory,
    ESGMetric,
    ESGRating,
    ESGScore,
    create_esg_agent,
    esg_agent_node,
)
from .financial.enhanced_financial import enhanced_financial_agent_node

# =============================================================================
# Financial Agents
# =============================================================================
from .financial.financial import financial_agent_node
from .financial.investment_analyst import (
    InvestmentAnalystAgent,
    create_investment_analyst,
    investment_analyst_agent_node,
)
from .market.competitor_scout import competitor_scout_agent_node, competitor_scout_agent_node_traced
from .market.enhanced_market import enhanced_market_agent_node

# =============================================================================
# Market Agents
# =============================================================================
from .market.market import market_agent_node

# =============================================================================
# Agent Mixins
# =============================================================================
from .mixins import (
    ConfidenceLevel,
    ReflectionAspect,
    ReflectionScore,
    SelfReflectionMixin,
    SelfReflectionResult,
    create_reflective_agent,
)

# =============================================================================
# Quality Agents
# =============================================================================
from .quality.logic_critic import logic_critic_agent_node, quick_logic_critic_node

# =============================================================================
# Research Agents
# =============================================================================
from .research.deep_research import (
    DeepResearchAgent,
    create_deep_research_agent,
    deep_research_agent_node,
)
from .research.reasoning import ReasoningAgent, create_reasoning_agent, reasoning_agent_node
from .specialized.brand_auditor import (
    BrandAuditorAgent,
    brand_auditor_agent_node,
    create_brand_auditor,
)

# =============================================================================
# Specialized Agents
# =============================================================================
from .specialized.product import product_agent_node
from .specialized.sales_intelligence import (
    SalesIntelligenceAgent,
    create_sales_intelligence_agent,
    sales_intelligence_agent_node,
)
from .specialized.social_media import (
    SocialMediaAgent,
    create_social_media_agent,
    social_media_agent_node,
)

__all__ = [
    # Base Infrastructure - Types
    "AgentStatus",
    "TokenUsage",
    "AgentOutput",
    "AgentResult",
    "SearchResult",
    "AgentConfig",
    "AgentContext",
    "create_empty_result",
    "create_agent_result",
    "merge_agent_results",
    # Base Infrastructure - Logging
    "AgentLogger",
    "AgentLogContext",
    "get_agent_logger",
    "configure_agent_logging",
    # Base Infrastructure - Node
    "BaseAgentNode",
    "NodeConfig",
    "agent_node",
    "format_search_results",
    # Core
    "BaseAgent",
    "ResearcherAgent",
    "researcher_agent_node",
    "create_researcher_agent",
    "AnalystAgent",
    "analyst_agent_node",
    "create_analyst_agent",
    "SynthesizerAgent",
    "synthesizer_agent_node",
    "create_synthesizer_agent",
    # Financial
    "financial_agent_node",
    "enhanced_financial_agent_node",
    "InvestmentAnalystAgent",
    "investment_analyst_agent_node",
    "create_investment_analyst",
    # Market
    "market_agent_node",
    "enhanced_market_agent_node",
    "competitor_scout_agent_node",
    "competitor_scout_agent_node_traced",
    # Specialized
    "product_agent_node",
    "BrandAuditorAgent",
    "brand_auditor_agent_node",
    "create_brand_auditor",
    "SocialMediaAgent",
    "social_media_agent_node",
    "create_social_media_agent",
    "SalesIntelligenceAgent",
    "sales_intelligence_agent_node",
    "create_sales_intelligence_agent",
    # Quality
    "logic_critic_agent_node",
    "quick_logic_critic_node",
    # Research
    "DeepResearchAgent",
    "deep_research_agent_node",
    "create_deep_research_agent",
    "ReasoningAgent",
    "reasoning_agent_node",
    "create_reasoning_agent",
    # ESG
    "ESGAgent",
    "ESGAnalysis",
    "ESGScore",
    "ESGMetric",
    "ESGCategory",
    "ESGRating",
    "Controversy",
    "ControversySeverity",
    "esg_agent_node",
    "create_esg_agent",
    # Mixins
    "SelfReflectionMixin",
    "SelfReflectionResult",
    "ReflectionScore",
    "ReflectionAspect",
    "ConfidenceLevel",
    "create_reflective_agent",
]
