"""Modal dialogs for SkyMusic bot."""

import discord
from discord.ui import Modal, TextInput
from discord.ext import commands
from typing import Optional
from ..utils.colors import PURPLE, ERROR
from player.player import Player
from bot.utils.emojis import SUCCESS


class AddSongModal(Modal, title="Add Song to Queue"):
    """Modal dialog to search and add songs."""
    
    song_query = TextInput(
        label="Song Title or YouTube Link",
        placeholder="Enter a song name or YouTube Music link",
        required=True,
        max_length=500,
        style=discord.TextStyle.short
    )
    
    def __init__(self, player: Player):
        super().__init__()
        self.player = player
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission."""
        await interaction.response.defer()
        
        query = self.song_query.value
        
        if not self.player:
            embed = discord.Embed(
                title="Error",
                description="No player active. Start playing music first with /play",
                color=ERROR
            )
            embed.set_footer(text="🌌 Powered by SkyMusic")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔍 Searching...",
            description=f"Looking for: **{query}**",
            color=PURPLE
        )
        embed.set_footer(text="🌌 Powered by SkyMusic")
        
        msg = await interaction.followup.send(embed=embed, ephemeral=True)
        
        try:
            # Add to queue (search is integrated in add_to_queue)
            song = await self.player.add_to_queue(query, str(interaction.user))
            
            if not song:
                embed = discord.Embed(
                    title="No Results",
                    description=f"Couldn't find any songs matching: **{query}**",
                    color=ERROR
                )
                embed.set_footer(text="🌌 Powered by SkyMusic")
                await msg.edit(embed=embed)
                return
            
            # Song was added successfully
            embed = discord.Embed(
                title=f"{SUCCESS} Added to Queue",
                description=f"**{song.title}**\n*{song.artist or 'Unknown'}*",
                color=PURPLE
            )
            
            if getattr(song, 'thumbnail', None):
                embed.set_thumbnail(url=song.thumbnail)
            
            queue_pos = len(self.player.queue.songs)
            embed.add_field(name="Position", value=f"#{queue_pos} in queue", inline=True)
            
            if song.duration:
                from ..utils.embeds import format_duration
                embed.add_field(name="Duration", value=format_duration(song.duration), inline=True)
            
            embed.set_footer(text="🌌 Powered by SkyMusic")
            await msg.edit(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Failed to search: {str(e)[:100]}",
                color=ERROR
            )
            embed.set_footer(text="🌌 Powered by SkyMusic")
            await msg.edit(embed=embed)


class SearchModal(Modal, title="Search for Song"):
    """Modal dialog for searching songs."""
    
    query = TextInput(
        label="Song Name or Artist",
        placeholder="e.g., 'Blinding Lights The Weeknd'",
        required=True,
        max_length=500,
        style=discord.TextStyle.short
    )
    
    def __init__(self, player: Player):
        super().__init__()
        self.player = player
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle search submission."""
        await interaction.response.defer()
        
        query = self.query.value
        
        if not self.player:
            embed = discord.Embed(
                title="Error",
                description="No player active. Start playing music first with /play",
                color=ERROR
            )
            embed.set_footer(text="🌌 Powered by SkyMusic")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        try:
            songs = await self.player.searcher.search(query)
            
            if not songs:
                embed = discord.Embed(
                    title="No Results",
                    description=f"No songs found for: **{query}**",
                    color=ERROR
                )
                embed.set_footer(text="🌌 Powered by SkyMusic")
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Show results (top 5)
            embed = discord.Embed(
                title=f"Search Results for '{query}' (showing top 5)",
                color=PURPLE
            )
            
            results_text = ""
            for i, song in enumerate(songs[:5], 1):
                artist = song.artist if isinstance(song, object) and hasattr(song, 'artist') else song.get('artist', 'Unknown')
                title = song.title if isinstance(song, object) and hasattr(song, 'title') else song.get('title', 'Unknown')
                results_text += f"{i}. **{title}** - {artist}\n"
            
            embed.description = results_text
            embed.set_footer(text="Use /play <song name> to add to queue")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"Search failed: {str(e)[:100]}",
                color=ERROR
            )
            embed.set_footer(text="🌌 Powered by SkyMusic")
            await interaction.followup.send(embed=embed, ephemeral=True)
