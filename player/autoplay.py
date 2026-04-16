"""Autoplay/Radio system for continuous music recommendations."""

import asyncio
import logging
from typing import Optional, List
from .queue import Song

logger = logging.getLogger(__name__)


class AutoplayEngine:
    """Handles automatic song recommendations when queue ends."""
    
    def __init__(self, searcher):
        """
        Initialize autoplay engine.
        
        Args:
            searcher: Searcher instance for recommendations and fallback search
        """
        self.searcher = searcher
        self.history: dict = {}  # guild_id -> list of played song IDs
        self.history_limit = 50  # Remember last 50 songs to avoid repeats
    
    async def get_recommendations(self, current_song: Song, limit: int = 8) -> Optional[List[Song]]:
        """
        Fetch recommended songs based on current track.
        
        Args:
            current_song: Current song playing
            limit: Number of recommendations to fetch (default 8)
        
        Returns:
            List of recommended Song objects, or None if failed
        """
        try:
            if not hasattr(current_song, 'video_id') or not current_song.video_id:
                logger.warning(f"Current song missing video_id: {current_song.title}")
                return await self._fallback_search(current_song)
            
            # Try to get watch playlist recommendations
            logger.info(f"Fetching recommendations for: {current_song.title}")
            
            try:
                # This would call ytmusicapi get_watch_playlist
                # For now, we use fallback search as ytmusicapi requires special setup
                recommendations = await self._fetch_watch_playlist(current_song.video_id)
            except Exception as e:
                logger.warning(f"Watch playlist failed, using fallback: {e}")
                recommendations = None
            
            # If primary method fails, use fallback search
            if not recommendations:
                logger.info(f"Using fallback search for: {current_song.title}")
                recommendations = await self._fallback_search(current_song)
            
            # Filter and deduplicate
            if recommendations:
                filtered = self._filter_recommendations(
                    recommendations, 
                    current_song,
                    limit
                )
                logger.info(f"Returning {len(filtered)} recommendations")
                return filtered
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching recommendations: {e}")
            return None
    
    async def _fetch_watch_playlist(self, video_id: str) -> Optional[List[Song]]:
        """
        Fetch recommendations from YouTube Music watch playlist.
        
        Args:
            video_id: YouTube video ID of current song
        
        Returns:
            List of recommended Song objects, or None if failed
        """
        try:
            # Use ytmusicapi.get_watch_playlist(videoId)
            # The API returns a dict with 'tracks' containing recommendations
            
            logger.info(f"Fetching watch playlist for video: {video_id}")
            
            loop = asyncio.get_event_loop()
            watch_playlist = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.searcher.ytmusic.get_watch_playlist(videoId=video_id)
                ),
                timeout=5.0
            )
            
            if not watch_playlist or 'tracks' not in watch_playlist:
                logger.warning(f"Watch playlist empty for {video_id}")
                return None
            
            # Convert raw results to Song objects
            songs = []
            tracks = watch_playlist.get('tracks', [])
            
            for track in tracks:
                try:
                    # Skip items without required fields
                    if 'videoId' not in track or 'title' not in track:
                        continue
                    
                    song = Song(
                        title=track.get('title', 'Unknown'),
                        artist=self._extract_artist(track),
                        duration=track.get('duration_seconds', 0),
                        url='',  # Will be fetched when played
                        requester='autoplay'
                    )
                    # Attach video_id for future autoplay chains
                    song.video_id = track.get('videoId')
                    songs.append(song)
                except Exception as e:
                    logger.debug(f"Failed to parse track: {e}")
                    continue
            
            logger.info(f"Got {len(songs)} recommendations from watch playlist")
            return songs if songs else None
            
        except asyncio.TimeoutError:
            logger.warning(f"Watch playlist timeout for {video_id}")
            return None
        except Exception as e:
            logger.warning(f"Failed to fetch watch playlist: {e}")
            return None
    
    def _extract_artist(self, track: dict) -> str:
        """Extract artist name from track data."""
        # Try different artist field names
        if 'artists' in track and isinstance(track['artists'], list) and track['artists']:
            if isinstance(track['artists'][0], dict):
                return track['artists'][0].get('name', 'Unknown')
            return str(track['artists'][0])
        
        if 'album' in track:
            return track['album']
        
        return 'Unknown'
    
    async def _fallback_search(self, current_song: Song) -> Optional[List[Song]]:
        """
        Fallback: Search for similar songs by title + artist.
        
        Args:
            current_song: Current song for search context
        
        Returns:
            List of search result Song objects
        """
        try:
            # Build search query
            query = f"{current_song.title} {current_song.artist or ''}"
            query = query.strip()
            
            logger.info(f"Fallback search: {query}")
            
            # Use ytmusicapi.search() directly to get multiple results
            loop = asyncio.get_event_loop()
            raw_results = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.searcher.ytmusic.search(
                        query=query,
                        filter='songs',
                        limit=10
                    )
                ),
                timeout=5.0
            )
            
            if not raw_results:
                logger.info(f"Fallback search returned no results for: {query}")
                return None
            
            # Convert raw results to Song objects
            songs = []
            for item in raw_results:
                try:
                    song = Song(
                        title=item.get('title', 'Unknown'),
                        artist=self._extract_artist(item),
                        duration=item.get('duration_seconds', 0),
                        url='',  # Will be fetched when played
                        requester='autoplay'
                    )
                    # Attach video_id if available for future autoplay chains
                    if 'videoId' in item:
                        song.video_id = item.get('videoId')
                    songs.append(song)
                except Exception as e:
                    logger.debug(f"Failed to parse search result: {e}")
                    continue
            
            logger.info(f"Fallback search returned {len(songs)} results")
            return songs if songs else None
            
        except asyncio.TimeoutError:
            logger.warning(f"Fallback search timeout for: {current_song.title}")
            return None
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return None
    
    def _filter_recommendations(
        self,
        recommendations: List[Song],
        current_song: Song,
        limit: int = 8
    ) -> List[Song]:
        """
        Filter and deduplicate recommendations.
        
        Args:
            recommendations: Raw recommendations from API/search
            current_song: Current song (to avoid repeating)
            limit: Maximum recommendations to return
        
        Returns:
            Filtered and deduplicated list of songs
        """
        filtered = []
        seen_ids = set()
        
        # Don't recommend the current song again
        current_id = getattr(current_song, 'video_id', None)
        if current_id:
            seen_ids.add(current_id)
        
        for song in recommendations:
            # Skip if already processed
            song_id = getattr(song, 'video_id', song.title)
            if song_id in seen_ids:
                continue
            
            # Skip invalid tracks
            if not self._is_valid_track(song):
                continue
            
            # Prefer same artist (score boost, but don't filter out)
            filtered.append(song)
            seen_ids.add(song_id)
            
            # Stop at limit
            if len(filtered) >= limit:
                break
        
        return filtered[:limit]
    
    def _is_valid_track(self, song: Song) -> bool:
        """
        Check if song is a valid music track.
        
        Args:
            song: Song object to validate
        
        Returns:
            True if valid, False otherwise
        """
        # Check required attributes
        if not hasattr(song, 'title') or not song.title:
            return False
        
        if not hasattr(song, 'url') or not song.url:
            return False
        
        # Skip very short titles (likely not songs)
        if len(song.title) < 3:
            return False
        
        # Skip if contains common non-music markers
        skip_keywords = ['podcast', 'audiobook', 'interview', 'commentary']
        title_lower = song.title.lower()
        if any(keyword in title_lower for keyword in skip_keywords):
            return False
        
        return True
    
    def update_history(self, guild_id: int, song_id: str):
        """
        Add song to history to avoid repeating.
        
        Args:
            guild_id: Guild ID
            song_id: Song's video ID or unique identifier
        """
        if guild_id not in self.history:
            self.history[guild_id] = []
        
        history = self.history[guild_id]
        
        # Add to front
        if song_id in history:
            history.remove(song_id)
        history.insert(0, song_id)
        
        # Keep only recent history
        self.history[guild_id] = history[:self.history_limit]
    
    def get_guild_history(self, guild_id: int) -> set:
        """
        Get set of recently played songs for guild.
        
        Args:
            guild_id: Guild ID
        
        Returns:
            Set of song IDs in recent history
        """
        return set(self.history.get(guild_id, []))
    
    def clear_history(self, guild_id: int):
        """
        Clear history for guild.
        
        Args:
            guild_id: Guild ID
        """
        if guild_id in self.history:
            del self.history[guild_id]
