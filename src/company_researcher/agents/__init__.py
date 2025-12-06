"""
Agents Module - Multi-agent research system.

Organized by category:
- core/: Base classes and essential agents
- financial/: Financial analysis agents
- market/: Market and competitive analysis agents
- specialized/: Domain-specific agents (brand, social, sales)
- quality/: Quality assurance agents
- research/: Deep research and reasoning agents

Usage:
    from company_researcher.agents import (
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
# Core Agents
# =============================================================================
from .core.base import BaseAgent
from .core.researcher import researcher_agent_node
from .core.analyst import analyst_agent_node
from .core.synthesizer import synthesizer_agent_node

# =============================================================================
# Financial Agents
# =============================================================================
from .financial.financial import financial_agent_node
from .financial.enhanced_financial import enhanced_financial_agent_node
from .financial.investment_analyst import (
    InvestmentAnalystAgent,
    investment_analyst_agent_node,
    create_investment_analyst,
)

# =============================================================================
# Market Agents
# =============================================================================
from .market.market import market_agent_node
from .market.enhanced_market import enhanced_market_agent_node
from .market.competitor_scout import (
    competitor_scout_agent_node,
    competitor_scout_agent_node_traced,
)

# =============================================================================
# Specialized Agents
# =============================================================================
from .specialized.product import product_agent_node
from .specialized.brand_auditor import (
    BrandAuditorAgent,
    brand_auditor_agent_node,
    create_brand_auditor,
)
from .specialized.social_media import (
    SocialMediaAgent,
    social_media_agent_node,
    create_social_media_agent,
)
from .specialized.sales_intelligence import (
    SalesIntelligenceAgent,
    sales_intelligence_agent_node,
    create_sales_intelligence_agent,
)

# =============================================================================
# Quality Agents
# =============================================================================
from .quality.logic_critic import (
    logic_critic_agent_node,
    quick_logic_critic_node,
)

# =============================================================================
# Research Agents
# =============================================================================
from .research.deep_research import (
    DeepResearchAgent,
    deep_research_agent_node,
    create_deep_research_agent,
)
from .research.reasoning import (
    ReasoningAgent,
    reasoning_agent_node,
    create_reasoning_agent,
)

__all__ = [
    # Core
    "BaseAgent",
    "researcher_agent_node",
    "analyst_agent_node",
    "synthesizer_agent_node",
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
]
