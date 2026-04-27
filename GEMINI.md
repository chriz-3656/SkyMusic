# SkyMusic Bot Context

SkyMusic is a high-performance Discord music bot (V8) that features a unified architecture combining a Discord bot and a real-time web control panel. It focuses on providing a seamless music experience with features like autoplay, search autocomplete, and a modern web dashboard.

## Project Overview

- **Core Functionality:** Music playback in Discord voice channels with support for YouTube and YouTube Music.
- **Unified Architecture:** A single process running both the `discord.py` bot and a `FastAPI` web server.
- **Key Features:**
  - Real-time web dashboard for controlling playback.
  - Per-guild player isolation with a centralized manager.
  - Advanced search with autocomplete.
  - Autoplay engine for continuous music.
  - Enhanced logging with colored console output.

## Tech Stack

- **Language:** Python 3.8+
- **Discord Library:** `discord.py` (v2.3.0+)
- **API Framework:** `FastAPI` (with `uvicorn`)
- **Music Extraction:** `yt-dlp` and `ytmusicapi`
- **Frontend:** Vanilla JavaScript, HTML, CSS (located in `web/`)
- **State Management:** Custom shared state and singleton `PlayerManager`.

## Project Structure

- `bot/`: Discord bot implementation.
  - `main.py`: Main entry point (starts both Bot and API).
  - `discord_bot.py`: Bot configuration and event handlers.
  - `cogs/`: Discord command groups (music, autoplay, interactive controls).
  - `ui/`: Discord UI components (Embeds, Views, Modals).
- `api/`: FastAPI server and models.
  - `server.py`: REST API endpoints and static file serving.
- `player/`: Core music logic.
  - `manager.py`: Centralized management of per-guild `PlayerInstance`s.
  - `queue.py`: Song and Queue data structures.
  - `playback.py`: Low-level FFmpeg playback handling.
  - `searcher.py`: YouTube/Music search integration.
  - `autoplay.py`: Logic for suggesting next tracks.
- `state/`: Shared state for inter-module communication.
- `web/`: Frontend assets for the web dashboard.
- `skymusic_emoji_pack/`: Custom assets for the bot's UI.

## Getting Started

### Prerequisites

1.  Python 3.8 or higher.
2.  FFmpeg installed and in the system path (required for audio playback).
3.  A Discord Bot Token from the [Discord Developer Portal](https://discord.com/developers/applications).

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```env
DISCORD_TOKEN=your_token_here
API_PORT=8000
SEARCH_TIMEOUT=10
```

### Running the Project

```bash
# Run both the Bot and the Web Dashboard
python bot/main.py
```

The bot will start, and the web dashboard will be accessible at `http://localhost:8000`.

## Development Conventions

- **Asynchronous Code:** The project heavily uses `asyncio`. Use `await` for all I/O bound operations.
- **Logging:** Use the enhanced logger configured in `bot/logger_config.py`. Avoid `print()` statements.
- **State Snapshots:** When communicating state changes to the UI (Web or Discord), use `StateSnapshot` objects from `player/manager.py` to ensure consistency.
- **Slash Commands:** The bot primarily uses Discord Slash Commands. Ensure to sync the command tree (`bot.tree.sync()`) when adding new commands.
- **Error Handling:** Use `try/except` blocks in command handlers to prevent the bot from crashing and provide feedback to the user via Discord embeds.
