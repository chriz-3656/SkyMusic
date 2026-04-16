"""Search result caching for improved autocomplete performance."""

import time
import logging
from typing import Dict, List, Optional
from player.queue import Song

logger = logging.getLogger(__name__)


class SearchCache:
    """Cache for search results to avoid repeated API calls."""
    
    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize search cache.
        
        Args:
            ttl_seconds: Time to live for cached results (default: 5 minutes)
        """
        self.ttl = ttl_seconds
        self.cache: Dict[str, tuple] = {}  # query -> (results, timestamp)
    
    def get(self, query: str) -> Optional[List[Song]]:
        """
        Get cached search results if available and not expired.
        
        Args:
            query: Search query string
        
        Returns:
            List of Song objects if cache hit and valid, None otherwise
        """
        if query not in self.cache:
            return None
        
        results, timestamp = self.cache[query]
        
        # Check if cache entry has expired
        if time.time() - timestamp > self.ttl:
            del self.cache[query]
            logger.debug(f"Cache expired for query: {query}")
            return None
        
        logger.debug(f"Cache hit for query: {query}")
        return results
    
    def set(self, query: str, results: List[Song]):
        """
        Store search results in cache.
        
        Args:
            query: Search query string
            results: List of Song objects to cache
        """
        self.cache[query] = (results, time.time())
        logger.debug(f"Cached {len(results)} results for query: {query}")
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Search cache cleared")
    
    def cleanup_expired(self):
        """Remove expired entries from cache."""
        now = time.time()
        expired_keys = [
            query for query, (_, timestamp) in self.cache.items()
            if now - timestamp > self.ttl
        ]
        
        for query in expired_keys:
            del self.cache[query]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            'entries': len(self.cache),
            'ttl': self.ttl,
            'size_mb': sum(
                len(str(results)) / (1024 * 1024)
                for results, _ in self.cache.values()
            )
        }
