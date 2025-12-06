"""
Quality Agents - Quality assurance and validation.

Agents for ensuring research quality:
- LogicCriticAgent: Fact verification and contradiction detection
"""

from .logic_critic import (
    LogicCriticAgent,
    logic_critic_agent_node,
    create_logic_critic,
    QualityIssue,
    IssueSeverity,
)

__all__ = [
    "LogicCriticAgent",
    "logic_critic_agent_node",
    "create_logic_critic",
    "QualityIssue",
    "IssueSeverity",
]
