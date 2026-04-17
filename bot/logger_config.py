"""Enhanced logging configuration for SkyMusic bot."""

import logging
import sys
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for different log levels."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
        'BOLD': '\033[1m',        # Bold
    }
    
    # Emoji icons for different log types
    ICONS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️ ',
        'WARNING': '⚠️ ',
        'ERROR': f'{ERROR}',
        'CRITICAL': '🔴',
    }
    
    def format(self, record):
        """Format log record with colors and icons."""
        # Short time format (HH:MM:SS)
        time_str = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Get color for this level
        level_color = self.COLORS.get(record.levelname, self.COLORS['INFO'])
        reset_color = self.COLORS['RESET']
        
        # Get icon for this level
        icon = self.ICONS.get(record.levelname, '•')
        
        # Filter out verbose module names
        module_name = record.name
        if module_name.startswith('discord.'):
            # Shorten discord.py logs
            parts = module_name.split('.')
            if len(parts) > 2:
                module_name = f"{parts[0]}.{parts[1]}"
        
        # Format the message
        message = record.getMessage()
        
        # Suppress FFmpeg warnings about -ac and -ar options (harmless)
        if 'Multiple -ac options' in message or 'Multiple -ar options' in message:
            return ''  # Skip this log
        
        # Suppress low-level discord.py info logs (voice handshake, etc.)
        if module_name.startswith('discord.') and record.levelname == 'INFO':
            if any(x in message for x in ['voice handshake', 'Voice handshake', 'connecting', 
                                          'Connecting', 'connection complete', 'Connection complete',
                                          'has connected', 'Voice connection', 'Shard ID']):
                return ''  # Skip verbose discord logs
        
        # Build the log line
        log_line = (
            f"{level_color}{icon} {reset_color}"
            f"[{time_str}] "
            f"{level_color}{record.levelname:<8}{reset_color} "
            f"│ {message}"
        )
        
        return log_line


def setup_logging(log_level=logging.INFO):
    """
    Configure logging with enhanced formatter.
    
    Args:
        log_level: Logging level (default: INFO)
    """
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Apply custom formatter
    formatter = ColoredFormatter()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers and add our custom one
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # Set specific log levels for verbose libraries
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('discord.gateway').setLevel(logging.WARNING)
    logging.getLogger('discord.client').setLevel(logging.WARNING)
    logging.getLogger('discord.voice_state').setLevel(logging.WARNING)
    logging.getLogger('discord.player').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    # Keep app logs at INFO level
    logging.getLogger('__main__').setLevel(log_level)
    logging.getLogger('bot').setLevel(log_level)
    logging.getLogger('player').setLevel(log_level)
    logging.getLogger('state').setLevel(log_level)
    logging.getLogger('api').setLevel(log_level)
    
    return root_logger
