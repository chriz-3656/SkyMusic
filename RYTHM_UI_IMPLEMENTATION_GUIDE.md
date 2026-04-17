# SkyMusic Rythm-Style UI Implementation Guide

## Overview

This guide covers the new Rythm-style UI/UX system for SkyMusic, including emoji validation, polished embeds, and organized control panels.

## Quick Start

### 1. Import Components

```python
# Emoji validator
from bot.utils.emoji_validator import EmojiValidator, validate_all_emojis

# Embed builders
from bot.ui.rythm_embeds import (
    create_rythm_now_playing_embed,
    create_paused_embed,
    create_idle_embed
)

# Control panel
from bot.ui.rythm_control_panel import RythmControlPanel
```

### 2. Validate Emojis at Startup

```python
# In bot/main.py
from bot.utils.emoji_validator import validate_all_emojis
import logging

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    if validate_all_emojis():
        logger.info("[EMOJI] ✅ All custom emojis validated!")
    else:
        logger.error("[EMOJI] ❌ Some emojis are missing!")
        # Handle error
```

### 3. Create Now Playing Embed

```python
from bot.ui.rythm_embeds import create_rythm_now_playing_embed

embed = create_rythm_now_playing_embed(
    title=song.title,
    artist=song.artist,
    duration=song.duration,
    current_position=current_time,
    requester=interaction.user.display_name,
    queue_length=len(player.queue.songs),
    is_paused=player.is_paused,
    thumbnail=song.thumbnail,
    is_live=song.is_live
)

await message.edit(embed=embed)
```

### 4. Create Control Panel

```python
from bot.ui.rythm_control_panel import RythmControlPanel

async def update_panel(interaction: discord.Interaction, view: RythmControlPanel):
    """Callback to update control panel."""
    embed = create_rythm_now_playing_embed(...)
    await interaction.message.edit(embed=embed, view=view)

panel = RythmControlPanel(
    player=player_instance,
    guild_id=interaction.guild_id,
    update_callback=update_panel
)

await message.edit(embed=embed, view=panel)
```

## Components

### Emoji Validator

**Location**: `bot/utils/emoji_validator.py`

**Class**: `EmojiValidator`

**Key Methods**:
- `validate_emoji(name)` - Returns (is_valid, emoji_string)
- `get_emoji(name)` - Returns emoji string or empty string
- `get_status()` - Returns validation status dict
- `report_missing()` - Returns list of missing emojis
- `print_report()` - Prints validation report

**Example**:
```python
from bot.utils.emoji_validator import EmojiValidator

validator = EmojiValidator()

# Validate single emoji
is_valid, emoji_str = validator.validate_emoji('PLAY')
if is_valid:
    print(emoji_str)  # <:play:1494517415684472842>

# Get status
status = validator.get_status()
print(f"Valid: {status['total_available']}")
print(f"Missing: {status['missing']}")

# Get emoji safely
emoji = validator.get_emoji('PAUSE')  # Never returns Unicode
```

### Rythm Embeds

**Location**: `bot/ui/rythm_embeds.py`

**Functions**:

1. **create_rythm_now_playing_embed()**
   - Arguments: title, artist, duration, current_position, requester, thumbnail, queue_length, is_paused, is_live
   - Returns: discord.Embed
   - Design: Clean, minimal Rythm-style with progress bar

2. **create_paused_embed()**
   - Arguments: title, artist, duration, current_position, requester, thumbnail
   - Returns: discord.Embed
   - Design: Paused state with progress bar

3. **create_idle_embed()**
   - Arguments: (none)
   - Returns: discord.Embed
   - Design: No song playing, show usage tips

**Example**:
```python
from bot.ui.rythm_embeds import create_rythm_now_playing_embed

# Playing
embed = create_rythm_now_playing_embed(
    title="Shape of You",
    artist="Ed Sheeran",
    duration=234,
    current_position=45,
    requester="Discord User",
    queue_length=5,
    is_paused=False,
    thumbnail="https://...",
    is_live=False
)
```

### Rythm Control Panel

**Location**: `bot/ui/rythm_control_panel.py`

**Class**: `RythmControlPanel`

