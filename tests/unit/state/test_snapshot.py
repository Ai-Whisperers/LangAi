"""Tests for state snapshot functionality."""

import shutil
import tempfile
from datetime import datetime, timezone

import pytest

from company_researcher.state.snapshot import (
    SnapshotStore,
    StateSnapshot,
    create_snapshot,
    restore_snapshot,
)


class TestStateSnapshot:
    """Tests for the StateSnapshot dataclass."""

    def test_create_snapshot(self):
        """StateSnapshot should store all fields correctly."""
        snap = StateSnapshot(
            id="snap-id",
            state={"key": "value"},
            created_at=datetime.now(timezone.utc),
            checksum="abc123",
            label="test-label",
            metadata={"source": "test"},
        )
        assert snap.id == "snap-id"
        assert snap.state == {"key": "value"}
        assert snap.checksum == "abc123"
        assert snap.label == "test-label"

    def test_snapshot_immutability(self):
        """StateSnapshot should be immutable after creation."""
        snap = StateSnapshot(
            id="snap-id",
            state={"key": "value"},
            created_at=datetime.now(timezone.utc),
            checksum="abc123",
        )

        with pytest.raises(AttributeError, match="immutable"):
            snap.id = "new-id"

    def test_state_deep_copied(self):
        """StateSnapshot should deep copy the state."""
        original = {"nested": {"value": 1}}
        snap = StateSnapshot(
            id="snap-id", state=original, created_at=datetime.now(timezone.utc), checksum="abc123"
        )

        original["nested"]["value"] = 999
        assert snap.state["nested"]["value"] == 1

    def test_to_dict(self):
        """StateSnapshot.to_dict should return correct dictionary."""
        created = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        snap = StateSnapshot(
            id="snap-id",
            state={"data": 123},
            created_at=created,
            checksum="checksum123",
            label="test",
            metadata={"tag": "unit"},
        )
        result = snap.to_dict()

        assert result["id"] == "snap-id"
        assert result["state"] == {"data": 123}
        assert result["checksum"] == "checksum123"
        assert result["label"] == "test"
        assert result["created_at"] == "2024-01-15T12:00:00+00:00"

    def test_from_dict(self):
        """StateSnapshot.from_dict should reconstruct snapshot."""
        data = {
            "id": "restored-id",
            "state": {"restored": True},
            "created_at": "2024-06-01T10:30:00+00:00",
            "checksum": "chk123",
            "label": "restored",
            "metadata": {"source": "backup"},
        }
        snap = StateSnapshot.from_dict(data)

        assert snap.id == "restored-id"
        assert snap.state == {"restored": True}
        assert snap.checksum == "chk123"
        assert snap.label == "restored"
        assert isinstance(snap.created_at, datetime)

    def test_from_dict_defaults(self):
        """StateSnapshot.from_dict should handle missing fields."""
        data = {}
        snap = StateSnapshot.from_dict(data)

        assert snap.id is not None
        assert snap.state == {}
        assert snap.checksum == ""
        assert snap.label is None


class TestStateSnapshotComparison:
    """Tests for snapshot comparison functionality."""

    def test_compare_same_snapshots(self):
        """compare should identify identical snapshots."""
        snap1 = StateSnapshot(
            id="snap-1",
            state={"key": "value"},
            created_at=datetime.now(timezone.utc),
            checksum="same-checksum",
        )
        snap2 = StateSnapshot(
            id="snap-2",
            state={"key": "value"},
            created_at=datetime.now(timezone.utc),
            checksum="same-checksum",
        )

        result = snap1.compare(snap2)

        assert result["same"] is True
        assert len(result["differences"]) == 0

    def test_compare_different_snapshots(self):
        """compare should identify differences."""
        snap1 = StateSnapshot(
            id="snap-1",
            state={"key": "old"},
            created_at=datetime.now(timezone.utc),
            checksum="checksum-1",
        )
        snap2 = StateSnapshot(
            id="snap-2",
            state={"key": "new"},
            created_at=datetime.now(timezone.utc),
            checksum="checksum-2",
        )

        result = snap1.compare(snap2)

        assert result["same"] is False
        assert len(result["differences"]) == 1
        assert result["differences"][0]["type"] == "changed"
        assert result["differences"][0]["path"] == "key"

    def test_compare_added_key(self):
        """compare should detect added keys."""
        snap1 = StateSnapshot(
            id="snap-1",
            state={"original": 1},
            created_at=datetime.now(timezone.utc),
            checksum="chk1",
        )
        snap2 = StateSnapshot(
            id="snap-2",
            state={"original": 1, "added": 2},
            created_at=datetime.now(timezone.utc),
            checksum="chk2",
        )

        result = snap1.compare(snap2)

        assert result["same"] is False
        diffs = {d["path"]: d for d in result["differences"]}
        assert "added" in diffs
        assert diffs["added"]["type"] == "added"

    def test_compare_removed_key(self):
        """compare should detect removed keys."""
        snap1 = StateSnapshot(
            id="snap-1",
            state={"original": 1, "removed": 2},
            created_at=datetime.now(timezone.utc),
            checksum="chk1",
        )
        snap2 = StateSnapshot(
            id="snap-2",
            state={"original": 1},
            created_at=datetime.now(timezone.utc),
            checksum="chk2",
        )

        result = snap1.compare(snap2)

        assert result["same"] is False
        diffs = {d["path"]: d for d in result["differences"]}
        assert "removed" in diffs
        assert diffs["removed"]["type"] == "removed"

    def test_compare_nested_differences(self):
        """compare should detect nested differences."""
        snap1 = StateSnapshot(
            id="snap-1",
            state={"nested": {"inner": "old"}},
            created_at=datetime.now(timezone.utc),
            checksum="chk1",
        )
        snap2 = StateSnapshot(
            id="snap-2",
            state={"nested": {"inner": "new"}},
            created_at=datetime.now(timezone.utc),
            checksum="chk2",
        )

        result = snap1.compare(snap2)

        assert result["same"] is False
        assert any(d["path"] == "nested.inner" for d in result["differences"])


