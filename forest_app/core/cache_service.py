"""
Distributed Caching Service for Forest App

This module implements a distributed caching system that can scale horizontally
while maintaining the intimate, personal experience for each user. It supports
both local memory caching and Redis-based distributed caching.
"""

import asyncio
<<<<<<< HEAD
import logging
import json
import hashlib
import time
import pickle
from typing import Any, Dict, List, Optional, Set, Tuple, Union, TypeVar, Generic, Callable
from datetime import datetime, timedelta
from functools import wraps
from enum import Enum
=======
import hashlib
import logging
import pickle
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

logger = logging.getLogger(__name__)

# Type variable for generic cache methods
<<<<<<< HEAD
T = TypeVar('T')

class CacheBackend(Enum):
    """Supported cache backend types."""
    MEMORY = "memory"  # Local in-memory cache
    REDIS = "redis"    # Redis distributed cache
    NONE = "none"      # No caching (for testing/debugging)

class CacheConfig:
    """Configuration for the cache service."""
    
=======
T = TypeVar("T")


class CacheBackend(Enum):
    """Supported cache backend types."""

    MEMORY = "memory"  # Local in-memory cache
    REDIS = "redis"  # Redis distributed cache
    NONE = "none"  # No caching (for testing/debugging)


class CacheConfig:
    """Configuration for the cache service."""

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    def __init__(
        self,
        backend: CacheBackend = CacheBackend.MEMORY,
        redis_url: Optional[str] = None,
        default_ttl: int = 3600,  # 1 hour
        namespace: str = "forest:",
        serializer: Optional[Callable] = None,
<<<<<<< HEAD
        deserializer: Optional[Callable] = None
    ):
        """
        Initialize cache configuration.
        
=======
        deserializer: Optional[Callable] = None,
    ):
        """
        Initialize cache configuration.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Args:
            backend: The cache backend to use
            redis_url: Redis connection URL (required for REDIS backend)
            default_ttl: Default time-to-live for cache entries in seconds
            namespace: Prefix for all cache keys
            serializer: Custom serializer function (default: pickle)
            deserializer: Custom deserializer function (default: pickle)
        """
        self.backend = backend
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.namespace = namespace
        self.serializer = serializer or pickle.dumps
        self.deserializer = deserializer or pickle.loads

<<<<<<< HEAD
class MemoryCache:
    """Simple in-memory cache implementation."""
    
    def __init__(self, config: CacheConfig):
        """
        Initialize memory cache.
        
=======

class MemoryCache:
    """Simple in-memory cache implementation."""

    def __init__(self, config: CacheConfig):
        """
        Initialize memory cache.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Args:
            config: Cache configuration
        """
        self.config = config
        self.cache: Dict[str, Tuple[Any, float]] = {}  # (value, expiry)
        self.namespace = config.namespace
        self.lock = asyncio.Lock()
<<<<<<< HEAD
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_task())
        
        logger.info("Memory cache initialized")
    
=======

        # Start cleanup task
        asyncio.create_task(self._cleanup_task())

        logger.info("Memory cache initialized")

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    async def _cleanup_task(self):
        """Background task to clean up expired cache entries."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self.cleanup()
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    async def cleanup(self):
        """Remove expired entries from cache."""
        now = time.time()
        expired_keys = []
<<<<<<< HEAD
        
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        async with self.lock:
            # Find expired keys
            for key, (_, expiry) in self.cache.items():
                if expiry < now:
                    expired_keys.append(key)
<<<<<<< HEAD
            
            # Remove expired keys
            for key in expired_keys:
                del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Removed {len(expired_keys)} expired cache entries")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
=======

            # Remove expired keys
            for key in expired_keys:
                del self.cache[key]

        if expired_keys:
            logger.debug(f"Removed {len(expired_keys)} expired cache entries")

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            Cached value or None if not found or expired
        """
        full_key = f"{self.namespace}{key}"
        now = time.time()
<<<<<<< HEAD
        
        async with self.lock:
            if full_key in self.cache:
                value, expiry = self.cache[full_key]
                
