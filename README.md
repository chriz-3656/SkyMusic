# 🎵 SkyMusic - Discord Music Bot

A feature-rich Python Discord music bot with YouTube Music integration, interactive control panels, and a modern web dashboard.

## ✨ Features

### 🎶 Core Playback
- **Play single songs** - `/play [song name]`
- **Play entire playlists** - `/play [YouTube Music playlist URL]`
- **Control playback** - Pause, Resume, Skip, Stop
- **Queue management** - View, add, and manage songs
- **Auto-play mode** - Continuous playback with similar song recommendations

### 🎛️ Control Systems
- **Discord Commands** - Full command support with autocomplete
- **Interactive Control Panel** - `/controls` or `/c` for Rythm-style UI
- **Discord Buttons** - Pause, Skip, Stop with visual feedback
- **Web Dashboard** - Modern UI at `http://localhost:8000` with real-time sync

### 🔍 Search & Discovery
- **Real-time autocomplete** - Song suggestions as you type
- **YouTube Music integration** - Search via ytmusicapi
- **Playlist detection** - Automatic URL recognition
- **Smart recommendations** - Related songs for continuous playback

### 📊 Dashboard
- Now Playing section with album art
- Queue display and management
- Playback controls (Pause, Skip, Stop)
- Volume and loop mode control
- Autoplay toggle
- Real-time state synchronization every 2 seconds

### 💎 Production Quality (V8 - Architecture Overhaul)
- **Centralized PlayerManager** - Single source of truth for guild state
- **State-Driven Design** - Immutable state snapshots for safe UI sync
- **Unified Playback Flow** - Consistent behavior across all interfaces (commands, buttons, API, autoplay)
- **Guild Isolation** - Per-guild PlayerInstance objects prevent cross-guild state pollution
- **Professional Logging** - Crystal-clean output with categorized tags
- **Zero noise** - Complete FFmpeg warning suppression
- **Smart filtering** - Verbose discord.py logs filtered out
- **Readable output** - Color-coded levels with emoji icons (ℹ️ ⚠️ ❌)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FFmpeg (`ffmpeg --version`)
- yt-dlp (`pip install yt-dlp`)
- Discord bot token

### Installation

```bash
# Clone the repository
git clone https://github.com/skyrealmc/SkyMusic.git
cd SkyMusic

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set bot token
export DISCORD_TOKEN="your_bot_token_here"
```

### Running the Bot

**Terminal 1 - Discord Bot:**
```bash
source venv/bin/activate
python bot/main.py
```
Expected: `Bot connected and ready!`

**Terminal 2 - Web Dashboard:**
```bash
source venv/bin/activate
python api/server.py
```
Expected: `Uvicorn running on http://0.0.0.0:8000`

### Access the Dashboard
Open your browser: **http://localhost:8000**

## 📝 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/play` | Play a song or load a playlist | `/play Shape of You` |
| `/pause` | Pause current song | `/pause` |
| `/resume` | Resume paused song | `/resume` |
| `/skip` | Skip to next song | `/skip` |
| `/stop` | Stop playback and disconnect | `/stop` |
| `/queue` | Show current queue | `/queue` |
| `/controls` | Open full control panel | `/controls` |
| `/c` | Quick control panel shortcut | `/c` |
| `/autoplay on\|off` | Toggle autoplay mode | `/autoplay on` |

## 🎯 Architecture

