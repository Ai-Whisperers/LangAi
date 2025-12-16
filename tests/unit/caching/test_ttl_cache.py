"""Tests for TTL cache implementation."""

import threading
import time
from unittest.mock import MagicMock

import pytest

from company_researcher.caching.ttl_cache import (
    TTLCache,
    TTLCacheConfig,
    TTLCacheItem,
    create_ttl_cache,
)


class TestTTLCacheConfig:
    """Tests for TTLCacheConfig."""

    def test_default_config(self):
        """TTLCacheConfig should have sensible defaults."""
        config = TTLCacheConfig()
        assert config.default_ttl == 300.0
        assert config.max_size == 10000
        assert config.cleanup_interval == 60.0
        assert config.sliding_expiration is False
        assert config.on_expire is None

    def test_custom_config(self):
        """TTLCacheConfig should accept custom values."""
        callback = MagicMock()
        config = TTLCacheConfig(
            default_ttl=60.0,
            max_size=1000,
            cleanup_interval=30.0,
            sliding_expiration=True,
            on_expire=callback,
        )
        assert config.default_ttl == 60.0
        assert config.max_size == 1000
        assert config.sliding_expiration is True
        assert config.on_expire is callback


class TestTTLCacheItem:
    """Tests for TTLCacheItem dataclass."""

    def test_cache_item_stores_value(self):
        """TTLCacheItem should store value and metadata."""
        now = time.time()
        item = TTLCacheItem(
            value="test_value",
            created_at=now,
            expires_at=now + 300,
            ttl=300,
            access_count=1,
            last_accessed=now,
        )
        assert item.value == "test_value"
        assert item.ttl == 300
        assert item.access_count == 1


class TestTTLCache:
    """Tests for TTLCache."""

    @pytest.fixture
    def cache(self):
        """Create a default TTL cache."""
        return TTLCache()

    @pytest.fixture
    def short_ttl_cache(self):
        """Create a cache with short TTL for expiration tests."""
        config = TTLCacheConfig(default_ttl=0.1)  # 100ms
        return TTLCache(config)

    @pytest.fixture
    def small_cache(self):
        """Create a small cache for eviction tests."""
        config = TTLCacheConfig(max_size=3)
        return TTLCache(config)

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

    def test_custom_ttl(self, cache):
        """put should accept custom TTL."""
        cache.put("key1", "value1", ttl=1.0)
        assert cache.get("key1") == "value1"

    def test_expiration(self, short_ttl_cache):
        """Items should expire after TTL."""
        short_ttl_cache.put("key1", "value1")
        assert short_ttl_cache.get("key1") == "value1"

        time.sleep(0.15)  # Wait for expiration

        assert short_ttl_cache.get("key1") is None

    def test_contains_checks_expiration(self, short_ttl_cache):
        """__contains__ should check expiration."""
        short_ttl_cache.put("key1", "value1")
        assert "key1" in short_ttl_cache

        time.sleep(0.15)

        assert "key1" not in short_ttl_cache

    def test_len_excludes_expired(self, short_ttl_cache):
        """__len__ should exclude expired items."""
        short_ttl_cache.put("key1", "value1")
        short_ttl_cache.put("key2", "value2", ttl=1.0)  # Longer TTL
        assert len(short_ttl_cache) == 2

        time.sleep(0.15)

        # key1 expired, key2 still valid
        assert len(short_ttl_cache) == 1

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

        cache.clear()

        assert len(cache) == 0

    def test_get_with_ttl(self, cache):
        """get_with_ttl should return value and remaining TTL."""
        cache.put("key1", "value1", ttl=10.0)

        value, remaining = cache.get_with_ttl("key1")

        assert value == "value1"
        assert remaining is not None
        assert 9.0 < remaining <= 10.0

    def test_get_with_ttl_missing(self, cache):
        """get_with_ttl should return None for missing keys."""
        value, remaining = cache.get_with_ttl("nonexistent")
        assert value is None
        assert remaining is None

    def test_refresh_ttl(self, cache):
        """refresh should extend item TTL."""
        cache.put("key1", "value1", ttl=1.0)
        time.sleep(0.5)

        refreshed = cache.refresh("key1", ttl=5.0)

        assert refreshed is True
        value, remaining = cache.get_with_ttl("key1")
        assert remaining > 4.0

    def test_refresh_nonexistent(self, cache):
        """refresh should return False for nonexistent keys."""
        result = cache.refresh("nonexistent")
        assert result is False

    def test_refresh_expired(self, short_ttl_cache):
        """refresh should return False for expired keys."""
        short_ttl_cache.put("key1", "value1")
        time.sleep(0.15)

        result = short_ttl_cache.refresh("key1")
        assert result is False

    def test_cleanup(self, short_ttl_cache):
        """cleanup should remove expired items."""
        short_ttl_cache.put("key1", "value1")
        short_ttl_cache.put("key2", "value2", ttl=1.0)
        time.sleep(0.15)

        removed = short_ttl_cache.cleanup()

        assert removed == 1  # Only key1 expired
        assert "key1" not in short_ttl_cache
        assert "key2" in short_ttl_cache

    def test_max_size_eviction(self, small_cache):
        """Cache should evict when max size reached."""
        small_cache.put("a", 1)
        small_cache.put("b", 2)
        small_cache.put("c", 3)
        small_cache.put("d", 4)  # Should evict oldest

        assert len(small_cache) <= 3

    def test_expiration_callback(self):
        """Expiration callback should be called on expiration."""
        callback = MagicMock()
        config = TTLCacheConfig(default_ttl=0.1, on_expire=callback)
        cache = TTLCache(config)

        cache.put("key1", "value1")
        time.sleep(0.15)
        cache.get("key1")  # Trigger expiration check

        callback.assert_called_once_with("key1", "value1")

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
        """get_keys should return non-expired keys."""
        cache.put("a", 1, ttl=10.0)
        cache.put("b", 2, ttl=10.0)

        keys = cache.get_keys()

        assert set(keys) == {"a", "b"}


