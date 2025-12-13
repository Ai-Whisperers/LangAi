"""Common utilities for AI components."""
from typing import Any, Dict, List, Optional, TypeVar, Type
from pydantic import BaseModel
import re
from ..utils import get_logger

logger = get_logger(__name__)

T = TypeVar('T', bound=BaseModel)


def safe_parse_model(
    data: Dict[str, Any],
    model_class: Type[T],
    default_factory: Optional[callable] = None
) -> T:
    """
    Safely parse data into a Pydantic model.

    Args:
        data: Dictionary data to parse
        model_class: Pydantic model class
        default_factory: Factory function to create default if parsing fails

    Returns:
        Parsed model instance or default
    """
    try:
        return model_class(**data)
    except Exception as e:
        logger.warning(f"Failed to parse {model_class.__name__}: {e}")
        if default_factory:
            return default_factory()
        raise


def truncate_text(text: str, max_length: int = 8000, suffix: str = "...") -> str:
    """
    Truncate text to maximum length for LLM context.

    Tries to truncate at sentence boundaries when possible.
    """
    if len(text) <= max_length:
        return text

    # Try to truncate at a sentence boundary
    truncated = text[:max_length]
    last_period = truncated.rfind('.')
    last_newline = truncated.rfind('\n')

    cut_point = max(last_period, last_newline)
    if cut_point > max_length * 0.8:  # Only use if we keep >80%
        return truncated[:cut_point + 1] + suffix

    return truncated + suffix


def extract_json_from_text(text: str) -> Optional[str]:
    """
    Extract JSON from text that may contain markdown or other content.

    Handles:
    - ```json ... ``` blocks
    - ``` ... ``` blocks
    - Raw JSON objects/arrays
    """
    # Try markdown code block first
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if json_match:
        return json_match.group(1).strip()

    # Try to find JSON object
    obj_match = re.search(r'\{[\s\S]*\}', text)
    if obj_match:
        return obj_match.group(0)

    # Try to find JSON array
    arr_match = re.search(r'\[[\s\S]*\]', text)
    if arr_match:
        return arr_match.group(0)

    return None


def normalize_confidence(value: Any) -> float:
    """
    Normalize a confidence value to 0.0-1.0 range.

    Handles various input formats:
    - Float 0.0-1.0 (returned as-is)
    - Float 0-100 (divided by 100)
    - String "0.85" or "85%" (parsed)
    - String "high", "medium", "low" (mapped)
    """
    if isinstance(value, (int, float)):
        if value > 1.0:
            return min(1.0, value / 100.0)
        return max(0.0, min(1.0, float(value)))

    if isinstance(value, str):
        # Try percentage
        if '%' in value:
            try:
                return float(value.replace('%', '').strip()) / 100.0
            except ValueError:
                pass

        # Try numeric string
        try:
            num = float(value)
            if num > 1.0:
                return min(1.0, num / 100.0)
            return max(0.0, min(1.0, num))
        except ValueError:
            pass

        # Map text values
        text_map = {
            'very_high': 0.95,
            'high': 0.8,
            'medium': 0.6,
            'moderate': 0.6,
            'low': 0.4,
            'very_low': 0.2,
            'none': 0.0
        }
        return text_map.get(value.lower().replace(' ', '_'), 0.5)

    return 0.5  # Default


def merge_results(results: List[Dict[str, Any]], key_field: str = "category") -> Dict[str, Any]:
    """
    Merge multiple result dictionaries, combining by a key field.

    Useful for combining results from multiple LLM calls.
    """
    merged = {}
    for result in results:
        key = result.get(key_field, "unknown")
        if key not in merged:
            merged[key] = result
        else:
            # Merge dictionaries
            for k, v in result.items():
                if k not in merged[key]:
                    merged[key][k] = v
                elif isinstance(v, list) and isinstance(merged[key][k], list):
                    merged[key][k].extend(v)
    return merged


def format_for_prompt(data: Any, max_items: int = 10, max_length: int = 500) -> str:
    """
    Format data for inclusion in a prompt.

    Handles lists, dicts, and other types with truncation.
    """
    if isinstance(data, list):
        items = data[:max_items]
        formatted = "\n".join(f"- {truncate_text(str(item), max_length)}" for item in items)
        if len(data) > max_items:
            formatted += f"\n... and {len(data) - max_items} more items"
        return formatted

    if isinstance(data, dict):
        items = list(data.items())[:max_items]
        formatted = "\n".join(f"- {k}: {truncate_text(str(v), max_length)}" for k, v in items)
        if len(data) > max_items:
            formatted += f"\n... and {len(data) - max_items} more items"
        return formatted

    return truncate_text(str(data), max_length * 2)


class CostTracker:
    """Track costs across AI operations."""

    def __init__(self, warn_threshold: float = 0.50, max_threshold: float = 1.00):
        self.warn_threshold = warn_threshold
        self.max_threshold = max_threshold
        self._total_cost = 0.0
        self._calls = []
        self._warned = False

    def add_cost(self, cost: float, component: str, operation: str = ""):
        """Add a cost entry."""
        self._total_cost += cost
        self._calls.append({
            "cost": cost,
            "component": component,
            "operation": operation,
            "cumulative": self._total_cost
        })

        # Check thresholds
        if self._total_cost >= self.max_threshold:
            from .exceptions import AICostLimitExceeded
            raise AICostLimitExceeded(
                component=component,
                current_cost=self._total_cost,
                limit=self.max_threshold
            )

        if not self._warned and self._total_cost >= self.warn_threshold:
            logger.warning(f"AI cost warning: ${self._total_cost:.4f} exceeds ${self.warn_threshold:.2f}")
            self._warned = True

    @property
    def total_cost(self) -> float:
        return self._total_cost

    def get_breakdown(self) -> Dict[str, float]:
        """Get cost breakdown by component."""
        breakdown = {}
        for call in self._calls:
            comp = call["component"]
            breakdown[comp] = breakdown.get(comp, 0) + call["cost"]
        return breakdown

    def reset(self):
        """Reset cost tracking."""
        self._total_cost = 0.0
        self._calls = []
        self._warned = False
