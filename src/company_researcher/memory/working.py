"""
Working Memory - Short-term context management.

Provides:
- Scratchpad for intermediate results
- Variable storage
- Context windows
- Temporal decay
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, TypeVar

T = TypeVar('T')


@dataclass
class WorkingMemoryItem:
    """An item in working memory."""
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    ttl: Optional[float] = None  # Seconds until expiry
    importance: float = 1.0  # Higher = more important
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if item has expired."""
        if self.ttl is None:
            return False
        return time.time() > self.created_at + self.ttl

    def access(self) -> Any:
        """Access the item, updating stats."""
        self.accessed_at = time.time()
        self.access_count += 1
        return self.value

    def age_seconds(self) -> float:
        """Get item age in seconds."""
        return time.time() - self.created_at

    def decay_factor(self, half_life: float = 300) -> float:
        """Calculate decay factor based on age."""
        age = self.age_seconds()
        return 2 ** (-age / half_life)


class WorkingMemory:
    """
    Short-term working memory with decay and importance.

    Usage:
        memory = WorkingMemory(max_items=20)

        # Store values
        memory.set("current_company", "Tesla")
        memory.set("query", "revenue Q3 2024", ttl=300)

        # Retrieve values
        company = memory.get("current_company")

        # Get with default
        value = memory.get("missing", default="unknown")

        # Check existence
        if memory.has("current_company"):
            ...

        # Get all context
        context = memory.get_context()

        # Clear specific or all
        memory.delete("old_key")
        memory.clear()
    """

    def __init__(
        self,
        max_items: int = 50,
        default_ttl: float = None,  # Seconds, None = no expiry
        decay_half_life: float = 300,  # Seconds for importance decay
        auto_cleanup: bool = True
    ):
        self.max_items = max_items
        self.default_ttl = default_ttl
        self.decay_half_life = decay_half_life
        self.auto_cleanup = auto_cleanup
        self._items: Dict[str, WorkingMemoryItem] = {}

    def set(
        self,
        key: str,
        value: Any,
        ttl: float = None,
        importance: float = 1.0,
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Store a value in working memory.

        Args:
            key: Item key
            value: Value to store
            ttl: Time-to-live in seconds
            importance: Item importance (affects eviction)
            metadata: Additional metadata
        """
        item = WorkingMemoryItem(
            key=key,
            value=value,
            ttl=ttl or self.default_ttl,
            importance=importance,
            metadata=metadata or {}
        )
        self._items[key] = item

        if self.auto_cleanup:
            self._cleanup()

    def get(self, key: str, default: T = None) -> T:
        """
        Retrieve a value from working memory.

        Args:
            key: Item key
            default: Default if not found

        Returns:
            Stored value or default
        """
        item = self._items.get(key)
        if item is None:
            return default

        if item.is_expired():
            del self._items[key]
            return default

        return item.access()

    def has(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        item = self._items.get(key)
        if item is None:
            return False
        if item.is_expired():
            del self._items[key]
            return False
        return True

    def delete(self, key: str) -> bool:
        """Delete an item."""
        if key in self._items:
            del self._items[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all items."""
        self._items.clear()

    def _cleanup(self) -> None:
        """Remove expired items and enforce max_items."""
        # Remove expired
        expired_keys = [k for k, v in self._items.items() if v.is_expired()]
        for key in expired_keys:
            del self._items[key]

        # Enforce max_items by removing least important
        while len(self._items) > self.max_items:
            least_important = min(
                self._items.values(),
                key=lambda x: x.importance * x.decay_factor(self.decay_half_life)
            )
            del self._items[least_important.key]

    def get_context(
        self,
        include_metadata: bool = False,
        min_importance: float = 0
    ) -> Dict[str, Any]:
        """
        Get current context as dictionary.

        Args:
            include_metadata: Include item metadata
            min_importance: Minimum importance to include

        Returns:
            Dictionary of key-value pairs
        """
        self._cleanup()
        context = {}

        for key, item in self._items.items():
            effective_importance = item.importance * item.decay_factor(self.decay_half_life)
            if effective_importance < min_importance:
                continue

            if include_metadata:
                context[key] = {
                    "value": item.value,
                    "importance": effective_importance,
                    "age_seconds": item.age_seconds(),
                    "access_count": item.access_count,
                    "metadata": item.metadata
                }
            else:
                context[key] = item.value

        return context

    def get_context_string(self) -> str:
        """Get context as formatted string."""
        lines = []
        for key, value in self.get_context().items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)

    def keys(self) -> List[str]:
        """Get all non-expired keys."""
        self._cleanup()
        return list(self._items.keys())

    def values(self) -> List[Any]:
        """Get all non-expired values."""
        self._cleanup()
        return [item.value for item in self._items.values()]

    def items(self) -> List[tuple]:
        """Get all non-expired key-value pairs."""
        self._cleanup()
        return [(k, v.value) for k, v in self._items.items()]

    def boost_importance(self, key: str, factor: float = 1.5) -> None:
        """Boost importance of an item."""
        if key in self._items:
            self._items[key].importance *= factor

    def update_many(self, items: Dict[str, Any], ttl: float = None) -> None:
        """Update multiple items at once."""
        for key, value in items.items():
            self.set(key, value, ttl=ttl)

    @property
    def size(self) -> int:
        """Get number of items."""
        self._cleanup()
        return len(self._items)