class TestSnapshotStore:
    """Tests for SnapshotStore."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)

    @pytest.fixture
    def store(self, temp_dir):
        """Create a SnapshotStore with temp storage."""
        return SnapshotStore(storage_dir=temp_dir)

    def test_create_snapshot(self, store):
        """create should create and store a snapshot."""
        state = {"company": "TestCorp"}
        snap = store.create(state, label="test")

        assert snap.state == state
        assert snap.label == "test"
        assert snap.checksum is not None
        assert snap.id is not None

    def test_checksum_consistency(self, store):
        """create should produce consistent checksums."""
        state = {"a": 1, "b": 2}
        snap1 = store.create(state)
        snap2 = store.create(state)

        assert snap1.checksum == snap2.checksum

    def test_checksum_different_for_different_states(self, store):
        """create should produce different checksums for different states."""
        snap1 = store.create({"a": 1})
        snap2 = store.create({"a": 2})

        assert snap1.checksum != snap2.checksum

    def test_load_snapshot(self, store):
        """load should retrieve a saved snapshot."""
        state = {"data": "test"}
        created = store.create(state)

        loaded = store.load(created.id)

        assert loaded is not None
        assert loaded.id == created.id
        assert loaded.state == state

    def test_load_nonexistent_returns_none(self, store):
        """load should return None for nonexistent snapshot."""
        result = store.load("nonexistent-id")
        assert result is None

    def test_restore_returns_state_copy(self, store):
        """restore should return a copy of the state."""
        state = {"value": 42}
        snap = store.create(state)

        restored = store.restore(snap.id)

        assert restored == state
        # Verify it's a copy by mutating
        restored["value"] = 100
        reloaded = store.restore(snap.id)
        assert reloaded["value"] == 42

    def test_restore_nonexistent_returns_none(self, store):
        """restore should return None for nonexistent snapshot."""
        result = store.restore("nonexistent")
        assert result is None

    def test_list_snapshots(self, store):
        """list should return all snapshots."""
        store.create({"a": 1})
        store.create({"b": 2})
        store.create({"c": 3})

        snaps = store.list()

        assert len(snaps) == 3

    def test_list_with_label_filter(self, store):
        """list should filter by label."""
        store.create({"a": 1}, label="important")
        store.create({"b": 2}, label="important")
        store.create({"c": 3}, label="other")

        important = store.list(label="important")

        assert len(important) == 2
        for snap in important:
            assert snap.label == "important"

    def test_list_sorted_by_time(self, store):
        """list should return newest first."""
        store.create({"order": 1})
        store.create({"order": 2})
        store.create({"order": 3})

        snaps = store.list()

        for i in range(len(snaps) - 1):
            assert snaps[i].created_at >= snaps[i + 1].created_at

    def test_list_respects_limit(self, store):
        """list should respect limit parameter."""
        for i in range(5):
            store.create({"i": i})

        snaps = store.list(limit=3)

        assert len(snaps) == 3

    def test_get_by_label(self, store):
        """get_by_label should return latest with label."""
        store.create({"first": True}, label="target")
        store.create({"latest": True}, label="target")

        result = store.get_by_label("target")

        assert result is not None
        assert result.label == "target"
        assert result.state["latest"] is True

    def test_get_by_label_nonexistent(self, store):
        """get_by_label should return None for nonexistent label."""
        result = store.get_by_label("nonexistent")
        assert result is None

    def test_delete_snapshot(self, store):
        """delete should remove snapshot."""
        snap = store.create({"to_delete": True})

        deleted = store.delete(snap.id)

        assert deleted is True
        assert store.load(snap.id) is None

    def test_delete_nonexistent(self, store):
        """delete should return False for nonexistent snapshot."""
        result = store.delete("nonexistent")
        assert result is False

    def test_compare_snapshots(self, store):
        """compare should compare two snapshots."""
        snap1 = store.create({"value": "old"})
        snap2 = store.create({"value": "new"})

        result = store.compare(snap1.id, snap2.id)

        assert result is not None
        assert result["same"] is False

    def test_compare_with_nonexistent(self, store):
        """compare should return None if snapshot doesn't exist."""
        snap = store.create({"value": 1})

        result = store.compare(snap.id, "nonexistent")

        assert result is None

    def test_cleanup_old(self, store):
        """cleanup_old should keep only most recent snapshots."""
        for i in range(5):
            store.create({"i": i})

        deleted = store.cleanup_old(keep_count=2)

        assert deleted == 3
        assert len(store.list()) == 2


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)

    def test_create_snapshot_function(self, temp_dir):
        """create_snapshot should create a snapshot."""
        state = {"test": "data"}
        snap = create_snapshot(state, label="test", storage_dir=temp_dir)

        assert snap.state == state
        assert snap.label == "test"

    def test_restore_snapshot_function(self, temp_dir):
        """restore_snapshot should restore state."""
        state = {"restore": "test"}
        snap = create_snapshot(state, storage_dir=temp_dir)

        restored = restore_snapshot(snap.id, storage_dir=temp_dir)

        assert restored == state
