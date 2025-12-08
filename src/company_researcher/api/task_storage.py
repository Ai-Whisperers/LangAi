"""
Task Storage - Persistent storage for API tasks.

Provides persistent task and batch storage with multiple backends:
- SQLite for single-instance deployments
- Redis for distributed deployments
- In-memory for testing

Replaces volatile in-memory dicts that lose data on restart.
"""

import json
import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import sqlite3

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


def _serialize_datetime(obj: Any) -> str:
    """JSON serializer for datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


# ============================================================================
# Abstract Interface
# ============================================================================

class TaskStorage(ABC):
    """Abstract interface for task storage."""

    @abstractmethod
    async def save_task(self, task_id: str, task: Dict[str, Any]) -> bool:
        """Save a task."""
        pass

    @abstractmethod
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID."""
        pass

    @abstractmethod
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update task fields."""
        pass

    @abstractmethod
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        pass

    @abstractmethod
    async def list_tasks(
        self,
        status: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List tasks with optional filtering."""
        pass

    @abstractmethod
    async def save_batch(self, batch_id: str, batch: Dict[str, Any]) -> bool:
        """Save a batch."""
        pass

    @abstractmethod
    async def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get a batch by ID."""
        pass

    @abstractmethod
    async def update_batch(self, batch_id: str, updates: Dict[str, Any]) -> bool:
        """Update batch fields."""
        pass

    @abstractmethod
    async def count_tasks(self, status: Optional[str] = None) -> int:
        """Count tasks by status."""
        pass

    @abstractmethod
    async def cleanup_old_tasks(self, max_age_days: int = 7) -> int:
        """Remove tasks older than max_age_days."""
        pass


# ============================================================================
# SQLite Implementation
# ============================================================================

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


# ============================================================================
# Redis Implementation (for distributed deployments)
# ============================================================================

class RedisTaskStorage(TaskStorage):
    """
    Redis-based task storage for distributed deployments.

    Usage:
        storage = RedisTaskStorage(host="localhost", port=6379)
        await storage.connect()
        await storage.save_task("task_123", {"company_name": "Tesla", ...})
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "research:",
        task_ttl: int = 604800  # 7 days
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.prefix = prefix
        self.task_ttl = task_ttl
        self._redis: Optional[Any] = None
        self._connected = False

    async def connect(self) -> bool:
        """Connect to Redis."""
        try:
            import redis.asyncio as redis

            self._redis = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True
            )
            await self._redis.ping()
            self._connected = True
            return True
        except ImportError:
            raise ImportError("redis package not installed")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return False

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._redis:
            await self._redis.close()
            self._connected = False

    def _task_key(self, task_id: str) -> str:
        return f"{self.prefix}task:{task_id}"

    def _batch_key(self, batch_id: str) -> str:
        return f"{self.prefix}batch:{batch_id}"

    async def save_task(self, task_id: str, task: Dict[str, Any]) -> bool:
        """Save a task to Redis."""
        if not self._connected:
            return False

        try:
            data = json.dumps(task, default=_serialize_datetime)
            await self._redis.setex(
                self._task_key(task_id),
                self.task_ttl,
                data
            )

            # Add to task index for listing
            await self._redis.zadd(
                f"{self.prefix}tasks:index",
                {task_id: _utcnow().timestamp()}
            )

            # Add to status-specific set
            status = task.get("status", "pending")
            await self._redis.sadd(f"{self.prefix}tasks:status:{status}", task_id)

            return True
        except Exception as e:
            logger.error(f"Failed to save task {task_id}: {e}")
            return False

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task from Redis."""
        if not self._connected:
            return None

        try:
            data = await self._redis.get(self._task_key(task_id))
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            return None

    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update task fields in Redis."""
        task = await self.get_task(task_id)
        if not task:
            return False

        old_status = task.get("status")
        task.update(updates)
        new_status = task.get("status")

        # Update status sets if status changed
        if old_status != new_status and self._connected:
            try:
                await self._redis.srem(f"{self.prefix}tasks:status:{old_status}", task_id)
                await self._redis.sadd(f"{self.prefix}tasks:status:{new_status}", task_id)
            except Exception:
                pass

        return await self.save_task(task_id, task)

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task from Redis."""
        if not self._connected:
            return False

        try:
            task = await self.get_task(task_id)
            if task:
                status = task.get("status", "pending")
                await self._redis.srem(f"{self.prefix}tasks:status:{status}", task_id)

            await self._redis.zrem(f"{self.prefix}tasks:index", task_id)
            result = await self._redis.delete(self._task_key(task_id))
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            return False

    async def list_tasks(
        self,
        status: Optional[str] = None,
        company: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List tasks with filtering."""
        if not self._connected:
            return []

        try:
            if status:
                # Get from status-specific set
                task_ids = await self._redis.smembers(f"{self.prefix}tasks:status:{status}")
                task_ids = list(task_ids)
            else:
                # Get from sorted index (newest first)
                task_ids = await self._redis.zrevrange(
                    f"{self.prefix}tasks:index",
                    offset,
                    offset + limit - 1
                )

            tasks = []
            for task_id in task_ids:
                task = await self.get_task(task_id)
                if task:
                    if company:
                        if company.lower() in task.get("company_name", "").lower():
                            tasks.append(task)
                    else:
                        tasks.append(task)

            # Apply offset/limit for status filter (already applied for index)
            if status:
                tasks = tasks[offset:offset + limit]

            return tasks
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            return []

    async def save_batch(self, batch_id: str, batch: Dict[str, Any]) -> bool:
        """Save a batch to Redis."""
        if not self._connected:
            return False

        try:
            data = json.dumps(batch, default=_serialize_datetime)
            await self._redis.setex(
                self._batch_key(batch_id),
                self.task_ttl,
                data
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save batch {batch_id}: {e}")
            return False

    async def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get a batch from Redis."""
        if not self._connected:
            return None

        try:
            data = await self._redis.get(self._batch_key(batch_id))
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get batch {batch_id}: {e}")
            return None

    async def update_batch(self, batch_id: str, updates: Dict[str, Any]) -> bool:
        """Update batch fields in Redis."""
        batch = await self.get_batch(batch_id)
        if not batch:
            return False

        batch.update(updates)
        return await self.save_batch(batch_id, batch)

    async def count_tasks(self, status: Optional[str] = None) -> int:
        """Count tasks by status."""
        if not self._connected:
            return 0

        try:
            if status:
                return await self._redis.scard(f"{self.prefix}tasks:status:{status}")
            else:
                return await self._redis.zcard(f"{self.prefix}tasks:index")
        except Exception:
            return 0

    async def cleanup_old_tasks(self, max_age_days: int = 7) -> int:
        """Remove tasks older than max_age_days."""
        if not self._connected:
            return 0

        try:
            cutoff = (_utcnow() - timedelta(days=max_age_days)).timestamp()

            # Get old task IDs
            old_task_ids = await self._redis.zrangebyscore(
                f"{self.prefix}tasks:index",
                "-inf",
                cutoff
            )

            count = 0
            for task_id in old_task_ids:
                if await self.delete_task(task_id):
                    count += 1

            return count
        except Exception as e:
            logger.error(f"Failed to cleanup old tasks: {e}")
            return 0


# ============================================================================
# In-Memory Implementation (for testing)
# ============================================================================

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


# ============================================================================
# Factory and Global Instance
# ============================================================================

_task_storage: Optional[TaskStorage] = None


def get_task_storage() -> TaskStorage:
    """
    Get the global task storage instance.

    Returns SQLiteTaskStorage by default, configurable via environment.
    """
    global _task_storage

    if _task_storage is None:
        import os

        backend = os.getenv("TASK_STORAGE_BACKEND", "sqlite")

        if backend == "redis":
            _task_storage = RedisTaskStorage(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                password=os.getenv("REDIS_PASSWORD")
            )
        elif backend == "memory":
            _task_storage = InMemoryTaskStorage()
        else:
            # Default to SQLite
            db_path = os.getenv("TASK_DB_PATH", "data/tasks.db")
            _task_storage = SQLiteTaskStorage(db_path)

    return _task_storage


def set_task_storage(storage: TaskStorage) -> None:
    """Set the global task storage instance (for testing)."""
    global _task_storage
    _task_storage = storage


async def init_task_storage() -> TaskStorage:
    """Initialize and return the task storage."""
    storage = get_task_storage()

    # Connect if Redis
    if isinstance(storage, RedisTaskStorage):
        await storage.connect()

    return storage
