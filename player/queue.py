from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Song:
    """Represents a song in the queue."""
    title: str
    url: str
    duration: int  # in seconds
    requester: str
    artist: str = "Unknown"
    
    def __str__(self):
        return f"{self.title} by {self.artist}"


class Queue:
    """Per-guild queue management."""
    
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.songs: list[Song] = []
        self.current_index: int = -1
    
    def add(self, song: Song) -> int:
        """Add a song to queue. Returns position in queue."""
        self.songs.append(song)
        return len(self.songs) - 1
    
    def remove(self, index: int) -> Optional[Song]:
        """Remove song at index. Adjust current_index if needed."""
        if 0 <= index < len(self.songs):
            song = self.songs.pop(index)
            if self.current_index > index:
                self.current_index -= 1
            elif self.current_index == index:
                self.current_index = -1
            return song
        return None
    
    def clear(self):
        """Clear the entire queue."""
        self.songs.clear()
        self.current_index = -1
    
    def get_current(self) -> Optional[Song]:
        """Get currently playing song."""
        if 0 <= self.current_index < len(self.songs):
            return self.songs[self.current_index]
        return None
    
    def get_next(self) -> Optional[Song]:
        """Get next song and advance index."""
        if self.current_index + 1 < len(self.songs):
            self.current_index += 1
            return self.songs[self.current_index]
        return None
    
    def peek_next(self) -> Optional[Song]:
        """Peek at next song without advancing."""
        if self.current_index + 1 < len(self.songs):
            return self.songs[self.current_index + 1]
        return None
    
    def skip(self) -> Optional[Song]:
        """Skip current song and play next."""
        return self.get_next()
    
    def get_list(self) -> list[Song]:
        """Get all songs in queue."""
        return self.songs.copy()
    
    def size(self) -> int:
        """Get queue size."""
        return len(self.songs)
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self.songs) == 0
