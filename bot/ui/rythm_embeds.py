"""Rythm-style Now Playing embed builder with auto-updating support."""

import discord
from datetime import datetime
from typing import Optional
from bot.utils.emojis import MUSIC, ARTIST, ALBUM, TIME, LIVE, PLAY, PAUSE
from bot.utils import colors
from ..ui.progress_bar import create_progress_line, format_time


def create_rythm_now_playing_embed(
    title: str,
    artist: str = "Unknown",
    duration: int = 0,
    current_position: int = 0,
    requester: str = "Unknown",
    thumbnail: Optional[str] = None,
    queue_length: int = 0,
    is_paused: bool = False,
    is_live: bool = False,
) -> discord.Embed:
    """
    Create a Rythm-style Now Playing embed with clean minimal design.
    
    Args:
        title: Song title
        artist: Artist/channel name
        duration: Duration in seconds
        current_position: Current playback position in seconds
        requester: User who requested the song
        thumbnail: URL to song thumbnail
        queue_length: Number of songs in queue
        is_paused: Whether playback is paused
        is_live: Whether song is live
    
    Returns:
        discord.Embed object with Rythm-style design
    """
    # Status icon
    status_icon = PAUSE if is_paused else PLAY
    status_text = "Paused" if is_paused else "Playing"
    
    # Live indicator
    live_text = f" {LIVE} LIVE" if is_live else ""
    
    # Create main embed
    embed = discord.Embed(
        title=f"{status_icon} {status_text}{live_text}",
        description=f"**{title}**\n*{artist}*",
        color=colors.PURPLE,
        timestamp=datetime.now()
    )
    
    # Thumbnail (right side)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    # Progress bar
    if not is_live and duration > 0:
        progress_bar = create_progress_line(current_position, duration, bar_length=15)
        embed.add_field(
            name=f"{TIME} Progress",
            value=f"```{progress_bar}```",
            inline=False
        )
    
    # Song info
    info_text = f"{ARTIST} {artist}\n{ALBUM} Duration: {format_time(duration) if duration > 0 else 'N/A'}"
    embed.add_field(
        name="Info",
        value=info_text,
        inline=False
    )
    
    # Queue info
    queue_text = f"📋 {queue_length} song{'s' if queue_length != 1 else ''} in queue"
    embed.add_field(
        name="Queue",
        value=queue_text,
        inline=False
    )
    
    # Requested by
    embed.add_field(
        name="Requested by",
        value=requester,
        inline=True
    )
    
    embed.set_footer(text="SkyMusic - Your personal music bot")
    
    return embed


def create_idle_embed() -> discord.Embed:
    """
    Create an idle state embed (nothing playing).
    
    Returns:
        discord.Embed object
    """
    embed = discord.Embed(
        title=f"{MUSIC} Nothing is Currently Playing",
        description="Use `/play <song>` to start the music!",
        color=colors.PURPLE,
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="How to get started:",
        value="1. Use `/play` to search for songs\n2. Add songs to the queue\n3. Use the control buttons below\n4. Enjoy!",
        inline=False
    )
    
    embed.set_footer(text="SkyMusic - Your personal music bot")
    
    return embed


def create_paused_embed(
    title: str,
    artist: str = "Unknown",
    duration: int = 0,
    current_position: int = 0,
    requester: str = "Unknown",
    thumbnail: Optional[str] = None,
) -> discord.Embed:
    """
    Create a paused state embed.
    
    Args:
        title: Song title
        artist: Artist name
        duration: Song duration in seconds
        current_position: Current position in seconds
        requester: User who requested
        thumbnail: Song thumbnail URL
    
    Returns:
        discord.Embed object
    """
    embed = discord.Embed(
        title=f"{PAUSE} Paused",
        description=f"**{title}**\n*{artist}*",
        color=colors.PURPLE,
        timestamp=datetime.now()
    )
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    if duration > 0:
        progress_bar = create_progress_line(current_position, duration, bar_length=15)
        embed.add_field(
            name=f"{TIME} Progress",
            value=f"```{progress_bar}```",
            inline=False
        )
    
    embed.add_field(
        name="Requested by",
        value=requester,
        inline=False
    )
    
    embed.set_footer(text="SkyMusic - Click resume to continue")
    
    return embed
