"""
ISOLATE Strategy (Phase 12.4).

Multi-agent context separation and management:
- Agent-specific context boundaries
- Information flow control
- Context inheritance management
- Cross-agent communication protocols

The ISOLATE strategy ensures agents have appropriate context
without leaking irrelevant information between agents.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import copy


# ============================================================================
# Enums and Data Models
# ============================================================================

class IsolationLevel(str, Enum):
    """Levels of context isolation between agents."""
    NONE = "none"            # Full context sharing
    MINIMAL = "minimal"      # Share most, isolate sensitive
    MODERATE = "moderate"    # Share relevant, isolate unrelated
    STRICT = "strict"        # Share only explicitly allowed
    COMPLETE = "complete"    # No sharing between agents


class SharePolicy(str, Enum):
    """Policies for sharing information between agents."""
    INHERIT = "inherit"      # Child inherits parent context
    EXPLICIT = "explicit"    # Only share explicitly shared items
    FILTERED = "filtered"    # Share through filter
    NONE = "none"           # No sharing


class ContextVisibility(str, Enum):
    """Visibility levels for context items."""
    GLOBAL = "global"        # Visible to all agents
    TEAM = "team"           # Visible to related agents
    PRIVATE = "private"      # Only visible to owner
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
    created_at: datetime = field(default_factory=datetime.now)
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
        return datetime.now() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "visibility": self.visibility.value,
            "owner": self.owner_agent,
            "tags": self.tags
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
        tags: Optional[List[str]] = None
    ) -> None:
        """Add item to context."""
        self.items[key] = ContextItem(
            key=key,
            value=value,
            visibility=visibility,
            owner_agent=self.agent_name,
            tags=tags or []
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
        return {
            key: item.value
            for key, item in self.items.items()
            if not item.is_expired()
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "isolation_level": self.isolation_level.value,
            "item_count": len(self.items),
            "parent": self.parent_agent,
            "children": self.child_agents
        }


# ============================================================================
# Context Filter
# ============================================================================

class ContextFilter:
    """
    Filter context items based on various criteria.

    Supports filtering by:
    - Visibility
    - Tags
    - Agent type
    - Content type
    - Custom rules
    """

    def __init__(self):
        self._type_filters: Dict[str, List[str]] = {
            # Agent type -> relevant tags
            "financial": ["financial", "revenue", "profit", "earnings", "cash"],
            "market": ["market", "tam", "sam", "som", "industry", "growth"],
            "competitive": ["competitor", "competition", "rival", "market_share"],
            "product": ["product", "feature", "technology", "innovation"],
            "synthesizer": ["summary", "finding", "key_point", "conclusion"]
        }

    def filter_for_agent(
        self,
        items: Dict[str, ContextItem],
        target_agent: str,
        target_type: str
    ) -> Dict[str, Any]:
        """
        Filter context items for a specific agent.

        Args:
            items: All context items
            target_agent: Target agent name
            target_type: Target agent type

        Returns:
            Filtered context dictionary
        """
        filtered = {}

        # Get relevant tags for agent type
        relevant_tags = self._type_filters.get(target_type, [])

        for key, item in items.items():
            # Skip expired items
            if item.is_expired():
                continue

            # Check visibility
            if not item.is_visible_to(target_agent):
                continue

            # Check tag relevance (if strict filtering)
            if relevant_tags and item.tags:
                if not any(tag in relevant_tags for tag in item.tags):
                    continue

            filtered[key] = item.value

        return filtered

    def filter_by_tags(
        self,
        items: Dict[str, ContextItem],
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Filter by tags."""
        filtered = {}

        for key, item in items.items():
            if item.is_expired():
                continue

            # Include filter
            if include_tags:
                if not any(tag in item.tags for tag in include_tags):
                    continue

            # Exclude filter
            if exclude_tags:
                if any(tag in item.tags for tag in exclude_tags):
                    continue

            filtered[key] = item.value

        return filtered

    def filter_by_visibility(
        self,
        items: Dict[str, ContextItem],
        visibility: ContextVisibility,
        agent_name: str
    ) -> Dict[str, Any]:
        """Filter by visibility level."""
        filtered = {}

        for key, item in items.items():
            if item.is_expired():
                continue

            if item.visibility == visibility or item.is_visible_to(agent_name):
                filtered[key] = item.value

        return filtered


