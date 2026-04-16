import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from state.shared import get_player, get_bot
from .models import (
    NowPlayingResponse, QueueResponse, QueueItemResponse,
    SongResponse, StatusResponse, ActionResponse,
    VolumeRequest, AutoplayRequest, LoopRequest
)

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure FastAPI app."""
    app = FastAPI(title="Music Bot API", version="1.0.0")
    
    # CORS middleware
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
        from state.shared import get_all_players
        players = get_all_players()
        if players:
            return list(players.keys())[0]  # Return first active guild
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
            is_paused=player.is_paused
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
        
        return {"enabled": player.autoplay_enabled}
    
    @app.post("/api/volume", response_model=ActionResponse)
    async def set_volume(request: VolumeRequest):
        """Set volume level (0-100)."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        if not 0 <= request.level <= 100:
            raise HTTPException(status_code=400, detail="Volume must be between 0 and 100")
        
        player.set_volume(request.level)
        return ActionResponse(success=True, message=f"Volume set to {request.level}%")
    
    @app.get("/api/volume")
    async def get_volume():
        """Get current volume level."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            return {"volume": 100}
        
        return {"volume": player.volume}
    
    @app.post("/api/loop", response_model=ActionResponse)
    async def toggle_loop(request: LoopRequest):
        """Toggle loop mode (off, song, queue)."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        if request.mode:
            if request.mode not in ('off', 'song', 'queue'):
                raise HTTPException(status_code=400, detail="Invalid loop mode")
            player.loop_mode = request.mode
        else:
            # Cycle through modes
            modes = ['off', 'song', 'queue']
            current_idx = modes.index(player.loop_mode)
            player.loop_mode = modes[(current_idx + 1) % len(modes)]
        
        return ActionResponse(success=True, message=f"Loop mode: {player.loop_mode}")
    
    @app.get("/api/loop")
    async def get_loop_status():
        """Get current loop mode."""
        guild_id = get_active_guild_id()
        player = get_player(guild_id)
        
        if not player:
            return {"mode": "off"}
        
        return {"mode": player.loop_mode}
    
    @app.get("/api/health")
    async def health():
        """Health check."""
        return {"status": "ok"}
    
    # Serve static files
    try:
        app.mount("/", StaticFiles(directory="web", html=True), name="static")
    except Exception as e:
        logger.warning(f"Could not mount static files: {e}")
    
    return app