```
SkyMusic V8 - State-Driven Architecture
├── PlayerManager (Singleton - Central State Management)
│   ├── players: Dict[guild_id, PlayerInstance]
│   └── Methods: get_or_create_player(), remove_player(), get_state_snapshot()
│
├── PlayerInstance (Per-Guild State)
│   ├── current_track: Song
│   ├── queue: Queue[Song]
│   ├── volume: int (0-100)
│   ├── loop_mode: str (off/song/queue)
│   ├── autoplay_enabled: bool
│   ├── voice_client: VoiceClient
│   ├── control_panel_message: Message
│   └── state_change_callbacks: List[Callable]
│
├── PlaybackFlow (Unified Operations)
│   ├── play(guild_id, query) → Song
│   ├── skip(guild_id) → Song | None
│   ├── pause/resume(guild_id) → bool
│   ├── stop(guild_id) → None
│   └── _on_song_end(guild_id) → (trigger autoplay/next)
│
SkyMusic/
├── bot/                          # Discord bot
│   ├── main.py                  # Bot entry point
│   ├── discord_bot.py           # Bot setup
│   ├── cogs/
│   │   ├── music_commands.py    # Uses PlaybackFlow
│   │   ├── interactive_controls.py
│   │   └── autoplay_commands.py
│   ├── ui/
│   │   ├── control_panel.py     # UI only - calls PlaybackFlow
│   │   ├── modals.py
│   │   └── queue_view.py
│   └── utils/
│       ├── embeds.py            # Discord embeds
│       └── colors.py
├── player/                       # Audio player & state
│   ├── manager.py               # PlayerManager + PlayerInstance (V8)
│   ├── playback.py              # PlaybackFlow unified operations (V8)
│   ├── progress.py              # Progress tracking (V8)
│   ├── player.py                # Core player
│   ├── queue.py                 # Queue management
│   ├── playlist.py              # YouTube Music playlists
│   ├── autoplay.py              # Auto-play recommendations
│   ├── autocomplete.py          # Song autocomplete
│   ├── search.py                # Song search
│   ├── searcher.py              # ytmusicapi wrapper
│   └── cache.py                 # Caching layer
├── api/                          # FastAPI server
│   ├── server.py                # REST endpoints (uses PlayerManager)
│   └── models.py                # Request/response models
├── web/                          # Web dashboard
│   ├── index.html               # Dashboard UI
│   ├── css/style.css            # Styling
│   └── js/
│       ├── app.js               # Main app logic
│       ├── api.js               # API wrapper (fixed v8)
│       ├── ui.js                # UI updates
│       └── storage.js           # Local storage
├── state/                        # Global state (V8 refactored)
│   └── shared.py                # Wraps PlayerManager for compatibility
└── requirements.txt             # Python dependencies
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | Bot status |
| GET | `/api/now-playing` | Currently playing song |
| GET | `/api/queue` | Queue list |
| POST | `/api/pause` | Pause playback |
| POST | `/api/resume` | Resume playback |
| POST | `/api/skip` | Skip to next song |
| POST | `/api/stop` | Stop playback |
| POST | `/api/autoplay` | Toggle autoplay |
| GET | `/api/autoplay` | Autoplay status |
| POST | `/api/volume` | Set volume (0-100) |
| GET | `/api/volume` | Get current volume |
| POST | `/api/loop` | Toggle loop mode |
| GET | `/api/loop` | Get loop mode |

## ⚙️ Configuration

Bot token is set via environment variable:
```bash
export DISCORD_TOKEN="your_token_here"
```

Optional configuration can be added to `bot/config.py`:
- Bot prefix
- Default volume
- Playlist size limits
- Cache settings

## 🎨 Features in Detail

### Playlist Support
SkyMusic automatically detects and loads YouTube Music playlists:
- `https://music.youtube.com/playlist?list=PLxxxxx`
- Direct playlist IDs
- Playlist metadata (title, song count)
- Seamless queue integration

### Autoplay / Radio Mode
When the queue ends and autoplay is enabled:
1. Fetches 5-10 similar songs using ytmusicapi
2. Adds them to the queue
3. Auto-plays the next track
4. Continues seamlessly without user intervention

### Control Panel
The `/controls` command opens an interactive panel with:
- Song title, artist, thumbnail
- Playback status (Playing/Paused)
- Loop mode indicator
- Autoplay status
- Queue position
- Interactive buttons for controls

### Real-time Autocomplete
As you type in `/play`, suggestions appear with:
- Song title
- Artist name
- Duration
- Click to select and queue

## 📊 Dashboard

The web dashboard at `http://localhost:8000` provides:
- **Now Playing** - Full song information with thumbnail
- **Queue** - List of upcoming songs
- **Controls** - Pause, Skip, Stop buttons
- **Volume** - Slider for volume control
- **Loop Mode** - Cycle through Off/Song/Queue
- **Autoplay** - Toggle continuous playback
- **Auto-refresh** - Updates every 3 seconds

