"""
SkyMusic V8 - Central Player Manager
Manages per-guild player instances with unified state and callbacks.
"""

import asyncio
import logging
from typing import Dict, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
import discord

from .queue import Queue, Song
from .searcher import Searcher
from .autoplay import AutoplayEngine

logger = logging.getLogger(__name__)


@dataclass
class StateSnapshot:
    """Immutable snapshot of player state for UI sync."""
    guild_id: int
    current_track: Optional[Song]
    queue: List[Song]
    volume: int
    loop_mode: str
    autoplay_enabled: bool
    is_playing: bool
    is_paused: bool
    position: int  # Current playback position in seconds
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        """Convert to dictionary for API/UI consumption."""
        return {
            'guild_id': self.guild_id,
            'current_track': {
                'title': self.current_track.title,
                'artist': self.current_track.artist,
                'duration': self.current_track.duration,
                'requester': self.current_track.requester,
                'thumbnail': getattr(self.current_track, 'thumbnail', None),
                'video_id': getattr(self.current_track, 'video_id', None),
                'url': self.current_track.url,
            } if self.current_track else None,
            'queue': [
                {
                    'title': song.title,
                    'artist': song.artist,
                    'duration': song.duration,
                    'requester': song.requester,
                } for song in self.queue
            ],
            'volume': self.volume,
            'loop_mode': self.loop_mode,
            'autoplay_enabled': self.autoplay_enabled,
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'position': self.position,
        }


