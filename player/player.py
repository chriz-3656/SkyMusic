import asyncio
import logging
from typing import Optional
import discord
from discord.ext import commands

from .queue import Queue, Song
from .searcher import Searcher

logger = logging.getLogger(__name__)


class Player:
    """Manages audio playback in Discord voice channels."""
    
    def __init__(self, guild_id: int, searcher: Searcher, autoplay_engine=None):
        self.guild_id = guild_id
        self.queue = Queue(guild_id)
        self.searcher = searcher
        self.autoplay_engine = autoplay_engine  # V4: Autoplay
        
        self.voice_client: Optional[discord.VoiceClient] = None
        self.current_song: Optional[Song] = None
        self.is_playing: bool = False
        self.is_paused: bool = False
        self._current_source: Optional[discord.PCMVolumeTransformer] = None
        
        # V3: Interactive features
        self.volume: int = 100
        self.loop_mode: str = 'off'  # off, song, queue
        self.favorites: list = []
        
        # V4: Autoplay features
        self.autoplay_enabled: bool = False
    
    async def connect(self, voice_channel: discord.VoiceChannel) -> bool:
        """Connect to a voice channel."""
        try:
            self.voice_client = await voice_channel.connect()
            logger.info(f"Connected to {voice_channel.name} in guild {self.guild_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to voice channel: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from voice channel."""
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
            self.is_playing = False
            self.is_paused = False
            logger.info(f"Disconnected from guild {self.guild_id}")
    
    async def play_song(self, song: Song) -> bool:
        """Play a song."""
        if not self.voice_client or not self.voice_client.is_connected():
            logger.warning(f"Not connected to voice in guild {self.guild_id}")
            return False
        
        try:
            # Ensure song has a valid URL
            if not song.url or song.url == '':
                logger.warning(f"Song missing URL, trying to fetch: {song.title}")
                video_id = getattr(song, 'video_id', None)
                if video_id:
                    url = await self.searcher.extract_stream_url(video_id)
                    if url:
                        song.url = url
                    else:
                        logger.error(f"Failed to fetch URL for {song.title}")
                        return False
                else:
                    logger.error(f"No video_id available for {song.title}")
                    return False
            
            # Create audio source with FFmpeg
            # FFmpeg will output PCM audio to stdout, discord.py handles the rest
            audio_source = discord.FFmpegPCMAudio(
                song.url,
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                options="-vn -c:a pcm_s16le -ar 48000 -ac 2"
            )
            
            audio_source = discord.PCMVolumeTransformer(audio_source)
            
            # Define callback for when song finishes
            def after_playing(error):
                if error:
                    logger.error(f"Playback error: {error}")
                asyncio.run_coroutine_threadsafe(
                    self._on_song_end(),
                    self.voice_client.loop
                )
            
            self.voice_client.play(audio_source, after=after_playing)
            self.current_song = song
            self.is_playing = True
            self.is_paused = False
            self._current_source = audio_source
            
            logger.info(f"Now playing: {song.title} in guild {self.guild_id}")
            return True
        
        except Exception as e:
            logger.error(f"Playback error for {song.title}: {e}")
            return False
    
    async def _on_song_end(self):
        """Called when current song finishes."""
        self.is_playing = False
        current_song_backup = self.current_song  # Save for autoplay
        self.current_song = None
        
        # Auto-play next song
        next_song = self.queue.get_next()
        if next_song:
            # Ensure song has URL before playing
            if not next_song.url or next_song.url == '':
                logger.info(f"Fetching URL for: {next_song.title}")
                video_id = getattr(next_song, 'video_id', None)
                if video_id:
                    url = await self.searcher.extract_stream_url(video_id)
                    if url:
                        next_song.url = url
                    else:
                        logger.error(f"Failed to fetch URL for {next_song.title}")
                        # Skip to next song
                        await self._on_song_end()
                        return
            await self.play_song(next_song)
        else:
            # V4: Autoplay - fetch recommendations if enabled
            if self.autoplay_enabled and current_song_backup and self.autoplay_engine:
                try:
                    logger.info(f"Autoplay triggered for guild {self.guild_id}")
                    recommendations = await self.autoplay_engine.get_recommendations(
                        current_song_backup,
                        limit=8
                    )
                    
                    if recommendations:
                        logger.info(f"Autoplay: Adding {len(recommendations)} recommendations")
                        for rec in recommendations:
                            self.queue.add(rec)
                        
                        # Play first recommendation
                        next_song = self.queue.get_next()
                        if next_song:
                            logger.info(f"Autoplay: Starting playback of {next_song.title}")
                            # Fetch URL for autoplay recommendation
                            if not next_song.url or next_song.url == '':
                                video_id = getattr(next_song, 'video_id', None)
                                if video_id:
                                    url = await self.searcher.extract_stream_url(video_id)
                                    if url:
                                        next_song.url = url
                                    else:
                                        logger.error(f"Failed to fetch URL for {next_song.title}")
                                        # Skip this song
                                        await self._on_song_end()
                                        return
                            await self.play_song(next_song)
                    else:
                        logger.warning(f"Autoplay: No recommendations found for {current_song_backup.title}")
                except Exception as e:
                    logger.error(f"Autoplay error: {e}")
            else:
                logger.info(f"Queue ended for guild {self.guild_id}")
    
    def pause(self) -> bool:
        """Pause playback."""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            self.is_paused = True
            logger.info(f"Paused playback in guild {self.guild_id}")
            return True
        return False
    
    def resume(self) -> bool:
        """Resume playback."""
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            self.is_paused = False
            logger.info(f"Resumed playback in guild {self.guild_id}")
            return True
        return False
    
    def stop(self) -> bool:
        """Stop playback and clear queue."""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_song = None
        self.queue.clear()
        logger.info(f"Stopped playback in guild {self.guild_id}")
        return True
    
    async def skip(self) -> Optional[Song]:
        """Skip current song and play next."""
        if not self.voice_client:
            return None
        
        if self.voice_client.is_playing() or self.voice_client.is_paused():
            self.voice_client.stop()
        
        next_song = self.queue.get_next()
        if next_song:
            await self.play_song(next_song)
            logger.info(f"Skipped to: {next_song.title} in guild {self.guild_id}")
        else:
            self.is_playing = False
            self.current_song = None
            logger.info(f"No more songs in queue for guild {self.guild_id}")
        
        return next_song
    
    async def add_to_queue(self, query: str, requester: str) -> Optional[Song]:
        """Search for and add song to queue."""
        try:
            song = await self.searcher.search(query, requester)
            if song:
                self.queue.add(song)
                
                # If nothing is playing, start playback
                if not self.is_playing and self.voice_client:
                    next_song = self.queue.get_next()
                    if next_song:
                        await self.play_song(next_song)
                
                return song
            return None
        except Exception as e:
            logger.error(f"Error adding to queue: {e}")
            return None
    
    def get_queue_list(self) -> list[Song]:
        """Get list of songs in queue."""
        return self.queue.get_list()
    
    def get_queue_size(self) -> int:
        """Get queue size."""
        return self.queue.size()
    
    def get_current_song(self) -> Optional[Song]:
        """Get currently playing song."""
        return self.current_song
    
    async def pause_song(self) -> bool:
        """Async wrapper for pause."""
        return self.pause()
    
    async def resume_song(self) -> bool:
        """Async wrapper for resume."""
        return self.resume()
    
    async def stop_song(self) -> bool:
        """Async wrapper for stop."""
        return self.stop()
    
    async def skip_song(self) -> Optional[Song]:
        """Async wrapper for skip."""
        return await self.skip()
    
    async def set_volume(self, volume: int) -> bool:
        """
        Set volume by percentage (0-100).
        
        Args:
            volume: Volume percentage (0-100)
        
        Returns:
            True if successful
        """
        # Convert percentage to discord.py volume (0.0-2.0)
        discord_volume = (volume / 100.0) * 2.0
        if self._current_source:
            self._current_source.volume = max(0.0, min(2.0, discord_volume))
            self.volume = volume
            logger.info(f"Set volume to {volume}% in guild {self.guild_id}")
            return True
        return False
