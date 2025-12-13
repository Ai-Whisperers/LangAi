"""
SQLite Task Storage Backend.

Provides persistent task storage using SQLite for single-instance deployments.
Thread-safe with thread-local connection management.

Features:
- Thread-local database connections for safe concurrent access
- Automatic schema initialization
- Task and batch CRUD operations
- Query filtering by status and company
- Cleanup of old tasks
- Indexed queries for performance

Usage:
    from company_researcher.api.storage.sqlite import SQLiteTaskStorage

    storage = SQLiteTaskStorage("tasks.db")
    await storage.save_task("task_123", {"company_name": "Tesla", ...})
    task = await storage.get_task("task_123")
"""

import json
import sqlite3
import threading
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import TaskStorage, _utcnow, _serialize_datetime
from ...utils import get_logger

logger = get_logger(__name__)


class SQLiteTaskStorage(TaskStorage):
    """
    SQLite-based task storage for single-instance deployments.

    Usage:
        storage = SQLiteTaskStorage("tasks.db")
        await storage.save_task("task_123", {"company_name": "Tesla", ...})
        task = await storage.get_task("task_123")
    """

    def __init__(self, db_path: str = "data/tasks.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                status TEXT NOT NULL,
                batch_id TEXT,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_company ON tasks(company_name)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_batch ON tasks(batch_id)
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS batches (
                batch_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_batches_status ON batches(status)
        """)
        conn.commit()

    async def save_task(self, task_id: str, task: Dict[str, Any]) -> bool:
        """Save a task to SQLite."""
        now = _utcnow().isoformat()
        conn = self._get_connection()

        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO tasks
                (task_id, company_name, status, batch_id, data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    task.get("company_name", ""),
                    task.get("status", "pending"),
                    task.get("batch_id"),
                    json.dumps(task, default=_serialize_datetime),
                    task.get("created_at", now) if isinstance(task.get("created_at"), str)
                        else task.get("created_at", _utcnow()).isoformat() if task.get("created_at")
                        else now,
                    now
                )
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save task {task_id}: {e}")
            return False

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task from SQLite."""
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT data FROM tasks WHERE task_id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row['data'])
        return None

    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update task fields in SQLite."""
        task = await self.get_task(task_id)
        if not task:
            return False

        task.update(updates)
        return await self.save_task(task_id, task)

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task from SQLite."""
        conn = self._get_connection()
        cursor = conn.execute(
            "DELETE FROM tasks WHERE task_id = ?",
            (task_id,)
        )
        conn.commit()
        return cursor.rowcount > 0

    async def list_tasks(
        self,
        status: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List tasks with filtering."""
        conn = self._get_connection()

        query = "SELECT data FROM tasks WHERE 1=1"
        params: List[Any] = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if company:
            query += " AND company_name LIKE ?"
            params.append(f"%{company}%")

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = conn.execute(query, params)
        return [json.loads(row['data']) for row in cursor.fetchall()]

    async def save_batch(self, batch_id: str, batch: Dict[str, Any]) -> bool:
        """Save a batch to SQLite."""
        now = _utcnow().isoformat()
        conn = self._get_connection()

        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO batches
                (batch_id, status, data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    batch.get("status", "pending"),
                    json.dumps(batch, default=_serialize_datetime),
                    batch.get("created_at", now) if isinstance(batch.get("created_at"), str)
                        else batch.get("created_at", _utcnow()).isoformat() if batch.get("created_at")
                        else now,
                    now
                )
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save batch {batch_id}: {e}")
            return False

    async def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get a batch from SQLite."""
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT data FROM batches WHERE batch_id = ?",
            (batch_id,)
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row['data'])
        return None

    async def update_batch(self, batch_id: str, updates: Dict[str, Any]) -> bool:
        """Update batch fields in SQLite."""
        batch = await self.get_batch(batch_id)
        if not batch:
            return False

        batch.update(updates)
        return await self.save_batch(batch_id, batch)

    async def count_tasks(self, status: Optional[str] = None) -> int:
        """Count tasks by status."""
        conn = self._get_connection()

        if status:
            cursor = conn.execute(
                "SELECT COUNT(*) as count FROM tasks WHERE status = ?",
                (status,)
            )
        else:
            cursor = conn.execute("SELECT COUNT(*) as count FROM tasks")

        row = cursor.fetchone()
        return row['count'] if row else 0

    async def cleanup_old_tasks(self, max_age_days: int = 7) -> int:
        """Remove tasks older than max_age_days."""
        cutoff = (_utcnow() - timedelta(days=max_age_days)).isoformat()
        conn = self._get_connection()

        # Delete old tasks
        cursor = conn.execute(
            "DELETE FROM tasks WHERE created_at < ?",
            (cutoff,)
        )
        tasks_deleted = cursor.rowcount

        # Delete old batches
        conn.execute(
            "DELETE FROM batches WHERE created_at < ?",
            (cutoff,)
        )
        conn.commit()

        logger.info(f"Cleaned up {tasks_deleted} old tasks")
        return tasks_deleted

    def close(self) -> None:
        """Close database connection."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            del self._local.connection
