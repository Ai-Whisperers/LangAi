"""
In-Memory Task Storage Backend.

Provides volatile task storage for testing and development.
Thread-safe with RLock synchronization.

Features:
- Fast in-memory storage
- Thread-safe operations with RLock
- Task and batch CRUD operations
- Filtering by status and company
- Cleanup of old tasks

Usage:
    from company_researcher.api.storage.memory import InMemoryTaskStorage

    storage = InMemoryTaskStorage()
    await storage.save_task("task_123", {"company_name": "Tesla", ...})
    task = await storage.get_task("task_123")
"""

import threading
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from .models import TaskStorage, _utcnow


class InMemoryTaskStorage(TaskStorage):
    """In-memory task storage for testing."""

    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._batches: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    async def save_task(self, task_id: str, task: Dict[str, Any]) -> bool:
        with self._lock:
            self._tasks[task_id] = task.copy()
        return True

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            task = self._tasks.get(task_id)
            return task.copy() if task else None

    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        with self._lock:
            if task_id not in self._tasks:
                return False
            self._tasks[task_id].update(updates)
        return True

    async def delete_task(self, task_id: str) -> bool:
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
            return False

    async def list_tasks(
        self,
        status: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        with self._lock:
            tasks = list(self._tasks.values())

        if status:
            tasks = [t for t in tasks if t.get("status") == status]
        if company:
            company_lower = company.lower()
            tasks = [t for t in tasks if company_lower in t.get("company_name", "").lower()]

        tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)
        return tasks[offset:offset + limit]

    async def save_batch(self, batch_id: str, batch: Dict[str, Any]) -> bool:
        with self._lock:
            self._batches[batch_id] = batch.copy()
        return True

    async def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            batch = self._batches.get(batch_id)
            return batch.copy() if batch else None

    async def update_batch(self, batch_id: str, updates: Dict[str, Any]) -> bool:
        with self._lock:
            if batch_id not in self._batches:
                return False
            self._batches[batch_id].update(updates)
        return True

    async def count_tasks(self, status: Optional[str] = None) -> int:
        with self._lock:
            if status:
                return sum(1 for t in self._tasks.values() if t.get("status") == status)
            return len(self._tasks)

    async def cleanup_old_tasks(self, max_age_days: int = 7) -> int:
        cutoff = _utcnow() - timedelta(days=max_age_days)
        count = 0

        with self._lock:
            to_delete = []
            for task_id, task in self._tasks.items():
                created_at = task.get("created_at")
                if isinstance(created_at, datetime):
                    # Make timezone-aware if naive
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=timezone.utc)
                    if created_at < cutoff:
                        to_delete.append(task_id)
                elif isinstance(created_at, str):
                    try:
                        parsed = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if parsed < cutoff:
                            to_delete.append(task_id)
                    except ValueError:
                        pass

            for task_id in to_delete:
                del self._tasks[task_id]
                count += 1

        return count