class TestTTLCacheSlidingExpiration:
    """Tests for sliding expiration functionality."""

    @pytest.fixture
    def sliding_cache(self):
        """Create cache with sliding expiration."""
        config = TTLCacheConfig(default_ttl=0.2, sliding_expiration=True)  # 200ms
        return TTLCache(config)

    def test_sliding_expiration_extends_ttl(self, sliding_cache):
        """Access should extend TTL with sliding expiration."""
        sliding_cache.put("key1", "value1")

        # Access multiple times
        for _ in range(3):
            time.sleep(0.1)  # 100ms
            value = sliding_cache.get("key1")
            assert value == "value1"

        # Total time > original TTL, but item should still be valid
        assert "key1" in sliding_cache


class TestTTLCacheThreadSafety:
    """Tests for thread safety of TTL cache."""

    def test_concurrent_puts(self):
        """Cache should handle concurrent puts safely."""
        cache = TTLCache()
        errors = []

        def put_items(prefix, count):
            try:
                for i in range(count):
                    cache.put(f"{prefix}_{i}", i)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=put_items, args=(f"t{i}", 100)) for i in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0

    def test_concurrent_reads_writes(self):
        """Cache should handle concurrent reads and writes."""
        cache = TTLCache()
        errors = []

        for i in range(100):
            cache.put(f"key_{i}", i, ttl=10.0)

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

        threads = [threading.Thread(target=reader) for _ in range(3)] + [
            threading.Thread(target=writer) for _ in range(2)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestCreateTtlCache:
    """Tests for create_ttl_cache factory function."""

    def test_create_with_defaults(self):
        """create_ttl_cache should create cache with defaults."""
        cache = create_ttl_cache()
        assert isinstance(cache, TTLCache)
        assert cache._config.default_ttl == 300.0

    def test_create_with_custom_ttl(self):
        """create_ttl_cache should accept custom TTL."""
        cache = create_ttl_cache(default_ttl=60.0)
        assert cache._config.default_ttl == 60.0

    def test_create_with_sliding_expiration(self):
        """create_ttl_cache should accept sliding expiration."""
        cache = create_ttl_cache(sliding_expiration=True)
        assert cache._config.sliding_expiration is True

    def test_create_with_callback(self):
        """create_ttl_cache should accept expiration callback."""
        callback = MagicMock()
        cache = create_ttl_cache(on_expire=callback)
        assert cache._config.on_expire is callback
