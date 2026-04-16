import logging
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


def create_bot():
    """Create and configure the Discord bot."""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    
    bot = commands.Bot(
        command_prefix="!",
        intents=intents,
        help_command=None
    )
    
    @bot.event
    async def on_command_error(ctx, error):
        """Handle command errors."""
        logger.error(f"Command error: {error}")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing argument: {error.param.name}")
        elif isinstance(error, commands.CommandNotFound):
            pass  # Ignore unknown commands
        else:
            await ctx.send(f"An error occurred: {str(error)[:100]}")
    
    return bot
