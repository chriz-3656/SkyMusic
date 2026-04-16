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
    position: int = 0  # Current playback position in seconds
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


# Request models
class VolumeRequest(BaseModel):
    """Volume control request."""
    level: int


class AutoplayRequest(BaseModel):
    """Autoplay toggle request."""
    enabled: bool


class LoopRequest(BaseModel):
    """Loop mode request."""
    mode: Optional[str] = None
