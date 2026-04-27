import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Add the current directory to the front of sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from bot.main import main as start_bot

# Configure basic logging for startup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SkyMusic-Launcher")

if __name__ == "__main__":
    logger.info("SkyMusic Root Launcher starting...")
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Launch the main bot process (which also starts the API)
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logger.info("SkyMusic shutting down...")
    except Exception as e:
        logger.error(f"Fatal error during startup: {e}", exc_info=True)
        sys.exit(1)
