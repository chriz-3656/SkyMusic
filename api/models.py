from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SongResponse(BaseModel):
    """Song response model."""
    title: str
    artist: str
    duration: int
    requester: str
    thumbnail: Optional[str] = None
    video_id: Optional[str] = None


class NowPlayingResponse(BaseModel):
    """Now playing response."""
    song: Optional[SongResponse] = None
    is_playing: bool
    is_paused: bool
    position: int = 0
    volume: int = 100


class QueueItemResponse(BaseModel):
    """Queue item response."""
    index: int
    song: SongResponse


class QueueResponse(BaseModel):
    """Queue response."""
    current_song: Optional[SongResponse] = None
    queue: List[QueueItemResponse]
    total_songs: int


class StatusResponse(BaseModel):
    """General status response."""
    connected: bool
    now_playing: Optional[SongResponse] = None
    queue_size: int
    is_playing: bool
    is_paused: bool


class ActionResponse(BaseModel):
    """Response for action commands."""
    success: bool
    message: str


class BotStatsResponse(BaseModel):
    """Bot statistics response."""
    uptime: str = "-"
    total_servers: int = 0
    total_users: int = 0
    playing_now: int = 0


# Request models
class VolumeRequest(BaseModel):
    """Volume control request."""
    level: Optional[int] = None
    volume: Optional[int] = None


class AutoplayRequest(BaseModel):
    """Autoplay toggle request."""
    enabled: bool


class LoopRequest(BaseModel):
    """Loop mode request."""
    mode: Optional[str] = None
