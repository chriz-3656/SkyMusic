"""UI state management for control panels."""

from dataclasses import dataclass, field
from typing import Optional, Dict
import discord


@dataclass
class ControlPanelState:
    """Holds state for a control panel in a guild."""
    
    guild_id: int
    message_id: Optional[int] = None  # ID of the persistent message
    message: Optional[discord.Message] = None  # Actual message object
    last_update: float = 0.0  # Timestamp of last update
    is_updating: bool = False  # Prevent concurrent updates
    
    async def update_message(self, embed: discord.Embed, view=None) -> bool:
        """
        Update the control panel message with new embed.
        
        Args:
            embed: New embed to display
            view: Discord view with buttons
        
        Returns:
            True if successful, False otherwise
        """
        if not self.message:
            return False
        
        if self.is_updating:
            return False
        
        try:
            self.is_updating = True
            await self.message.edit(embed=embed, view=view)
            return True
        except Exception as e:
            print(f"Failed to update panel message: {e}")
            return False
        finally:
            self.is_updating = False
    
    async def delete_message(self) -> bool:
        """Delete the control panel message."""
        if not self.message:
            return False
        
        try:
            await self.message.delete()
            self.message = None
            self.message_id = None
            return True
        except Exception as e:
            print(f"Failed to delete panel message: {e}")
            return False


class ControlPanelManager:
    """Manages control panels for all guilds."""
    
    def __init__(self):
        self.panels: Dict[int, ControlPanelState] = {}
    
    def get_panel(self, guild_id: int) -> Optional[ControlPanelState]:
        """Get panel state for a guild."""
        return self.panels.get(guild_id)
    
    def create_panel(self, guild_id: int) -> ControlPanelState:
        """Create a new panel state for a guild."""
        panel = ControlPanelState(guild_id=guild_id)
        self.panels[guild_id] = panel
        return panel
    
    def set_panel_message(self, guild_id: int, message: discord.Message) -> None:
        """Store the message reference for a panel."""
        if guild_id not in self.panels:
            self.create_panel(guild_id)
        
        panel = self.panels[guild_id]
        panel.message = message
        panel.message_id = message.id
    
    async def delete_panel(self, guild_id: int) -> None:
        """Delete panel and its message."""
        if guild_id in self.panels:
            panel = self.panels[guild_id]
            await panel.delete_message()
            del self.panels[guild_id]
    
    def clear_all(self) -> None:
        """Clear all panels."""
        self.panels.clear()


# Global instance
_panel_manager = ControlPanelManager()


def get_panel_manager() -> ControlPanelManager:
    """Get the global control panel manager."""
    return _panel_manager
