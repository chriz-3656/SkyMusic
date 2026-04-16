import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import time

from state.shared import get_player, get_bot, get_all_players
from .models import (
    NowPlayingResponse, QueueResponse, QueueItemResponse,
    SongResponse, StatusResponse, ActionResponse, BotStatsResponse,
    VolumeRequest, AutoplayRequest, LoopRequest
)

logger = logging.getLogger(__name__)

# Track bot start time
_bot_start_time = time.time()


def create_app():
    """Create and configure FastAPI app."""
    app = FastAPI(title="Music Bot API", version="1.0.0")
    
    # CORS middleware - allow all origins (frontend can be on any origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # API Routes
    
    def get_active_guild_id():
        """Get the first active guild ID."""
        players = get_all_players()
        if players:
            return list(players.keys())[0]
        return 0
    
    @app.get("/api/status", response_model=StatusResponse)
    async def get_status():
        """Get current status."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            return StatusResponse(
                connected=False,
                queue_size=0,
                is_playing=False,
                is_paused=False
            )
        
        return StatusResponse(
            connected=player.voice_client is not None,
            now_playing=SongResponse(
                title=player.current_song.title,
                artist=player.current_song.artist,
                duration=player.current_song.duration,
                requester=player.current_song.requester,
                thumbnail=getattr(player.current_song, 'thumbnail', None),
                video_id=getattr(player.current_song, 'video_id', None)
            ) if player.current_song else None,
            queue_size=player.get_queue_size(),
            is_playing=player.is_playing,
            is_paused=player.is_paused
        )
    
    @app.get("/api/now-playing", response_model=NowPlayingResponse)
    async def get_now_playing():
        """Get currently playing song."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player or not player.current_song:
            return NowPlayingResponse(is_playing=False, is_paused=False)
        
        return NowPlayingResponse(
            song=SongResponse(
                title=player.current_song.title,
                artist=player.current_song.artist,
                duration=player.current_song.duration,
                requester=player.current_song.requester,
                thumbnail=getattr(player.current_song, 'thumbnail', None),
                video_id=getattr(player.current_song, 'video_id', None)
            ),
            is_playing=player.is_playing,
            is_paused=player.is_paused,
            volume=getattr(player, 'volume', 100)
        )
    
    @app.get("/api/queue", response_model=QueueResponse)
    async def get_queue():
        """Get queue list."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            return QueueResponse(queue=[], total_songs=0)
        
        queue_list = player.get_queue_list()
        queue_items = [
            QueueItemResponse(
                index=i,
                song=SongResponse(
                    title=song.title,
                    artist=song.artist,
                    duration=song.duration,
                    requester=song.requester,
                    thumbnail=getattr(song, 'thumbnail', None),
                    video_id=getattr(song, 'video_id', None)
                )
            )
            for i, song in enumerate(queue_list)
        ]
        
        return QueueResponse(
            current_song=SongResponse(
                title=player.current_song.title,
                artist=player.current_song.artist,
                duration=player.current_song.duration,
                requester=player.current_song.requester,
                thumbnail=getattr(player.current_song, 'thumbnail', None),
                video_id=getattr(player.current_song, 'video_id', None)
            ) if player.current_song else None,
            queue=queue_items,
            total_songs=len(queue_list)
        )
    
    @app.post("/api/pause", response_model=ActionResponse)
    async def pause_playback():
        """Pause playback."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        if player.pause():
            return ActionResponse(success=True, message="Playback paused")
        return ActionResponse(success=False, message="Could not pause playback")
    
    @app.post("/api/resume", response_model=ActionResponse)
    async def resume_playback():
        """Resume playback."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        if player.resume():
            return ActionResponse(success=True, message="Playback resumed")
        return ActionResponse(success=False, message="Could not resume playback")
    
    @app.post("/api/skip", response_model=ActionResponse)
    async def skip_song():
        """Skip current song."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        next_song = await player.skip()
        if next_song:
            return ActionResponse(
                success=True,
                message=f"Skipped to: {next_song.title}"
            )
        return ActionResponse(success=True, message="Queue ended")
    
    @app.post("/api/stop", response_model=ActionResponse)
    async def stop_playback():
        """Stop playback."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        player.stop()
        await player.disconnect()
        
        return ActionResponse(success=True, message="Playback stopped")
    
    @app.post("/api/autoplay", response_model=ActionResponse)
    async def toggle_autoplay(request: AutoplayRequest):
        """Toggle autoplay."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        player.autoplay_enabled = request.enabled
        status = "enabled" if request.enabled else "disabled"
        return ActionResponse(success=True, message=f"Autoplay {status}")
    
    @app.get("/api/autoplay")
    async def get_autoplay_status():
        """Get autoplay status."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            return {"enabled": False}
        
        return {"enabled": getattr(player, 'autoplay_enabled', False)}
    
    @app.post("/api/volume", response_model=ActionResponse)
    async def set_volume(request: VolumeRequest):
        """Set volume level (0-100)."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Support both 'level' and 'volume' parameter names
        volume = request.level if request.level is not None else request.volume
        if volume is None:
            raise HTTPException(status_code=400, detail="Volume level required")
        
        if not 0 <= volume <= 100:
            raise HTTPException(status_code=400, detail="Volume must be between 0 and 100")
        
        player.set_volume(volume)
        return ActionResponse(success=True, message=f"Volume set to {volume}%")
    
    @app.get("/api/volume")
    async def get_volume():
        """Get current volume level."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            return {"volume": 100}
        
        return {"volume": getattr(player, 'volume', 100)}
    
    @app.post("/api/loop", response_model=ActionResponse)
    async def toggle_loop(request: Optional[LoopRequest] = None):
        """Toggle loop mode (off, song, queue)."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        if request and request.mode:
            if request.mode not in ('off', 'song', 'queue'):
                raise HTTPException(status_code=400, detail="Invalid loop mode")
            player.loop_mode = request.mode
        else:
            # Cycle through modes
            modes = ['off', 'song', 'queue']
            current_mode = getattr(player, 'loop_mode', 'off')
            try:
                current_idx = modes.index(current_mode)
            except ValueError:
                current_idx = 0
            player.loop_mode = modes[(current_idx + 1) % len(modes)]
        
        return ActionResponse(success=True, message=f"Loop mode: {player.loop_mode}")
    
    @app.get("/api/loop")
    async def get_loop_status():
        """Get current loop mode."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            return {"mode": "off"}
        
        return {"mode": getattr(player, 'loop_mode', 'off')}
    
    @app.post("/api/shuffle", response_model=ActionResponse)
    async def toggle_shuffle():
        """Toggle shuffle."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        current_shuffle = getattr(player, 'shuffle_enabled', False)
        player.shuffle_enabled = not current_shuffle
        status = "enabled" if player.shuffle_enabled else "disabled"
        return ActionResponse(success=True, message=f"Shuffle {status}")
    
    @app.get("/api/shuffle")
    async def get_shuffle_status():
        """Get shuffle status."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            return {"enabled": False}
        
        return {"enabled": getattr(player, 'shuffle_enabled', False)}
    
    @app.post("/api/queue/clear", response_model=ActionResponse)
    async def clear_queue():
        """Clear entire queue."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Clear the queue
        if hasattr(player, 'queue'):
            player.queue.queue.clear()
        
        return ActionResponse(success=True, message="Queue cleared")
    
    @app.post("/api/queue/remove/{index}", response_model=ActionResponse)
    async def remove_from_queue(index: int):
        """Remove song from queue at index."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        try:
            if hasattr(player, 'queue'):
                queue_list = player.get_queue_list()
                if 0 <= index < len(queue_list):
                    player.queue.queue.pop(index)
                    return ActionResponse(success=True, message=f"Removed song at index {index}")
        except Exception as e:
            pass
        
        return ActionResponse(success=False, message="Could not remove song")
    
    @app.post("/api/seek", response_model=ActionResponse)
    async def seek(request: dict):
        """Seek to position."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Seeking is not fully implemented, but we accept the request
        return ActionResponse(success=True, message="Seek request received")
    
    @app.get("/api/bot/stats", response_model=BotStatsResponse)
    async def get_bot_stats():
        """Get bot statistics."""
        bot = get_bot()
        players = get_all_players()
        
        # Calculate uptime
        uptime_seconds = time.time() - _bot_start_time
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        uptime_str = f"{hours}h {minutes}m"
        
        # Count active servers and users
        total_servers = len(players) if players else 0
        playing_now = sum(1 for p in (players.values() if players else []) if getattr(p, 'is_playing', False))
        total_users = 0
        if bot:
            total_users = sum(len(guild.members) for guild in bot.guilds)
        
        return BotStatsResponse(
            uptime=uptime_str,
            total_servers=total_servers,
            total_users=total_users,
            playing_now=playing_now
        )
    
    @app.get("/api/health")
    async def health():
        """Health check."""
        return {"status": "ok"}
    
    # Serve static files (web dashboard)
    try:
        app.mount("/", StaticFiles(directory="web", html=True), name="static")
    except Exception as e:
        logger.warning(f"Could not mount static files: {e}")
    
    return app
