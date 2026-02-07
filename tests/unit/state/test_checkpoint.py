"""Tests for state checkpointing functionality."""

import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from company_researcher.state.checkpoint import (
    Checkpoint,
    CheckpointManager,
    create_checkpoint,
    list_checkpoints,
    restore_checkpoint,
)


class TestCheckpoint:
    """Tests for the Checkpoint dataclass."""

    def test_create_checkpoint(self):
        """Checkpoint should store all fields correctly."""
        cp = Checkpoint(
            id="test-id",
            thread_id="thread-123",
            state={"key": "value"},
            created_at=datetime.now(timezone.utc),
            metadata={"source": "test"},
            step=5,
            parent_id="parent-id",
        )
        assert cp.id == "test-id"
        assert cp.thread_id == "thread-123"
        assert cp.state == {"key": "value"}
        assert cp.step == 5
        assert cp.parent_id == "parent-id"

    def test_to_dict(self):
        """Checkpoint.to_dict should return correct dictionary."""
        created = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        cp = Checkpoint(
            id="test-id",
            thread_id="thread-123",
            state={"data": 123},
            created_at=created,
            metadata={"tag": "test"},
            step=2,
            parent_id=None,
        )
        result = cp.to_dict()

        assert result["id"] == "test-id"
        assert result["thread_id"] == "thread-123"
        assert result["state"] == {"data": 123}
        assert result["created_at"] == "2024-01-15T12:00:00+00:00"
        assert result["metadata"] == {"tag": "test"}
        assert result["step"] == 2
        assert result["parent_id"] is None

    def test_from_dict(self):
        """Checkpoint.from_dict should reconstruct checkpoint."""
        data = {
            "id": "restored-id",
            "thread_id": "thread-abc",
            "state": {"restored": True},
            "created_at": "2024-06-01T10:30:00+00:00",
            "metadata": {"source": "backup"},
            "step": 10,
            "parent_id": "prev-id",
        }
        cp = Checkpoint.from_dict(data)

        assert cp.id == "restored-id"
        assert cp.thread_id == "thread-abc"
        assert cp.state == {"restored": True}
        assert cp.step == 10
        assert cp.parent_id == "prev-id"
        assert isinstance(cp.created_at, datetime)

    def test_from_dict_defaults(self):
        """Checkpoint.from_dict should handle missing fields with defaults."""
        data = {}
        cp = Checkpoint.from_dict(data)

        assert cp.id is not None  # Generated UUID
        assert cp.thread_id == ""
        assert cp.state == {}
        assert cp.step == 0
        assert cp.parent_id is None