class ScratchpadMemory:
    """
    Scratchpad for intermediate computation results.

    Provides named slots for storing intermediate values during
    multi-step reasoning or computation.

    Usage:
        scratchpad = ScratchpadMemory()

        # Store intermediate results
        scratchpad.write("step1_result", calculation_result)
        scratchpad.write("extracted_entities", entities)

        # Read results
        step1 = scratchpad.read("step1_result")

        # Append to list slot
        scratchpad.append("findings", new_finding)

        # Get all as string for LLM context
        context = scratchpad.to_string()
    """

    def __init__(self, max_slots: int = 20):
        self.max_slots = max_slots
        self._slots: Dict[str, Any] = {}
        self._history: List[Dict[str, Any]] = []

    def write(self, slot: str, value: Any, append: bool = False) -> None:
        """
        Write to a slot.

        Args:
            slot: Slot name
            value: Value to write
            append: If True and slot is list, append instead of replace
        """
        if append and slot in self._slots and isinstance(self._slots[slot], list):
            self._slots[slot].append(value)
        else:
            self._slots[slot] = value

        self._history.append({
            "action": "write",
            "slot": slot,
            "value_type": type(value).__name__,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Enforce max slots
        while len(self._slots) > self.max_slots:
            oldest_slot = next(iter(self._slots))
            del self._slots[oldest_slot]

    def read(self, slot: str, default: Any = None) -> Any:
        """Read from a slot."""
        return self._slots.get(slot, default)

    def append(self, slot: str, value: Any) -> None:
        """Append to a list slot (creates list if doesn't exist)."""
        if slot not in self._slots:
            self._slots[slot] = []
        if not isinstance(self._slots[slot], list):
            self._slots[slot] = [self._slots[slot]]
        self._slots[slot].append(value)

    def clear_slot(self, slot: str) -> None:
        """Clear a specific slot."""
        if slot in self._slots:
            del self._slots[slot]

    def clear_all(self) -> None:
        """Clear all slots."""
        self._slots.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Get all slots as dictionary."""
        return self._slots.copy()

    def to_string(self, format: str = "text") -> str:
        """
        Convert scratchpad to string.

        Args:
            format: Output format (text, markdown, json)

        Returns:
            Formatted string
        """
        if format == "json":
            import json
            return json.dumps(self._slots, indent=2, default=str)

        if format == "markdown":
            lines = ["## Scratchpad\n"]
            for slot, value in self._slots.items():
                lines.append(f"### {slot}")
                lines.append(f"```\n{value}\n```\n")
            return "\n".join(lines)

        # Default text format
        lines = ["=== Scratchpad ==="]
        for slot, value in self._slots.items():
            lines.append(f"[{slot}]: {value}")
        return "\n".join(lines)

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent scratchpad history."""
        return self._history[-limit:]

    @property
    def slots(self) -> List[str]:
        """Get list of slot names."""
        return list(self._slots.keys())


# Convenience functions


def create_working_memory(
    max_items: int = 50,
    default_ttl: float = None
) -> WorkingMemory:
    """Create a working memory."""
    return WorkingMemory(max_items=max_items, default_ttl=default_ttl)


def create_scratchpad() -> ScratchpadMemory:
    """Create a scratchpad memory."""
    return ScratchpadMemory()
