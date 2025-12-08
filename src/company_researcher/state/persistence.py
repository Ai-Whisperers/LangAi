"""
State Persistence - Durable storage backends.

Provides:
- SQLite persistence
- In-memory persistence
- Persistence interface
"""

import json
import sqlite3
import threading
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class StatePersistence(ABC):
    """Abstract base class for state persistence."""

    @abstractmethod
    def save(self, key: str, state: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save state and return ID."""
        pass

    @abstractmethod
    def load(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Load state by ID."""
        pass

    @abstractmethod
    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """List all keys with optional prefix filter."""
        pass

    @abstractmethod
    def delete(self, state_id: str) -> bool:
        """Delete state by ID."""
        pass


class InMemoryPersistence(StatePersistence):
    """
    In-memory state persistence.

    Useful for testing and development.
    """

    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    def save(self, key: str, state: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save state to memory."""
        state_id = f"{key}:{uuid.uuid4()}"
        with self._lock:
            self._storage[state_id] = state.copy()
            self._metadata[state_id] = {
                "key": key,
                "created_at": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
        return state_id

    def load(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Load state from memory."""
        with self._lock:
            return self._storage.get(state_id, {}).copy() if state_id in self._storage else None

    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """List all keys."""
        with self._lock:
            keys = list(self._storage.keys())
            if prefix:
                keys = [k for k in keys if k.startswith(prefix)]
            return keys

    def delete(self, state_id: str) -> bool:
        """Delete state from memory."""
        with self._lock:
            if state_id in self._storage:
                del self._storage[state_id]
                self._metadata.pop(state_id, None)
                return True
            return False

    def clear(self) -> None:
        """Clear all storage."""
        with self._lock:
            self._storage.clear()
            self._metadata.clear()


class SQLitePersistence(StatePersistence):
    """
    SQLite-based state persistence.

    Usage:
        persistence = SQLitePersistence("state.db")

        # Save state
        state_id = persistence.save("thread-123", {"messages": []})

        # Load state
        state = persistence.load(state_id)
    """

    def __init__(self, db_path: str = "state.db"):
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
            CREATE TABLE IF NOT EXISTS states (
                id TEXT PRIMARY KEY,
                key TEXT NOT NULL,
                state TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_states_key ON states(key)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_states_created ON states(created_at)
        """)
        conn.commit()

    def save(self, key: str, state: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save state to SQLite."""
        state_id = f"{key}:{uuid.uuid4()}"
        now = datetime.utcnow().isoformat()

        conn = self._get_connection()
        conn.execute(
            """
            INSERT INTO states (id, key, state, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                state_id,
                key,
                json.dumps(state, default=str),
                json.dumps(metadata or {}, default=str),
                now,
                now
            )
        )
        conn.commit()
        return state_id

    def load(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Load state from SQLite."""
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT state FROM states WHERE id = ?",
            (state_id,)
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row['state'])
        return None

    def update(self, state_id: str, state: Dict[str, Any]) -> bool:
        """Update existing state."""
        conn = self._get_connection()
        cursor = conn.execute(
            """
            UPDATE states
            SET state = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                json.dumps(state, default=str),
                datetime.utcnow().isoformat(),
                state_id
            )
        )
        conn.commit()
        return cursor.rowcount > 0

    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """List all state IDs."""
        conn = self._get_connection()
        if prefix:
            cursor = conn.execute(
                "SELECT id FROM states WHERE key LIKE ? ORDER BY created_at DESC",
                (f"{prefix}%",)
            )
        else:
            cursor = conn.execute(
                "SELECT id FROM states ORDER BY created_at DESC"
            )
        return [row['id'] for row in cursor.fetchall()]

    def list_for_key(self, key: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List all states for a key."""
        conn = self._get_connection()
        cursor = conn.execute(
            """
            SELECT id, key, state, metadata, created_at, updated_at
            FROM states
            WHERE key = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (key, limit)
        )
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row['id'],
                "key": row['key'],
                "state": json.loads(row['state']),
                "metadata": json.loads(row['metadata']),
                "created_at": row['created_at'],
                "updated_at": row['updated_at']
            })
        return results

    def get_latest(self, key: str) -> Optional[Dict[str, Any]]:
        """Get the latest state for a key."""
        results = self.list_for_key(key, limit=1)
        return results[0] if results else None

    def delete(self, state_id: str) -> bool:
        """Delete state from SQLite."""
        conn = self._get_connection()
        cursor = conn.execute(
            "DELETE FROM states WHERE id = ?",
            (state_id,)
        )
        conn.commit()
        return cursor.rowcount > 0

    def delete_for_key(self, key: str) -> int:
        """Delete all states for a key."""
        conn = self._get_connection()
        cursor = conn.execute(
            "DELETE FROM states WHERE key = ?",
            (key,)
        )
        conn.commit()
        return cursor.rowcount

    def cleanup_old(self, key: str, keep_count: int = 10) -> int:
        """Remove old states, keeping only the most recent."""
        conn = self._get_connection()

        # Get IDs to keep
        cursor = conn.execute(
            """
            SELECT id FROM states
            WHERE key = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (key, keep_count)
        )
        keep_ids = [row['id'] for row in cursor.fetchall()]

        if not keep_ids:
            return 0

        # Delete older entries
        placeholders = ','.join('?' * len(keep_ids))
        cursor = conn.execute(
            f"""
            DELETE FROM states
            WHERE key = ? AND id NOT IN ({placeholders})
            """,
            (key, *keep_ids)
        )
        conn.commit()
        return cursor.rowcount

    def close(self) -> None:
        """Close database connection."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            del self._local.connection


def create_persistence(
    backend: str = "sqlite",
    **kwargs
) -> StatePersistence:
    """
    Factory function to create persistence backend.

    Args:
        backend: Backend type ("sqlite", "memory")
        **kwargs: Backend-specific arguments

    Returns:
        StatePersistence instance
    """
    if backend == "sqlite":
        return SQLitePersistence(**kwargs)
    elif backend == "memory":
        return InMemoryPersistence()
    else:
        raise ValueError(f"Unknown backend: {backend}")
