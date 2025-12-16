"""
Isolation Context Models.

Data models and enums for context isolation:
- IsolationLevel enum
- SharePolicy enum
- ContextVisibility enum
- ContextItem dataclass
- AgentContext dataclass
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from ...utils import utc_now


class IsolationLevel(str, Enum):
    """Levels of context isolation between agents."""

    NONE = "none"  # Full context sharing
    MINIMAL = "minimal"  # Share most, isolate sensitive
    MODERATE = "moderate"  # Share relevant, isolate unrelated
    STRICT = "strict"  # Share only explicitly allowed
    COMPLETE = "complete"  # No sharing between agents


class SharePolicy(str, Enum):
    """Policies for sharing information between agents."""

    INHERIT = "inherit"  # Child inherits parent context
    EXPLICIT = "explicit"  # Only share explicitly shared items
    FILTERED = "filtered"  # Share through filter
    NONE = "none"  # No sharing


class ContextVisibility(str, Enum):
    """Visibility levels for context items."""

    GLOBAL = "global"  # Visible to all agents
    TEAM = "team"  # Visible to related agents
    PRIVATE = "private"  # Only visible to owner
    RESTRICTED = "restricted"  # Visible with permission


@dataclass
class ContextItem:
    """A single item in agent context."""

    key: str
    value: Any
    visibility: ContextVisibility = ContextVisibility.TEAM
    owner_agent: str = ""
    allowed_agents: Set[str] = field(default_factory=set)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)
    expires_at: Optional[datetime] = None

    def is_visible_to(self, agent_name: str) -> bool:
        """Check if item is visible to an agent."""
        if self.visibility == ContextVisibility.GLOBAL:
            return True
        if self.visibility == ContextVisibility.PRIVATE:
            return agent_name == self.owner_agent
        if self.visibility == ContextVisibility.RESTRICTED:
            return agent_name in self.allowed_agents or agent_name == self.owner_agent
        # TEAM visibility - check if in same team
        return True  # Default to visible for TEAM

    def is_expired(self) -> bool:
        """Check if item has expired."""
        if self.expires_at is None:
            return False
        return utc_now() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "key": self.key,
            "value": self.value,
            "visibility": self.visibility.value,
            "owner": self.owner_agent,
            "tags": self.tags,
        }


@dataclass
class AgentContext:
    """Context container for a single agent."""

    agent_name: str
    agent_type: str
    items: Dict[str, ContextItem] = field(default_factory=dict)
    parent_agent: Optional[str] = None
    child_agents: List[str] = field(default_factory=list)
    isolation_level: IsolationLevel = IsolationLevel.MODERATE
    share_policy: SharePolicy = SharePolicy.FILTERED

    def add(
        self,
        key: str,
        value: Any,
        visibility: ContextVisibility = ContextVisibility.TEAM,
        tags: Optional[List[str]] = None,
    ) -> None:
        """Add item to context."""
        self.items[key] = ContextItem(
            key=key,
            value=value,
            visibility=visibility,
            owner_agent=self.agent_name,
            tags=tags or [],
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Get item from context."""
        item = self.items.get(key)
        if item and not item.is_expired():
            return item.value
        return default

    def remove(self, key: str) -> bool:
        """Remove item from context."""
        if key in self.items:
            del self.items[key]
            return True
        return False

    def get_visible_items(self) -> Dict[str, Any]:
        """Get all non-expired items as dict."""
        return {key: item.value for key, item in self.items.items() if not item.is_expired()}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "isolation_level": self.isolation_level.value,
            "item_count": len(self.items),
            "parent": self.parent_agent,
            "children": self.child_agents,
        }
