"""Migration utilities for transitioning from legacy to AI."""
from typing import Callable, Any, Optional, Dict, List
from functools import wraps
import logging
import random
import asyncio
from dataclasses import dataclass, field
from datetime import datetime

from .config import get_ai_config

logger = logging.getLogger(__name__)


@dataclass
class ComparisonResult:
    """Result of comparing AI vs legacy output."""
    component: str
    timestamp: datetime
    ai_result: Any
    legacy_result: Any
    match: bool
    similarity_score: float
    differences: List[str] = field(default_factory=list)
    ai_latency_ms: float = 0.0
    legacy_latency_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "component": self.component,
            "timestamp": self.timestamp.isoformat(),
            "match": self.match,
            "similarity_score": self.similarity_score,
            "differences": self.differences,
            "ai_latency_ms": self.ai_latency_ms,
            "legacy_latency_ms": self.legacy_latency_ms,
        }


def gradual_rollout(
    component_name: str,
    rollout_percentage: float = 100.0
) -> Callable:
    """
    Decorator for gradual rollout of AI components.

    Randomly skips AI for some requests based on percentage.

    Args:
        component_name: Name of the component
        rollout_percentage: Percentage of requests to use AI (0-100)

    Example:
        @gradual_rollout("sentiment", 50.0)  # 50% use AI
        async def analyze_sentiment(text):
            return await ai_analyzer.analyze(text)
    """
    def decorator(ai_func: Callable) -> Callable:
        @wraps(ai_func)
        async def wrapper(*args, **kwargs):
            config = get_ai_config()

            # Check global enabled
            if not config.global_enabled:
                logger.debug(f"AI globally disabled for {component_name}")
                return None

            # Check component enabled
            component_config = config.get_component_config(component_name)
            if component_config and not component_config.enabled:
                logger.debug(f"AI {component_name} disabled")
                return None

            # Rollout check
            if random.random() * 100 > rollout_percentage:
                logger.debug(f"Skipping AI {component_name} (rollout: {rollout_percentage}%)")
                return None  # Signal to use legacy

            return await ai_func(*args, **kwargs)
        return wrapper
    return decorator


