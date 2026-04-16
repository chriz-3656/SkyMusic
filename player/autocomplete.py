"""Autocomplete engine for song search suggestions."""

import asyncio
import logging
from typing import List, Optional
from player.queue import Song
from player.searcher import Searcher
from player.cache import SearchCache

logger = logging.getLogger(__name__)


class SearchAutocomplete:
    """Provides autocomplete suggestions for song search."""
    
    def __init__(self, searcher: Searcher, cache_ttl: int = 300):
        """
        Initialize autocomplete engine.
        
        Args:
            searcher: Searcher instance for API access
            cache_ttl: Cache time-to-live in seconds (default: 5 minutes)
        """
        self.searcher = searcher
        self.cache = SearchCache(ttl_seconds=cache_ttl)
        self.min_query_length = 2  # Minimum characters before searching
    
    async def get_suggestions(
        self,
        query: str,
        limit: int = 5,
        timeout: float = 6.0
    ) -> List[Song]:
        """
        Get autocomplete suggestions for a search query.
        
        Args:
            query: Search query (song title, artist, etc.)
            limit: Maximum number of suggestions (default: 5)
            timeout: Maximum time to wait for results in seconds (default: 6s)
        
        Returns:
            List of Song objects, max length = limit
        """
        # Too short to search
        if not query or len(query.strip()) < self.min_query_length:
            return []
        
        query_clean = query.strip()
        
        try:
            # Check cache first
            cached = self.cache.get(query_clean)
            if cached is not None:
                return cached[:limit]
            
            # Fetch fresh results with timeout
            results = await asyncio.wait_for(
                self._fetch_suggestions(query_clean, limit),
                timeout=timeout
            )
            
            # Cache for future queries
            if results:
                self.cache.set(query_clean, results)
            
            return results[:limit]
            
        except asyncio.TimeoutError:
            logger.warning(f"Autocomplete timeout for query: {query_clean}")
            return []
        except Exception as e:
            logger.error(f"Autocomplete error for query {query_clean}: {e}")
            return []
    
    async def _fetch_suggestions(self, query: str, limit: int) -> List[Song]:
        """
        Fetch suggestions from search API.
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of Song objects
        """
        try:
            # Use ytmusicapi directly for fast suggestions (don't need stream URLs yet)
            loop = asyncio.get_event_loop()
            raw_results = await asyncio.wait_for(
                loop.run_in_executor(
                    None, 
                    lambda: self.searcher.ytmusic.search(
                        query=query,
                        filter='songs',
                        limit=limit + 2
                    )
                ),
                timeout=5.0
            )
            
            if not raw_results:
                logger.debug(f"No raw results for: {query}")
                return []
            
            # Convert raw results to Song objects (without stream URLs for speed)
            songs = []
            for item in raw_results:
                try:
                    song = Song(
                        title=item.get('title', 'Unknown'),
                        artist=item.get('artists', [{'name': 'Unknown'}])[0].get('name', 'Unknown'),
                        duration=item.get('duration_seconds', 0),
                        url='',  # Don't fetch URL for autocomplete suggestions
                        requester='autocomplete'
                    )
                    songs.append(song)
                except Exception as e:
                    logger.debug(f"Failed to parse search result: {e}")
                    continue
            
            # Validate and filter results
            suggestions = self._filter_suggestions(songs, limit)
            
            logger.debug(f"Fetched {len(suggestions)} suggestions for: {query}")
            return suggestions
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching suggestions for: {query}")
            return []
        except Exception as e:
            logger.error(f"Failed to fetch suggestions: {e}")
            return []
    
    def _filter_suggestions(self, songs: List[Song], limit: int) -> List[Song]:
        """
        Filter suggestions to ensure quality.
        
        Args:
            songs: List of songs from search
            limit: Maximum to return
        
        Returns:
            Filtered list of songs
        """
        filtered = []
        
        for song in songs:
            # Skip invalid entries
            if not self._is_valid_suggestion(song):
                continue
            
            filtered.append(song)
            
            # Stop at limit
            if len(filtered) >= limit:
                break
        
        return filtered
    
    def _is_valid_suggestion(self, song: Song) -> bool:
        """
        Check if song is a valid autocomplete suggestion.
        
        Args:
            song: Song object to validate
        
        Returns:
            True if valid, False otherwise
        """
        # Must have title
        if not hasattr(song, 'title') or not song.title:
            return False
        
        # Skip very short titles (likely garbage)
        if len(song.title) < 2:
            return False
        
        # Skip very long titles (likely not songs)
        if len(song.title) > 200:
            return False
        
        return True
    
    def format_suggestion(self, song: Song) -> str:
        """
        Format a song suggestion for display.
        
        Args:
            song: Song object
        
        Returns:
            Formatted string like "Title — Artist (3:45)"
        """
        title = song.title or "Unknown"
        artist = getattr(song, 'artist', None) or "Unknown Artist"
        
        # Get duration if available
        duration_str = ""
        if hasattr(song, 'duration') and song.duration:
            try:
                # Convert seconds to MM:SS format
                duration = int(song.duration)
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f" ({minutes}:{seconds:02d})"
            except (ValueError, TypeError):
                duration_str = ""
        
        # Format: "Title — Artist (Duration)"
        suggestion = f"{title} — {artist}{duration_str}"
        
        # Truncate if too long (Discord limit is 100 chars per suggestion)
        if len(suggestion) > 95:
            suggestion = suggestion[:92] + "..."
        
        return suggestion
    
    async def get_formatted_suggestions(
        self,
        query: str,
        limit: int = 5,
        timeout: float = 6.0
    ) -> List[str]:
        """
        Get formatted autocomplete suggestions.
        
        Args:
            query: Search query
            limit: Maximum number of suggestions
            timeout: Maximum time to wait
        
        Returns:
            List of formatted suggestion strings
        """
        songs = await self.get_suggestions(query, limit, timeout)
        return [self.format_suggestion(song) for song in songs]
    
    def clear_cache(self):
        """Clear the search cache."""
        self.cache.clear()
    
    def cleanup_cache(self):
        """Remove expired entries from cache."""
        self.cache.cleanup_expired()