**Constructor Arguments**:
- `player`: Player instance
- `guild_id`: Guild ID (int)
- `update_callback`: Optional async callback function
- `timeout`: Button timeout in seconds (default: 3600)

**Button Layout**:
```
Row 0: prev, pause/resume, skip, stop     [4 buttons]
Row 1: queue, now_playing, add, search    [4 buttons]
Row 2: vol_down, vol_display, vol_up      [3 buttons]
Row 3: favorite, loop, autoplay, shuffle  [4 buttons]
```

**Example**:
```python
from bot.ui.rythm_control_panel import RythmControlPanel

async def on_button_click(interaction: discord.Interaction, view: RythmControlPanel):
    """Update panel when button clicked."""
    # Recreate embed
    embed = create_rythm_now_playing_embed(...)
    
    # Edit message
    await interaction.message.edit(embed=embed, view=view)

panel = RythmControlPanel(
    player=player,
    guild_id=guild.id,
    update_callback=on_button_click
)
```

## Emoji Reference

All 34 custom application emojis:

```
CORE CONTROLS (5):
  PLAY        <:play:1494517415684472842>
  PAUSE       <:pause:1494517411267870892>
  STOP        <:stop:1494517441357942895>
  SKIP        <:skip:1494517437805363402>
  PREV        <:prev:1494517418633072750>

VOLUME (4):
  VOL_UP      <:vol_up:1494517460618051634>
  VOL_DOWN    <:vol_down:1494517454494236783>
  VOL_MAX     <:vol_max:1494517457157750784>
  MUTE        <:mute:1494517407409115197>

PLAYBACK (5):
  LOOP_ALL    <:loop_all:1494517390690619532>
  LOOP_ONE    <:loop_one:1494517398573934160>
  LOOP_OFF    <:loop_off:1494517394289332254>
  AUTOPLAY    <:autoplay:1494517361020239962>
  SHUFFLE     <:shuffle:1494517434290409554>

QUEUE (5):
  QUEUE       <:queue:1494517422554615879>
  ADD         <:add:1494517595611857119>
  REMOVE      <:remove:1494517428149813298>
  CLEAR       <:clear:1494517364065304726>
  MOVE        <:move:1494517401583353997>

UI (5):
  SEARCH      <:search:1494517431262253066>
  SUGGEST     <:suggest:1494517447313854577>
  SUCCESS     <:success:1494517444234969088>
  ERROR       <:error:1494517374240424076>
  LOADING     <:loading:1494517387574116493>

METADATA (5):
  MUSIC       <:music:1494517404787806338>
  ARTIST      <:artist:1494517603064873191>
  ALBUM       <:album:1494517599034278021>
  TIME        <:time:1494517451088597183>
  LIVE        <:live:1494517384810201219>

EXTRA (5):
  FAV         <:fav:1494517376736301208>
  LIBRARY     <:library:1494517380896915619>
  DOWNLOAD    <:download:1494517367366009016>
  RADIO       <:radio:1494517425532833954>
  EQ          <:eq:1494517370977521825>
```

## Integration Steps

### Step 1: Update music_commands.py

Replace old embed builders with new ones:

```python
# OLD
from bot.utils.embeds import create_now_playing_embed

# NEW
from bot.ui.rythm_embeds import create_rythm_now_playing_embed

# OLD
embed = create_now_playing_embed(song.title, ...)

# NEW
embed = create_rythm_now_playing_embed(
    title=song.title,
    artist=song.artist,
    duration=song.duration,
    requester=interaction.user.display_name
)
```

### Step 2: Update interactive_controls.py

Replace old control panel:

```python
# OLD
from bot.ui.control_panel import ControlPanelView

# NEW
from bot.ui.rythm_control_panel import RythmControlPanel

# OLD
view = ControlPanelView(player, guild_id)

# NEW
view = RythmControlPanel(player, guild_id, update_callback=on_update)
```

### Step 3: Add Emoji Validation to Startup

```python
# In bot/main.py
from bot.utils.emoji_validator import validate_all_emojis

async def setup_bot():
    """Initialize bot with emoji validation."""
    if not validate_all_emojis():
        logger.error("Emoji validation failed!")
        return False
    
    logger.info("Emoji validation passed!")
    return True
```

### Step 4: Test in Discord