class MigrationValidator:
    """
    Validates AI migration by comparing to legacy results.

    Useful during migration to ensure AI produces similar
    or better results than legacy logic.

    Example:
        validator = MigrationValidator("sentiment")

        result = await validator.validate(
            ai_func=ai_sentiment,
            legacy_func=legacy_sentiment,
            text="Company reported record earnings"
        )

        print(f"Match: {result.match}")
        print(f"Similarity: {result.similarity_score}")
    """

    def __init__(self, component_name: str):
        self.component_name = component_name
        self.comparisons: List[ComparisonResult] = []
        self._max_history = 1000  # Limit stored comparisons

    async def validate(
        self,
        ai_func: Callable,
        legacy_func: Callable,
        *args,
        **kwargs
    ) -> ComparisonResult:
        """
        Run both AI and legacy, compare results.

        Args:
            ai_func: Async AI function
            legacy_func: Sync legacy function
            *args, **kwargs: Arguments for both functions

        Returns:
            ComparisonResult with both outputs and comparison
        """
        # Run AI
        ai_start = datetime.now()
        try:
            if asyncio.iscoroutinefunction(ai_func):
                ai_result = await ai_func(*args, **kwargs)
            else:
                ai_result = ai_func(*args, **kwargs)
        except Exception as e:
            ai_result = {"error": str(e)}
            logger.warning(f"AI {self.component_name} error during validation: {e}")
        ai_latency = (datetime.now() - ai_start).total_seconds() * 1000

        # Run legacy
        legacy_start = datetime.now()
        try:
            legacy_result = legacy_func(*args, **kwargs)
        except Exception as e:
            legacy_result = {"error": str(e)}
            logger.warning(f"Legacy {self.component_name} error during validation: {e}")
        legacy_latency = (datetime.now() - legacy_start).total_seconds() * 1000

        # Compare
        match, similarity, differences = self._compare_results(ai_result, legacy_result)

        comparison = ComparisonResult(
            component=self.component_name,
            timestamp=datetime.now(),
            ai_result=ai_result,
            legacy_result=legacy_result,
            match=match,
            similarity_score=similarity,
            differences=differences,
            ai_latency_ms=ai_latency,
            legacy_latency_ms=legacy_latency
        )

        self.comparisons.append(comparison)

        # Trim history
        if len(self.comparisons) > self._max_history:
            self.comparisons = self.comparisons[-self._max_history:]

        return comparison

    def _compare_results(
        self,
        ai_result: Any,
        legacy_result: Any
    ) -> tuple:
        """Compare AI and legacy results."""
        differences = []

        # Handle None results
        if ai_result is None and legacy_result is None:
            return True, 1.0, []

        if ai_result is None or legacy_result is None:
            differences.append(f"One result is None: AI={ai_result is not None}, Legacy={legacy_result is not None}")
            return False, 0.0, differences

        # Direct equality
        if ai_result == legacy_result:
            return True, 1.0, []

        # Dict comparison
        if isinstance(ai_result, dict) and isinstance(legacy_result, dict):
            similarity = self._compare_dicts(ai_result, legacy_result, differences)
            return similarity > 0.8, similarity, differences

        # List comparison
        if isinstance(ai_result, list) and isinstance(legacy_result, list):
            similarity = self._compare_lists(ai_result, legacy_result, differences)
            return similarity > 0.8, similarity, differences

        # String comparison
        if isinstance(ai_result, str) and isinstance(legacy_result, str):
            similarity = self._compare_strings(ai_result, legacy_result, differences)
            return similarity > 0.8, similarity, differences

        # Numeric comparison
        if isinstance(ai_result, (int, float)) and isinstance(legacy_result, (int, float)):
            similarity = self._compare_numbers(ai_result, legacy_result, differences)
            return similarity > 0.9, similarity, differences

        # Type mismatch
        differences.append(f"Type mismatch: {type(ai_result).__name__} vs {type(legacy_result).__name__}")
        return False, 0.0, differences

    def _compare_dicts(
        self,
        d1: Dict,
        d2: Dict,
        differences: List[str]
    ) -> float:
        """Compare two dicts and return similarity score."""
        all_keys = set(d1.keys()) | set(d2.keys())
        if not all_keys:
            return 1.0

        matching = 0
        for key in all_keys:
            v1 = d1.get(key)
            v2 = d2.get(key)

            if v1 == v2:
                matching += 1
            elif key not in d1:
                differences.append(f"Missing in AI: {key}")
            elif key not in d2:
                differences.append(f"Extra in AI: {key}")
            else:
                differences.append(f"Different {key}: AI={v1}, Legacy={v2}")

        return matching / len(all_keys)

    def _compare_lists(
        self,
        l1: List,
        l2: List,
        differences: List[str]
    ) -> float:
        """Compare two lists and return similarity score."""
        if not l1 and not l2:
            return 1.0
        if not l1 or not l2:
            differences.append(f"List length mismatch: {len(l1)} vs {len(l2)}")
            return 0.0

        # Simple overlap calculation
        set1 = set(str(x) for x in l1)
        set2 = set(str(x) for x in l2)
        overlap = len(set1 & set2)
        total = len(set1 | set2)

        if overlap < total:
            differences.append(f"List overlap: {overlap}/{total} items match")

        return overlap / total if total > 0 else 0.0

    def _compare_strings(
        self,
        s1: str,
        s2: str,
        differences: List[str]
    ) -> float:
        """Compare two strings and return similarity score."""
        if s1.lower().strip() == s2.lower().strip():
            return 1.0

        # Simple word overlap
        words1 = set(s1.lower().split())
        words2 = set(s2.lower().split())
        overlap = len(words1 & words2)
        total = len(words1 | words2)

        if total > 0:
            similarity = overlap / total
            if similarity < 1.0:
                differences.append(f"String word overlap: {overlap}/{total}")
            return similarity

        return 0.0

    def _compare_numbers(
        self,
        n1: float,
        n2: float,
        differences: List[str]
    ) -> float:
        """Compare two numbers and return similarity score."""
        if n1 == n2:
            return 1.0

        # Calculate relative difference
        max_val = max(abs(n1), abs(n2), 1)
        diff = abs(n1 - n2) / max_val

        if diff > 0.1:
            differences.append(f"Number difference: {n1} vs {n2} (diff: {diff:.2%})")

        return max(0, 1 - diff)

    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        if not self.comparisons:
            return {"component": self.component_name, "validations": 0}

        matches = sum(1 for c in self.comparisons if c.match)
        avg_similarity = sum(c.similarity_score for c in self.comparisons) / len(self.comparisons)
        avg_ai_latency = sum(c.ai_latency_ms for c in self.comparisons) / len(self.comparisons)
        avg_legacy_latency = sum(c.legacy_latency_ms for c in self.comparisons) / len(self.comparisons)

        return {
            "component": self.component_name,
            "validations": len(self.comparisons),
            "match_rate": matches / len(self.comparisons),
            "avg_similarity": avg_similarity,
            "avg_ai_latency_ms": avg_ai_latency,
            "avg_legacy_latency_ms": avg_legacy_latency,
            "ai_faster": avg_ai_latency < avg_legacy_latency,
            "latency_diff_ms": avg_legacy_latency - avg_ai_latency
        }

    def get_recent_differences(self, n: int = 10) -> List[Dict]:
        """Get recent comparison differences."""
        recent = self.comparisons[-n:]
        return [
            {
                "timestamp": c.timestamp.isoformat(),
                "match": c.match,
                "similarity": c.similarity_score,
                "differences": c.differences[:5]  # Limit
            }
            for c in recent
            if not c.match
        ]

    def clear_history(self):
        """Clear comparison history."""
        self.comparisons = []


class MigrationRegistry:
    """Registry for all migration validators."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._validators = {}
        return cls._instance

    def get_validator(self, component_name: str) -> MigrationValidator:
        """Get or create validator for component."""
        if component_name not in self._validators:
            self._validators[component_name] = MigrationValidator(component_name)
        return self._validators[component_name]

    def get_all_stats(self) -> Dict[str, Any]:
        """Get stats for all validators."""
        return {
            name: validator.get_stats()
            for name, validator in self._validators.items()
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get summary across all validators."""
        all_stats = self.get_all_stats()

        if not all_stats:
            return {"total_validations": 0}

        total_validations = sum(s["validations"] for s in all_stats.values())
        avg_match_rate = (
            sum(s["match_rate"] * s["validations"] for s in all_stats.values() if s["validations"] > 0)
            / total_validations
            if total_validations > 0 else 0
        )

        return {
            "total_validations": total_validations,
            "avg_match_rate": avg_match_rate,
            "components": list(all_stats.keys()),
            "component_stats": all_stats
        }

    def clear_all_history(self):
        """Clear history for all validators."""
        for validator in self._validators.values():
            validator.clear_history()


def get_migration_registry() -> MigrationRegistry:
    """Get migration registry singleton."""
    return MigrationRegistry()


def reset_migration_registry():
    """Reset migration registry (for testing)."""
    MigrationRegistry._instance = None
