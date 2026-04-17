from bot.utils.emojis import ADD, AUTOPLAY, PAUSE, PLAY, QUEUE, SEARCH, SKIP, STOP, VOL_DOWN, VOL_UP
"""Control panel view with interactive buttons for music control."""

import discord
from discord.ui import View, Button, button
from discord.ext import commands
from typing import Optional, Callable
from ..utils.colors import PURPLE, SUCCESS, ERROR


class ControlPanelView(View):
    """Main control panel with multiple rows of buttons."""
    
    def __init__(self, player, guild_id: int, timeout: Optional[float] = 3600):
        """
        Initialize control panel view.
        
        Args:
            player: Player instance
            guild_id: Guild ID for state management
            timeout: How long the view lasts (default 1 hour)
        """
        super().__init__(timeout=timeout)
        self.player = player
        self.guild_id = guild_id
        self._update_button_states()
    
    def _update_button_states(self):
        """Update button disabled states based on player state."""
        is_playing = self.player and self.player.is_playing
        
        for item in self.children:
            if hasattr(item, 'name'):
                if item.name in ('pause_resume', 'skip', 'previous', 'stop', 'queue_btn', 'add_song', 'vol_up', 'vol_down', 'loop_toggle'):
                    item.disabled = not is_playing if item.name != 'add_song' else False
    
    @button(label=PREV + " ", style=discord.ButtonStyle.secondary, custom_id="prev_btn", row=0)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        """Previous song button."""
        await interaction.response.defer()
        if self.player and len(self.player.queue.songs) > 0:
            await self.player.skip()
            await self._update_panel(interaction)
    
    @button(label=PAUSE + " ", style=discord.ButtonStyle.primary, custom_id="pause_resume_btn", row=0)
    async def pause_resume_button(self, interaction: discord.Interaction, button: Button):
        """Pause/Resume button."""
        await interaction.response.defer()
        if self.player:
            if self.player.is_paused:
                self.player.resume()
                button.label = f"{PAUSE}"
            else:
                self.player.pause()
                button.label = f"{PLAY}"
            await self._update_panel(interaction)
    
    @button(label=f"{SKIP}", style=discord.ButtonStyle.secondary, custom_id="skip_btn", row=0)
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        """Skip to next song."""
        await interaction.response.defer()
        if self.player:
            await self.player.skip()
            await self._update_panel(interaction)
    
    @button(label=f"{STOP}", style=discord.ButtonStyle.danger, custom_id="stop_btn", row=0)
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        """Stop playback."""
        await interaction.response.defer()
        if self.player:
            self.player.stop()
            await self._update_panel(interaction)
    
    @button(label=f"{QUEUE} Queue", style=discord.ButtonStyle.secondary, custom_id="queue_btn", row=1)
    async def queue_button(self, interaction: discord.Interaction, button: Button):
        """Show queue."""
        await interaction.response.defer()
        if not self.player or not self.player.current_song:
            embed = discord.Embed(
                title="Queue Empty",
                description="No songs in queue. Use /play to start!",
                color=ERROR
            )
            embed.set_footer(text="Powered by SkyMusic")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Create queue embed
        queue_items = self.player.queue.songs[:10] if self.player.queue.songs else []
        embed = discord.Embed(
            title=f"Queue ({len(self.player.queue.songs) if self.player.queue.songs else 0} songs)",
            color=PURPLE
        )
        
        if self.player.current_song:
            embed.add_field(
                name=f"{PLAY} Now Playing",
                value=f"**{self.player.current_song.title}**\n*{self.player.current_song.artist or 'Unknown'}*",
                inline=False
            )
        
        if queue_items:
            queue_text = ""
            for i, song in enumerate(queue_items, 1):
                queue_text += f"{i}. **{song.title}** - {song.artist or 'Unknown'}\n"
            embed.add_field(
                name="Next Up",
                value=queue_text,
                inline=False
            )
        
        embed.set_footer(text="Powered by SkyMusic")
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @button(label="ADD  Add Song", style=discord.ButtonStyle.success, custom_id="add_song_btn", row=1)
    async def add_song_button(self, interaction: discord.Interaction, button: Button):
        """Open add song modal."""
        from .modals import AddSongModal
        modal = AddSongModal(self.player)
        await interaction.response.send_modal(modal)
    
    @button(label="SEARCH  Search", style=discord.ButtonStyle.secondary, custom_id="search_btn", row=1)
    async def search_button(self, interaction: discord.Interaction, button: Button):
        """Open search modal."""
        from .modals import SearchModal
        modal = SearchModal(self.player)
        await interaction.response.send_modal(modal)
    
    @button(label="VOL_DOWN ", style=discord.ButtonStyle.secondary, custom_id="vol_down_btn", row=2)
    async def volume_down_button(self, interaction: discord.Interaction, button: Button):
        """Volume down."""
        await interaction.response.defer()
        if self.player:
            new_volume = max(0, self.player.volume - 10)
            await self.player.set_volume(new_volume)
            await self._update_panel(interaction)
    
    @button(label="Vol: 100%", style=discord.ButtonStyle.secondary, custom_id="vol_display", row=2, disabled=True)
    async def volume_display_button(self, interaction: discord.Interaction, button: Button):
        """Volume display (informational)."""
        pass
    
    @button(label=f"{VOL_UP}", style=discord.ButtonStyle.secondary, custom_id="vol_up_btn", row=2)
    async def volume_up_button(self, interaction: discord.Interaction, button: Button):
        """Volume up."""
        await interaction.response.defer()
        if self.player:
            new_volume = min(100, self.player.volume + 10)
            await self.player.set_volume(new_volume)
            await self._update_panel(interaction)
    
    @button(label=f"{AUTOPLAY} Off", style=discord.ButtonStyle.secondary, custom_id="loop_btn", row=3)
    async def loop_button(self, interaction: discord.Interaction, button: Button):
        """Toggle loop mode."""
        await interaction.response.defer()
        if self.player:
            # Cycle through: off -> song -> queue -> off
            if not hasattr(self.player, 'loop_mode'):
                self.player.loop_mode = 'off'
            
            if self.player.loop_mode == 'off':
                self.player.loop_mode = 'song'
                button.label = f"{AUTOPLAY} Song"
            elif self.player.loop_mode == 'song':
                self.player.loop_mode = 'queue'
                button.label = f"{AUTOPLAY} Queue"
            else:
                self.player.loop_mode = 'off'
                button.label = "{AUTOPLAY} Off"
            
            await self._update_panel(interaction)
    
    @button(label=FAV + " ", style=discord.ButtonStyle.secondary, custom_id="fav_btn", row=3)
    async def favorite_button(self, interaction: discord.Interaction, button: Button):
        """Add current song to favorites."""
        await interaction.response.defer()
        if self.player and self.player.current_song:
            if not hasattr(self.player, 'favorites'):
                self.player.favorites = []
            
            song_id = getattr(self.player.current_song, 'video_id', self.player.current_song.title)
            if song_id not in self.player.favorites:
                self.player.favorites.append(song_id)
                embed = discord.Embed(
                    title="Added to Favorites FAV",
                    description=f"**{self.player.current_song.title}**",
                    color=SUCCESS
                )
            else:
                self.player.favorites.remove(song_id)
                embed = discord.Embed(
                    title="Removed from Favorites",
                    description=f"**{self.player.current_song.title}**",
                    color=ERROR
                )
            
            embed.set_footer(text="Powered by SkyMusic")
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    async def _update_panel(self, interaction: discord.Interaction):
        """Update control panel with current player state."""
        if not self.player or not self.player.current_song:
            return
        
        # Update volume display button
        for item in self.children:
            if hasattr(item, 'custom_id') and item.custom_id == 'vol_display':
                item.label = f"Vol: {self.player.volume}%"
            
            # Update pause/resume button label
            if hasattr(item, 'custom_id') and item.custom_id == 'pause_resume_btn':
                item.label = f"{PAUSE}" if self.player.is_playing and not self.player.is_paused else f"{PLAY}"
        
        self._update_button_states()
        
        # Try to edit the message (may fail if message was deleted)
        try:
            if interaction.message:
                await interaction.message.edit(view=self)
        except Exception:
            pass