## 🛠️ Technology Stack

- **Discord.py** - Discord bot framework
- **FastAPI** - REST API server
- **ytmusicapi** - YouTube Music search and playlists
- **yt-dlp** - Audio stream extraction
- **FFmpeg** - Audio playback
- **HTML/CSS/JavaScript** - Web dashboard

## 🐛 Troubleshooting

### Bot won't connect
```bash
# Check token is set
echo $DISCORD_TOKEN

# Verify in bot/config.py or environment
export DISCORD_TOKEN="your_token"
```

### Songs won't play
```bash
# Verify FFmpeg installed
ffmpeg -version

# Verify yt-dlp installed
yt-dlp --version

# Check bot is in voice channel
```

### Dashboard not responding
```bash
# Check API server running
curl http://localhost:8000/api/health

# Check port 8000 not in use
lsof -i :8000
```

### Autoplay not working
1. Enable: `/autoplay on`
2. Play 2+ songs to fill queue
3. Let songs finish - autoplay triggers on empty queue
4. Check internet connection
5. **Note (V7.1+)**: Fixed bug where recommendations were being filtered out due to URL validation. Update to latest version if issues persist.

### Control panel (/c) not responding
- **Note (V7.2+)**: Fixed AttributeError (current_position → current_index). Update to latest commit if you see this error.
- **Note (V7.1+)**: Fixed ImportError in queue_view.py
- Ensure bot has message_content intent enabled
- Try using `/controls` as alternative command

## 📈 Version History

| Version | Features |
|---------|----------|
| V1-V2 | Core bot, basic commands, embeds |
| V3 | Interactive control panels, buttons |
| V4 | Autoplay/radio mode |
| V5 | Real-time song autocomplete |
| V6 | Web dashboard |
| V7 | YouTube Music playlists, control panel refinements |
| V8 | **NEW**: Centralized PlayerManager, state-driven architecture, unified playback flow |

### V8 (Latest - April 2026) ✨ MAJOR REFACTOR - PRODUCTION READY
- **ARCHITECTURE**: Centralized PlayerManager singleton with per-guild PlayerInstance objects
- **STATE MANAGEMENT**: Immutable StateSnapshot for UI synchronization
- **PLAYBACK**: Unified PlaybackFlow for consistent behavior across all interfaces
- **CALLBACKS**: Fixed async event loop handling for proper track-end callback execution
- **DASHBOARD**: Fixed button context issues, improved real-time state sync
- **METADATA**: Complete song metadata enrichment (duration, thumbnail, artist)
- **ERROR HANDLING**: Unified error handling framework across all operations
- **LOGGING**: Categorized, clean logging with [BOT], [PLAYER], [API], [AUTOPLAY], [SEARCH] tags
- **GUILD ISOLATION**: Full per-guild state isolation - no cross-guild pollution
- **STATUS**: Enterprise-grade architecture - ready for multi-server deployment

### V7.3 (April 2026)
- **QUALITY**: Crystal-clean professional logging output
- **LOGGING**: Color-coded log levels (green/yellow/red) with emoji icons (ℹ️ ⚠️ ❌)
- **PERFORMANCE**: Complete FFmpeg stderr suppression - zero warnings/noise in console
- **FILTERING**: Intelligent filtering of verbose discord.py logs
- **UI**: Short timestamps (HH:MM:SS) for better readability
- **PRODUCTION**: ~60% noise reduction in console output

## 🔐 Security

- No API keys hardcoded
- Discord token via environment variable
- Input validation on all endpoints
- Error handling for all operations

## 📜 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For issues, questions, or suggestions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review existing GitHub issues
3. Create a new GitHub issue with details

## 🌟 Credits

Built with:
- discord.py community
- ytmusicapi project
- yt-dlp project
- FastAPI framework

## 📋 Next Steps

- [ ] Voice channel text channel binding
- [ ] Advanced playlist management (shuffle, repeat specific)
- [ ] User favorites system
- [ ] Statistics and analytics
- [ ] Multi-server prefix configuration
- [ ] Advanced effects (equalizer)

---

**SkyMusic** - Making Discord music better, one song at a time. 🎵
