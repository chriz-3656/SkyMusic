"""Queue view with select menu for song navigation."""

import discord
from discord.ui import View, Select, select
from discord.ext import commands
from typing import Optional
from ..utils.colors import PURPLE, ERROR
from state.shared import get_guild_player


class QueueView(View):
    """Queue display with select menu for navigation."""
    
    def __init__(self, guild_id: int, page: int = 0, timeout: Optional[float] = 300):
        """
        Initialize queue view.
        
        Args:
            guild_id: Guild ID
            page: Current page number
            timeout: View timeout
        """
        super().__init__(timeout=timeout)
        self.guild_id = guild_id
        self.page = page
        self.page_size = 10
        self._build_select_menu()
    
    def _build_select_menu(self):
        """Build select menu with queue items."""
        player = get_guild_player(self.guild_id)
        if not player or not player.queue:
            return
        
        options = []
        start_idx = self.page * self.page_size
        end_idx = start_idx + self.page_size
        
        for i, song in enumerate(player.queue[start_idx:end_idx], start=start_idx + 1):
            label = song.get('title', 'Unknown')[:100]
            value = str(i - 1)  # Store queue index
            
            option = discord.SelectOption(
                label=f"{i}. {label}",
                value=value,
                description=song.get('artist', 'Unknown')[:50]
            )
            options.append(option)
        
        if options:
            self.select_song.options = options
    
    @select(
        placeholder="Select a song to jump to",
        min_values=1,
        max_values=1,
        custom_id="queue_select"
    )
    async def select_song(self, interaction: discord.Interaction, select: Select):
        """Handle song selection from queue."""
        await interaction.response.defer()
        
        player = get_guild_player(self.guild_id)
        if not player:
            return
        
        song_index = int(select.values[0])
        
        # Skip to selected song
        if 0 <= song_index < len(player.queue):
            # Remove all songs before the selected one
            for _ in range(song_index):
                if player.queue:
                    player.queue.pop(0)
            
            await player.skip_song()
            
            embed = discord.Embed(
                title="⏭️ Jumped to Song",
                color=PURPLE
            )
            embed.set_footer(text="🌌 Powered by SkyMusic")
            await interaction.followup.send(embed=embed, ephemeral=True)


class QueuePageView(View):
    """Queue with pagination."""
    
    def __init__(self, guild_id: int, embed_fn, page: int = 0, timeout: Optional[float] = 300):
        """
        Initialize paginated queue view.
        
        Args:
            guild_id: Guild ID
            embed_fn: Function to generate embed
            page: Current page
            timeout: View timeout
        """
        super().__init__(timeout=timeout)
        self.guild_id = guild_id
        self.embed_fn = embed_fn
        self.page = page
        self._update_buttons()
    
    def _update_buttons(self):
        """Update button states based on page."""
        player = get_guild_player(self.guild_id)
        max_pages = 1
        if player and player.queue:
            max_pages = (len(player.queue) - 1) // 10 + 1
        
        self.prev_button.disabled = self.page <= 0
        self.next_button.disabled = self.page >= max_pages - 1
    
    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary, custom_id="queue_prev")
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Previous page button."""
        await interaction.response.defer()
        if self.page > 0:
            self.page -= 1
            embed = self.embed_fn(self.page)
            self._update_buttons()
            await interaction.message.edit(embed=embed, view=self)
    
    @discord.ui.button(label="Next ▶️", style=discord.ButtonStyle.secondary, custom_id="queue_next")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Next page button."""
        await interaction.response.defer()
        player = get_guild_player(self.guild_id)
        max_pages = 1
        if player and player.queue:
            max_pages = (len(player.queue) - 1) // 10 + 1
        
        if self.page < max_pages - 1:
            self.page += 1
            embed = self.embed_fn(self.page)
            self._update_buttons()
            await interaction.message.edit(embed=embed, view=self)