=======

        async with self.lock:
            if full_key in self.cache:
                value, expiry = self.cache[full_key]

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                # Check if expired
                if expiry < now:
                    del self.cache[full_key]
                    return None
<<<<<<< HEAD
                
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                # Return cached value
                try:
                    return self.config.deserializer(value)
                except Exception as e:
                    logger.error(f"Error deserializing cached value: {e}")
                    return None
<<<<<<< HEAD
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in the cache.
        
=======

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in the cache.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
<<<<<<< HEAD
            
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            True if successful, False otherwise
        """
        full_key = f"{self.namespace}{key}"
        ttl = ttl if ttl is not None else self.config.default_ttl
        expiry = time.time() + ttl
<<<<<<< HEAD
        
        try:
            # Serialize value
            serialized_value = self.config.serializer(value)
            
            # Store in cache
            async with self.lock:
                self.cache[full_key] = (serialized_value, expiry)
            
=======

        try:
            # Serialize value
            serialized_value = self.config.serializer(value)

            # Store in cache
            async with self.lock:
                self.cache[full_key] = (serialized_value, expiry)

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            return True
        except Exception as e:
            logger.error(f"Error setting cache value: {e}")
            return False
<<<<<<< HEAD
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
=======

    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            True if deleted, False if not found
        """
        full_key = f"{self.namespace}{key}"
<<<<<<< HEAD
        
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        async with self.lock:
            if full_key in self.cache:
                del self.cache[full_key]
                return True
<<<<<<< HEAD
        
        return False
    
    async def flush(self) -> bool:
        """
        Clear the entire cache.
        
=======

        return False

    async def flush(self) -> bool:
        """
        Clear the entire cache.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            True if successful
        """
        async with self.lock:
            self.cache.clear()
<<<<<<< HEAD
        
        logger.info("Memory cache flushed")
        return True

class RedisCache:
    """Redis-based distributed cache implementation."""
    
    def __init__(self, config: CacheConfig):
        """
        Initialize Redis cache.
        
=======

        logger.info("Memory cache flushed")
        return True


class RedisCache:
    """Redis-based distributed cache implementation."""

    def __init__(self, config: CacheConfig):
        """
        Initialize Redis cache.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Args:
            config: Cache configuration
        """
        self.config = config
        self.namespace = config.namespace
        self.redis = None
        self.lock = asyncio.Lock()
<<<<<<< HEAD
        
        # Import Redis here to avoid dependency if not used
        try:
            import redis.asyncio as aioredis
            self.redis = aioredis.from_url(config.redis_url)
            logger.info("Redis cache initialized with URL: " + config.redis_url.split("@")[-1])  # Hide credentials
=======

        # Import Redis here to avoid dependency if not used
        try:
            import redis.asyncio as aioredis

            self.redis = aioredis.from_url(config.redis_url)
            logger.info(
                "Redis cache initialized with URL: " + config.redis_url.split("@")[-1]
            )  # Hide credentials
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        except ImportError:
            logger.error("Redis package not installed. Please install 'redis' package.")
            raise
        except Exception as e:
            logger.error(f"Error initializing Redis connection: {e}")
            raise
<<<<<<< HEAD
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
=======

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            Cached value or None if not found or expired
        """
        if not self.redis:
            return None
<<<<<<< HEAD
        
        full_key = f"{self.namespace}{key}"
        
        try:
            # Get value from Redis
            value = await self.redis.get(full_key)
            
            if value is None:
                return None
            
=======

        full_key = f"{self.namespace}{key}"

        try:
            # Get value from Redis
            value = await self.redis.get(full_key)

            if value is None:
                return None

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            # Deserialize value
            return self.config.deserializer(value)
        except Exception as e:
            logger.error(f"Error getting value from Redis: {e}")
            return None
<<<<<<< HEAD
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in the cache.
        
=======

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in the cache.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
<<<<<<< HEAD
            
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            return False
<<<<<<< HEAD
        
        full_key = f"{self.namespace}{key}"
        ttl = ttl if ttl is not None else self.config.default_ttl
        
        try:
            # Serialize value
            serialized_value = self.config.serializer(value)
            
            # Store in Redis
            await self.redis.set(full_key, serialized_value, ex=ttl)
            
=======

        full_key = f"{self.namespace}{key}"
        ttl = ttl if ttl is not None else self.config.default_ttl

        try:
            # Serialize value
            serialized_value = self.config.serializer(value)

            # Store in Redis
            await self.redis.set(full_key, serialized_value, ex=ttl)

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            return True
        except Exception as e:
            logger.error(f"Error setting value in Redis: {e}")
            return False
<<<<<<< HEAD
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
=======

    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            True if deleted, False if not found
        """
        if not self.redis:
            return False
