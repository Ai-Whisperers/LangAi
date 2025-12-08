"""
Snapshot Testing - Output comparison against saved snapshots.

Provides:
- Snapshot creation and storage
- Snapshot comparison
- Update mechanism
"""

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union


@dataclass
class Snapshot:
    """A saved snapshot for comparison."""
    name: str
    data: Any
    created_at: datetime
    checksum: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "checksum": self.checksum,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Snapshot":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.utcnow()

        return cls(
            name=data.get("name", ""),
            data=data.get("data"),
            created_at=created_at,
            checksum=data.get("checksum", ""),
            metadata=data.get("metadata", {})
        )


class SnapshotManager:
    """
    Manage snapshots for testing.

    Usage:
        manager = SnapshotManager("tests/snapshots")

        # Assert against snapshot
        result = workflow()
        manager.assert_match("test_workflow", result)

        # Update snapshots
        manager.update("test_workflow", new_result)
    """

    def __init__(
        self,
        snapshot_dir: str = "tests/snapshots",
        auto_update: bool = False
    ):
        self.snapshot_dir = Path(snapshot_dir)
        self.auto_update = auto_update
        self._snapshots: Dict[str, Snapshot] = {}

        # Create directory if needed
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def _get_snapshot_path(self, name: str) -> Path:
        """Get path for a snapshot file."""
        safe_name = name.replace("/", "_").replace("\\", "_")
        return self.snapshot_dir / f"{safe_name}.snap.json"

    def _calculate_checksum(self, data: Any) -> str:
        """Calculate checksum for data."""
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(serialized.encode()).hexdigest()

    def _serialize(self, data: Any) -> Any:
        """Serialize data for storage."""
        if hasattr(data, 'to_dict'):
            return data.to_dict()
        elif hasattr(data, '__dict__'):
            return {k: self._serialize(v) for k, v in data.__dict__.items()
                    if not k.startswith('_')}
        elif isinstance(data, dict):
            return {k: self._serialize(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self._serialize(v) for v in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        return data

    def save(self, name: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> Snapshot:
        """
        Save a new snapshot.

        Args:
            name: Snapshot name
            data: Data to snapshot
            metadata: Optional metadata

        Returns:
            Created Snapshot
        """
        serialized = self._serialize(data)
        checksum = self._calculate_checksum(serialized)

        snapshot = Snapshot(
            name=name,
            data=serialized,
            created_at=datetime.utcnow(),
            checksum=checksum,
            metadata=metadata or {}
        )

        # Save to file
        path = self._get_snapshot_path(name)
        with open(path, 'w') as f:
            json.dump(snapshot.to_dict(), f, indent=2, default=str)

        self._snapshots[name] = snapshot
        return snapshot

    def load(self, name: str) -> Optional[Snapshot]:
        """
        Load a snapshot.

        Args:
            name: Snapshot name

        Returns:
            Snapshot if found, None otherwise
        """
        # Check cache
        if name in self._snapshots:
            return self._snapshots[name]

        # Load from file
        path = self._get_snapshot_path(name)
        if not path.exists():
            return None

        with open(path, 'r') as f:
            data = json.load(f)

        snapshot = Snapshot.from_dict(data)
        self._snapshots[name] = snapshot
        return snapshot

    def exists(self, name: str) -> bool:
        """Check if snapshot exists."""
        return self._get_snapshot_path(name).exists()

    def delete(self, name: str) -> bool:
        """Delete a snapshot."""
        path = self._get_snapshot_path(name)
        if path.exists():
            path.unlink()
            self._snapshots.pop(name, None)
            return True
        return False

    def compare(self, name: str, data: Any) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Compare data against snapshot.

        Args:
            name: Snapshot name
            data: Data to compare

        Returns:
            Tuple of (matches, diff_info)
        """
        snapshot = self.load(name)
        if snapshot is None:
            return False, {"error": "Snapshot not found"}

        serialized = self._serialize(data)
        new_checksum = self._calculate_checksum(serialized)

        if new_checksum == snapshot.checksum:
            return True, None

        # Find differences
        diff = self._find_diff(snapshot.data, serialized)
        return False, diff

    def _find_diff(self, expected: Any, actual: Any, path: str = "") -> Dict[str, Any]:
        """Find differences between expected and actual."""
        diff = {"path": path, "differences": []}

        if type(expected) != type(actual):
            diff["differences"].append({
                "type": "type_mismatch",
                "expected_type": type(expected).__name__,
                "actual_type": type(actual).__name__
            })
            return diff

        if isinstance(expected, dict):
            all_keys = set(expected.keys()) | set(actual.keys())
            for key in all_keys:
                key_path = f"{path}.{key}" if path else key

                if key not in expected:
                    diff["differences"].append({
                        "path": key_path,
                        "type": "added",
                        "value": actual[key]
                    })
                elif key not in actual:
                    diff["differences"].append({
                        "path": key_path,
                        "type": "removed",
                        "value": expected[key]
                    })
                elif expected[key] != actual[key]:
                    if isinstance(expected[key], (dict, list)):
                        sub_diff = self._find_diff(expected[key], actual[key], key_path)
                        diff["differences"].extend(sub_diff.get("differences", []))
                    else:
                        diff["differences"].append({
                            "path": key_path,
                            "type": "changed",
                            "expected": expected[key],
                            "actual": actual[key]
                        })

        elif isinstance(expected, list):
            if len(expected) != len(actual):
                diff["differences"].append({
                    "path": path,
                    "type": "length_mismatch",
                    "expected_length": len(expected),
                    "actual_length": len(actual)
                })
            for i, (e, a) in enumerate(zip(expected, actual)):
                if e != a:
                    item_path = f"{path}[{i}]"
                    if isinstance(e, (dict, list)):
                        sub_diff = self._find_diff(e, a, item_path)
                        diff["differences"].extend(sub_diff.get("differences", []))
                    else:
                        diff["differences"].append({
                            "path": item_path,
                            "type": "changed",
                            "expected": e,
                            "actual": a
                        })

        elif expected != actual:
            diff["differences"].append({
                "path": path or "root",
                "type": "changed",
                "expected": expected,
                "actual": actual
            })

        return diff

    def assert_match(
        self,
        name: str,
        data: Any,
        update: bool = False
    ) -> None:
        """
        Assert that data matches snapshot.

        Args:
            name: Snapshot name
            data: Data to compare
            update: Update snapshot if mismatch

        Raises:
            AssertionError if data doesn't match and update is False
        """
        if not self.exists(name) or update or self.auto_update:
            self.save(name, data)
            return

        matches, diff = self.compare(name, data)
        if not matches:
            raise AssertionError(
                f"Snapshot mismatch for '{name}':\n{json.dumps(diff, indent=2)}"
            )

    def update(self, name: str, data: Any) -> Snapshot:
        """Update an existing snapshot."""
        return self.save(name, data)

    def list_snapshots(self) -> List[str]:
        """List all snapshot names."""
        return [
            p.stem.replace(".snap", "")
            for p in self.snapshot_dir.glob("*.snap.json")
        ]


# Global snapshot manager
_snapshot_manager: Optional[SnapshotManager] = None


def _get_snapshot_manager() -> SnapshotManager:
    """Get or create global snapshot manager."""
    global _snapshot_manager
    if _snapshot_manager is None:
        _snapshot_manager = SnapshotManager()
    return _snapshot_manager


def snapshot_test(name: str):
    """
    Decorator for snapshot testing.

    Usage:
        @snapshot_test("my_test")
        def test_workflow():
            return workflow()
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            manager = _get_snapshot_manager()
            manager.assert_match(name, result)
            return result
        return wrapper
    return decorator


def update_snapshots(
    snapshot_dir: str = "tests/snapshots",
    names: Optional[List[str]] = None
) -> int:
    """
    Update snapshots interactively.

    Args:
        snapshot_dir: Directory containing snapshots
        names: Optional list of specific snapshots to update

    Returns:
        Number of snapshots updated
    """
    manager = SnapshotManager(snapshot_dir)
    snapshots = names or manager.list_snapshots()

    updated = 0
    for name in snapshots:
        snapshot = manager.load(name)
        if snapshot:
            print(f"Snapshot: {name}")
            print(f"  Created: {snapshot.created_at}")
            print(f"  Checksum: {snapshot.checksum}")
            # In interactive mode, would prompt for update
            updated += 1

    return updated
