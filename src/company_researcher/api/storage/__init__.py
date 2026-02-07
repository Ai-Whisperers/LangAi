"""
Task Storage Package.

Provides persistent task and batch storage with multiple backends:
- SQLite for single-instance deployments
- Redis for distributed deployments
- In-memory for testing

Usage:
    from company_researcher.api.storage import init_task_storage, get_task_storage

    # Initialize storage (auto-detects backend from environment)
    storage = await init_task_storage()

    # Or manually configure
    from company_researcher.api.storage import SQLiteTaskStorage
    storage = SQLiteTaskStorage("tasks.db")
    await storage.save_task("task_123", {...})

Environment Variables:
    TASK_STORAGE_BACKEND - Backend type: "sqlite" (default), "redis", "memory"
    TASK_DB_PATH - SQLite database path (default: "data/tasks.db")
    REDIS_HOST - Redis host (default: "localhost")
    REDIS_PORT - Redis port (default: 6379)
    REDIS_PASSWORD - Redis password (optional)
"""

from typing import Optional

from ...utils import get_config
from .memory import InMemoryTaskStorage

# Import all classes from submodules
from .models import TaskStorage, _serialize_datetime, _utcnow
from .redis import RedisTaskStorage
from .sqlite import SQLiteTaskStorage

# Re-export all public APIs
__all__ = [
    # Abstract interface
    "TaskStorage",
    # Implementations
    "SQLiteTaskStorage",
    "RedisTaskStorage",
    "InMemoryTaskStorage",
    # Factory functions
    "get_task_storage",
    "set_task_storage",
    "init_task_storage",
    # Utilities
    "_utcnow",
    "_serialize_datetime",
]


# Global storage instance
_task_storage: Optional[TaskStorage] = None


def get_task_storage() -> TaskStorage:
    """
    Get the global task storage instance.

    Returns SQLiteTaskStorage by default, configurable via environment.

    Environment Variables:
        TASK_STORAGE_BACKEND - Backend type: "sqlite", "redis", "memory"
        TASK_DB_PATH - SQLite database path (default: "data/tasks.db")
        REDIS_HOST - Redis host (default: "localhost")
        REDIS_PORT - Redis port (default: 6379)
        REDIS_PASSWORD - Redis password (optional)

    Returns:
        TaskStorage instance based on environment configuration

    Example:
        storage = get_task_storage()
        await storage.save_task("task_123", {...})
    """
    global _task_storage

    if _task_storage is None:
        backend = get_config("TASK_STORAGE_BACKEND", default="sqlite")

        if backend == "redis":
            _task_storage = RedisTaskStorage(
                host=get_config("REDIS_HOST", default="localhost"),
                port=int(get_config("REDIS_PORT", default="6379")),
                password=get_config("REDIS_PASSWORD"),
            )
        elif backend == "memory":
            _task_storage = InMemoryTaskStorage()
        else:
            # Default to SQLite
            db_path = get_config("TASK_DB_PATH", default="data/tasks.db")
            _task_storage = SQLiteTaskStorage(db_path)

    return _task_storage


def set_task_storage(storage: TaskStorage) -> None:
    """
    Set the global task storage instance (for testing).

    Args:
        storage: TaskStorage instance to set as global

    Example:
        from company_researcher.api.storage import InMemoryTaskStorage, set_task_storage

        # Use in-memory storage for tests
        test_storage = InMemoryTaskStorage()
        set_task_storage(test_storage)
    """
    global _task_storage
    _task_storage = storage


async def init_task_storage() -> TaskStorage:
    """
    Initialize and return the task storage.

    Automatically connects to Redis if Redis backend is configured.

    Returns:
        Initialized TaskStorage instance

    Example:
        storage = await init_task_storage()
        await storage.save_task("task_123", {...})
    """
    storage = get_task_storage()

    # Connect if Redis
    if isinstance(storage, RedisTaskStorage):
        await storage.connect()

    return storage
