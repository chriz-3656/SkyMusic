"""YouTube Music playlist support for SkyMusic bot."""

import logging
import asyncio
import re
from typing import Optional, List
from ytmusicapi import YTMusic
from .queue import Song

logger = logging.getLogger(__name__)


class PlaylistParser:
    """Parse and load YouTube Music playlists."""
    
    def __init__(self, ytmusic: YTMusic):
        """
        Initialize playlist parser.
        
        Args:
            ytmusic: YTMusic instance
        """
        self.ytmusic = ytmusic
    
    @staticmethod
    def extract_playlist_id(url: str) -> Optional[str]:
        """
        Extract playlist ID from YouTube Music URL.
        
        Args:
            url: YouTube Music URL (https://music.youtube.com/playlist?list=PLxxxxxxxxxx)
        
        Returns:
            Playlist ID or None if not valid
        """
        if not url:
            return None
        
        # Match YouTube Music playlist URL
        match = re.search(r'[?&]list=([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        
        # Try as direct playlist ID
        if re.match(r'^[a-zA-Z0-9_-]{30,}$', url):
            return url
        
        return None
    
    @staticmethod
    def is_playlist_url(query: str) -> bool:
        """
        Check if query is a playlist URL.
        
        Args:
            query: Query string to check
        
        Returns:
            True if query appears to be a playlist URL
        """
        if not query:
            return False
        
        return bool(
            'music.youtube.com/playlist' in query or
            'list=' in query or
            re.match(r'^[a-zA-Z0-9_-]{30,}$', query)  # Playlist ID length
        )
    
    async def get_playlist(self, playlist_id: str) -> Optional[dict]:
        """
        Fetch playlist metadata from YouTube Music.
        
        Args:
            playlist_id: YouTube Music playlist ID
        
        Returns:
            Playlist data or None if failed
        """
        try:
            logger.info(f"Fetching playlist: {playlist_id}")
            
            loop = asyncio.get_event_loop()
            playlist_data = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.ytmusic.get_playlist(playlistId=playlist_id)
                ),
                timeout=10.0
            )
            
            if not playlist_data:
                logger.warning(f"Playlist not found: {playlist_id}")
                return None
            
            logger.info(f"Got playlist: {playlist_data.get('header', {}).get('title', 'Unknown')}")
            return playlist_data
            
        except asyncio.TimeoutError:
            logger.warning(f"Playlist fetch timeout: {playlist_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch playlist {playlist_id}: {e}")
            return None
    
    async def get_playlist_songs(self, playlist_id: str, limit: int = 100) -> Optional[List[Song]]:
        """
        Fetch all songs from a playlist.
        
        Args:
            playlist_id: YouTube Music playlist ID
            limit: Maximum number of songs to fetch
        
        Returns:
            List of Song objects or None if failed
        """
        try:
            playlist_data = await self.get_playlist(playlist_id)
            if not playlist_data:
                return None
            
            # Extract songs from playlist
            songs = []
            tracks = playlist_data.get('contents', [])
            
            logger.info(f"Extracting {len(tracks)} tracks from playlist")
            
            for track in tracks[:limit]:
                try:
                    # Skip invalid entries
                    if 'videoId' not in track or 'title' not in track:
                        continue
                    
                    song = Song(
                        title=track.get('title', 'Unknown'),
                        artist=self._extract_artist(track),
                        duration=self._parse_duration(track.get('duration', 0)),
                        url='',  # Will be fetched when played
                        requester='playlist',
                        thumbnail=track.get('thumbnail', [{}])[0].get('url') if track.get('thumbnail') else None
                    )
                    
                    # Store video_id for stream extraction
                    song.video_id = track.get('videoId')
                    
                    # Store album if available
                    if track.get('album'):
                        song.album = track['album'].get('name', 'Unknown')
                    
                    songs.append(song)
                    
                except Exception as e:
                    logger.debug(f"Failed to parse track: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(songs)} playable songs")
            return songs if songs else None
            
        except Exception as e:
            logger.error(f"Failed to get playlist songs: {e}")
            return None
    
    @staticmethod
    def _extract_artist(track: dict) -> str:
        """Extract artist name from track data."""
        if 'artists' in track and isinstance(track['artists'], list) and track['artists']:
            if isinstance(track['artists'][0], dict):
                return track['artists'][0].get('name', 'Unknown')
            return str(track['artists'][0])
        
        if 'album' in track and isinstance(track['album'], dict):
            return track['album'].get('name', 'Unknown')
        
        return 'Unknown'
    
    @staticmethod
    def _parse_duration(duration: int) -> int:
        """
        Parse duration to seconds.
        
        Args:
            duration: Duration value (could be seconds or minutes)
        
        Returns:
            Duration in seconds
        """
        if isinstance(duration, int):
            return duration
        
        if isinstance(duration, str):
            # Parse "MM:SS" format
            parts = duration.split(':')
            if len(parts) == 2:
                try:
                    minutes, seconds = int(parts[0]), int(parts[1])
                    return minutes * 60 + seconds
                except ValueError:
                    pass
        
        return 0
    
    async def get_playlist_info(self, playlist_id: str) -> Optional[dict]:
        """
        Get playlist metadata (title, description, song count).
        
        Args:
            playlist_id: YouTube Music playlist ID
        
        Returns:
            Playlist info dict or None
        """
        try:
            playlist_data = await self.get_playlist(playlist_id)
            if not playlist_data:
                return None
            
            header = playlist_data.get('header', {})
            
            return {
                'title': header.get('title', 'Unknown Playlist'),
                'description': header.get('description', ''),
                'song_count': len(playlist_data.get('contents', [])),
                'thumbnail': header.get('subtitle_thumbnail', ''),
                'author': self._extract_author(header)
            }
            
        except Exception as e:
            logger.error(f"Failed to get playlist info: {e}")
            return None
    
    @staticmethod
    def _extract_author(header: dict) -> str:
        """Extract playlist author/creator."""
        if 'subtitle' in header and isinstance(header['subtitle'], list):
            for item in header['subtitle']:
                if isinstance(item, dict) and 'text' in item:
                    return item['text']
        
        return 'Unknown'