class TestCheckpointManager:
    """Tests for CheckpointManager."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)

    @pytest.fixture
    def manager(self, temp_dir):
        """Create a CheckpointManager with temp storage."""
        return CheckpointManager(storage_dir=temp_dir)

    def test_create_checkpoint(self, manager):
        """create should create and store a checkpoint."""
        state = {"company": "TestCorp", "revenue": 1000000}
        cp = manager.create(thread_id="thread-1", state=state, step=1, metadata={"source": "test"})

        assert cp.thread_id == "thread-1"
        assert cp.state == state
        assert cp.step == 1
        assert cp.metadata == {"source": "test"}
        assert cp.id is not None

    def test_create_copies_state(self, manager):
        """create should copy state to avoid mutation."""
        state = {"key": "original"}
        cp = manager.create("thread-1", state)

        state["key"] = "mutated"
        assert cp.state["key"] == "original"

    def test_load_checkpoint(self, manager):
        """load should retrieve a saved checkpoint."""
        state = {"data": "test"}
        created = manager.create("thread-1", state)

        loaded = manager.load(created.id)

        assert loaded is not None
        assert loaded.id == created.id
        assert loaded.state == state

    def test_load_from_cache(self, manager):
        """load should use cache when available."""
        cp = manager.create("thread-1", {"cached": True})

        # Load twice - second should come from cache
        loaded1 = manager.load(cp.id)
        loaded2 = manager.load(cp.id)

        assert loaded1 is loaded2  # Same object from cache

    def test_load_nonexistent_returns_none(self, manager):
        """load should return None for nonexistent checkpoint."""
        result = manager.load("nonexistent-id")
        assert result is None

    def test_restore_returns_state_copy(self, manager):
        """restore should return a copy of the state."""
        state = {"value": 42}
        cp = manager.create("thread-1", state)

        restored = manager.restore(cp.id)

        assert restored == state
        restored["value"] = 100
        assert cp.state["value"] == 42  # Original unchanged

    def test_restore_nonexistent_returns_none(self, manager):
        """restore should return None for nonexistent checkpoint."""
        result = manager.restore("nonexistent")
        assert result is None

    def test_list_for_thread(self, manager):
        """list_for_thread should return checkpoints for thread."""
        manager.create("thread-1", {"cp": 1})
        manager.create("thread-1", {"cp": 2})
        manager.create("thread-2", {"cp": 3})

        thread1_cps = manager.list_for_thread("thread-1")

        assert len(thread1_cps) == 2
        for cp in thread1_cps:
            assert cp.thread_id == "thread-1"

    def test_list_for_thread_sorted_by_time(self, manager):
        """list_for_thread should return newest first."""
        cp1 = manager.create("thread-1", {"order": 1})
        cp2 = manager.create("thread-1", {"order": 2})

        cps = manager.list_for_thread("thread-1")

        assert cps[0].created_at >= cps[1].created_at

    def test_list_for_thread_respects_limit(self, manager):
        """list_for_thread should respect limit parameter."""
        for i in range(5):
            manager.create("thread-1", {"i": i})

        cps = manager.list_for_thread("thread-1", limit=3)

        assert len(cps) == 3

    def test_list_for_nonexistent_thread(self, manager):
        """list_for_thread should return empty list for nonexistent thread."""
        result = manager.list_for_thread("nonexistent")
        assert result == []

    def test_get_latest(self, manager):
        """get_latest should return most recent checkpoint."""
        manager.create("thread-1", {"first": True})
        manager.create("thread-1", {"second": True})
        latest = manager.create("thread-1", {"latest": True})

        result = manager.get_latest("thread-1")

        assert result is not None
        assert result.state == {"latest": True}

    def test_get_latest_nonexistent(self, manager):
        """get_latest should return None for nonexistent thread."""
        result = manager.get_latest("nonexistent")
        assert result is None

    def test_delete_checkpoint(self, manager):
        """delete should remove checkpoint."""
        cp = manager.create("thread-1", {"to_delete": True})

        deleted = manager.delete(cp.id)

        assert deleted is True
        assert manager.load(cp.id) is None

    def test_delete_nonexistent(self, manager):
        """delete should return False for nonexistent checkpoint."""
        result = manager.delete("nonexistent")
        assert result is False

    def test_delete_thread(self, manager):
        """delete_thread should remove all checkpoints for thread."""
        manager.create("thread-1", {"cp": 1})
        manager.create("thread-1", {"cp": 2})
        manager.create("thread-2", {"cp": 3})

        count = manager.delete_thread("thread-1")

        assert count == 2
        assert len(manager.list_for_thread("thread-1")) == 0
        assert len(manager.list_for_thread("thread-2")) == 1

    def test_cleanup_old(self, manager):
        """cleanup_old should keep only most recent checkpoints."""
        for i in range(5):
            manager.create("thread-1", {"i": i})

        deleted = manager.cleanup_old("thread-1", keep_count=2)

        assert deleted == 3
        assert len(manager.list_for_thread("thread-1")) == 2

    def test_cleanup_old_no_action_if_under_limit(self, manager):
        """cleanup_old should do nothing if under keep_count."""
        manager.create("thread-1", {"only": True})

        deleted = manager.cleanup_old("thread-1", keep_count=10)

        assert deleted == 0
        assert len(manager.list_for_thread("thread-1")) == 1


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)

    def test_create_checkpoint_function(self, temp_dir):
        """create_checkpoint should create a checkpoint."""
        state = {"test": "data"}
        cp = create_checkpoint("thread-1", state, storage_dir=temp_dir)

        assert cp.state == state
        assert cp.thread_id == "thread-1"

    def test_restore_checkpoint_function(self, temp_dir):
        """restore_checkpoint should restore state."""
        state = {"restore": "test"}
        cp = create_checkpoint("thread-1", state, storage_dir=temp_dir)

        restored = restore_checkpoint(cp.id, storage_dir=temp_dir)

        assert restored == state

    def test_list_checkpoints_function(self, temp_dir):
        """list_checkpoints should list checkpoints."""
        create_checkpoint("thread-1", {"a": 1}, storage_dir=temp_dir)
        create_checkpoint("thread-1", {"b": 2}, storage_dir=temp_dir)

        cps = list_checkpoints("thread-1", storage_dir=temp_dir)

        assert len(cps) == 2
