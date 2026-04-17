"""Progress bar utilities for music playback display."""


def create_progress_bar(
    current: int,
    total: int,
    bar_length: int = 10,
    empty_char: str = "░",
    filled_char: str = "█"
) -> str:
    """
    Create a visual progress bar.
    
    Args:
        current: Current position in seconds
        total: Total duration in seconds
        bar_length: Length of the bar (default 10 chars)
        empty_char: Character for empty portion
        filled_char: Character for filled portion
    
    Returns:
        Formatted progress bar string
    
    Example:
        >>> create_progress_bar(30, 60)
        '█████░░░░░'
    """
    if total <= 0:
        return empty_char * bar_length
    
    if current < 0:
        current = 0
    if current > total:
        current = total
    
    filled_length = int(bar_length * current / total)
    bar = filled_char * filled_length + empty_char * (bar_length - filled_length)
    
    return bar


def format_time(seconds: int) -> str:
    """
    Format seconds to MM:SS or H:MM:SS format.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted time string
    
    Example:
        >>> format_time(125)
        '2:05'
        >>> format_time(3661)
        '1:01:01'
    """
    if seconds < 0:
        return "0:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def create_progress_line(
    current: int,
    total: int,
    bar_length: int = 20
) -> str:
    """
    Create a complete progress line with times.
    
    Args:
        current: Current position in seconds
        total: Total duration in seconds
        bar_length: Length of the progress bar
    
    Returns:
        Complete progress line like "0:30 ████████░░░░░░░░░░ 3:45"
    
    Example:
        >>> create_progress_line(30, 225)
        '0:30 █████░░░░░░░░░░░░░░ 3:45'
    """
    bar = create_progress_bar(current, total, bar_length)
    current_time = format_time(current)
    total_time = format_time(total)
    
    return f"{current_time} {bar} {total_time}"


if __name__ == "__main__":
    # Test examples
    print("Progress bar examples:")
    print(create_progress_line(30, 225))
    print(create_progress_line(112, 225))
    print(create_progress_line(225, 225))
    print(create_progress_line(0, 0))
