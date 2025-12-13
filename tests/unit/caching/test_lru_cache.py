"""Tests for LRU cache implementation."""

import pytest
import threading
import time
from unittest.mock import MagicMock

from company_researcher.caching.lru_cache import (
    LRUCache,
    LRUCacheConfig,
    CacheItem,
    create_lru_cache,
)


class TestLRUCacheConfig:
    """Tests for LRUCacheConfig."""

    def test_default_config(self):
        """LRUCacheConfig should have sensible defaults."""
        config = LRUCacheConfig()
        assert config.max_size == 1000
        assert config.max_memory_mb is None
        assert config.on_evict is None

    def test_custom_config(self):
        """LRUCacheConfig should accept custom values."""
        callback = MagicMock()
        config = LRUCacheConfig(
            max_size=500,
            max_memory_mb=10.0,
            on_evict=callback
        )
        assert config.max_size == 500
        assert config.max_memory_mb == 10.0
        assert config.on_evict is callback


class TestCacheItem:
    """Tests for CacheItem dataclass."""

    def test_cache_item_stores_value(self):
        """CacheItem should store value and metadata."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        item = CacheItem(
            value="test_value",
            created_at=now,
            last_accessed=now,
            access_count=1,
            size_bytes=100
        )
        assert item.value == "test_value"
        assert item.access_count == 1
        assert item.size_bytes == 100


class TestLRUCache:
    """Tests for LRUCache."""

    @pytest.fixture
    def cache(self):
        """Create a default LRU cache."""
        return LRUCache()

    @pytest.fixture
    def small_cache(self):
        """Create a small LRU cache for eviction tests."""
        config = LRUCacheConfig(max_size=3)
        return LRUCache(config)

    def test_put_and_get(self, cache):
        """Cache should store and retrieve values."""
        cache.put("key1", "value1")
        result = cache.get("key1")
        assert result == "value1"

    def test_get_missing_returns_none(self, cache):
        """get should return None for missing keys."""
        result = cache.get("nonexistent")
        assert result is None

    def test_get_missing_returns_default(self, cache):
        """get should return default for missing keys."""
        result = cache.get("nonexistent", default="fallback")
        assert result == "fallback"

    def test_contains(self, cache):
        """Cache should support __contains__ check."""
        cache.put("key1", "value1")
        assert "key1" in cache
        assert "key2" not in cache

    def test_len(self, cache):
        """Cache should report correct length."""
        assert len(cache) == 0
        cache.put("key1", "value1")
        assert len(cache) == 1
        cache.put("key2", "value2")
        assert len(cache) == 2

    def test_delete(self, cache):
        """delete should remove items from cache."""
        cache.put("key1", "value1")
        assert "key1" in cache

        deleted = cache.delete("key1")

        assert deleted is True
        assert "key1" not in cache

    def test_delete_nonexistent(self, cache):
        """delete should return False for nonexistent keys."""
        result = cache.delete("nonexistent")
        assert result is False

    def test_clear(self, cache):
        """clear should remove all items."""
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        assert len(cache) == 2

        cache.clear()

        assert len(cache) == 0

    def test_lru_eviction(self, small_cache):
        """Cache should evict least recently used items."""
        small_cache.put("a", 1)
        small_cache.put("b", 2)
        small_cache.put("c", 3)

        # Access 'a' to make it most recently used
        small_cache.get("a")

        # Add 'd' which should evict 'b' (least recently used)
        small_cache.put("d", 4)

        assert "a" in small_cache  # Accessed, should remain
        assert "b" not in small_cache  # Should be evicted
        assert "c" in small_cache
        assert "d" in small_cache

    def test_update_existing_key(self, cache):
        """Updating existing key should replace value."""
        cache.put("key1", "original")
        cache.put("key1", "updated")

        result = cache.get("key1")

        assert result == "updated"
        assert len(cache) == 1

    def test_get_updates_access_order(self, small_cache):
        """get should update access order for LRU."""
        small_cache.put("a", 1)
        small_cache.put("b", 2)
        small_cache.put("c", 3)

        # Access 'a' multiple times
        small_cache.get("a")
        small_cache.get("a")

        # Add new item, should evict 'b'
        small_cache.put("d", 4)

        assert "a" in small_cache
        assert "b" not in small_cache

    def test_eviction_callback(self):
        """Eviction callback should be called on eviction."""
        callback = MagicMock()
        config = LRUCacheConfig(max_size=2, on_evict=callback)
        cache = LRUCache(config)

        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # Should evict 'a'

        callback.assert_called_once_with("a", 1)

    def test_get_stats(self, cache):
        """get_stats should return cache statistics."""
        cache.put("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("missing")  # Miss

        stats = cache.get_stats()

        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == pytest.approx(0.5)

    def test_get_keys(self, cache):
        """get_keys should return all cache keys."""
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)

        keys = cache.get_keys()

        assert set(keys) == {"a", "b", "c"}

    def test_get_item_info(self, cache):
        """get_item_info should return item metadata."""
        cache.put("key1", "value1")
        cache.get("key1")

        info = cache.get_item_info("key1")

        assert info is not None
        assert "created_at" in info
        assert "last_accessed" in info
        assert info["access_count"] == 2  # put + get

    def test_get_item_info_nonexistent(self, cache):
        """get_item_info should return None for missing key."""
        result = cache.get_item_info("nonexistent")
        assert result is None


class TestLRUCacheThreadSafety:
    """Tests for thread safety of LRU cache."""

    def test_concurrent_puts(self):
        """Cache should handle concurrent puts safely."""
        cache = LRUCache()
        errors = []

        def put_items(prefix, count):
            try:
                for i in range(count):
                    cache.put(f"{prefix}_{i}", i)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=put_items, args=(f"t{i}", 100))
            for i in range(5)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(cache) == 500

    def test_concurrent_reads_writes(self):
        """Cache should handle concurrent reads and writes."""
        cache = LRUCache()
        errors = []

        for i in range(100):
            cache.put(f"key_{i}", i)

        def reader():
            try:
                for _ in range(100):
                    cache.get(f"key_{_ % 100}")
            except Exception as e:
                errors.append(e)

        def writer():
            try:
                for i in range(100):
                    cache.put(f"new_key_{i}", i)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=reader) for _ in range(3)
        ] + [
            threading.Thread(target=writer) for _ in range(2)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestLRUCacheMemoryLimit:
    """Tests for memory-limited LRU cache."""

    def test_memory_limit_eviction(self):
        """Cache should evict items when memory limit exceeded."""
        config = LRUCacheConfig(max_size=1000, max_memory_mb=0.001)  # 1KB
        cache = LRUCache(config)

        # Add items that exceed memory limit
        for i in range(100):
            cache.put(f"key_{i}", "x" * 100)  # ~100 bytes each

        # Should have evicted some items
        assert len(cache) < 100


class TestCreateLruCache:
    """Tests for create_lru_cache factory function."""

    def test_create_with_defaults(self):
        """create_lru_cache should create cache with defaults."""
        cache = create_lru_cache()
        assert isinstance(cache, LRUCache)
        assert cache._config.max_size == 1000

    def test_create_with_custom_size(self):
        """create_lru_cache should accept custom max_size."""
        cache = create_lru_cache(max_size=500)
        assert cache._config.max_size == 500

    def test_create_with_memory_limit(self):
        """create_lru_cache should accept memory limit."""
        cache = create_lru_cache(max_memory_mb=50.0)
        assert cache._config.max_memory_mb == 50.0

    def test_create_with_callback(self):
        """create_lru_cache should accept eviction callback."""
        callback = MagicMock()
        cache = create_lru_cache(on_evict=callback)
        assert cache._config.on_evict is callback
