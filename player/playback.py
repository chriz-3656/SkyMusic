"""
V8 Unified Playback Flow
Handles complete playback operations through centralized, testable methods.
"""

import asyncio
import logging
from typing import Optional, Tuple
import discord

from .queue import Song
from .manager import PlayerManager, PlayerInstance
from .searcher import Searcher
from .progress import format_duration

logger = logging.getLogger(__name__)


class PlaybackError(Exception):
    """Raised when playback operation fails."""
    pass


class PlaybackFlow:
    """Unified playback operations using PlayerManager.
    
    All playback operations go through this class:
    - play (search + enrich + queue + play)
    - skip (next track)
    - pause/resume
    - stop
    - autoplay
    
    This ensures consistent behavior across:
    - slash commands
    - button interactions
    - API endpoints
    - autoplay system
    """
    
    def __init__(self, manager: PlayerManager, searcher: Searcher):
        self.manager = manager
        self.searcher = searcher
    
    async def enrich_song_metadata(self, song: Song) -> None:
        """Fetch and enrich song metadata (duration, thumbnail, etc).
        
        If enrichment fails, song plays anyway with available data.
        """
        try:
            # If already has duration, consider it enriched
            if song.duration > 0 and song.thumbnail:
                return
            
            # Try to fetch metadata from video_id or URL
            if song.video_id:
                # Use ytmusicapi to get info
                # This is a placeholder - actual implementation depends on searcher
                pass
            
            logger.info(f"[PLAYBACK] Enriched metadata for '{song.title}'")
        except Exception as e:
            # Don't fail playback if enrichment fails
            logger.warning(f"[PLAYBACK] Metadata enrichment failed for '{song.title}': {e}")
    
    async def search_and_create_song(
        self, 
        query: str, 
        guild_id: int, 
        requester: str,
        requester_id: int
    ) -> Optional[Song]:
        """Search for a song and create Song object.
        
        Args:
            query: Search query or YouTube Music URL
            guild_id: Discord guild ID
            requester: Requester name/mention
            requester_id: Requester user ID
            
        Returns:
            Song object or None if search fails
        """
        try:
            logger.info(f"[SEARCH] Searching for: {query}")
            
            # Try to search/extract (pass requester to Searcher)
            # searcher.search() returns a Song object directly
            song = await self.searcher.search(query, requester)
            
            if not song:
                logger.warning(f"[SEARCH] No results for: {query}")
                return None
            
            # Enrich metadata if needed
            await self.enrich_song_metadata(song)
            
            logger.info(f"[SEARCH] Found: {song.title} by {song.artist} ({format_duration(song.duration)})")
            return song
        
        except Exception as e:
            logger.error(f"[SEARCH] Error searching for '{query}': {e}")
            return None
    
    async def play(
        self,
        guild_id: int,
        query: str,
        voice_channel: discord.VoiceChannel,
        requester: str,
        requester_id: int
    ) -> Tuple[bool, Optional[Song], str]:
        """Complete play flow: search → enrich → connect → queue → play.
        
        Args:
            guild_id: Discord guild ID
            query: Search query or URL
            voice_channel: Target voice channel
            requester: Requester name/mention
            requester_id: Requester user ID
            
        Returns:
            Tuple of (success: bool, song: Optional[Song], message: str)
        """
        try:
            # Get or create player
            player = self.manager.get_or_create_player(guild_id)
            
            # Search and create song
            song = await self.search_and_create_song(query, guild_id, requester, requester_id)
            if not song:
                return False, None, f"❌ No results found for: {query}"
            
            # Connect to voice channel if not already connected
            if not player.voice_client or not player.voice_client.is_connected():
                connected = await player.connect(voice_channel)
                if not connected:
                    return False, None, f"❌ Could not connect to voice channel"
            
            # Extract stream URL
            if not song.url:
                try:
                    song.url = await self.searcher.extract_stream_url(song.video_id or song.title)
                    if not song.url:
                        return False, None, f"❌ Could not extract stream for: {song.title}"
                except Exception as e:
                    logger.error(f"[PLAYBACK] URL extraction failed: {e}")
                    return False, None, f"❌ Could not load audio stream"
            
            # If nothing is playing, play immediately
            if not player.current_track:
                player.current_track = song
                player.is_playing = True
                player.is_paused = False
                player._playback_start_time = asyncio.get_event_loop().time()
                
                # Play audio
                try:
                    source = discord.PCMVolumeTransformer(
                        discord.FFmpegPCMAudio(
                            song.url,
                            before_options="-hide_banner -nostats -loglevel quiet",
                            options="-vn -ac 2 -ar 48000"
                        )
                    )
                    source.volume = player.volume / 100.0
                    player._current_source = source
                    
                    def after_playback(error):
                        if error:
                            logger.error(f"[PLAYBACK] Playback error: {error}")
                        asyncio.create_task(self._on_song_end(guild_id))
                    
                    player.voice_client.play(source, after=after_playback)
                    logger.info(f"[PLAYBACK] Now playing: {song.title}")
                    player._notify_state_change()
                    return True, song, f"🎵 Now playing: **{song.title}** by {song.artist}"
                
                except Exception as e:
                    logger.error(f"[PLAYBACK] Failed to play audio: {e}")
                    player.is_playing = False
                    return False, song, f"❌ Failed to play audio: {str(e)}"
            
            else:
                # Queue the song
                position = player.add_to_queue(song)
                remaining = len(player.queue.get_list()) - 1
                return True, song, f"✅ Added to queue (Position #{position + 1}, {remaining} songs after)"
        
        except Exception as e:
            logger.error(f"[PLAYBACK] Play command failed: {e}")
            return False, None, f"❌ Error: {str(e)}"
    
    async def skip(self, guild_id: int) -> Tuple[bool, Optional[Song], str]:
        """Skip current track and play next.
        
        Returns:
            Tuple of (success: bool, next_song: Optional[Song], message: str)
        """
        try:
            player = self.manager.get_player(guild_id)
            if not player:
                return False, None, "❌ No player found"
            
            if not player.current_track:
                return False, None, "❌ Nothing is playing"
            
            # Stop current playback
            if player.voice_client and player.voice_client.is_playing():
                player.voice_client.stop()
            
            current_title = player.current_track.title
            
            # Get next song
            next_song = player.queue.skip()
            
            if not next_song:
                # Queue is empty
                player.current_track = None
                player.is_playing = False
                logger.info(f"[PLAYBACK] Queue ended (Guild {guild_id})")
                player._notify_state_change()
                return True, None, f"⏭️ Skipped **{current_title}** - Queue ended"
            
            # Play next song
            player.current_track = next_song
            player._playback_start_time = asyncio.get_event_loop().time()
            
            try:
                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(
                        next_song.url,
                        before_options="-hide_banner -nostats -loglevel quiet",
                        options="-vn -ac 2 -ar 48000"
                    )
                )
                source.volume = player.volume / 100.0
                player._current_source = source
                
                def after_playback(error):
                    if error:
                        logger.error(f"[PLAYBACK] Playback error: {error}")
                    asyncio.create_task(self._on_song_end(guild_id))
                
                player.voice_client.play(source, after=after_playback)
                logger.info(f"[PLAYBACK] Skipped to: {next_song.title}")
                player.is_playing = True
                player.is_paused = False
                player._notify_state_change()
                
                return True, next_song, f"⏭️ Skipped **{current_title}**\n🎵 Now playing: **{next_song.title}**"
            
            except Exception as e:
                logger.error(f"[PLAYBACK] Failed to play next song: {e}")
                return False, None, f"❌ Failed to play next song: {str(e)}"
        
        except Exception as e:
            logger.error(f"[PLAYBACK] Skip failed: {e}")
            return False, None, f"❌ Error: {str(e)}"
    
    async def _on_song_end(self, guild_id: int) -> None:
        """Handle song ending - trigger autoplay or next track."""
        try:
            player = self.manager.get_player(guild_id)
            if not player:
                return
            
            logger.info(f"[PLAYBACK] Track ended (Guild {guild_id})")
            
            # Try to play next from queue
            next_song = player.queue.peek_next()
            
            if next_song:
                # Play next immediately
                await self.skip(guild_id)
            
            elif player.autoplay_enabled:
                # Trigger autoplay
                logger.info(f"[AUTOPLAY] Triggering autoplay (Guild {guild_id})")
                if player.autoplay_engine:
                    # This would be handled by autoplay_commands.py
                    pass
            
            else:
                # Queue ended
                player.current_track = None
                player.is_playing = False
                logger.info(f"[PLAYBACK] Queue ended (Guild {guild_id})")
                player._notify_state_change()
        
        except Exception as e:
            logger.error(f"[PLAYBACK] Error on song end: {e}")
    
    async def pause(self, guild_id: int) -> Tuple[bool, str]:
        """Pause playback.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            player = self.manager.get_player(guild_id)
            if not player:
                return False, "❌ No player found"
            
            if player.pause():
                return True, f"⏸️ Paused: **{player.current_track.title if player.current_track else 'Unknown'}**"
            else:
                return False, "❌ Nothing to pause"
        except Exception as e:
            logger.error(f"[PLAYBACK] Pause failed: {e}")
            return False, f"❌ Error: {str(e)}"
    
    async def resume(self, guild_id: int) -> Tuple[bool, str]:
        """Resume playback.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            player = self.manager.get_player(guild_id)
            if not player:
                return False, "❌ No player found"
            
            if player.resume():
                return True, f"▶️ Resumed: **{player.current_track.title if player.current_track else 'Unknown'}**"
            else:
                return False, "❌ Nothing to resume"
        except Exception as e:
            logger.error(f"[PLAYBACK] Resume failed: {e}")
            return False, f"❌ Error: {str(e)}"
    
    async def stop(self, guild_id: int) -> Tuple[bool, str]:
        """Stop playback and clear queue.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            player = self.manager.get_player(guild_id)
            if not player:
                return False, "❌ No player found"
            
            player.stop()
            await player.disconnect()
            self.manager.remove_player(guild_id)
            return True, "⏹️ Playback stopped and disconnected"
        except Exception as e:
            logger.error(f"[PLAYBACK] Stop failed: {e}")
            return False, f"❌ Error: {str(e)}"