<<<<<<< HEAD
        
        full_key = f"{self.namespace}{key}"
        
=======

        full_key = f"{self.namespace}{key}"

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        try:
            # Delete from Redis
            result = await self.redis.delete(full_key)
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting value from Redis: {e}")
            return False
<<<<<<< HEAD
    
    async def flush(self) -> bool:
        """
        Clear all cache entries with this namespace.
        
=======

    async def flush(self) -> bool:
        """
        Clear all cache entries with this namespace.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            True if successful
        """
        if not self.redis:
            return False
<<<<<<< HEAD
        
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        try:
            # Find all keys with this namespace
            pattern = f"{self.namespace}*"
            keys = []
<<<<<<< HEAD
            
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            # Scan for keys in batches to avoid blocking Redis
            cursor = 0
            while True:
                cursor, batch = await self.redis.scan(cursor, match=pattern, count=100)
                keys.extend(batch)
<<<<<<< HEAD
                
                if cursor == 0:
                    break
            
=======

                if cursor == 0:
                    break

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            # Delete keys if found
            if keys:
                await self.redis.delete(*keys)
                logger.info(f"Flushed {len(keys)} keys from Redis cache")
<<<<<<< HEAD
            
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            return True
        except Exception as e:
            logger.error(f"Error flushing Redis cache: {e}")
            return False

<<<<<<< HEAD
class CacheService:
    """
    Distributed caching service for improving performance and scalability.
    
=======

class CacheService:
    """
    Distributed caching service for improving performance and scalability.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    This service provides a unified interface for caching data, whether using
    local memory or Redis, making it easy to scale horizontally while maintaining
    the intimate, personal experience for each user.
    """
<<<<<<< HEAD
    
    _instance = None
    
    @classmethod
    def get_instance(cls, config: Optional[CacheConfig] = None) -> 'CacheService':
=======

    _instance = None

    @classmethod
    def get_instance(cls, config: Optional[CacheConfig] = None) -> "CacheService":
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        """Get the singleton instance of the CacheService."""
        if cls._instance is None:
            cls._instance = CacheService(config or CacheConfig())
        elif config is not None:
            logger.warning("Cache already initialized, ignoring new config")
        return cls._instance
<<<<<<< HEAD
    
    def __init__(self, config: CacheConfig):
        """
        Initialize the cache service.
        
=======

    def __init__(self, config: CacheConfig):
        """
        Initialize the cache service.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Args:
            config: Cache configuration
        """
        self.config = config
<<<<<<< HEAD
        
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        # Initialize backend
        if config.backend == CacheBackend.MEMORY:
            self.backend = MemoryCache(config)
        elif config.backend == CacheBackend.REDIS:
            if not config.redis_url:
                raise ValueError("Redis URL is required for Redis backend")
            self.backend = RedisCache(config)
        elif config.backend == CacheBackend.NONE:
            self.backend = None
            logger.warning("Cache disabled (NONE backend)")
        else:
            raise ValueError(f"Unsupported cache backend: {config.backend}")
<<<<<<< HEAD
        
        logger.info(f"Cache service initialized with {config.backend.value} backend")
    
    async def get(self, key: str) -> Optional[T]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
=======

        logger.info(f"Cache service initialized with {config.backend.value} backend")

    async def get(self, key: str) -> Optional[T]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            Cached value or None if not found
        """
        if not self.backend:
            return None
<<<<<<< HEAD
        
        value = await self.backend.get(key)
        logger.debug(f"Cache {'hit' if value is not None else 'miss'} for key: {key}")
        return value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in the cache.
        
