"""
Redis Cache - Distributed caching with Redis.

Provides:
- Distributed cache across multiple instances
- Persistence options
- Pub/sub for cache invalidation
- Connection pooling
"""

import json
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, TypeVar
from ..utils import get_logger, utc_now

logger = get_logger(__name__)

K = TypeVar('K')
V = TypeVar('V')


@dataclass
class RedisCacheConfig:
    """Configuration for Redis cache."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    prefix: str = "company_researcher:"
    default_ttl: int = 3600  # seconds
    max_connections: int = 10
    socket_timeout: float = 5.0
    retry_on_timeout: bool = True
    decode_responses: bool = True


class RedisCache(Generic[K, V]):
    """
    Redis-based distributed cache.

    Usage:
        cache = RedisCache(RedisCacheConfig(host="localhost"))
        await cache.connect()

        # Store value
        await cache.put("key1", {"data": "value"})

        # Get value
        value = await cache.get("key1")

        # Store with custom TTL
        await cache.put("key2", "value", ttl=60)

        await cache.disconnect()

    Note: Requires redis-py package (pip install redis)
    """

    def __init__(self, config: Optional[RedisCacheConfig] = None):
        self._config = config or RedisCacheConfig()
        self._redis: Optional[Any] = None
        self._connected = False
        self._hits = 0
        self._misses = 0

    async def connect(self) -> bool:
        """
        Connect to Redis server.

        Returns:
            True if connected successfully
        """
        try:
            import redis.asyncio as redis

            self._redis = redis.Redis(
                host=self._config.host,
                port=self._config.port,
                db=self._config.db,
                password=self._config.password,
                socket_timeout=self._config.socket_timeout,
                retry_on_timeout=self._config.retry_on_timeout,
                decode_responses=self._config.decode_responses,
                max_connections=self._config.max_connections
            )

            # Test connection
            await self._redis.ping()
            self._connected = True
            return True

        except ImportError:
            raise ImportError(
                "Redis package not installed. Install with: pip install redis"
            )
        except Exception as e:
            self._connected = False
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    async def disconnect(self) -> None:
        """Disconnect from Redis server."""
        if self._redis:
            await self._redis.close()
            self._connected = False

    def _make_key(self, key: K) -> str:
        """Create prefixed Redis key."""
        if isinstance(key, str):
            return f"{self._config.prefix}{key}"
        else:
            # Hash complex keys
            key_str = json.dumps(key, sort_keys=True, default=str)
            key_hash = hashlib.md5(key_str.encode()).hexdigest()
            return f"{self._config.prefix}{key_hash}"

    def _serialize(self, value: V) -> str:
        """Serialize value for storage."""
        return json.dumps({
            "value": value,
            "stored_at": utc_now().isoformat(),
            "type": type(value).__name__
        }, default=str)

    def _deserialize(self, data: str) -> V:
        """Deserialize stored value."""
        parsed = json.loads(data)
        return parsed.get("value")

    async def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """
        Get value from Redis.

        Args:
            key: Cache key
            default: Default if not found

        Returns:
            Cached value or default
        """
        if not self._connected:
            return default

        redis_key = self._make_key(key)

        try:
            data = await self._redis.get(redis_key)
            if data:
                self._hits += 1
                return self._deserialize(data)
            else:
                self._misses += 1
                return default
        except Exception:
            self._misses += 1
            return default

    async def put(
        self,
        key: K,
        value: V,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Put value into Redis.

        Args:
            key: Cache key
            value: Value to store
            ttl: Time-to-live in seconds

        Returns:
            True if stored successfully
        """
        if not self._connected:
            return False

        redis_key = self._make_key(key)
        actual_ttl = ttl if ttl is not None else self._config.default_ttl

        try:
            data = self._serialize(value)
            await self._redis.setex(redis_key, actual_ttl, data)
            return True
        except Exception:
            return False

    async def delete(self, key: K) -> bool:
        """Delete key from Redis."""
        if not self._connected:
            return False

        redis_key = self._make_key(key)

        try:
            result = await self._redis.delete(redis_key)
            return result > 0
        except Exception:
            return False

    async def exists(self, key: K) -> bool:
        """Check if key exists in Redis."""
        if not self._connected:
            return False

        redis_key = self._make_key(key)

        try:
            return await self._redis.exists(redis_key) > 0
        except Exception:
            return False

    async def get_ttl(self, key: K) -> Optional[int]:
        """Get remaining TTL for a key."""
        if not self._connected:
            return None

        redis_key = self._make_key(key)

        try:
            ttl = await self._redis.ttl(redis_key)
            return ttl if ttl > 0 else None
        except Exception:
            return None

    async def refresh_ttl(self, key: K, ttl: Optional[int] = None) -> bool:
        """Refresh TTL for a key."""
        if not self._connected:
            return False

        redis_key = self._make_key(key)
        actual_ttl = ttl if ttl is not None else self._config.default_ttl

        try:
            return await self._redis.expire(redis_key, actual_ttl)
        except Exception:
            return False

    async def get_many(self, keys: List[K]) -> Dict[K, Optional[V]]:
        """Get multiple values at once."""
        if not self._connected:
            return {k: None for k in keys}

        redis_keys = [self._make_key(k) for k in keys]

        try:
            values = await self._redis.mget(redis_keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    self._hits += 1
                    result[key] = self._deserialize(value)
                else:
                    self._misses += 1
                    result[key] = None
            return result
        except Exception:
            return {k: None for k in keys}

    async def put_many(
        self,
        items: Dict[K, V],
        ttl: Optional[int] = None
    ) -> bool:
        """Put multiple values at once."""
        if not self._connected:
            return False

        actual_ttl = ttl if ttl is not None else self._config.default_ttl

        try:
            pipe = self._redis.pipeline()
            for key, value in items.items():
                redis_key = self._make_key(key)
                data = self._serialize(value)
                pipe.setex(redis_key, actual_ttl, data)
            await pipe.execute()
            return True
        except Exception:
            return False

    async def delete_many(self, keys: List[K]) -> int:
        """Delete multiple keys at once."""
        if not self._connected:
            return 0

        redis_keys = [self._make_key(k) for k in keys]

        try:
            return await self._redis.delete(*redis_keys)
        except Exception:
            return 0

    async def clear_prefix(self, prefix: str = "") -> int:
        """Clear all keys with given prefix."""
        if not self._connected:
            return 0

        pattern = f"{self._config.prefix}{prefix}*"

        try:
            keys = []
            async for key in self._redis.scan_iter(pattern):
                keys.append(key)

            if keys:
                return await self._redis.delete(*keys)
            return 0
        except Exception:
            return 0

    async def get_keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern."""
        if not self._connected:
            return []

        full_pattern = f"{self._config.prefix}{pattern}"

        try:
            keys = []
            async for key in self._redis.scan_iter(full_pattern):
                # Remove prefix from returned key
                clean_key = key.replace(self._config.prefix, "", 1)
                keys.append(clean_key)
            return keys
        except Exception:
            return []

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        stats = {
            "connected": self._connected,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "prefix": self._config.prefix
        }

        if self._connected:
            try:
                info = await self._redis.info("memory")
                stats["used_memory"] = info.get("used_memory_human", "unknown")
                stats["used_memory_bytes"] = info.get("used_memory", 0)
            except Exception as e:
                logger.debug(f"Failed to get Redis memory info: {e}")

        return stats

    @property
    def is_connected(self) -> bool:
        """Check if connected to Redis."""
        return self._connected


def create_redis_cache(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: Optional[str] = None,
    prefix: str = "company_researcher:",
    default_ttl: int = 3600
) -> RedisCache:
    """
    Factory function to create Redis cache.

    Args:
        host: Redis host
        port: Redis port
        db: Redis database number
        password: Optional password
        prefix: Key prefix
        default_ttl: Default TTL in seconds

    Returns:
        Configured RedisCache instance
    """
    config = RedisCacheConfig(
        host=host,
        port=port,
        db=db,
        password=password,
        prefix=prefix,
        default_ttl=default_ttl
    )
    return RedisCache(config)