# ============================================================================
# Context Isolation Manager
# ============================================================================

class ContextIsolationManager:
    """
    Manage context isolation between multiple agents.

    Provides:
    - Agent context creation and management
    - Information flow control
    - Context inheritance
    - Cross-agent communication

    Usage:
        manager = ContextIsolationManager()

        # Create agent contexts
        financial_ctx = manager.create_context("financial_agent", "financial")
        market_ctx = manager.create_context("market_agent", "market")

        # Add items
        financial_ctx.add("revenue_data", {...}, visibility=ContextVisibility.TEAM)

        # Get context for another agent
        ctx = manager.get_context_for_agent("market_agent", include_shared=True)
    """

    def __init__(
        self,
        default_isolation: IsolationLevel = IsolationLevel.MODERATE,
        default_policy: SharePolicy = SharePolicy.FILTERED
    ):
        """
        Initialize manager.

        Args:
            default_isolation: Default isolation level
            default_policy: Default sharing policy
        """
        self._contexts: Dict[str, AgentContext] = {}
        self._global_context: Dict[str, ContextItem] = {}
        self._default_isolation = default_isolation
        self._default_policy = default_policy
        self._filter = ContextFilter()

        # Agent relationships
        self._agent_teams: Dict[str, Set[str]] = {}

    # ==========================================================================
    # Context Management
    # ==========================================================================

    def create_context(
        self,
        agent_name: str,
        agent_type: str,
        parent_agent: Optional[str] = None,
        isolation_level: Optional[IsolationLevel] = None,
        share_policy: Optional[SharePolicy] = None
    ) -> AgentContext:
        """
        Create context for an agent.

        Args:
            agent_name: Unique agent identifier
            agent_type: Type of agent (financial, market, etc.)
            parent_agent: Parent agent name (for inheritance)
            isolation_level: Isolation level override
            share_policy: Share policy override

        Returns:
            Created AgentContext
        """
        context = AgentContext(
            agent_name=agent_name,
            agent_type=agent_type,
            parent_agent=parent_agent,
            isolation_level=isolation_level or self._default_isolation,
            share_policy=share_policy or self._default_policy
        )

        self._contexts[agent_name] = context

        # Set up parent relationship
        if parent_agent and parent_agent in self._contexts:
            self._contexts[parent_agent].child_agents.append(agent_name)

        # Add to team based on type
        if agent_type not in self._agent_teams:
            self._agent_teams[agent_type] = set()
        self._agent_teams[agent_type].add(agent_name)

        return context

    def get_context(self, agent_name: str) -> Optional[AgentContext]:
        """Get agent's own context."""
        return self._contexts.get(agent_name)

    def get_context_for_agent(
        self,
        agent_name: str,
        include_shared: bool = True,
        include_global: bool = True,
        include_inherited: bool = True
    ) -> Dict[str, Any]:
        """
        Get full context available to an agent.

        Args:
            agent_name: Agent name
            include_shared: Include shared items from other agents
            include_global: Include global context
            include_inherited: Include context from parent agents

        Returns:
            Combined context dictionary
        """
        result = {}
        agent_ctx = self._contexts.get(agent_name)

        if not agent_ctx:
            return result

        # 1. Add global context
        if include_global:
            for key, item in self._global_context.items():
                if item.is_visible_to(agent_name) and not item.is_expired():
                    result[key] = item.value

        # 2. Add inherited context
        if include_inherited and agent_ctx.parent_agent:
            inherited = self._get_inherited_context(agent_name)
            result.update(inherited)

        # 3. Add shared context from other agents
        if include_shared:
            shared = self._get_shared_context(agent_name, agent_ctx.agent_type)
            result.update(shared)

        # 4. Add own context (highest priority)
        result.update(agent_ctx.get_visible_items())

        return result

    def _get_inherited_context(self, agent_name: str) -> Dict[str, Any]:
        """Get context inherited from parent agents."""
        result = {}
        agent_ctx = self._contexts.get(agent_name)

        if not agent_ctx or not agent_ctx.parent_agent:
            return result

        parent_ctx = self._contexts.get(agent_ctx.parent_agent)
        if not parent_ctx:
            return result

        # Filter parent's items based on visibility
        for key, item in parent_ctx.items.items():
            if item.is_visible_to(agent_name) and not item.is_expired():
                result[key] = item.value

        # Recursively get grandparent context
        if parent_ctx.parent_agent:
            grandparent = self._get_inherited_context(parent_ctx.agent_name)
            # Don't override with grandparent (parent takes precedence)
            for k, v in grandparent.items():
                if k not in result:
                    result[k] = v

        return result

    def _get_shared_context(
        self,
        agent_name: str,
        agent_type: str
    ) -> Dict[str, Any]:
        """Get context shared by other agents."""
        result = {}
        agent_ctx = self._contexts.get(agent_name)

        if not agent_ctx:
            return result

        for other_name, other_ctx in self._contexts.items():
            if other_name == agent_name:
                continue

            # Apply filtering based on isolation level
            if agent_ctx.isolation_level == IsolationLevel.COMPLETE:
                continue

            if agent_ctx.isolation_level == IsolationLevel.STRICT:
                # Only items explicitly shared with this agent
                for key, item in other_ctx.items.items():
                    if agent_name in item.allowed_agents:
                        result[key] = item.value
            else:
                # Use filter for MODERATE/MINIMAL
                filtered = self._filter.filter_for_agent(
                    other_ctx.items,
                    agent_name,
                    agent_type
                )
                result.update(filtered)

        return result

    # ==========================================================================
    # Global Context
    # ==========================================================================

    def add_global(
        self,
        key: str,
        value: Any,
        tags: Optional[List[str]] = None
    ) -> None:
        """Add item to global context (visible to all)."""
        self._global_context[key] = ContextItem(
            key=key,
            value=value,
            visibility=ContextVisibility.GLOBAL,
            owner_agent="global",
            tags=tags or []
        )

    def get_global(self, key: str, default: Any = None) -> Any:
        """Get item from global context."""
        item = self._global_context.get(key)
        if item and not item.is_expired():
            return item.value
        return default

    def remove_global(self, key: str) -> bool:
        """Remove item from global context."""
        if key in self._global_context:
            del self._global_context[key]
            return True
        return False

    # ==========================================================================
    # Cross-Agent Communication
    # ==========================================================================

    def share_item(
        self,
        from_agent: str,
        to_agents: List[str],
        key: str
    ) -> bool:
        """
        Share a specific item with other agents.

        Args:
            from_agent: Source agent
            to_agents: Target agents
            key: Item key to share

        Returns:
            True if shared successfully
        """
        from_ctx = self._contexts.get(from_agent)
        if not from_ctx or key not in from_ctx.items:
            return False

        item = from_ctx.items[key]
        item.allowed_agents.update(to_agents)

        return True

    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message: str,
        message_type: str = "info"
    ) -> str:
        """
        Send a message from one agent to another.

        Args:
            from_agent: Sender agent
            to_agent: Receiver agent
            message: Message content
            message_type: Type of message

        Returns:
            Message ID
        """
        to_ctx = self._contexts.get(to_agent)
        if not to_ctx:
            return ""

        msg_id = f"msg_{from_agent}_{datetime.now().timestamp()}"

        to_ctx.add(
            key=msg_id,
            value={
                "from": from_agent,
                "message": message,
                "type": message_type,
                "timestamp": datetime.now().isoformat()
            },
            visibility=ContextVisibility.PRIVATE,
            tags=["message", message_type]
        )

        return msg_id

    def broadcast(
        self,
        from_agent: str,
        message: str,
        to_team: Optional[str] = None,
        message_type: str = "broadcast"
    ) -> int:
        """
        Broadcast message to multiple agents.

        Args:
            from_agent: Sender agent
            message: Message content
            to_team: Target team (None = all)
            message_type: Type of message

        Returns:
            Number of agents reached
        """
        count = 0

        # Determine target agents
        if to_team and to_team in self._agent_teams:
            targets = self._agent_teams[to_team]
        else:
            targets = set(self._contexts.keys())

        for target in targets:
            if target != from_agent:
                self.send_message(from_agent, target, message, message_type)
                count += 1

        return count

    # ==========================================================================
    # Context Templates
    # ==========================================================================

    def apply_template(
        self,
        agent_name: str,
        template_name: str
    ) -> bool:
        """
        Apply a context template to an agent.

        Args:
            agent_name: Target agent
            template_name: Template to apply

        Returns:
            True if applied successfully
        """
        templates = {
            "research_agent": {
                "allowed_tags": ["overview", "general", "company_info"],
                "isolation": IsolationLevel.MODERATE,
                "share_policy": SharePolicy.FILTERED
            },
            "analysis_agent": {
                "allowed_tags": ["finding", "analysis", "summary"],
                "isolation": IsolationLevel.MINIMAL,
                "share_policy": SharePolicy.INHERIT
            },
            "verification_agent": {
                "allowed_tags": ["all"],  # Access everything for verification
                "isolation": IsolationLevel.NONE,
                "share_policy": SharePolicy.INHERIT
            }
        }

        template = templates.get(template_name)
        if not template:
            return False

        ctx = self._contexts.get(agent_name)
        if not ctx:
            return False

        ctx.isolation_level = template.get("isolation", ctx.isolation_level)
        ctx.share_policy = template.get("share_policy", ctx.share_policy)

        return True

    # ==========================================================================
    # Utility Methods
    # ==========================================================================

    def clear_agent_context(self, agent_name: str) -> int:
        """Clear all items from an agent's context."""
        ctx = self._contexts.get(agent_name)
        if not ctx:
            return 0

        count = len(ctx.items)
        ctx.items.clear()
        return count

    def clear_all(self) -> int:
        """Clear all contexts."""
        count = sum(len(ctx.items) for ctx in self._contexts.values())
        count += len(self._global_context)

        self._contexts.clear()
        self._global_context.clear()
        self._agent_teams.clear()

        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics."""
        return {
            "agent_count": len(self._contexts),
            "global_items": len(self._global_context),
            "teams": {k: len(v) for k, v in self._agent_teams.items()},
            "agents": {
                name: ctx.to_dict()
                for name, ctx in self._contexts.items()
            }
        }


# ============================================================================
# Agent Context Builder
# ============================================================================

class AgentContextBuilder:
    """
    Build optimized context for specific agent invocations.

    Combines:
    - Relevant stored research
    - Scratchpad notes
    - Retrieved context
    - Global configuration
    """

    def __init__(
        self,
        isolation_manager: Optional[ContextIsolationManager] = None,
        memory=None,
        scratchpad=None
    ):
        """
        Initialize builder.

        Args:
            isolation_manager: Context isolation manager
            memory: DualLayerMemory instance
            scratchpad: Scratchpad instance
        """
        self._manager = isolation_manager or ContextIsolationManager()
        self._memory = memory
        self._scratchpad = scratchpad

    def build_for_agent(
        self,
        agent_name: str,
        agent_type: str,
        company_name: str,
        task_description: str,
        max_tokens: int = 4000
    ) -> str:
        """
        Build context string for agent invocation.

        Args:
            agent_name: Agent name
            agent_type: Agent type
            company_name: Company being researched
            task_description: Description of the task
            max_tokens: Maximum context tokens

        Returns:
            Formatted context string
        """
        sections = []

        # 1. Task context
        sections.append(f"## Task\n{task_description}\n")

        # 2. Company context
        sections.append(f"## Company: {company_name}\n")

        # 3. Relevant stored context from manager
        if self._manager:
            agent_ctx = self._manager.get_context_for_agent(agent_name)
            if agent_ctx:
                ctx_str = self._format_context_items(agent_ctx)
                if ctx_str:
                    sections.append(f"## Relevant Context\n{ctx_str}\n")

        # 4. Memory-based context
        if self._memory:
            memory_ctx = self._get_memory_context(
                company_name, agent_type, max_tokens // 3
            )
            if memory_ctx:
                sections.append(f"## Research Memory\n{memory_ctx}\n")

        # 5. Scratchpad notes
        if self._scratchpad:
            notes = self._get_scratchpad_notes(agent_type)
            if notes:
                sections.append(f"## Notes from Other Agents\n{notes}\n")

        # Combine and truncate if needed
        context = "\n".join(sections)

        max_chars = max_tokens * 4  # Approximate
        if len(context) > max_chars:
            context = context[:max_chars - 100] + "\n\n[Context truncated]"

        return context

    def _format_context_items(self, items: Dict[str, Any]) -> str:
        """Format context items for inclusion."""
        if not items:
            return ""

        lines = []
        for key, value in list(items.items())[:10]:  # Limit items
            if isinstance(value, dict):
                lines.append(f"**{key}**: {str(value)[:200]}")
            else:
                lines.append(f"**{key}**: {str(value)[:200]}")

        return "\n".join(lines)

    def _get_memory_context(
        self,
        company_name: str,
        agent_type: str,
        max_chars: int
    ) -> str:
        """Get relevant context from memory."""
        if not self._memory:
            return ""

        try:
            items = self._memory.recall_company(
                company_name=company_name,
                data_type=agent_type,
                k=5
            )

            lines = []
            current_chars = 0

            for item in items:
                preview = item.content[:500]
                if current_chars + len(preview) > max_chars:
                    break
                lines.append(f"- {preview}")
                current_chars += len(preview)

            return "\n".join(lines)
        except Exception:
            return ""

    def _get_scratchpad_notes(self, agent_type: str) -> str:
        """Get relevant scratchpad notes."""
        if not self._scratchpad:
            return ""

        try:
            # Get findings and insights
            findings = self._scratchpad.read_findings(limit=5)
            notes = []

            for note in findings:
                notes.append(f"- [{note.agent_source}] {note.content[:200]}")

            return "\n".join(notes)
        except Exception:
            return ""


# ============================================================================
# Factory Functions
# ============================================================================

def create_isolation_manager(
    isolation_level: str = "moderate",
    share_policy: str = "filtered"
) -> ContextIsolationManager:
    """
    Create a context isolation manager.

    Args:
        isolation_level: "none", "minimal", "moderate", "strict", "complete"
        share_policy: "inherit", "explicit", "filtered", "none"

    Returns:
        ContextIsolationManager instance
    """
    return ContextIsolationManager(
        default_isolation=IsolationLevel(isolation_level),
        default_policy=SharePolicy(share_policy)
    )


def build_agent_context(
    agent_type: str,
    company_name: str,
    task: str,
    memory=None,
    scratchpad=None
) -> str:
    """
    Quick function to build context for an agent.

    Args:
        agent_type: Type of agent
        company_name: Company name
        task: Task description
        memory: Optional memory instance
        scratchpad: Optional scratchpad instance

    Returns:
        Context string
    """
    builder = AgentContextBuilder(memory=memory, scratchpad=scratchpad)
    return builder.build_for_agent(
        agent_name=f"{agent_type}_agent",
        agent_type=agent_type,
        company_name=company_name,
        task_description=task
    )