=======

        value = await self.backend.get(key)
        logger.debug(f"Cache {'hit' if value is not None else 'miss'} for key: {key}")
        return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in the cache.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
<<<<<<< HEAD
            
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            True if successful, False otherwise
        """
        if not self.backend:
            return False
<<<<<<< HEAD
        
        success = await self.backend.set(key, value, ttl)
        if success:
            logger.debug(f"Cached value for key: {key} (TTL: {ttl or self.config.default_ttl}s)")
        return success
    
    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
=======

        success = await self.backend.set(key, value, ttl)
        if success:
            logger.debug(
                f"Cached value for key: {key} (TTL: {ttl or self.config.default_ttl}s)"
            )
        return success

    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            True if deleted, False if not found
        """
        if not self.backend:
            return False
<<<<<<< HEAD
        
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        success = await self.backend.delete(key)
        if success:
            logger.debug(f"Deleted cached value for key: {key}")
        return success
<<<<<<< HEAD
    
    async def flush(self) -> bool:
        """
        Clear the entire cache.
        
=======

    async def flush(self) -> bool:
        """
        Clear the entire cache.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            True if successful
        """
        if not self.backend:
            return False
<<<<<<< HEAD
        
        return await self.backend.flush()

=======

        return await self.backend.flush()


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
# Decorator for cacheable functions
def cacheable(key_pattern: str, ttl: Optional[int] = None):
    """
    Decorator for caching function results.
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    Args:
        key_pattern: Pattern for cache key, using {arg_name} for arg values
                    For positional args, use {0}, {1}, etc.
        ttl: Time-to-live in seconds (uses default if None)
<<<<<<< HEAD
        
    Returns:
        Decorated function with caching
    """
=======

    Returns:
        Decorated function with caching
    """

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache service
            cache = CacheService.get_instance()
<<<<<<< HEAD
            
            # Skip if cache is disabled
            if not cache.backend:
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
=======

            # Skip if cache is disabled
            if not cache.backend:
                return (
                    await func(*args, **kwargs)
                    if asyncio.iscoroutinefunction(func)
                    else func(*args, **kwargs)
                )

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            # Build cache key from pattern
            key_context = kwargs.copy()
            # Add positional args to context
            for i, arg in enumerate(args):
                # Skip self/cls for methods
<<<<<<< HEAD
                if i == 0 and func.__name__ == func.__qualname__.split('.')[-1]:
                    continue
                key_context[str(i)] = arg
            
            try:
                # Format key pattern with args
                cache_key = key_pattern.format(**key_context)
                
                # Hash long or complex keys
                if len(cache_key) > 100:
                    cache_key = hashlib.md5(cache_key.encode()).hexdigest()
                
                # Add function name prefix
                cache_key = f"{func.__module__}.{func.__name__}:{cache_key}"
                
=======
                if i == 0 and func.__name__ == func.__qualname__.split(".")[-1]:
                    continue
                key_context[str(i)] = arg

            try:
                # Format key pattern with args
                cache_key = key_pattern.format(**key_context)

                # Hash long or complex keys
                if len(cache_key) > 100:
                    cache_key = hashlib.md5(cache_key.encode()).hexdigest()

                # Add function name prefix
                cache_key = f"{func.__module__}.{func.__name__}:{cache_key}"

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                # Check cache first
                cached_value = await cache.get(cache_key)
                if cached_value is not None:
                    return cached_value
<<<<<<< HEAD
                
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                # Call function if cache miss
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
<<<<<<< HEAD
                
                # Cache result
                await cache.set(cache_key, result, ttl)
                
                return result
                
            except Exception as e:
                logger.warning(f"Error in cache logic: {e}, falling back to uncached function")
                # Fall back to uncached function call
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        
        return wrapper
    
=======

                # Cache result
                await cache.set(cache_key, result, ttl)

                return result

            except Exception as e:
                logger.warning(
                    f"Error in cache logic: {e}, falling back to uncached function"
                )
                # Fall back to uncached function call
                return (
                    await func(*args, **kwargs)
                    if asyncio.iscoroutinefunction(func)
                    else func(*args, **kwargs)
                )

        return wrapper

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    return decorator
