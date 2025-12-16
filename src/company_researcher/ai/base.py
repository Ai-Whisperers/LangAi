"""Base classes and utilities for AI components."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel

from ..utils import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class AIComponent(ABC, Generic[T]):
    """
    Base class for AI-driven components.

    All AI components should inherit from this class to ensure
    consistent behavior, cost tracking, and error handling.

    Example:
        class MySentimentAnalyzer(AIComponent[SentimentResult]):
            component_name = "sentiment"
            default_task_type = TaskType.CLASSIFICATION

            def process(self, text: str) -> SentimentResult:
                return self._call_llm(prompt, response_model=SentimentResult)
    """

    component_name: str = "base"
    default_task_type: str = "reasoning"  # TaskType enum value
    default_complexity: str = "medium"

    def __init__(self):
        self._client = None
        self._call_count = 0
        self._total_cost = 0.0
        self._total_input_tokens = 0
        self._total_output_tokens = 0

    @property
    def client(self):
        """Lazy-load the smart client."""
        if self._client is None:
            from ..llm import get_smart_client

            self._client = get_smart_client()
        return self._client

    def _call_llm(
        self,
        prompt: str,
        task_type: Optional[str] = None,
        complexity: Optional[str] = None,
        response_model: Optional[type] = None,
        max_tokens: Optional[int] = None,
        system: Optional[str] = None,
        json_mode: bool = False,
    ) -> Any:
        """
        Call LLM with standard handling.

        Args:
            prompt: The prompt to send to the LLM
            task_type: Override default task type
            complexity: Override default complexity (low, medium, high)
            response_model: Pydantic model to parse response into
            max_tokens: Maximum tokens for response
            system: System prompt
            json_mode: Enable JSON mode for structured output

        Returns:
            Parsed response model if provided, otherwise raw content string
        """
        from ..llm.response_parser import parse_json_response

        # Build completion kwargs
        kwargs = {
            "prompt": prompt,
            "task_type": task_type or self.default_task_type,
            "complexity": complexity or self.default_complexity,
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if system:
            kwargs["system"] = system
        if json_mode or response_model:
            kwargs["json_mode"] = True

        result = self.client.complete(**kwargs)

        # Track usage
        self._call_count += 1
        self._total_cost += getattr(result, "cost", 0.0)
        self._total_input_tokens += getattr(result, "input_tokens", 0)
        self._total_output_tokens += getattr(result, "output_tokens", 0)

        # Parse response if model provided
        if response_model:
            parsed = parse_json_response(result.content, default={})
            try:
                return response_model(**parsed)
            except Exception as e:
                logger.warning(f"Failed to parse response into {response_model}: {e}")
                # Return parsed dict if model instantiation fails
                return parsed

        return result.content

    def get_stats(self) -> Dict[str, Any]:
        """Get component usage statistics."""
        return {
            "component": self.component_name,
            "call_count": self._call_count,
            "total_cost": self._total_cost,
            "total_input_tokens": self._total_input_tokens,
            "total_output_tokens": self._total_output_tokens,
            "avg_cost_per_call": self._total_cost / self._call_count if self._call_count > 0 else 0,
        }

    def reset_stats(self):
        """Reset usage statistics."""
        self._call_count = 0
        self._total_cost = 0.0
        self._total_input_tokens = 0
        self._total_output_tokens = 0

    @abstractmethod
    def process(self, *args, **kwargs) -> T:
        """
        Main processing method to implement.

        Subclasses must implement this method with their specific logic.
        """


class AIComponentRegistry:
    """
    Registry for AI components with feature flags.

    Singleton pattern to manage all AI components and their enable/disable state.

    Example:
        registry = get_ai_registry()
        registry.register("sentiment", SentimentAnalyzer(), enabled=True)

        if registry.is_enabled("sentiment"):
            analyzer = registry.get("sentiment")
            result = await analyzer.process(text)
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._components: Dict[str, AIComponent] = {}
            cls._instance._feature_flags: Dict[str, bool] = {}
        return cls._instance

    def register(self, name: str, component: AIComponent, enabled: bool = True):
        """Register an AI component."""
        self._components[name] = component
        self._feature_flags[name] = enabled
        logger.info(f"Registered AI component: {name} (enabled={enabled})")

    def get(self, name: str) -> Optional[AIComponent]:
        """Get a registered component if enabled."""
        if self._feature_flags.get(name, False):
            return self._components.get(name)
        return None

    def get_unchecked(self, name: str) -> Optional[AIComponent]:
        """Get a registered component regardless of enabled state."""
        return self._components.get(name)

    def is_enabled(self, name: str) -> bool:
        """Check if a component is enabled."""
        return self._feature_flags.get(name, False)

    def is_registered(self, name: str) -> bool:
        """Check if a component is registered."""
        return name in self._components

    def enable(self, name: str):
        """Enable a component."""
        if name in self._components:
            self._feature_flags[name] = True
            logger.info(f"Enabled AI component: {name}")
        else:
            logger.warning(f"Cannot enable unregistered component: {name}")

    def disable(self, name: str):
        """Disable a component."""
        if name in self._components:
            self._feature_flags[name] = False
            logger.info(f"Disabled AI component: {name}")

    def list_components(self) -> Dict[str, bool]:
        """List all registered components and their enabled state."""
        return {name: self._feature_flags.get(name, False) for name in self._components}

    def get_all_stats(self) -> Dict[str, Dict]:
        """Get stats for all enabled components."""
        return {
            name: comp.get_stats()
            for name, comp in self._components.items()
            if self._feature_flags.get(name, False)
        }

    def reset_all_stats(self):
        """Reset stats for all components."""
        for comp in self._components.values():
            comp.reset_stats()


# Singleton accessor
_registry_instance: Optional[AIComponentRegistry] = None


def get_ai_registry() -> AIComponentRegistry:
    """Get the AI component registry singleton."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = AIComponentRegistry()
    return _registry_instance
