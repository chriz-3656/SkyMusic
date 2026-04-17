import asyncio
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import threading

import discord
from discord.ext import commands

from bot.discord_bot import create_bot
from bot.cogs.music_commands import setup as setup_music_commands
from bot.cogs.autoplay_commands import setup as setup_autoplay_commands
from bot.logger_config import setup_logging
from player.searcher import Searcher
from player.autoplay import AutoplayEngine
from player.autocomplete import SearchAutocomplete
from bot.utils.emojis import SUCCESS, ERROR, MUSIC
from state.shared import set_bot, set_autoplay_engine, set_autocomplete_engine
from api.server import create_app

# Configure logging with enhanced formatter
setup_logging(logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
API_PORT = int(os.getenv('API_PORT', '8000'))
SEARCH_TIMEOUT = int(os.getenv('SEARCH_TIMEOUT', '10'))

if not DISCORD_TOKEN:
    logger.error("DISCORD_TOKEN not found in .env")
    exit(1)


def run_fastapi():
    """Run FastAPI server in a separate thread."""
    import uvicorn
    
    app = create_app()
    
    logger.info(f"Starting FastAPI server on port {API_PORT}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=API_PORT,
        log_level="error"  # Reduce spam from INFO logs
    )


async def setup_bot():
    """Set up Discord bot with commands."""
    searcher = Searcher(search_timeout=SEARCH_TIMEOUT)
    
    # V8: Initialize PlayerManager with searcher
    from state.shared import initialize_manager
    initialize_manager(searcher)
    
    # V4: Initialize autoplay engine
    autoplay_engine = AutoplayEngine(searcher)
    set_autoplay_engine(autoplay_engine)
    
    # V5: Initialize autocomplete engine
    autocomplete_engine = SearchAutocomplete(searcher)
    set_autocomplete_engine(autocomplete_engine)
    
    bot = create_bot()
    
    # Set bot reference in shared state
    set_bot(bot)
    
    # Load music commands FIRST (with autocomplete)
    await setup_music_commands(bot, searcher, autocomplete_engine)
    
    # V4: Load autoplay commands
    await setup_autoplay_commands(bot, autoplay_engine)
    
    synced_once = False
    
    @bot.event
    async def on_ready():
        nonlocal synced_once
        logger.info(f"Bot logged in as {bot.user}")
        logger.info(f"Bot app_commands tree has {len(bot.tree._get_all_commands())} commands registered")
        
        # Sync app commands on first ready
        if not synced_once:
            try:
                logger.info("Attempting to sync app commands with Discord...")
                synced = await bot.tree.sync()
                logger.info(f"{SUCCESS} Successfully synced {len(synced)} app commands with Discord:")
                for cmd in synced:
                    logger.info(f"  ✓ /{cmd.name}")
                synced_once = True
            except Exception as e:
                logger.error(f"{ERROR} Failed to sync commands: {e}", exc_info=True)
                synced_once = False  # Retry on next ready
        
        # Start presence update task if not already running
        if not bot.presence_task or bot.presence_task.done():
            bot.presence_task = asyncio.create_task(update_presence_task(bot))
    
    async def update_presence_task(bot: commands.Bot):
        """Update bot presence based on playback status."""
        from state.shared import get_all_players
        
        await bot.wait_until_ready()
        
        while not bot.is_closed():
            try:
                players = get_all_players()
                
                # Find first playing song
                current_song = None
                for player in players.values():
                    if player.current_song and player.is_playing:
                        current_song = player.current_song
                        break
                
                if current_song:
                    # Show now playing
                    await bot.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.listening,
                            name=f"{current_song.title} - {current_song.artist}"
                        )
                    )
                else:
                    # Show default status
                    await bot.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.listening,
                            name=f"{MUSIC} Use /play to start music"
                        )
                    )
            except Exception as e:
                logger.error(f"Presence update error: {e}")
            
            # Update every 30 seconds
            await asyncio.sleep(30)
    
    # Initialize presence task attribute
    bot.presence_task = None
    
    return bot


async def main():
    """Main entry point."""
    logger.info("Discord Music Bot starting...")
    
    # Start FastAPI in background thread
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()
    logger.info(f"FastAPI thread started (serving on port {API_PORT})")
    
    # Small delay to ensure API starts before bot
    await asyncio.sleep(2)
    
    # Set up and start Discord bot
    bot = await setup_bot()
    
    logger.info("Starting Discord bot...")
    try:
        await bot.start(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)
