import logging
from typing import Dict, Optional
from player.player import Player
from player.searcher import Searcher
from player.autoplay import AutoplayEngine

logger = logging.getLogger(__name__)

# Global state
_players: Dict[int, Player] = {}  # guild_id -> Player
_bot = None
_autoplay_engine: Optional[AutoplayEngine] = None
_autocomplete_engine = None  # V5: Autocomplete engine


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


def create_player(guild_id: int, searcher: Searcher) -> Player:
    """Create a new player for a guild."""
    player = Player(guild_id, searcher, autoplay_engine=_autoplay_engine)
    _players[guild_id] = player
    logger.info(f"Created player for guild {guild_id}")
    return player


def get_player(guild_id: int) -> Optional[Player]:
    """Get player for a guild."""
    return _players.get(guild_id)


def remove_player(guild_id: int) -> bool:
    """Remove player for a guild."""
    if guild_id in _players:
        del _players[guild_id]
        logger.info(f"Removed player for guild {guild_id}")
        return True
    return False


def get_all_players() -> Dict[int, Player]:
    """Get all active players."""
    return _players.copy()
