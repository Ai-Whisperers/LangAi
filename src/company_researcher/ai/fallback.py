"""Fallback handlers for AI components."""
from typing import Callable, TypeVar, Any, Optional
from functools import wraps
import logging
import asyncio

from .config import get_ai_config
from .exceptions import AIFallbackTriggered, AIComponentError

logger = logging.getLogger(__name__)

T = TypeVar('T')


def with_fallback(
    legacy_func: Callable[..., T],
    component_name: str
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to add fallback to legacy logic.

    Use this decorator on async AI functions to automatically
    fall back to legacy (sync) functions on failure.

    Example:
        def legacy_sentiment(text):
            # Old keyword-based logic
            return {"sentiment": "neutral"}

        @with_fallback(legacy_sentiment, "sentiment")
        async def ai_sentiment(text):
            # New AI logic
            return await analyzer.analyze(text)
    """

    def decorator(ai_func: Callable[..., T]) -> Callable[..., T]:
        @wraps(ai_func)
        async def wrapper(*args, **kwargs) -> T:
            config = get_ai_config()
            component_config = config.get_component_config(component_name)

            # Check if AI is enabled
            if not config.global_enabled:
                logger.debug(f"AI globally disabled, using legacy for {component_name}")
                return legacy_func(*args, **kwargs)

            if component_config and not component_config.enabled:
                logger.debug(f"AI {component_name} disabled, using legacy")
                return legacy_func(*args, **kwargs)

            try:
                return await ai_func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"AI {component_name} failed: {e}")

                if component_config and component_config.fallback_to_legacy:
                    logger.info(f"Falling back to legacy {component_name}")
                    return legacy_func(*args, **kwargs)
                else:
                    raise AIFallbackTriggered(
                        component=component_name,
                        message="AI failed and fallback disabled",
                        original_error=e,
                        used_fallback=False
                    )

        return wrapper
    return decorator


class FallbackHandler:
    """
    Handler for managing fallbacks between AI and legacy logic.

    Tracks success/failure rates and provides statistics.

    Example:
        handler = FallbackHandler("sentiment")

        result = await handler.execute(
            ai_func=ai_sentiment,
            legacy_func=legacy_sentiment,
            text="Company reported record profits"
        )

        print(handler.get_stats())
    """

    def __init__(self, component_name: str):
        self.component_name = component_name
        self._ai_success_count = 0
        self._ai_failure_count = 0
        self._fallback_count = 0
        self._legacy_only_count = 0

    async def execute(
        self,
        ai_func: Callable,
        legacy_func: Callable,
        *args,
        use_ai: Optional[bool] = None,
        **kwargs
    ) -> Any:
        """
        Execute AI function with fallback to legacy.

        Args:
            ai_func: Async AI function
            legacy_func: Sync legacy function
            *args: Arguments to pass to both functions
            use_ai: Override config to force AI or legacy
            **kwargs: Keyword arguments to pass to both functions

        Returns:
            Result from AI or legacy function
        """
        config = get_ai_config()
        component_config = config.get_component_config(self.component_name)

        # Determine if we should use AI
        should_use_ai = use_ai
        if should_use_ai is None:
            should_use_ai = (
                config.global_enabled and
                component_config and
                component_config.enabled
            )

        if not should_use_ai:
            self._legacy_only_count += 1
            return legacy_func(*args, **kwargs)

        try:
            # Handle both sync and async ai_func
            if asyncio.iscoroutinefunction(ai_func):
                result = await ai_func(*args, **kwargs)
            else:
                result = ai_func(*args, **kwargs)

            self._ai_success_count += 1
            return result

        except Exception as e:
            self._ai_failure_count += 1
            logger.warning(f"AI {self.component_name} failed: {e}")

            # Check if fallback is enabled
            if component_config and component_config.fallback_to_legacy:
                self._fallback_count += 1
                logger.info(f"Using fallback for {self.component_name}")
                return legacy_func(*args, **kwargs)
            else:
                raise

    def get_stats(self) -> dict:
        """Get fallback statistics."""
        total_ai_attempts = self._ai_success_count + self._ai_failure_count
        total_calls = total_ai_attempts + self._legacy_only_count

        return {
            "component": self.component_name,
            "total_calls": total_calls,
            "ai_success_count": self._ai_success_count,
            "ai_failure_count": self._ai_failure_count,
            "fallback_count": self._fallback_count,
            "legacy_only_count": self._legacy_only_count,
            "ai_success_rate": (
                self._ai_success_count / total_ai_attempts
                if total_ai_attempts > 0 else 0
            ),
            "ai_usage_rate": (
                total_ai_attempts / total_calls
                if total_calls > 0 else 0
            )
        }

    def reset_stats(self):
        """Reset statistics."""
        self._ai_success_count = 0
        self._ai_failure_count = 0
        self._fallback_count = 0
        self._legacy_only_count = 0


class FallbackRegistry:
    """Registry for all fallback handlers."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers = {}
        return cls._instance

    def get_handler(self, component_name: str) -> FallbackHandler:
        """Get or create a fallback handler for a component."""
        if component_name not in self._handlers:
            self._handlers[component_name] = FallbackHandler(component_name)
        return self._handlers[component_name]

    def get_all_stats(self) -> dict:
        """Get stats for all handlers."""
        return {
            name: handler.get_stats()
            for name, handler in self._handlers.items()
        }

    def reset_all_stats(self):
        """Reset stats for all handlers."""
        for handler in self._handlers.values():
            handler.reset_stats()


def get_fallback_registry() -> FallbackRegistry:
    """Get the fallback registry singleton."""
    return FallbackRegistry()
