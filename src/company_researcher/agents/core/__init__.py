"""
Core Agents - Essential research agents.

Base classes and fundamental agents:
- BaseAgent: Abstract base class
- ResearcherAgent: Initial research
- AnalystAgent: Data analysis
- SynthesizerAgent: Result synthesis
"""

from .base import BaseAgent
from .researcher import ResearcherAgent, researcher_agent_node, create_researcher_agent
from .analyst import AnalystAgent, analyst_agent_node, create_analyst_agent
from .synthesizer import SynthesizerAgent, synthesizer_agent_node, create_synthesizer_agent

__all__ = [
    # Base
    "BaseAgent",
    # Researcher
    "ResearcherAgent",
    "researcher_agent_node",
    "create_researcher_agent",
    # Analyst
    "AnalystAgent",
    "analyst_agent_node",
    "create_analyst_agent",
    # Synthesizer
    "SynthesizerAgent",
    "synthesizer_agent_node",
    "create_synthesizer_agent",
]
