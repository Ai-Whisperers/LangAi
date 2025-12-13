"""
State Checkpointing - Save and restore workflow state.

Provides:
- Checkpoint creation
- Checkpoint restoration
- Checkpoint management
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..utils import utc_now


@dataclass
class Checkpoint:
    """A saved checkpoint of workflow state."""
    id: str
    thread_id: str
    state: Dict[str, Any]
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    step: int = 0
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "thread_id": self.thread_id,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
            "step": self.step,
            "parent_id": self.parent_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Checkpoint":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = utc_now()

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            thread_id=data.get("thread_id", ""),
            state=data.get("state", {}),
            created_at=created_at,
            metadata=data.get("metadata", {}),
            step=data.get("step", 0),
            parent_id=data.get("parent_id")
        )


class CheckpointManager:
    """
    Manage workflow checkpoints.

    Usage:
        manager = CheckpointManager("checkpoints/")

        # Create checkpoint
        checkpoint = manager.create(thread_id, state)

        # List checkpoints for thread
        checkpoints = manager.list_for_thread(thread_id)

        # Restore checkpoint
        state = manager.restore(checkpoint_id)
    """

    def __init__(self, storage_dir: str = "checkpoints"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._checkpoints: Dict[str, Checkpoint] = {}

    def create(
        self,
        thread_id: str,
        state: Dict[str, Any],
        step: int = 0,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Checkpoint:
        """
        Create a new checkpoint.

        Args:
            thread_id: Thread identifier
            state: State to checkpoint
            step: Step number
            parent_id: Parent checkpoint ID
            metadata: Optional metadata

        Returns:
            Created Checkpoint
        """
        checkpoint = Checkpoint(
            id=str(uuid.uuid4()),
            thread_id=thread_id,
            state=state.copy(),
            created_at=utc_now(),
            metadata=metadata or {},
            step=step,
            parent_id=parent_id
        )

        # Save to storage
        self._save_checkpoint(checkpoint)
        self._checkpoints[checkpoint.id] = checkpoint

        return checkpoint

    def _save_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Save checkpoint to storage."""
        thread_dir = self.storage_dir / checkpoint.thread_id
        thread_dir.mkdir(parents=True, exist_ok=True)

        filepath = thread_dir / f"{checkpoint.id}.json"
        with open(filepath, 'w') as f:
            json.dump(checkpoint.to_dict(), f, indent=2, default=str)

    def load(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Load a checkpoint by ID."""
        # Check cache
        if checkpoint_id in self._checkpoints:
            return self._checkpoints[checkpoint_id]

        # Search storage
        for filepath in self.storage_dir.glob(f"*/{checkpoint_id}.json"):
            with open(filepath, 'r') as f:
                data = json.load(f)
            checkpoint = Checkpoint.from_dict(data)
            self._checkpoints[checkpoint_id] = checkpoint
            return checkpoint

        return None

    def restore(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Restore state from a checkpoint.

        Args:
            checkpoint_id: Checkpoint ID

        Returns:
            Restored state or None
        """
        checkpoint = self.load(checkpoint_id)
        if checkpoint:
            return checkpoint.state.copy()
        return None

    def list_for_thread(
        self,
        thread_id: str,
        limit: int = 100
    ) -> List[Checkpoint]:
        """
        List checkpoints for a thread.

        Args:
            thread_id: Thread identifier
            limit: Maximum number to return

        Returns:
            List of checkpoints, newest first
        """
        thread_dir = self.storage_dir / thread_id
        if not thread_dir.exists():
            return []

        checkpoints = []
        for filepath in thread_dir.glob("*.json"):
            with open(filepath, 'r') as f:
                data = json.load(f)
            checkpoints.append(Checkpoint.from_dict(data))

        # Sort by created_at descending
        checkpoints.sort(key=lambda c: c.created_at, reverse=True)
        return checkpoints[:limit]

    def get_latest(self, thread_id: str) -> Optional[Checkpoint]:
        """Get the latest checkpoint for a thread."""
        checkpoints = self.list_for_thread(thread_id, limit=1)
        return checkpoints[0] if checkpoints else None

    def delete(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint."""
        for filepath in self.storage_dir.glob(f"*/{checkpoint_id}.json"):
            filepath.unlink()
            self._checkpoints.pop(checkpoint_id, None)
            return True
        return False

    def delete_thread(self, thread_id: str) -> int:
        """Delete all checkpoints for a thread."""
        thread_dir = self.storage_dir / thread_id
        if not thread_dir.exists():
            return 0

        count = 0
        for filepath in thread_dir.glob("*.json"):
            checkpoint_id = filepath.stem
            filepath.unlink()
            self._checkpoints.pop(checkpoint_id, None)
            count += 1

        # Remove directory if empty
        if not any(thread_dir.iterdir()):
            thread_dir.rmdir()

        return count

    def cleanup_old(
        self,
        thread_id: str,
        keep_count: int = 10
    ) -> int:
        """
        Cleanup old checkpoints, keeping only the most recent.

        Args:
            thread_id: Thread identifier
            keep_count: Number of checkpoints to keep

        Returns:
            Number of checkpoints deleted
        """
        checkpoints = self.list_for_thread(thread_id, limit=1000)
        if len(checkpoints) <= keep_count:
            return 0

        deleted = 0
        for checkpoint in checkpoints[keep_count:]:
            if self.delete(checkpoint.id):
                deleted += 1

        return deleted


# Convenience functions
def create_checkpoint(
    thread_id: str,
    state: Dict[str, Any],
    storage_dir: str = "checkpoints",
    **kwargs
) -> Checkpoint:
    """Create a checkpoint."""
    manager = CheckpointManager(storage_dir)
    return manager.create(thread_id, state, **kwargs)


def restore_checkpoint(
    checkpoint_id: str,
    storage_dir: str = "checkpoints"
) -> Optional[Dict[str, Any]]:
    """Restore state from checkpoint."""
    manager = CheckpointManager(storage_dir)
    return manager.restore(checkpoint_id)


def list_checkpoints(
    thread_id: str,
    storage_dir: str = "checkpoints",
    limit: int = 100
) -> List[Checkpoint]:
    """List checkpoints for a thread."""
    manager = CheckpointManager(storage_dir)
    return manager.list_for_thread(thread_id, limit)
