"""
Core Agents - Essential research agents.

Base classes and fundamental agents:
- BaseAgent: Abstract base class
- ResearcherAgent: Initial research
- AnalystAgent: Data analysis
- SynthesizerAgent: Result synthesis
"""

from .base import BaseAgent
from .researcher import researcher_agent_node

__all__ = [
    # Base
    "BaseAgent",
    # Researcher
    "researcher_agent_node",
]
