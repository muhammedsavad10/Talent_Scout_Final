"""
Cache Service Module for TalentScout Enterprise (Phase D Database & Persistence Review).
Provides in-memory caching layer with TTL expiration and bounded capacity eviction.
"""
import time
import logging
from typing import Optional, Any, Dict, Tuple

logger = logging.getLogger(__name__)

class CacheService:
    """
    In-memory caching service with TTL support and bounded memory capacity eviction.
    """
    def __init__(self, max_items: int = 1000):
        self._cache: Dict[str, Tuple[Any, Optional[float]]] = {}
        self.max_items = max_items

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieves cached value by key. Checks for TTL expiration.
        """
        if key not in self._cache:
            return None
        val, expires_at = self._cache[key]
        if expires_at is not None and time.time() > expires_at:
            logger.debug("Cache key expired: %s", key)
            del self._cache[key]
            return None
        return val

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Stores key-value pair in cache with optional TTL in seconds.
        Performs FIFO eviction if max_items limit is reached.
        """
        if len(self._cache) >= self.max_items and key not in self._cache:
            oldest_key = next(iter(self._cache))
            logger.debug("Evicting oldest cache key: %s", oldest_key)
            del self._cache[oldest_key]
            
        expires_at = (time.time() + ttl) if ttl else None
        self._cache[key] = (value, expires_at)
        return True

    async def delete(self, key: str) -> bool:
        """
        Deletes key from cache.
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def clear(self) -> bool:
        """
        Clears all cached entries.
        """
        self._cache.clear()
        return True

# Singleton instance
cache_service = CacheService()
