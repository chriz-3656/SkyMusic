"""
Custom Application Emojis for SkyMusic
All emojis are custom Discord application emojis using correct IDs from Discord Developer Portal.
These IDs must match exactly - any mismatch causes "Invalid emoji.id" errors.
"""


def E(name: str, emoji_id: int) -> str:
    """Format a custom emoji for use in messages."""
    return f"<:{name}:{emoji_id}>"


# Core Controls
PLAY = E("play", 1494517415684472842)
PAUSE = E("pause", 1494517411267870892)
STOP = E("stop", 1494517441357942895)
SKIP = E("skip", 1494517437805363402)
PREV = E("prev", 1494517418633072750)

# Volume
VOL_UP = E("vol_up", 1494517460618051634)
VOL_DOWN = E("vol_down", 1494517454494236783)
VOL_MAX = E("vol_max", 1494517457157750784)
MUTE = E("mute", 1494517407409115197)

# Playback
LOOP_ALL = E("loop_all", 1494517390690619532)
LOOP_ONE = E("loop_one", 1494517398573934160)
LOOP_OFF = E("loop_off", 1494517394289332254)
AUTOPLAY = E("autoplay", 1494517361020239962)
SHUFFLE = E("shuffle", 1494517434290409554)

# Queue
QUEUE = E("queue", 1494517422554615879)
ADD = E("add", 1494517595611857119)
REMOVE = E("remove", 1494517428149813298)
CLEAR = E("clear", 1494517364065304726)
MOVE = E("move", 1494517401583353997)

# UI
SEARCH = E("search", 1494517431262253066)
SUGGEST = E("suggest", 1494517447313854577)
SUCCESS = E("success", 1494517444234969088)
ERROR = E("error", 1494517374240424076)
LOADING = E("loading", 1494517387574116493)

# Metadata
MUSIC = E("music", 1494517404787806338)
ARTIST = E("artist", 1494517603064873191)
ALBUM = E("album", 1494517599034278021)
TIME = E("time", 1494517451088597183)
LIVE = E("live", 1494517384810201219)

# Extra
FAV = E("fav", 1494517376736301208)
LIBRARY = E("library", 1494517380896915619)
DOWNLOAD = E("download", 1494517367366009016)
RADIO = E("radio", 1494517425532833954)
EQ = E("eq", 1494517370977521825)

# Status indicators
CONNECTED = SUCCESS
DISCONNECTED = ERROR
PLAYING = PLAY
PAUSED = PAUSE
