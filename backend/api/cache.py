"""Redis caching utilities."""

import hashlib
import json
import os
from functools import wraps
from typing import Any, Callable, Optional

from redis import ConnectionError as RedisConnectionError
from redis import Redis

from api.middleware.logging_config import get_logger

logger = get_logger(__name__)

# Initialize Redis client (lazy connection)
_redis_client: Optional[Redis] = None


def get_redis() -> Optional[Redis]:
    """
    Get Redis client instance.

    Returns:
        Redis client or None if Redis is not available
    """
    global _redis_client

    # Return None if caching is disabled
    if os.getenv("CACHE_ENABLED", "true").lower() != "true":
        return None

    # Create client if not exists
    if _redis_client is None:
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            _redis_client = Redis.from_url(redis_url, decode_responses=True)
            # Test connection
            _redis_client.ping()
            logger.info("Redis cache connected successfully")
        except (RedisConnectionError, Exception) as e:
            logger.warning(f"Redis cache not available: {e}")
            _redis_client = None

    return _redis_client


def cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from function arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        MD5 hash of the arguments
    """
    # Create a stable string representation
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    key_str = ":".join(key_parts)

    # Return MD5 hash
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(prefix: str, ttl: int = 300):
    """
    Decorator to cache function results in Redis.

    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (default: 5 minutes)

    Usage:
        @cached(prefix="big_rocks:list", ttl=300)
        def get_all_big_rocks():
            return crud.get_big_rocks(db)

    Note:
        If Redis is not available, the function executes normally without caching.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            redis = get_redis()

            # If Redis is not available, execute function normally
            if redis is None:
                return await func(*args, **kwargs)

            # Generate cache key
            key_suffix = cache_key(*args, **kwargs)
            full_key = f"{prefix}:{key_suffix}"

            try:
                # Try to get from cache
                cached_value = redis.get(full_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {full_key}")
                    return json.loads(cached_value)

                # Cache miss - execute function
                logger.debug(f"Cache miss: {full_key}")
                result = await func(*args, **kwargs)

                # Store in cache
                redis.setex(full_key, ttl, json.dumps(result, default=str))

                return result

            except Exception as e:
                logger.warning(f"Cache error: {e}, executing function")
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            redis = get_redis()

            # If Redis is not available, execute function normally
            if redis is None:
                return func(*args, **kwargs)

            # Generate cache key
            key_suffix = cache_key(*args, **kwargs)
            full_key = f"{prefix}:{key_suffix}"

            try:
                # Try to get from cache
                cached_value = redis.get(full_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {full_key}")
                    return json.loads(cached_value)

                # Cache miss - execute function
                logger.debug(f"Cache miss: {full_key}")
                result = func(*args, **kwargs)

                # Store in cache
                redis.setex(full_key, ttl, json.dumps(result, default=str))

                return result

            except Exception as e:
                logger.warning(f"Cache error: {e}, executing function")
                return func(*args, **kwargs)

        # Return appropriate wrapper based on function type
        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def invalidate_cache(prefix: str, *args, **kwargs):
    """
    Invalidate cache for specific key.

    Args:
        prefix: Cache key prefix
        *args: Positional arguments used in the original cache key
        **kwargs: Keyword arguments used in the original cache key
    """
    redis = get_redis()
    if redis is None:
        return

    try:
        key_suffix = cache_key(*args, **kwargs)
        full_key = f"{prefix}:{key_suffix}"
        redis.delete(full_key)
        logger.debug(f"Cache invalidated: {full_key}")
    except Exception as e:
        logger.warning(f"Cache invalidation error: {e}")


def invalidate_pattern(pattern: str):
    """
    Invalidate all cache keys matching a pattern.

    Args:
        pattern: Redis key pattern (e.g., "big_rocks:*")
    """
    redis = get_redis()
    if redis is None:
        return

    try:
        keys = redis.keys(pattern)
        if keys:
            redis.delete(*keys)
            logger.debug(f"Cache pattern invalidated: {pattern} ({len(keys)} keys)")
    except Exception as e:
        logger.warning(f"Cache pattern invalidation error: {e}")
