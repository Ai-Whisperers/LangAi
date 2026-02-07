"""
ESG Agent Module.

Provides Environmental, Social, and Governance analysis:
- ESG scoring framework
- Environmental impact assessment
- Social responsibility analysis
- Governance structure evaluation
- Sustainability report parsing
- Controversy detection

Usage:
    from company_researcher.agents.esg import (
        ESGAgent,
        ESGAnalysis,
        ESGScore,
        create_esg_agent
    )
"""

from .agent import ESGAgent, create_esg_agent, esg_agent_node
from .models import (  # Enums; Dataclasses; Indicator frameworks
    ENVIRONMENTAL_INDICATORS,
    GOVERNANCE_INDICATORS,
    SOCIAL_INDICATORS,
    Controversy,
    ControversySeverity,
    ESGAnalysis,
    ESGCategory,
    ESGMetric,
    ESGRating,
    ESGScore,
)
from .scorer import ESGScorer

__all__ = [
    # Enums
    "ESGCategory",
    "ESGRating",
    "ControversySeverity",
    # Dataclasses
    "ESGMetric",
    "Controversy",
    "ESGScore",
    "ESGAnalysis",
    # Indicators
    "ENVIRONMENTAL_INDICATORS",
    "SOCIAL_INDICATORS",
    "GOVERNANCE_INDICATORS",
    # Classes
    "ESGScorer",
    "ESGAgent",
    # Functions
    "esg_agent_node",
    "create_esg_agent",
]
