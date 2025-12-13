"""
Redis Task Storage Backend.

Provides distributed task storage using Redis for multi-instance deployments.
Supports async operations with automatic TTL management.

Features:
- Distributed task storage with Redis
- Automatic task expiration (TTL)
- Task indexing with sorted sets
- Status-based task filtering
- Batch operations support
- Connection management

Usage:
    from company_researcher.api.storage.redis import RedisTaskStorage

    storage = RedisTaskStorage(host="localhost", port=6379)
    await storage.connect()
    await storage.save_task("task_123", {"company_name": "Tesla", ...})
"""

import json
from datetime import timedelta
from typing import Any, Dict, List, Optional

from .models import TaskStorage, _utcnow, _serialize_datetime
from ...utils import get_logger

logger = get_logger(__name__)


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
            except Exception as e:
                logger.debug(f"Failed to update task status index: {e}")

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
