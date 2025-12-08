"""
ESG Agent - Environmental, Social, and Governance analysis.

DEPRECATED: This module re-exports from the modular esg package.
Import directly from company_researcher.agents.esg instead:

    from company_researcher.agents.esg import (
        ESGAgent,
        ESGAnalysis,
        ESGScore,
        ESGCategory,
        create_esg_agent
    )
"""

# Re-export all public API from the esg package for backward compatibility
from .esg import (
    # Enums
    ESGCategory,
    ESGRating,
    ControversySeverity,
    # Dataclasses
    ESGMetric,
    Controversy,
    ESGScore,
    ESGAnalysis,
    # Indicator frameworks
    ENVIRONMENTAL_INDICATORS,
    SOCIAL_INDICATORS,
    GOVERNANCE_INDICATORS,
    # Classes
    ESGScorer,
    ESGAgent,
    # Functions
    esg_agent_node,
    create_esg_agent,
)

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
