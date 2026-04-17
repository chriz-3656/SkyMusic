from bot.utils.emojis import ERROR, MUSIC, PAUSE, PLAY, SEARCH, VOL_UP
"""Interactive control system for SkyMusic bot."""

import discord
from discord.ext import commands, tasks
from typing import Optional
from ..ui.control_panel import ControlPanelView
from .music_commands import NowPlayingView
from ..ui.state import get_panel_manager
from ..utils.colors import PURPLE, ERROR, SUCCESS
from state.shared import get_player, get_bot


class InteractiveControls(commands.Cog):
    """Cog for interactive music controls."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.control_panel_messages = {}  # guild_id -> message_id
        self.panel_manager = get_panel_manager()
    
    async def update_or_create_panel(
        self,
        guild_id: int,
        channel: discord.TextChannel,
        embed: discord.Embed,
        view: discord.ui.View = None
    ) -> Optional[discord.Message]:
        """
        Update existing control panel or create new one.
        
        Args:
            guild_id: Guild ID
            channel: Channel to send/update message in
            embed: Embed to display
            view: Discord view with buttons
        
        Returns:
            Message object or None if failed
        """
        panel = self.panel_manager.get_panel(guild_id)
        
        # Try to update existing message
        if panel and panel.message:
            try:
                await panel.message.edit(embed=embed, view=view)
                return panel.message
            except discord.NotFound:
                # Message was deleted, create new one
                panel.message = None
                panel.message_id = None
            except Exception as e:
                print(f"Failed to update panel: {e}")
        
        # Create new message
        try:
            message = await channel.send(embed=embed, view=view)
            self.panel_manager.set_panel_message(guild_id, message)
            return message
        except Exception as e:
            print(f"Failed to create panel: {e}")
            return None
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Bot ready event."""
        print(f"[Interactive Controls] Ready - {self.bot.user}")
    
    async def send_now_playing_message(self, guild_id: int, channel: discord.TextChannel):
        """
        Send now playing message with control button.
        
        Args:
            guild_id: Guild ID
            channel: Channel to send message to
        """
        player = get_player(guild_id)
        if not player or not player.current_song:
            return
        
        song = player.current_song
        
        # Create now playing embed
        embed = discord.Embed(
            title=f"{MUSIC} Now Playing",
            description=f"**{song['title']}**\n*{song.get('artist', 'Unknown')}*",
            color=PURPLE
        )
        
        if song.get('thumbnail'):
            embed.set_thumbnail(url=song['thumbnail'])
        
        # Add metadata
        duration = song.get('duration', 0)
        if duration:
            from ..utils.embeds import format_duration
            embed.add_field(
                name="Duration",
                value=format_duration(duration),
                inline=True
            )
        
        if song.get('requester'):
            embed.add_field(
                name="Requested by",
                value=song['requester'],
                inline=True
            )
        
        if player.queue:
            embed.add_field(
                name="Queue",
                value=f"{len(player.queue)} songs",
                inline=True
            )
        
        embed.add_field(
            name="Volume",
            value=f"{player.volume}%",
            inline=True
        )
        
        embed.set_footer(text="Powered by SkyMusic")
        
        # Send with now playing view
        view = NowPlayingView(guild_id)
        try:
            msg = await channel.send(embed=embed, view=view)
            self.control_panel_messages[guild_id] = msg.id
        except Exception as e:
            print(f"[Interactive Controls] Failed to send now playing: {e}")
    
    async def send_control_panel(self, interaction: discord.Interaction, guild_id: int):
        """
        Send control panel message.
        
        Args:
            interaction: Discord interaction
            guild_id: Guild ID
        """
        player = get_player(guild_id)
        if not player or not player.current_song:
            embed = discord.Embed(
                title=f"{ERROR} No Song Playing",
                description="Start playing music with /play",
                color=ERROR
            )
            embed.set_footer(text="Powered by SkyMusic")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        song = player.current_song
        
        # Create control panel embed
        embed = discord.Embed(
            title="Music Control Panel",
            description=f"**{song['title']}**\n*{song.get('artist', 'Unknown')}*",
            color=PURPLE
        )
        
        if song.get('thumbnail'):
            embed.set_thumbnail(url=song['thumbnail'])
        
        # Status
        status_text = f"{MUSIC} Playing" if not player.is_paused else f"{PAUSE} Paused"
        loop_mode = getattr(player, 'loop_mode', 'off')
        
        embed.add_field(
            name="Status",
            value=f"{status_text} • Loop: {loop_mode.title()}",
            inline=False
        )
        
        embed.add_field(
            name="Volume",
            value=f"{player.volume}% {VOL_UP}",
            inline=True
        )
        
        if player.queue:
            embed.add_field(
                name="Queue",
                value=f"{len(player.queue)} songs",
                inline=True
            )
        
        embed.set_footer(text="Powered by SkyMusic • Click buttons to control")
        
        # Send with control panel view
        view = ControlPanelView(guild_id)
        await interaction.response.send_message(embed=embed, view=view)
    
    async def send_jump_back_in(self, guild_id: int, channel: discord.TextChannel):
        """
        Send 'Jump Back In' panel after reconnection.
        
        Args:
            guild_id: Guild ID
            channel: Channel to send message to
        """
        player = get_player(guild_id)
        if not player or not player.current_song:
            return
        
        song = player.current_song
        
        embed = discord.Embed(
            title=f"{MUSIC} Jump Back In",
            description=f"**{song['title']}**\n*{song.get('artist', 'Unknown')}*",
            color=PURPLE
        )
        
        if song.get('thumbnail'):
            embed.set_thumbnail(url=song['thumbnail'])
        
        embed.add_field(
            name="Status",
            value="Music paused • Ready to resume",
            inline=False
        )
        
        queue_count = len(player.queue) if player.queue else 0
        embed.add_field(
            name="Queue",
            value=f"{queue_count} songs queued",
            inline=True
        )
        
        embed.set_footer(text="Powered by SkyMusic")
        
        # Create quick access buttons
        view = JumpBackInView(guild_id)
        
        try:
            await channel.send(embed=embed, view=view)
        except Exception as e:
            print(f"[Interactive Controls] Failed to send jump back in: {e}")


class JumpBackInView(discord.ui.View):
    """Quick access buttons for reconnection."""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=3600)
        self.guild_id = guild_id
    
    @discord.ui.button(emoji=PLAY, label="Continue", style=discord.ButtonStyle.success, custom_id="continue_btn")
    async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Resume playback."""
        await interaction.response.defer()
        
        player = get_player(self.guild_id)
        if player:
            await player.resume_song()
            
            embed = discord.Embed(
                title=f"{PLAY} Resuming...",
                color=SUCCESS
            )
            embed.set_footer(text="Powered by SkyMusic")
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Search", style=discord.ButtonStyle.secondary, custom_id="search_jump_btn")
    async def search_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open search modal."""
        from ..ui.modals import SearchModal
        modal = SearchModal(self.guild_id)
        await interaction.response.send_modal(modal)


async def setup(bot: commands.Bot):
    """Setup function to load cog."""
    await bot.add_cog(InteractiveControls(bot))
