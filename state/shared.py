import logging
from typing import Optional
from player.manager import PlayerManager
from player.searcher import Searcher
from player.autoplay import AutoplayEngine

logger = logging.getLogger(__name__)

# Global state
_bot = None
_autoplay_engine: Optional[AutoplayEngine] = None
_autocomplete_engine = None

# V8: Use PlayerManager as single source of truth
_manager = PlayerManager()


def set_bot(bot):
    """Set bot reference for API access."""
    global _bot
    _bot = bot


def get_bot():
    """Get bot reference."""
    return _bot


def set_autoplay_engine(engine: AutoplayEngine):
    """Set the autoplay engine."""
    global _autoplay_engine
    _autoplay_engine = engine
    _manager.set_autoplay_engine(engine)
    logger.info("Autoplay engine initialized")


def get_autoplay_engine() -> Optional[AutoplayEngine]:
    """Get the autoplay engine."""
    return _autoplay_engine


def set_autocomplete_engine(engine):
    """V5: Set the autocomplete engine."""
    global _autocomplete_engine
    _autocomplete_engine = engine
    logger.info("Autocomplete engine initialized")


def get_autocomplete_engine():
    """V5: Get the autocomplete engine."""
    return _autocomplete_engine


def initialize_manager(searcher: Searcher) -> None:
    """Initialize PlayerManager with searcher."""
    _manager.set_searcher(searcher)
    logger.info("[MANAGER] PlayerManager initialized with searcher")


def get_manager() -> PlayerManager:
    """Get the global PlayerManager instance."""
    return _manager


def create_player(guild_id: int, searcher: Searcher):
    """DEPRECATED: Use get_manager().get_or_create_player() instead.
    
    Kept for backward compatibility with V7.3 code.
    """
    _manager.set_searcher(searcher)
    return _manager.get_or_create_player(guild_id)


def get_player(guild_id: int):
    """DEPRECATED: Use get_manager().get_player() instead.
    
    Kept for backward compatibility with V7.3 code.
    Returns PlayerInstance (V8) or creates if doesn't exist.
    """
    player = _manager.get_player(guild_id)
    if not player and _manager.searcher:
        player = _manager.get_or_create_player(guild_id)
    return player


def remove_player(guild_id: int) -> bool:
    """Remove player for a guild."""
    return _manager.remove_player(guild_id)


def get_all_players():
    """Get all active players."""
    return _manager.get_all_players()
