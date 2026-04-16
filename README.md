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
- **Web Dashboard** - Modern UI at `http://localhost:8000`

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
- Auto-refresh every 3 seconds

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
SkyMusic/
├── bot/                          # Discord bot
│   ├── main.py                  # Bot entry point
│   ├── discord_bot.py           # Bot setup
│   ├── cogs/
│   │   ├── music_commands.py    # Play, pause, skip, etc.
│   │   ├── interactive_controls.py
│   │   └── autoplay_commands.py
│   ├── ui/
│   │   ├── control_panel.py     # Interactive buttons
│   │   ├── modals.py
│   │   └── queue_view.py
│   └── utils/
│       ├── embeds.py            # Discord embeds
│       └── colors.py
├── player/                       # Audio player
│   ├── player.py                # Core player
│   ├── queue.py                 # Queue management
│   ├── playlist.py              # YouTube Music playlists
│   ├── autoplay.py              # Auto-play recommendations
│   ├── autocomplete.py          # Song autocomplete
│   ├── search.py                # Song search
│   ├── searcher.py              # ytmusicapi wrapper
│   └── cache.py                 # Caching layer
├── api/                          # FastAPI server
│   ├── server.py                # REST endpoints
│   └── models.py                # Request/response models
├── web/                          # Web dashboard
│   ├── index.html               # Dashboard UI
│   ├── css/style.css            # Styling
│   └── js/app.js                # Client logic
├── state/                        # Global state
│   └── shared.py                # Shared player state
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

## 📈 Version History

| Version | Features |
|---------|----------|
| V1-V2 | Core bot, basic commands, embeds |
| V3 | Interactive control panels, buttons |
| V4 | Autoplay/radio mode |
| V5 | Real-time song autocomplete |
| V6 | Web dashboard |
| **V7** | YouTube Music playlists, control panel shortcuts, full fixes |

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
