from bot.utils.emojis import MUSIC, PLAY, VOL_UP, SUCCESS, ERROR
"""Embed builder utilities for SkyMusic bot."""

import discord
from datetime import datetime
from typing import Optional, List
from .colors import PURPLE, SUCCESS, ERROR, FOOTER_TEXT

def format_duration(seconds: int) -> str:
    """Format seconds to MM:SS format."""
    if seconds <= 0:
        return "0:00"
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def create_progress_bar(current: int, total: int, length: int = 20) -> str:
    """
    Create a text-based progress bar.
    
    Args:
        current: Current position in seconds
        total: Total duration in seconds
        length: Length of the progress bar
    
    Returns:
        String like "████░░░░ 1:23 / 3:45"
    """
    if total <= 0:
        return "░" * length + f" {format_duration(current)} / 0:00"
    
    filled = int((current / total) * length)
    bar = "█" * filled + "░" * (length - filled)
    current_time = format_duration(current)
    total_time = format_duration(total)
    
    return f"{bar} {current_time} / {total_time}"


def create_now_playing_embed(
    title: str,
    artist: str = "Unknown Artist",
    duration: int = 0,
    requester: str = "Unknown",
    thumbnail: Optional[str] = None,
    current_position: int = 0,
    queue_length: int = 0,
    volume: int = 100,
) -> discord.Embed:
    """
    Create a rich Now Playing embed.
    
    Args:
        title: Song title
        artist: Artist/channel name
        duration: Duration in seconds
        requester: User who requested the song
        thumbnail: URL to song thumbnail
        current_position: Current playback position in seconds
        queue_length: Number of songs in queue
        volume: Volume level (0-100)
    
    Returns:
        discord.Embed object
    """
    embed = discord.Embed(
        title=f"{MUSIC} Now Playing",
        description=f"**{title}**",
        color=PURPLE,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="Artist",
        value=artist,
        inline=True
    )
    
    embed.add_field(
        name="Duration",
        value=format_duration(duration),
        inline=True
    )
    
    progress = create_progress_bar(current_position, duration)
    embed.add_field(
        name="Progress",
        value=f"`{progress}`",
        inline=False
    )
    
    embed.add_field(
        name="Requested by",
        value=requester,
        inline=True
    )
    
    embed.add_field(
        name="Queue",
        value=f"{queue_length} song{'s' if queue_length != 1 else ''} remaining",
        inline=True
    )
    
    embed.add_field(
        name="Volume",
        value=f"{VOL_UP} {volume}%",
        inline=True
    )
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    embed.set_footer(text=FOOTER_TEXT)
    
    return embed


def create_queue_embed(
    songs: List[dict],
    current_index: int = 0,
    page: int = 1,
    page_size: int = 5
) -> discord.Embed:
    """
    Create a queue embed with pagination.
    
    Args:
        songs: List of song dicts with 'title', 'artist', 'duration', 'requester'
        current_index: Index of current song
        page: Current page number (1-indexed)
        page_size: Songs per page
    
    Returns:
        discord.Embed object
    """
    if not songs:
        embed = discord.Embed(
            title="📋 Queue",
            description="Queue is empty",
            color=PURPLE,
            timestamp=datetime.now()
        )
        embed.set_footer(text=FOOTER_TEXT)
        return embed
    
    total_pages = (len(songs) - 1) // page_size + 1
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, len(songs))
    
    embed = discord.Embed(
        title="📋 Queue",
        description=f"Page {page}/{total_pages}",
        color=PURPLE,
        timestamp=datetime.now()
    )
    
    queue_text = ""
    for i in range(start_idx, end_idx):
        song = songs[i]
        number = i + 1
        title = song.get('title', 'Unknown')
        artist = song.get('artist', 'Unknown Artist')
        duration = song.get('duration', 0)
        requester = song.get('requester', 'Unknown')
        
        if i == current_index:
            marker = f"{PLAY}"
        else:
            marker = f"{number}."
        
        duration_str = format_duration(duration)
        queue_text += f"{marker} **{title}** - {artist} ({duration_str})\n"
        queue_text += f"   └─ Requested by {requester}\n"
    
    if queue_text:
        embed.description = queue_text
    else:
        embed.description = "No songs to display"
    
    embed.set_footer(text=FOOTER_TEXT)
    
    return embed


def create_song_added_embed(
    title: str,
    artist: str = "Unknown Artist",
    duration: int = 0,
    requester: str = "Unknown",
    position: int = 1,
    thumbnail: Optional[str] = None,
) -> discord.Embed:
    """
    Create a Song Added to Queue embed.
    
    Args:
        title: Song title
        artist: Artist/channel name
        duration: Duration in seconds
        requester: User who added the song
        position: Position in queue
        thumbnail: URL to song thumbnail
    
    Returns:
        discord.Embed object
    """
    embed = discord.Embed(
        title=f"{SUCCESS} Added to Queue",
        description=f"**{title}**",
        color=SUCCESS,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="Artist",
        value=artist,
        inline=True
    )
    
    embed.add_field(
        name="Duration",
        value=format_duration(duration),
        inline=True
    )
    
    embed.add_field(
        name="Position",
        value=f"#{position}",
        inline=True
    )
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    embed.set_footer(text=FOOTER_TEXT)
    
    return embed


def create_error_embed(
    title: str,
    description: str = "An error occurred"
) -> discord.Embed:
    """
    Create an error embed with consistent styling.
    
    Args:
        title: Error title
        description: Error description/details
    
    Returns:
        discord.Embed object
    """
    embed = discord.Embed(
        title=f"{ERROR} {title}",
        description=description,
        color=ERROR,
        timestamp=datetime.now()
    )
    
    embed.set_footer(text=FOOTER_TEXT)
    
    return embed


def create_info_embed(
    title: str,
    description: str = ""
) -> discord.Embed:
    """
    Create an info embed with consistent styling.
    
    Args:
        title: Info title
        description: Info description
    
    Returns:
        discord.Embed object
    """
    embed = discord.Embed(
        title=f"ℹ️ {title}",
        description=description,
        color=PURPLE,
        timestamp=datetime.now()
    )
    
    embed.set_footer(text=FOOTER_TEXT)
    
    return embed
