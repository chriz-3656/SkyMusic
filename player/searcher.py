import asyncio
import logging
from typing import Optional
from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL
from .queue import Song

logger = logging.getLogger(__name__)


class Searcher:
    """Handle song search and stream extraction."""
    
    def __init__(self, search_timeout: int = 10):
        self.ytmusic = YTMusic()
        self.timeout = search_timeout
        
        # yt-dlp config for stream extraction
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'extract_flat': False,
        }
    
    async def search(self, query: str, requester: str) -> Optional[Song]:
        """
        Search for a song using ytmusicapi.
        Returns Song object with stream URL and metadata or None if not found.
        """
        try:
            # Run blocking ytmusic search in executor
            loop = asyncio.get_event_loop()
            results = await asyncio.wait_for(
                loop.run_in_executor(None, self._search_ytmusic, query),
                timeout=self.timeout
            )
            
            if not results:
                logger.warning(f"No results found for: {query}")
                return None
            
            # Get first result
            song_data = results[0]
            video_id = song_data.get('videoId')
            title = song_data.get('title', 'Unknown')
            artist = song_data.get('artists', [{'name': 'Unknown'}])[0].get('name', 'Unknown')
            
            if not video_id:
                logger.error(f"No video ID found for song: {title}")
                return None
            
            # Extract stream URL and metadata
            info = await self._extract_full_info(video_id)
            if not info or 'url' not in info:
                logger.error(f"Failed to extract stream URL for: {title}")
                return None
            
            stream_url = info['url']
            duration = info.get('duration', song_data.get('duration_seconds', 0))
            thumbnail = info.get('thumbnail', song_data.get('thumbnail', None))
            
            song = Song(
                title=title,
                url=stream_url,
                duration=duration,
                requester=requester,
                artist=artist
            )
            
            # Add metadata attributes
            song.thumbnail = thumbnail
            song.video_id = video_id
            
            return song
        
        except asyncio.TimeoutError:
            logger.error(f"Search timeout for query: {query}")
            return None
        except Exception as e:
            logger.error(f"Search error for query '{query}': {e}")
            return None
    
    def _search_ytmusic(self, query: str) -> list:
        """Blocking ytmusic search."""
        try:
            return self.ytmusic.search(query, filter='songs', limit=5)
        except Exception as e:
            logger.error(f"YTMusic search error: {e}")
            return []
    
    async def extract_stream_url(self, video_id: str) -> Optional[str]:
        """
        Extract stream URL from YouTube video using yt-dlp.
        """
        try:
            loop = asyncio.get_event_loop()
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            info = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    self._extract_info,
                    url
                ),
                timeout=self.timeout
            )
            
            if info and 'url' in info:
                return info['url']
            
            logger.warning(f"No stream URL found for video: {video_id}")
            return None
        
        except asyncio.TimeoutError:
            logger.error(f"Stream extraction timeout for: {video_id}")
            return None
        except Exception as e:
            logger.error(f"Stream extraction error for {video_id}: {e}")
            return None
    
    async def _extract_full_info(self, video_id: str) -> Optional[dict]:
        """Extract full info including URL, duration, and thumbnail."""
        try:
            loop = asyncio.get_event_loop()
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            info = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    self._extract_info,
                    url
                ),
                timeout=self.timeout
            )
            
            if info:
                return {
                    'url': info.get('url'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', None)
                }
            return None
        except Exception as e:
            logger.error(f"Full info extraction error for {video_id}: {e}")
            return None
    
    def _extract_info(self, url: str) -> Optional[dict]:
        """Blocking yt-dlp extraction."""
        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            logger.error(f"yt-dlp extraction error: {e}")
            return None
    
    async def _get_duration(self, video_id: str) -> int:
        """Get video duration from yt-dlp."""
        try:
            loop = asyncio.get_event_loop()
            info = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    self._extract_info,
                    f"https://www.youtube.com/watch?v={video_id}"
                ),
                timeout=self.timeout
            )
            
            if info and 'duration' in info:
                return info['duration']
            return 0
        except Exception as e:
            logger.error(f"Duration extraction error: {e}")
            return 0