class PlayerInstance:
    """Per-guild player instance with complete state isolation."""
    
    def __init__(self, guild_id: int, searcher: Searcher, autoplay_engine: Optional[AutoplayEngine] = None):
        self.guild_id = guild_id
        self.searcher = searcher
        self.autoplay_engine = autoplay_engine
        
        # State
        self.queue = Queue(guild_id)
        self.current_track: Optional[Song] = None
        self.volume: int = 100
        self.loop_mode: str = 'off'  # off, song, queue
        self.autoplay_enabled: bool = False
        
        # Playback state
        self.voice_client: Optional[discord.VoiceClient] = None
        self.is_playing: bool = False
        self.is_paused: bool = False
        self._current_source: Optional[discord.PCMVolumeTransformer] = None
        self._playback_start_time: Optional[float] = None
        
        # UI
        self.control_panel_message: Optional[discord.Message] = None
        
        # Callbacks for state changes
        self.state_change_callbacks: List[Callable[[StateSnapshot], None]] = []
    
    @property
    def current_song(self) -> Optional[Song]:
        """Backward compatibility property - returns current_track."""
        return self.current_track
    
    @current_song.setter
    def current_song(self, value: Optional[Song]):
        """Backward compatibility setter - sets current_track."""
        self.current_track = value
    
    def register_state_change_callback(self, callback: Callable[['StateSnapshot'], None]):
        """Register a callback to be called when state changes."""
        self.state_change_callbacks.append(callback)
    
    def get_state_snapshot(self) -> StateSnapshot:
        """Get current state as immutable snapshot."""
        return StateSnapshot(
            guild_id=self.guild_id,
            current_track=self.current_track,
            queue=self.queue.get_list(),
            volume=self.volume,
            loop_mode=self.loop_mode,
            autoplay_enabled=self.autoplay_enabled,
            is_playing=self.is_playing,
            is_paused=self.is_paused,
            position=self._get_playback_position(),
        )
    
    def _notify_state_change(self):
        """Notify all callbacks of state change."""
        snapshot = self.get_state_snapshot()
        for callback in self.state_change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(snapshot))
                else:
                    callback(snapshot)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")
    
    def _get_playback_position(self) -> int:
        """Get current playback position in seconds."""
        if not self.is_playing or not self._playback_start_time:
            return 0
        elapsed = asyncio.get_event_loop().time() - self._playback_start_time
        return int(elapsed)
    
    async def connect(self, voice_channel: discord.VoiceChannel) -> bool:
        """Connect to voice channel."""
        try:
            self.voice_client = await voice_channel.connect()
            logger.info(f"[PLAYER] Connected to {voice_channel.name} (Guild {self.guild_id})")
            self._notify_state_change()
            return True
        except Exception as e:
            logger.error(f"[PLAYER] Failed to connect: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from voice channel."""
        try:
            if self.voice_client:
                await self.voice_client.disconnect()
                self.voice_client = None
                self.is_playing = False
                self.is_paused = False
                logger.info(f"[PLAYER] Disconnected (Guild {self.guild_id})")
                self._notify_state_change()
        except Exception as e:
            logger.error(f"[PLAYER] Disconnect error: {e}")
    
    def set_volume(self, level: int) -> None:
        """Set playback volume (0-100)."""
        self.volume = max(0, min(100, level))
        if self._current_source:
            self._current_source.volume = self.volume / 100.0
        logger.info(f"[PLAYER] Volume set to {self.volume}% (Guild {self.guild_id})")
        self._notify_state_change()
    
    def set_loop_mode(self, mode: str) -> None:
        """Set loop mode: off, song, queue."""
        if mode in ('off', 'song', 'queue'):
            self.loop_mode = mode
            logger.info(f"[PLAYER] Loop mode: {mode} (Guild {self.guild_id})")
            self._notify_state_change()
    
    def toggle_autoplay(self) -> bool:
        """Toggle autoplay on/off."""
        self.autoplay_enabled = not self.autoplay_enabled
        logger.info(f"[PLAYER] Autoplay {'enabled' if self.autoplay_enabled else 'disabled'} (Guild {self.guild_id})")
        self._notify_state_change()
        return self.autoplay_enabled
    
    def get_queue_size(self) -> int:
        """Get size of queue."""
        return self.queue.size()
    
    def get_queue_list(self) -> List[Song]:
        """Get list of all songs in queue."""
        return self.queue.get_list()
    
    def add_to_queue(self, song: Song) -> int:
        """Add song to queue. Returns queue position."""
        position = self.queue.add(song)
        logger.info(f"[PLAYER] Added '{song.title}' to queue (Position {position}, Guild {self.guild_id})")
        self._notify_state_change()
        return position
    
    def remove_from_queue(self, index: int) -> Optional[Song]:
        """Remove song from queue."""
        song = self.queue.remove(index)
        if song:
            logger.info(f"[PLAYER] Removed '{song.title}' from queue (Guild {self.guild_id})")
            self._notify_state_change()
        return song
    
    def pause(self) -> bool:
        """Pause playback."""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            self.is_paused = True
            self.is_playing = False
            logger.info(f"[PLAYER] Paused (Guild {self.guild_id})")
            self._notify_state_change()
            return True
        return False
    
    def resume(self) -> bool:
        """Resume playback."""
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            self.is_paused = False
            self.is_playing = True
            logger.info(f"[PLAYER] Resumed (Guild {self.guild_id})")
            self._notify_state_change()
            return True
        return False
    
    def stop(self) -> None:
        """Stop playback."""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_track = None
        self.queue.clear()
        logger.info(f"[PLAYER] Stopped (Guild {self.guild_id})")
        self._notify_state_change()


class PlayerManager:
    """Central manager for all player instances (singleton)."""
    
    _instance: Optional['PlayerManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlayerManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.players: Dict[int, PlayerInstance] = {}
        self.searcher: Optional[Searcher] = None
        self.autoplay_engine: Optional[AutoplayEngine] = None
        self._initialized = True
        logger.info("[MANAGER] PlayerManager initialized")
    
    def set_searcher(self, searcher: Searcher) -> None:
        """Set the searcher instance."""
        self.searcher = searcher
    
    def set_autoplay_engine(self, engine: AutoplayEngine) -> None:
        """Set the autoplay engine."""
        self.autoplay_engine = engine
    
    def get_or_create_player(self, guild_id: int) -> PlayerInstance:
        """Get existing player or create new one."""
        if guild_id not in self.players:
            if not self.searcher:
                raise RuntimeError("Searcher not set on PlayerManager")
            
            player = PlayerInstance(
                guild_id=guild_id,
                searcher=self.searcher,
                autoplay_engine=self.autoplay_engine
            )
            self.players[guild_id] = player
            logger.info(f"[MANAGER] Created player for guild {guild_id}")
        
        return self.players[guild_id]
    
    def get_player(self, guild_id: int) -> Optional[PlayerInstance]:
        """Get player for a guild, or None if doesn't exist."""
        return self.players.get(guild_id)
    
    def remove_player(self, guild_id: int) -> bool:
        """Remove player for a guild."""
        if guild_id in self.players:
            del self.players[guild_id]
            logger.info(f"[MANAGER] Removed player for guild {guild_id}")
            return True
        return False
    
    def get_all_players(self) -> Dict[int, PlayerInstance]:
        """Get all active players."""
        return self.players.copy()
    
    def get_active_player_count(self) -> int:
        """Get number of active players."""
        return len(self.players)
    
    async def shutdown(self) -> None:
        """Disconnect all players."""
        logger.info(f"[MANAGER] Shutting down {len(self.players)} players...")
        for guild_id, player in list(self.players.items()):
            try:
                await player.disconnect()
            except Exception as e:
                logger.error(f"[MANAGER] Error disconnecting guild {guild_id}: {e}")
        self.players.clear()
        logger.info("[MANAGER] All players disconnected")
