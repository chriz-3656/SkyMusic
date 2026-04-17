"""Autoplay/Radio system commands for SkyMusic bot."""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

from player.autoplay import AutoplayEngine
from state.shared import get_player, get_autoplay_engine
from bot.utils.embeds import create_info_embed, create_error_embed
from bot.utils.colors import SUCCESS, ERROR, PURPLE
from bot.utils.emojis import AUTOPLAY, SUCCESS, ERROR

import logging

logger = logging.getLogger(__name__)


class AutoplayCommands(commands.Cog):
    """Autoplay/Radio mode commands."""
    
    def __init__(self, bot: commands.Bot, autoplay_engine: Optional[AutoplayEngine] = None):
        """
        Initialize autoplay commands.
        
        Args:
            bot: Discord bot instance
            autoplay_engine: AutoplayEngine instance (created if None)
        """
        self.bot = bot
        self.autoplay_engine = autoplay_engine or get_autoplay_engine()
        self.autoplay_state: dict = {}  # guild_id -> bool (enabled/disabled)
    
    def is_autoplay_enabled(self, guild_id: int) -> bool:
        """Check if autoplay is enabled for guild."""
        return self.autoplay_state.get(guild_id, False)
    
    def set_autoplay(self, guild_id: int, enabled: bool):
        """Set autoplay state for guild."""
        self.autoplay_state[guild_id] = enabled
        
        # Also update the player's autoplay_enabled flag
        player = get_player(guild_id)
        if player:
            player.autoplay_enabled = enabled
        
        logger.info(f"Guild {guild_id}: Autoplay {'enabled' if enabled else 'disabled'}")
    
    @app_commands.command(name="autoplay", description="Toggle autoplay/radio mode")
    @app_commands.describe(
        mode="Enable or disable autoplay (on/off)"
    )
    async def autoplay(self, interaction: discord.Interaction, mode: str):
        """Toggle autoplay mode on/off."""
        await interaction.response.defer()
        
        mode_lower = mode.lower()
        guild_id = interaction.guild_id
        
        if mode_lower not in ('on', 'off'):
            embed = create_error_embed(
                "Invalid Mode",
                "Use: /autoplay on  or  /autoplay off"
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        is_enabling = mode_lower == 'on'
        
        try:
            player = get_player(guild_id)
            
            if not player or not player.is_playing:
                embed = create_error_embed(
                    "No Music Playing",
                    "Start playing a song before enabling autoplay"
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Set autoplay state
            self.set_autoplay(guild_id, is_enabling)
            
            # Create response embed
            if is_enabling:
                embed = discord.Embed(
                    title=f"{AUTOPLAY} Autoplay Enabled",
                    description="When the queue ends, similar songs will play automatically",
                    color=SUCCESS
                )
                embed.add_field(
                    name="How it works",
                    value="• Current song finishes\n• Queue ends\n• Similar songs fetch automatically\n• Next track plays seamlessly",
                    inline=False
                )
                embed.add_field(
                    name="What you need",
                    value="Just keep the music playing! Songs continue in radio mode.",
                    inline=False
                )
            else:
                embed = discord.Embed(
                    title=f"{AUTOPLAY} Autoplay Disabled",
                    description="Music will stop when the queue ends",
                    color=ERROR
                )
            
            embed.set_footer(text="🌌 Powered by SkyMusic")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            embed = create_error_embed(
                "Error",
                f"Failed to toggle autoplay: {str(e)[:100]}"
            )
            logger.error(f"Error toggling autoplay: {e}")
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="autoplay_status", description="Check autoplay status")
    async def autoplay_status(self, interaction: discord.Interaction):
        """Check if autoplay is enabled."""
        await interaction.response.defer()
        
        guild_id = interaction.guild_id
        is_enabled = self.is_autoplay_enabled(guild_id)
        player = get_player(guild_id)
        
        embed = discord.Embed(
            title=f"{AUTOPLAY} Autoplay Status",
            color=PURPLE
        )
        
        # Status
        status_text = f"{SUCCESS} ENABLED" if is_enabled else f"{ERROR} DISABLED"
        embed.add_field(name="Status", value=status_text, inline=True)
        
        # Current song
        if player and player.current_song:
            embed.add_field(
                name="Now Playing",
                value=f"**{player.current_song.title}**\n*{player.current_song.artist or 'Unknown'}*",
                inline=False
            )
        else:
            embed.add_field(
                name="Now Playing",
                value="Nothing (start with /play)",
                inline=False
            )
        
        # Queue
        queue_count = 0
        if player and player.queue and player.queue.songs:
            queue_count = len(player.queue.songs)
        
        embed.add_field(
            name="Queue",
            value=f"{queue_count} songs queued",
            inline=True
        )
        
        # Info
        if is_enabled:
            embed.add_field(
                name="Info",
                value="When queue ends, similar songs will be added automatically",
                inline=False
            )
        else:
            embed.add_field(
                name="Info",
                value="Use `/autoplay on` to enable radio mode",
                inline=False
            )
        
        embed.set_footer(text="🌌 Powered by SkyMusic")
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot, autoplay_engine: Optional[AutoplayEngine] = None):
    """Load the autoplay cog."""
    await bot.add_cog(AutoplayCommands(bot, autoplay_engine))
