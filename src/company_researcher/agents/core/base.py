"""
Base agent class for all research agents.
"""

from typing import Dict, Any
from abc import ABC, abstractmethod
from ..state import OverallState


class BaseAgent(ABC):
    """Base class for all research agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Agent name for identification.

        Returns:
            Agent name string
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Agent role description.

        Returns:
            Description of agent's responsibilities
        """
        pass

    @abstractmethod
    def execute(self, state: OverallState) -> Dict[str, Any]:
        """
        Execute agent's task.

        Args:
            state: Current workflow state

        Returns:
            State update dictionary with agent's contributions
        """
        pass
