"""Rythm-style polished control panel with organized button rows."""

import discord
from discord.ui import View, Button, button
from typing import Optional, Callable
from bot.utils.emojis import (
    PREV, PLAY, PAUSE, SKIP, STOP,
    QUEUE, ADD, SEARCH, MUSIC,
    VOL_DOWN, VOL_UP,
    FAV, LOOP_ALL, LOOP_ONE, LOOP_OFF, AUTOPLAY, SHUFFLE,
    LIBRARY, DOWNLOAD
)
from bot.utils import colors
from .rythm_embeds import create_rythm_now_playing_embed, create_idle_embed, create_paused_embed


class RythmControlPanel(View):
    """Polished Rythm-style control panel with organized button rows."""
    
    def __init__(self, player, guild_id: int, update_callback: Optional[Callable] = None, timeout: float = 3600):
        """
        Initialize the control panel.
        
        Args:
            player: Player instance
            guild_id: Guild ID for state management
            update_callback: Callback function to update the panel
            timeout: Button timeout in seconds
        """
        super().__init__(timeout=timeout)
        self.player = player
        self.guild_id = guild_id
        self.update_callback = update_callback
        self._update_button_states()
    
    def _update_button_states(self):
        """Update button states based on player state."""
        if not self.player:
            return
        
        is_playing = self.player.is_playing if hasattr(self.player, 'is_playing') else False
        current_song = self.player.current_song if hasattr(self.player, 'current_song') else None
        
        # Disable playback buttons if nothing is playing
        for item in self.children:
            if hasattr(item, 'custom_id'):
                # Disable buttons that require active playback
                if item.custom_id in ('prev_btn', 'pause_resume_btn', 'skip_btn', 'stop_btn', 'queue_display_btn'):
                    item.disabled = not current_song
                
                # Volume always available
                if item.custom_id in ('vol_down_btn', 'vol_up_btn'):
                    item.disabled = False
                
                # Add/Search always available
                if item.custom_id in ('add_song_btn', 'search_btn'):
                    item.disabled = False
                
                # Favorite requires current song
                if item.custom_id == 'favorite_btn':
                    item.disabled = not current_song
                
                # Loop/Autoplay always available
                if item.custom_id in ('loop_btn', 'autoplay_btn', 'shuffle_btn'):
                    item.disabled = False
    
    async def _update_panel(self, interaction: discord.Interaction):
        """Update the control panel embed."""
        if self.update_callback:
            try:
                await self.update_callback(interaction, self)
            except Exception as e:
                await interaction.followup.send(f"Error updating panel: {e}", ephemeral=True)
    
    # ==================== ROW 0: PLAYBACK CONTROLS ====================
    
    @button(emoji=PREV, style=discord.ButtonStyle.secondary, custom_id="prev_btn", row=0)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        """Previous song button."""
        await interaction.response.defer()
        if self.player and hasattr(self.player, 'skip'):
            await self.player.skip()
            await self._update_panel(interaction)
    
    @button(emoji=PAUSE, style=discord.ButtonStyle.primary, custom_id="pause_resume_btn", row=0)
    async def pause_resume_button(self, interaction: discord.Interaction, button: Button):
        """Pause/Resume button."""
        await interaction.response.defer()
        if self.player:
            is_paused = getattr(self.player, 'is_paused', False)
            if is_paused:
                if hasattr(self.player, 'resume'):
                    await self.player.resume()
                button.emoji = PAUSE
            else:
                if hasattr(self.player, 'pause'):
                    self.player.pause()
                button.emoji = PLAY
            await self._update_panel(interaction)
    
    @button(emoji=SKIP, style=discord.ButtonStyle.secondary, custom_id="skip_btn", row=0)
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        """Skip to next song."""
        await interaction.response.defer()
        if self.player and hasattr(self.player, 'skip'):
            await self.player.skip()
            await self._update_panel(interaction)
    
    @button(emoji=STOP, style=discord.ButtonStyle.danger, custom_id="stop_btn", row=0)
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        """Stop playback."""
        await interaction.response.defer()
        if self.player and hasattr(self.player, 'stop'):
            self.player.stop()
            await self._update_panel(interaction)
    
    # ==================== ROW 1: MUSIC CONTROLS ====================
    
    @button(emoji=QUEUE, style=discord.ButtonStyle.secondary, custom_id="queue_display_btn", row=1)
    async def queue_button(self, interaction: discord.Interaction, button: Button):
        """Show queue."""
        await interaction.response.defer()
        if not self.player or not getattr(self.player, 'current_song', None):
            embed = discord.Embed(
                title="Queue Empty",
                description="No songs in queue. Use `/play` to start!",
                color=colors.ERROR
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        queue_songs = getattr(self.player, 'queue', {}).songs if hasattr(self.player, 'queue') else []
        current_song = getattr(self.player, 'current_song', None)
        
        embed = discord.Embed(
            title=f"{QUEUE} Queue ({len(queue_songs)} songs)",
            color=colors.PURPLE
        )
        
        if current_song:
            embed.add_field(
                name=f"{PLAY} Now Playing",
                value=f"**{getattr(current_song, 'title', 'Unknown')}**\n*{getattr(current_song, 'artist', 'Unknown')}*",
                inline=False
            )
        
        if queue_songs:
            queue_text = ""
            for i, song in enumerate(queue_songs[:10], 1):
                song_title = getattr(song, 'title', 'Unknown')
                song_artist = getattr(song, 'artist', 'Unknown')
                queue_text += f"{i}. **{song_title}** - *{song_artist}*\n"
            
            embed.add_field(
                name="Next Up",
                value=queue_text,
                inline=False
            )
        
        embed.set_footer(text="SkyMusic Queue")
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @button(emoji=MUSIC, style=discord.ButtonStyle.secondary, custom_id="now_playing_btn", row=1)
    async def now_playing_button(self, interaction: discord.Interaction, button: Button):
        """Show detailed now playing info."""
        await interaction.response.defer()
        
        if not self.player or not getattr(self.player, 'current_song', None):
            embed = create_idle_embed()
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        current_song = self.player.current_song
        title = getattr(current_song, 'title', 'Unknown')
        artist = getattr(current_song, 'artist', 'Unknown')
        duration = getattr(current_song, 'duration', 0)
        thumbnail = getattr(current_song, 'thumbnail', None)
        requester = getattr(current_song, 'requester', 'Unknown')
        is_paused = getattr(self.player, 'is_paused', False)
        
        if is_paused:
            embed = create_paused_embed(title, artist, duration, 0, requester, thumbnail)
        else:
            embed = create_rythm_now_playing_embed(
                title, artist, duration, 0, requester, thumbnail,
                len(getattr(self.player, 'queue', {}).songs if hasattr(self.player, 'queue') else []),
                is_paused=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @button(emoji=ADD, style=discord.ButtonStyle.success, custom_id="add_song_btn", row=1)
    async def add_song_button(self, interaction: discord.Interaction, button: Button):
        """Open add song modal."""
        from .modals import AddSongModal
        modal = AddSongModal(self.player)
        await interaction.response.send_modal(modal)
    
    @button(emoji=SEARCH, style=discord.ButtonStyle.secondary, custom_id="search_btn", row=1)
    async def search_button(self, interaction: discord.Interaction, button: Button):
        """Open search modal."""
        from .modals import SearchModal
        modal = SearchModal(self.player)
        await interaction.response.send_modal(modal)
    
    # ==================== ROW 2: VOLUME CONTROLS ====================
    
    @button(emoji=VOL_DOWN, style=discord.ButtonStyle.secondary, custom_id="vol_down_btn", row=2)
    async def volume_down_button(self, interaction: discord.Interaction, button: Button):
        """Decrease volume."""
        await interaction.response.defer()
        if self.player:
            current_vol = getattr(self.player, 'volume', 100)
            new_volume = max(0, current_vol - 10)
            if hasattr(self.player, 'set_volume'):
                await self.player.set_volume(new_volume)
            else:
                self.player.volume = new_volume
            await self._update_panel(interaction)
    
    @button(label="🔊 100%", style=discord.ButtonStyle.secondary, custom_id="vol_display", row=2, disabled=True)
    async def volume_display_button(self, interaction: discord.Interaction, button: Button):
        """Volume display (informational)."""
        pass
    
    @button(emoji=VOL_UP, style=discord.ButtonStyle.secondary, custom_id="vol_up_btn", row=2)
    async def volume_up_button(self, interaction: discord.Interaction, button: Button):
        """Increase volume."""
        await interaction.response.defer()
        if self.player:
            current_vol = getattr(self.player, 'volume', 100)
            new_volume = min(100, current_vol + 10)
            if hasattr(self.player, 'set_volume'):
                await self.player.set_volume(new_volume)
            else:
                self.player.volume = new_volume
            await self._update_panel(interaction)
    
    # ==================== ROW 3: MODE CONTROLS ====================
    
    @button(emoji=FAV, style=discord.ButtonStyle.secondary, custom_id="favorite_btn", row=3)
    async def favorite_button(self, interaction: discord.Interaction, button: Button):
        """Add to favorites."""
        await interaction.response.defer()
        if self.player and getattr(self.player, 'current_song', None):
            await interaction.followup.send("Favorite feature coming soon!", ephemeral=True)
    
    @button(emoji=LOOP_ALL, style=discord.ButtonStyle.secondary, custom_id="loop_btn", row=3)
    async def loop_button(self, interaction: discord.Interaction, button: Button):
        """Cycle loop mode: off → all → one → off."""
        await interaction.response.defer()
        if self.player:
            await interaction.followup.send("Loop feature coming soon!", ephemeral=True)
    
    @button(emoji=AUTOPLAY, style=discord.ButtonStyle.secondary, custom_id="autoplay_btn", row=3)
    async def autoplay_button(self, interaction: discord.Interaction, button: Button):
        """Toggle autoplay."""
        await interaction.response.defer()
        if self.player:
            await interaction.followup.send("Autoplay feature coming soon!", ephemeral=True)
    
    @button(emoji=SHUFFLE, style=discord.ButtonStyle.secondary, custom_id="shuffle_btn", row=3)
    async def shuffle_button(self, interaction: discord.Interaction, button: Button):
        """Toggle shuffle mode."""
        await interaction.response.defer()
        if self.player:
            await interaction.followup.send("Shuffle feature coming soon!", ephemeral=True)
