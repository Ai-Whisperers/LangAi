"""
Task Storage - Persistent storage for API tasks.

Provides persistent task and batch storage with multiple backends:
- SQLite for single-instance deployments
- Redis for distributed deployments
- In-memory for testing

Replaces volatile in-memory dicts that lose data on restart.

This module now serves as a backward-compatible entry point.
The actual implementations are in the storage/ package:
- storage/models.py: TaskStorage abstract interface
- storage/sqlite.py: SQLiteTaskStorage implementation
- storage/redis.py: RedisTaskStorage implementation
- storage/memory.py: InMemoryTaskStorage implementation
- storage/__init__.py: Factory functions and exports

Usage:
    from company_researcher.api.task_storage import init_task_storage

    # Initialize storage (auto-detects backend from environment)
    storage = await init_task_storage()
    await storage.save_task("task_123", {"company_name": "Tesla", ...})

    # Or manually configure backend
    from company_researcher.api.task_storage import SQLiteTaskStorage
    storage = SQLiteTaskStorage("tasks.db")
"""

# Import from storage package for backward compatibility
from .storage import (
    # Abstract interface
    TaskStorage,
    # Implementations
    SQLiteTaskStorage,
    RedisTaskStorage,
    InMemoryTaskStorage,
    # Factory functions
    get_task_storage,
    set_task_storage,
    init_task_storage,
    # Utilities
    _utcnow,
    _serialize_datetime,
)

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
    # Utilities (for compatibility)
    "_utcnow",
    "_serialize_datetime",
]


# ============================================================================
# Demo and Testing
# ============================================================================

if __name__ == "__main__":
    import asyncio

    async def demo():
        """Demonstrate task storage backends."""
        print("Task Storage Backends Demo")
        print("=" * 60)

        # 1. SQLite Backend
        print("\n1. SQLite Backend (Single-Instance)")
        print("-" * 60)
        sqlite_storage = SQLiteTaskStorage("data/demo_tasks.db")

        task_data = {
            "task_id": "task_001",
            "company_name": "Tesla Inc",
            "status": "running",
            "created_at": _utcnow().isoformat(),
        }

        await sqlite_storage.save_task("task_001", task_data)
        print(f"   ✓ Saved task: {task_data['task_id']}")

        retrieved = await sqlite_storage.get_task("task_001")
        print(f"   ✓ Retrieved: {retrieved['company_name']} - Status: {retrieved['status']}")

        await sqlite_storage.update_task("task_001", {"status": "completed"})
        updated = await sqlite_storage.get_task("task_001")
        print(f"   ✓ Updated status: {updated['status']}")

        count = await sqlite_storage.count_tasks(status="completed")
        print(f"   ✓ Tasks with status 'completed': {count}")

        sqlite_storage.close()
        print("   ✓ Connection closed")

        # 2. In-Memory Backend
        print("\n2. In-Memory Backend (Testing)")
        print("-" * 60)
        memory_storage = InMemoryTaskStorage()

        for i in range(3):
            task = {
                "task_id": f"task_{i:03d}",
                "company_name": f"Company {i}",
                "status": "pending" if i % 2 == 0 else "completed",
                "created_at": _utcnow().isoformat(),
            }
            await memory_storage.save_task(f"task_{i:03d}", task)
        print("   ✓ Saved 3 tasks")

        tasks = await memory_storage.list_tasks(status="pending")
        print(f"   ✓ Found {len(tasks)} pending tasks")

        all_tasks = await memory_storage.list_tasks()
        print(f"   ✓ Total tasks: {len(all_tasks)}")

        # 3. Batch Operations
        print("\n3. Batch Operations")
        print("-" * 60)
        batch_data = {
            "batch_id": "batch_001",
            "status": "running",
            "task_ids": ["task_001", "task_002", "task_003"],
            "created_at": _utcnow().isoformat(),
        }

        await memory_storage.save_batch("batch_001", batch_data)
        print(f"   ✓ Saved batch: {batch_data['batch_id']}")

        batch = await memory_storage.get_batch("batch_001")
        print(f"   ✓ Retrieved batch with {len(batch['task_ids'])} tasks")

        await memory_storage.update_batch("batch_001", {"status": "completed"})
        updated_batch = await memory_storage.get_batch("batch_001")
        print(f"   ✓ Updated batch status: {updated_batch['status']}")

        # 4. Factory Function
        print("\n4. Factory Function (Environment-Based)")
        print("-" * 60)
        import os

        # Set environment for SQLite
        os.environ["TASK_STORAGE_BACKEND"] = "sqlite"
        os.environ["TASK_DB_PATH"] = "data/factory_tasks.db"

        storage = await init_task_storage()
        print(f"   ✓ Initialized storage: {type(storage).__name__}")

        await storage.save_task("factory_task", {
            "company_name": "Factory Test",
            "status": "pending",
            "created_at": _utcnow().isoformat(),
        })
        print("   ✓ Saved task via factory storage")

        task = await storage.get_task("factory_task")
        print(f"   ✓ Retrieved: {task['company_name']}")

        if isinstance(storage, SQLiteTaskStorage):
            storage.close()

        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("  ✓ SQLite backend with persistent storage")
        print("  ✓ In-memory backend for testing")
        print("  ✓ CRUD operations (Create, Read, Update, Delete)")
        print("  ✓ Batch operations")
        print("  ✓ Status filtering and counting")
        print("  ✓ Factory function with environment variables")
        print("  ✓ Thread-safe operations")

    asyncio.run(demo())
