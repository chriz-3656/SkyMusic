"""
Progress tracking utility for music playback.
Generates progress bars and time displays.
"""


def format_duration(seconds: int) -> str:
    """Format seconds to MM:SS format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string like "3:45"
    """
    if seconds < 0:
        seconds = 0
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def generate_progress_bar(current: int, total: int, length: int = 20) -> str:
    """Generate a visual progress bar.
    
    Args:
        current: Current position in seconds
        total: Total duration in seconds
        length: Length of progress bar in characters
        
    Returns:
        Progress bar string like "████████░░░░░░░░░░░░"
    """
    if total <= 0:
        return "░" * length
    
    progress = min(current / total, 1.0)
    filled = int(length * progress)
    empty = length - filled
    
    return "█" * filled + "░" * empty


def format_progress_display(current: int, total: int, bar_length: int = 20) -> str:
    """Format progress with bar and time display.
    
    Args:
        current: Current position in seconds
        total: Total duration in seconds
        bar_length: Length of progress bar
        
    Returns:
        Formatted string like:
        "████████░░░░░░░░░░░░
         1:23 / 3:45"
    """
    bar = generate_progress_bar(current, total, bar_length)
    time_display = f"{format_duration(current)} / {format_duration(total)}"
    return f"{bar}\n{time_display}"


def get_progress_percentage(current: int, total: int) -> int:
    """Get progress as percentage.
    
    Args:
        current: Current position in seconds
        total: Total duration in seconds
        
    Returns:
        Percentage (0-100)
    """
    if total <= 0:
        return 0
    return min(int((current / total) * 100), 100)
