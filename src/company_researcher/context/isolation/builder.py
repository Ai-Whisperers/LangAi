"""
Agent Context Builder.

Builds optimized context for specific agent invocations by combining:
- Relevant stored research
- Scratchpad notes
- Retrieved context
- Global configuration
"""

from typing import Any, Dict, Optional

from .manager import ContextIsolationManager
from .models import IsolationLevel, SharePolicy


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
        scratchpad=None,
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
        max_tokens: int = 4000,
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
            memory_ctx = self._get_memory_context(company_name, agent_type, max_tokens // 3)
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
            context = context[: max_chars - 100] + "\n\n[Context truncated]"

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

    def _get_memory_context(self, company_name: str, agent_type: str, max_chars: int) -> str:
        """Get relevant context from memory."""
        if not self._memory:
            return ""

        try:
            items = self._memory.recall_company(
                company_name=company_name, data_type=agent_type, k=5
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
    isolation_level: str = "moderate", share_policy: str = "filtered"
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
        default_isolation=IsolationLevel(isolation_level), default_policy=SharePolicy(share_policy)
    )


def build_agent_context(
    agent_type: str, company_name: str, task: str, memory=None, scratchpad=None
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
        task_description=task,
    )
