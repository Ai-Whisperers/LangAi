"""
Token Cache - Caching for token usage metrics.

Tracks:
- Token counts per request
- Cumulative usage
- Cost estimation
- Usage analytics
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .lru_cache import LRUCache, LRUCacheConfig


@dataclass
class TokenUsage:
    """Token usage for a single request."""
    request_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Cost tracking (optional)
    prompt_cost: float = 0.0
    completion_cost: float = 0.0
    total_cost: float = 0.0

    # Context
    operation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "timestamp": self.timestamp.isoformat(),
            "prompt_cost": self.prompt_cost,
            "completion_cost": self.completion_cost,
            "total_cost": self.total_cost,
            "operation": self.operation,
            "metadata": self.metadata
        }


# Token pricing (per 1K tokens) - approximate
MODEL_PRICING = {
    # OpenAI
    "gpt-4": {"prompt": 0.03, "completion": 0.06},
    "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
    "gpt-4o": {"prompt": 0.005, "completion": 0.015},
    "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
    # Anthropic
    "claude-3-opus": {"prompt": 0.015, "completion": 0.075},
    "claude-3-sonnet": {"prompt": 0.003, "completion": 0.015},
    "claude-3-haiku": {"prompt": 0.00025, "completion": 0.00125},
    "claude-3.5-sonnet": {"prompt": 0.003, "completion": 0.015},
    # Default
    "default": {"prompt": 0.01, "completion": 0.03}
}


class TokenCache:
    """
    Cache for token usage tracking and analytics.

    Usage:
        cache = TokenCache()

        # Track usage
        usage = cache.track(
            request_id="req-123",
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=50
        )

        # Get statistics
        stats = cache.get_stats()
        print(f"Total cost: ${stats['total_cost']:.4f}")

        # Get usage by model
        by_model = cache.get_usage_by_model()
    """

    def __init__(
        self,
        max_entries: int = 10000,
        retention_hours: int = 24
    ):
        self._cache = LRUCache[str, TokenUsage](LRUCacheConfig(max_size=max_entries))
        self._history: List[TokenUsage] = []
        self._retention_hours = retention_hours
        self._lock = threading.RLock()

        # Cumulative stats
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._total_cost = 0.0
        self._usage_by_model: Dict[str, Dict[str, int]] = {}
        self._usage_by_operation: Dict[str, Dict[str, int]] = {}

    def track(
        self,
        request_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        operation: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TokenUsage:
        """
        Track token usage for a request.

        Args:
            request_id: Unique request identifier
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            operation: Operation type (e.g., "research", "analysis")
            metadata: Additional metadata

        Returns:
            TokenUsage record
        """
        # Calculate cost
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]

        usage = TokenUsage(
            request_id=request_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            prompt_cost=prompt_cost,
            completion_cost=completion_cost,
            total_cost=prompt_cost + completion_cost,
            operation=operation,
            metadata=metadata or {}
        )

        with self._lock:
            # Store in cache
            self._cache.put(request_id, usage)
            self._history.append(usage)

            # Update cumulative stats
            self._total_prompt_tokens += prompt_tokens
            self._total_completion_tokens += completion_tokens
            self._total_cost += usage.total_cost

            # Update by-model stats
            if model not in self._usage_by_model:
                self._usage_by_model[model] = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "request_count": 0
                }
            self._usage_by_model[model]["prompt_tokens"] += prompt_tokens
            self._usage_by_model[model]["completion_tokens"] += completion_tokens
            self._usage_by_model[model]["total_tokens"] += usage.total_tokens
            self._usage_by_model[model]["total_cost"] += usage.total_cost
            self._usage_by_model[model]["request_count"] += 1

            # Update by-operation stats
            if operation:
                if operation not in self._usage_by_operation:
                    self._usage_by_operation[operation] = {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                        "total_cost": 0.0,
                        "request_count": 0
                    }
                self._usage_by_operation[operation]["prompt_tokens"] += prompt_tokens
                self._usage_by_operation[operation]["completion_tokens"] += completion_tokens
                self._usage_by_operation[operation]["total_tokens"] += usage.total_tokens
                self._usage_by_operation[operation]["total_cost"] += usage.total_cost
                self._usage_by_operation[operation]["request_count"] += 1

            # Cleanup old entries
            self._cleanup_old_entries()

        return usage

    def get(self, request_id: str) -> Optional[TokenUsage]:
        """Get usage for a specific request."""
        return self._cache.get(request_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get cumulative statistics."""
        with self._lock:
            return {
                "total_prompt_tokens": self._total_prompt_tokens,
                "total_completion_tokens": self._total_completion_tokens,
                "total_tokens": self._total_prompt_tokens + self._total_completion_tokens,
                "total_cost": self._total_cost,
                "request_count": len(self._history),
                "avg_tokens_per_request": (
                    (self._total_prompt_tokens + self._total_completion_tokens) / len(self._history)
                    if self._history else 0
                ),
                "avg_cost_per_request": (
                    self._total_cost / len(self._history)
                    if self._history else 0
                )
            }

    def get_usage_by_model(self) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics by model."""
        with self._lock:
            return dict(self._usage_by_model)

    def get_usage_by_operation(self) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics by operation."""
        with self._lock:
            return dict(self._usage_by_operation)

    def get_recent_usage(
        self,
        hours: int = 1,
        limit: int = 100
    ) -> List[TokenUsage]:
        """Get recent usage entries."""
        with self._lock:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            recent = [u for u in self._history if u.timestamp >= cutoff]
            return recent[-limit:]

    def get_hourly_summary(self, hours: int = 24) -> Dict[str, Dict[str, Any]]:
        """Get hourly usage summary."""
        with self._lock:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            hourly = {}

            for usage in self._history:
                if usage.timestamp >= cutoff:
                    hour_key = usage.timestamp.strftime("%Y-%m-%d %H:00")
                    if hour_key not in hourly:
                        hourly[hour_key] = {
                            "total_tokens": 0,
                            "total_cost": 0.0,
                            "request_count": 0
                        }
                    hourly[hour_key]["total_tokens"] += usage.total_tokens
                    hourly[hour_key]["total_cost"] += usage.total_cost
                    hourly[hour_key]["request_count"] += 1

            return hourly

    def estimate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Estimate cost for given token counts."""
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        return prompt_cost + completion_cost

    def _cleanup_old_entries(self) -> None:
        """Remove entries older than retention period."""
        cutoff = datetime.utcnow() - timedelta(hours=self._retention_hours)
        self._history = [u for u in self._history if u.timestamp >= cutoff]

    def clear(self) -> None:
        """Clear all cached data."""
        with self._lock:
            self._cache.clear()
            self._history.clear()
            self._total_prompt_tokens = 0
            self._total_completion_tokens = 0
            self._total_cost = 0.0
            self._usage_by_model.clear()
            self._usage_by_operation.clear()


# Global token cache
_token_cache: Optional[TokenCache] = None


def _get_token_cache() -> TokenCache:
    """Get or create global token cache."""
    global _token_cache
    if _token_cache is None:
        _token_cache = TokenCache()
    return _token_cache


def track_tokens(
    request_id: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    operation: Optional[str] = None,
    **metadata
) -> TokenUsage:
    """
    Track token usage with global cache.

    Args:
        request_id: Unique request ID
        model: Model name
        prompt_tokens: Prompt token count
        completion_tokens: Completion token count
        operation: Operation type
        **metadata: Additional metadata

    Returns:
        TokenUsage record
    """
    cache = _get_token_cache()
    return cache.track(
        request_id=request_id,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        operation=operation,
        metadata=metadata
    )
