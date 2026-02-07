"""
Task Storage Abstract Interface.

This module defines the abstract interface for task storage backends.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utcnow() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


def _serialize_datetime(obj: Any) -> str:
    """JSON serializer for datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class TaskStorage(ABC):
    """
    Abstract interface for task storage.

    Implementations must provide methods for:
    - Task CRUD operations (save, get, update, delete, list)
    - Batch operations (save, get, update)
    - Utility operations (count, cleanup)

    Supported backends:
    - SQLiteTaskStorage: Single-instance deployments
    - RedisTaskStorage: Distributed deployments
    - InMemoryTaskStorage: Testing
    """

    @abstractmethod
    async def save_task(self, task_id: str, task: Dict[str, Any]) -> bool:
        """
        Save a task.

        Args:
            task_id: Unique task identifier
            task: Task data dictionary

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task data dictionary or None if not found
        """

    @abstractmethod
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update task fields.

        Args:
            task_id: Task identifier
            updates: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task identifier

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    async def list_tasks(
        self,
        status: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List tasks with optional filtering.

        Args:
            status: Filter by status (e.g., "pending", "running", "completed")
            company: Filter by company name
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip

        Returns:
            List of task dictionaries
        """

    @abstractmethod
    async def save_batch(self, batch_id: str, batch: Dict[str, Any]) -> bool:
        """
        Save a batch.

        Args:
            batch_id: Unique batch identifier
            batch: Batch data dictionary

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    async def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a batch by ID.

        Args:
            batch_id: Batch identifier

        Returns:
            Batch data dictionary or None if not found
        """

    @abstractmethod
    async def update_batch(self, batch_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update batch fields.

        Args:
            batch_id: Batch identifier
            updates: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    async def count_tasks(self, status: Optional[str] = None) -> int:
        """
        Count tasks by status.

        Args:
            status: Optional status filter

        Returns:
            Number of tasks matching criteria
        """

    @abstractmethod
    async def cleanup_old_tasks(self, max_age_days: int = 7) -> int:
        """
        Remove tasks older than max_age_days.

        Args:
            max_age_days: Age threshold in days

        Returns:
            Number of tasks deleted
        """
