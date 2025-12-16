"""
Context Filter Module.

Provides filtering capabilities for context items based on:
- Visibility levels
- Tags
- Agent types
- Custom rules
"""

from typing import Any, Dict, List, Optional

from ...utils import utc_now
from .models import ContextItem, ContextVisibility


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
        """Initialize filter with default type mappings."""
        self._type_filters: Dict[str, List[str]] = {
            # Agent type -> relevant tags
            "financial": ["financial", "revenue", "profit", "earnings", "cash"],
            "market": ["market", "tam", "sam", "som", "industry", "growth"],
            "competitive": ["competitor", "competition", "rival", "market_share"],
            "product": ["product", "feature", "technology", "innovation"],
            "synthesizer": ["summary", "finding", "key_point", "conclusion"],
        }

    def add_type_filter(self, agent_type: str, tags: List[str]) -> None:
        """
        Add or update type filter mapping.

        Args:
            agent_type: Agent type name
            tags: Relevant tags for this type
        """
        self._type_filters[agent_type] = tags

    def get_type_tags(self, agent_type: str) -> List[str]:
        """Get relevant tags for an agent type."""
        return self._type_filters.get(agent_type, [])

    def filter_for_agent(
        self, items: Dict[str, ContextItem], target_agent: str, target_type: str
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
        exclude_tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Filter items by tags.

        Args:
            items: Context items to filter
            include_tags: Tags to include (items must have at least one)
            exclude_tags: Tags to exclude (items must not have any)

        Returns:
            Filtered context dictionary
        """
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
        self, items: Dict[str, ContextItem], visibility: ContextVisibility, agent_name: str
    ) -> Dict[str, Any]:
        """
        Filter items by visibility level.

        Args:
            items: Context items to filter
            visibility: Required visibility level
            agent_name: Agent requesting the filter

        Returns:
            Filtered context dictionary
        """
        filtered = {}

        for key, item in items.items():
            if item.is_expired():
                continue

            if item.visibility == visibility or item.is_visible_to(agent_name):
                filtered[key] = item.value

        return filtered

    def filter_by_owner(
        self, items: Dict[str, ContextItem], owner_agents: List[str]
    ) -> Dict[str, Any]:
        """
        Filter items by owner agent.

        Args:
            items: Context items to filter
            owner_agents: List of owner agents to include

        Returns:
            Filtered context dictionary
        """
        filtered = {}

        for key, item in items.items():
            if item.is_expired():
                continue

            if item.owner_agent in owner_agents:
                filtered[key] = item.value

        return filtered

    def filter_recent(
        self, items: Dict[str, ContextItem], max_age_seconds: int = 3600
    ) -> Dict[str, Any]:
        """
        Filter items by age.

        Args:
            items: Context items to filter
            max_age_seconds: Maximum age in seconds

        Returns:
            Filtered context dictionary with recent items only
        """
        from datetime import timedelta

        filtered = {}
        cutoff = utc_now() - timedelta(seconds=max_age_seconds)

        for key, item in items.items():
            if item.is_expired():
                continue

            if item.created_at >= cutoff:
                filtered[key] = item.value

        return filtered
