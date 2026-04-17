"""Emoji validation system for SkyMusic custom emojis."""

import logging
from typing import Dict, List, Set, Tuple
from . import emojis

logger = logging.getLogger(__name__)


class EmojiValidator:
    """Validates and tracks custom emoji usage."""
    
    # All available custom emojis in SkyMusic
    AVAILABLE_EMOJIS = {
        # Core Controls
        'PLAY': emojis.PLAY,
        'PAUSE': emojis.PAUSE,
        'STOP': emojis.STOP,
        'SKIP': emojis.SKIP,
        'PREV': emojis.PREV,
        
        # Volume
        'VOL_UP': emojis.VOL_UP,
        'VOL_DOWN': emojis.VOL_DOWN,
        'VOL_MAX': emojis.VOL_MAX,
        'MUTE': emojis.MUTE,
        
        # Playback
        'LOOP_ALL': emojis.LOOP_ALL,
        'LOOP_ONE': emojis.LOOP_ONE,
        'LOOP_OFF': emojis.LOOP_OFF,
        'AUTOPLAY': emojis.AUTOPLAY,
        'SHUFFLE': emojis.SHUFFLE,
        
        # Queue
        'QUEUE': emojis.QUEUE,
        'ADD': emojis.ADD,
        'REMOVE': emojis.REMOVE,
        'CLEAR': emojis.CLEAR,
        'MOVE': emojis.MOVE,
        
        # UI
        'SEARCH': emojis.SEARCH,
        'SUGGEST': emojis.SUGGEST,
        'SUCCESS': emojis.SUCCESS,
        'ERROR': emojis.ERROR,
        'LOADING': emojis.LOADING,
        
        # Metadata
        'MUSIC': emojis.MUSIC,
        'ARTIST': emojis.ARTIST,
        'ALBUM': emojis.ALBUM,
        'TIME': emojis.TIME,
        'LIVE': emojis.LIVE,
        
        # Extra
        'FAV': emojis.FAV,
        'LIBRARY': emojis.LIBRARY,
        'DOWNLOAD': emojis.DOWNLOAD,
        'RADIO': emojis.RADIO,
        'EQ': emojis.EQ,
    }
    
    def __init__(self):
        """Initialize emoji validator."""
        self.used_emojis: Set[str] = set()
        self.missing_emojis: List[str] = []
        self.valid_emoji_ids: Dict[str, int] = self._extract_ids()
    
    def _extract_ids(self) -> Dict[str, int]:
        """Extract emoji IDs from emoji strings."""
        ids = {}
        for name, emoji_str in self.AVAILABLE_EMOJIS.items():
            # Parse "<:name:id>" format
            try:
                emoji_id = int(emoji_str.split(':')[-1].rstrip('>'))
                ids[name] = emoji_id
            except (ValueError, IndexError):
                logger.warning(f"[EMOJI] Failed to parse emoji ID from: {emoji_str}")
        return ids
    
    def validate_emoji(self, emoji_name: str) -> Tuple[bool, str]:
        """
        Validate if an emoji exists and return its string.
        
        Args:
            emoji_name: Name of the emoji (e.g., 'PLAY', 'PAUSE')
        
        Returns:
            Tuple of (is_valid, emoji_string)
        """
        if emoji_name not in self.AVAILABLE_EMOJIS:
            self.missing_emojis.append(emoji_name)
            logger.warning(f"[EMOJI] Missing emoji: {emoji_name}")
            return False, ""
        
        self.used_emojis.add(emoji_name)
        emoji_str = self.AVAILABLE_EMOJIS[emoji_name]
        
        # Validate the emoji string format
        if not self._is_valid_format(emoji_str):
            logger.warning(f"[EMOJI] Invalid format for {emoji_name}: {emoji_str}")
            return False, ""
        
        return True, emoji_str
    
    def _is_valid_format(self, emoji_str: str) -> bool:
        """Check if emoji string is in correct format: <:name:id>"""
        if not emoji_str.startswith('<:') or not emoji_str.endswith('>'):
            return False
        
        parts = emoji_str[2:-1].split(':')
        if len(parts) != 2:
            return False
        
        name, emoji_id = parts
        if not name or not emoji_id.isdigit():
            return False
        
        return True
    
    def get_emoji(self, emoji_name: str) -> str:
        """
        Get emoji string, with validation.
        Falls back to empty string if missing (NO Unicode fallback).
        
        Args:
            emoji_name: Name of the emoji
        
        Returns:
            Emoji string or empty string
        """
        is_valid, emoji_str = self.validate_emoji(emoji_name)
        return emoji_str if is_valid else ""
    
    def report_missing(self) -> List[str]:
        """
        Get list of missing emojis that were requested.
        
        Returns:
            List of missing emoji names
        """
        return list(set(self.missing_emojis))  # Remove duplicates
    
    def report_unused(self) -> List[str]:
        """
        Get list of available emojis that were never used.
        
        Returns:
            List of unused emoji names
        """
        return [name for name in self.AVAILABLE_EMOJIS.keys() 
                if name not in self.used_emojis]
    
    def get_status(self) -> Dict:
        """Get validation status report."""
        missing = self.report_missing()
        unused = self.report_unused()
        
        return {
            'total_available': len(self.AVAILABLE_EMOJIS),
            'used': len(self.used_emojis),
            'missing': missing,
            'unused': unused,
            'status': 'VALID' if not missing else 'INCOMPLETE'
        }
    
    def print_report(self):
        """Print validation report to logger."""
        status = self.get_status()
        
        logger.info(f"[EMOJI] Validation Report:")
        logger.info(f"  Total Available: {status['total_available']}")
        logger.info(f"  Used: {status['used']}")
        logger.info(f"  Status: {status['status']}")
        
        if status['missing']:
            logger.warning(f"[EMOJI] Missing emojis ({len(status['missing'])}):")
            for emoji_name in sorted(status['missing']):
                logger.warning(f"  - {emoji_name}")
        
        if status['unused']:
            logger.debug(f"[EMOJI] Unused emojis ({len(status['unused'])}):")
            for emoji_name in sorted(status['unused']):
                logger.debug(f"  - {emoji_name}")


# Global validator instance
_validator = None


def get_validator() -> EmojiValidator:
    """Get global emoji validator instance."""
    global _validator
    if _validator is None:
        _validator = EmojiValidator()
    return _validator


def validate_all_emojis():
    """Validate all emojis are available."""
    validator = get_validator()
    missing = validator.report_missing()
    
    if missing:
        logger.warning(f"[EMOJI] {len(missing)} emojis are missing:")
        for emoji_name in sorted(missing):
            logger.warning(f"  [MISSING] {emoji_name}")
        return False
    
    return True