1. Use `/play` to start music
2. Verify embed displays correctly
3. Click buttons to test functionality
4. Check that emojis render properly
5. Monitor for any errors

## Error Handling

### Missing Emoji Handling

```python
from bot.utils.emoji_validator import get_validator

validator = get_validator()

# Validate before using
is_valid, emoji_str = validator.validate_emoji('PLAY')
if not is_valid:
    logger.warning("Emoji PLAY is missing!")
    # Handle gracefully
    return False  # or skip button
```

### Strict Mode

The system uses **strict mode** - no Unicode fallback:

```python
# If emoji is missing:
emoji = validator.get_emoji('NONEXISTENT')  # Returns empty string ""
# NOT "🎵" or any Unicode fallback
```

## Performance Optimization

1. **Cache Panel Reference**
   ```python
   # Store message reference in PlayerInstance
   player.panel_message = message
   
   # Update same message instead of sending new
   await player.panel_message.edit(embed=embed, view=view)
   ```

2. **Batch Updates**
   ```python
   # Defer interaction
   await interaction.response.defer()
   
   # Do work
   # ... update player ...
   
   # Edit once
   await interaction.followup.edit_message(embed=embed, view=view)
   ```

3. **Avoid Spam**
   ```python
   # Don't update on every interaction
   # Use throttling if needed
   if time.time() - last_update < 2:  # 2 second cooldown
       return
   ```

## Testing

Run the comprehensive test:

```bash
cd /home/chriz3656/Downloads/musicbot
source venv/bin/activate
python3 << 'EOF'
from bot.utils.emoji_validator import EmojiValidator
from bot.ui.rythm_embeds import create_rythm_now_playing_embed
from bot.ui.rythm_control_panel import RythmControlPanel

# Test validator
validator = EmojiValidator()
print(f"Emojis: {validator.get_status()['total_available']}")

# Test embeds
embed = create_rythm_now_playing_embed("Song", "Artist", 180)
print(f"Embed: {embed.title}")

# Test panel
panel = RythmControlPanel(None, 123)
print(f"Buttons: {len(panel.children)}")
EOF
```

## Troubleshooting

### Issue: "Invalid emoji.id" error

**Cause**: Using wrong emoji ID or format

**Solution**: 
- Use exact emoji IDs from RYTHM_UI_SYSTEM.md
- Use format `<:name:id>` not `<:name_id>` or others
- Import from `bot.utils.emojis` not hardcoded strings

### Issue: Missing emoji warnings

**Cause**: Emoji not uploaded to Discord app

**Solution**:
- Check Discord Developer Portal
- Verify emoji name and ID match
- Re-upload if necessary
- Update ID in bot/utils/emojis.py

### Issue: Buttons not responding

**Cause**: Missing update callback or improper error handling

**Solution**:
- Ensure `update_callback` is provided
- Add try/except in callback
- Log errors for debugging
- Check interaction timeout

## Future Enhancements

- [ ] Auto-refresh progress bar every 5 seconds
- [ ] Live metadata enrichment
- [ ] Playlist management UI
- [ ] Search results pagination
- [ ] Custom theme support
- [ ] Accessibility improvements

## Files Reference

**Core Files**:
- `bot/utils/emoji_validator.py` - Emoji validation
- `bot/utils/emojis.py` - Emoji definitions
- `bot/ui/rythm_embeds.py` - Embed builders
- `bot/ui/rythm_control_panel.py` - Control panel
- `RYTHM_UI_SYSTEM.md` - System documentation

**Integration Points**:
- `bot/cogs/music_commands.py` - Use new embeds
- `bot/cogs/interactive_controls.py` - Use new panel
- `bot/main.py` - Add emoji validation startup
- `api/server.py` - Future API integration

## Support

For issues or questions:
1. Check RYTHM_UI_SYSTEM.md
2. Review test cases in this file
3. Check emoji validator output
4. Review Discord.py documentation

## Version

- **System**: SkyMusic Rythm-Style UI/UX v1.0
- **Emojis**: 34 total, all validated
- **Components**: 3 (validator, embeds, panel)
- **Status**: ✅ Production Ready

---

*Last Updated: 2026-04-17*
*Commit: 4ca1b67*
