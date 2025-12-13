"""
Context Isolation Manager.

Main manager class for context isolation between multiple agents.
Provides:
- Agent context creation and management
- Information flow control
- Context inheritance
- Cross-agent communication
"""

from typing import Dict, Any, List, Optional, Set

from .models import (
    IsolationLevel,
    SharePolicy,
    ContextVisibility,
    ContextItem,
    AgentContext,
)
from .filter import ContextFilter
from ...utils import utc_now


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

        msg_id = f"msg_{from_agent}_{utc_now().timestamp()}"

        to_ctx.add(
            key=msg_id,
            value={
                "from": from_agent,
                "message": message,
                "type": message_type,
                "timestamp": utc_now().isoformat()
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

    def list_agents(self) -> List[str]:
        """List all registered agents."""
        return list(self._contexts.keys())

    def list_teams(self) -> Dict[str, List[str]]:
        """List all teams with their agents."""
        return {
            team: list(agents)
            for team, agents in self._agent_teams.items()
        }
