"""
State Snapshots - Point-in-time state capture.

Provides:
- Immutable snapshots
- Snapshot comparison
- Snapshot storage
"""

import copy
import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils import utc_now


@dataclass
class StateSnapshot:
    """
    Immutable snapshot of state at a point in time.

    Snapshots are immutable - once created, they cannot be modified.
    """

    id: str
    state: Dict[str, Any]
    created_at: datetime
    checksum: str
    label: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    _initialized: bool = field(default=False, repr=False, compare=False)

    def __post_init__(self):
        # Make state immutable by deep copying
        object.__setattr__(self, "state", copy.deepcopy(self.state))
        # Mark as initialized to enable immutability
        object.__setattr__(self, "_initialized", True)

    def __setattr__(self, name, value):
        # Allow setting during initialization, block after
        if getattr(self, "_initialized", False) and name != "_initialized":
            raise AttributeError("Snapshots are immutable")
        object.__setattr__(self, name, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "checksum": self.checksum,
            "label": self.label,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateSnapshot":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = utc_now()

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            state=data.get("state", {}),
            created_at=created_at,
            checksum=data.get("checksum", ""),
            label=data.get("label"),
            metadata=data.get("metadata", {}),
        )

    def compare(self, other: "StateSnapshot") -> Dict[str, Any]:
        """
        Compare with another snapshot.

        Returns:
            Comparison dictionary with differences
        """
        return {
            "same": self.checksum == other.checksum,
            "this_id": self.id,
            "other_id": other.id,
            "this_created": self.created_at.isoformat(),
            "other_created": other.created_at.isoformat(),
            "differences": self._find_differences(self.state, other.state),
        }

    def _find_differences(
        self, state1: Dict[str, Any], state2: Dict[str, Any], path: str = ""
    ) -> List[Dict[str, Any]]:
        """Find differences between two states."""
        differences = []
        all_keys = set(state1.keys()) | set(state2.keys())

        for key in all_keys:
            current_path = f"{path}.{key}" if path else key

            if key not in state1:
                differences.append({"path": current_path, "type": "added", "value": state2[key]})
            elif key not in state2:
                differences.append({"path": current_path, "type": "removed", "value": state1[key]})
            elif state1[key] != state2[key]:
                if isinstance(state1[key], dict) and isinstance(state2[key], dict):
                    differences.extend(
                        self._find_differences(state1[key], state2[key], current_path)
                    )
                else:
                    differences.append(
                        {
                            "path": current_path,
                            "type": "changed",
                            "old_value": state1[key],
                            "new_value": state2[key],
                        }
                    )

        return differences


class SnapshotStore:
    """
    Storage for state snapshots.

    Usage:
        store = SnapshotStore("snapshots/")

        # Create snapshot
        snapshot = store.create(state, label="before-processing")

        # List snapshots
        snapshots = store.list(limit=10)

        # Restore from snapshot
        state = store.restore(snapshot_id)
    """

    def __init__(self, storage_dir: str = "snapshots"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, StateSnapshot] = {}
        self._last_created_at: Optional[datetime] = None

    def _calculate_checksum(self, state: Dict[str, Any]) -> str:
        """Calculate checksum for state."""
        serialized = json.dumps(state, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def create(
        self,
        state: Dict[str, Any],
        label: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StateSnapshot:
        """
        Create a new snapshot.

        Args:
            state: State to snapshot
            label: Optional label
            metadata: Optional metadata

        Returns:
            Created StateSnapshot
        """
        created_at = utc_now()
        if self._last_created_at is not None and created_at <= self._last_created_at:
            created_at = self._last_created_at + timedelta(microseconds=1)
        self._last_created_at = created_at

        snapshot = StateSnapshot(
            id=str(uuid.uuid4()),
            state=state,
            created_at=created_at,
            checksum=self._calculate_checksum(state),
            label=label,
            metadata=metadata or {},
        )

        # Save to storage
        self._save(snapshot)
        self._cache[snapshot.id] = snapshot

        return snapshot

    def _save(self, snapshot: StateSnapshot) -> None:
        """Save snapshot to storage."""
        filepath = self.storage_dir / f"{snapshot.id}.json"
        with open(filepath, "w") as f:
            json.dump(snapshot.to_dict(), f, indent=2, default=str)

    def load(self, snapshot_id: str) -> Optional[StateSnapshot]:
        """Load a snapshot by ID."""
        # Check cache
        if snapshot_id in self._cache:
            return self._cache[snapshot_id]

        # Load from file
        filepath = self.storage_dir / f"{snapshot_id}.json"
        if not filepath.exists():
            return None

        with open(filepath, "r") as f:
            data = json.load(f)

        snapshot = StateSnapshot.from_dict(data)
        self._cache[snapshot_id] = snapshot
        return snapshot

    def restore(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """
        Restore state from a snapshot.

        Args:
            snapshot_id: Snapshot ID

        Returns:
            Copy of snapshot state
        """
        snapshot = self.load(snapshot_id)
        if snapshot:
            return copy.deepcopy(snapshot.state)
        return None

    def list(self, label: Optional[str] = None, limit: int = 100) -> List[StateSnapshot]:
        """
        List snapshots.

        Args:
            label: Filter by label
            limit: Maximum number to return

        Returns:
            List of snapshots, newest first
        """
        snapshots = []

        for filepath in self.storage_dir.glob("*.json"):
            with open(filepath, "r") as f:
                data = json.load(f)
            snapshot = StateSnapshot.from_dict(data)

            if label is None or snapshot.label == label:
                snapshots.append(snapshot)

        # Sort by created_at descending
        snapshots.sort(key=lambda s: s.created_at, reverse=True)
        return snapshots[:limit]

    def get_by_label(self, label: str) -> Optional[StateSnapshot]:
        """Get latest snapshot with a specific label."""
        snapshots = self.list(label=label, limit=1)
        return snapshots[0] if snapshots else None

    def delete(self, snapshot_id: str) -> bool:
        """Delete a snapshot."""
        filepath = self.storage_dir / f"{snapshot_id}.json"
        if filepath.exists():
            filepath.unlink()
            self._cache.pop(snapshot_id, None)
            return True
        return False

    def compare(self, snapshot_id1: str, snapshot_id2: str) -> Optional[Dict[str, Any]]:
        """Compare two snapshots."""
        snap1 = self.load(snapshot_id1)
        snap2 = self.load(snapshot_id2)

        if snap1 is None or snap2 is None:
            return None

        return snap1.compare(snap2)

    def cleanup_old(self, keep_count: int = 100) -> int:
        """Remove old snapshots, keeping only the most recent."""
        snapshots = self.list(limit=10000)
        if len(snapshots) <= keep_count:
            return 0

        deleted = 0
        for snapshot in snapshots[keep_count:]:
            if self.delete(snapshot.id):
                deleted += 1

        return deleted


# Convenience functions
def create_snapshot(
    state: Dict[str, Any], label: Optional[str] = None, storage_dir: str = "snapshots"
) -> StateSnapshot:
    """Create a snapshot."""
    store = SnapshotStore(storage_dir)
    return store.create(state, label=label)


def restore_snapshot(snapshot_id: str, storage_dir: str = "snapshots") -> Optional[Dict[str, Any]]:
    """Restore state from snapshot."""
    store = SnapshotStore(storage_dir)
    return store.restore(snapshot_id)
