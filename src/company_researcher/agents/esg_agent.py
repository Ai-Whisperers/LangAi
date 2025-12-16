"""
ESG Agent - Environmental, Social, and Governance analysis.

DEPRECATED: This module re-exports from the modular esg package.
This file will be removed in a future version.

Update your imports:

    # Old import (deprecated)
    from company_researcher.agents.esg_agent import ESGAgent

    # New import (recommended)
    from company_researcher.agents.esg import (
        ESGAgent,
        ESGAnalysis,
        ESGScore,
        ESGCategory,
        create_esg_agent
    )
"""

import warnings

warnings.warn(
    "company_researcher.agents.esg_agent is deprecated. "
    "Use company_researcher.agents.esg instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export all public API from the esg package for backward compatibility
from .esg import (  # Enums; Dataclasses; Indicator frameworks; Classes; Functions
    ENVIRONMENTAL_INDICATORS,
    GOVERNANCE_INDICATORS,
    SOCIAL_INDICATORS,
    Controversy,
    ControversySeverity,
    ESGAgent,
    ESGAnalysis,
    ESGCategory,
    ESGMetric,
    ESGRating,
    ESGScore,
    ESGScorer,
    create_esg_agent,
    esg_agent_node,
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
