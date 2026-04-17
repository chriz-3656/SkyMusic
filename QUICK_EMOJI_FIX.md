# ⚡ Quick Emoji ID Fix

## The Problem
```
❌ Invalid Form Body - Invalid emoji.id in components
```

Your Discord app has emojis, but the IDs in the code don't match.

## Quick Fix (2 minutes)

### Step 1: Get Your Emoji IDs
Go to: https://discord.com/developers/applications/YOUR_APP_ID/emojis

You'll see a table like:
```
EMOJI     UPLOADED BY  EMOJI ID
play      chriz3656    1494517456844782842
pause     chriz3656    1494517412678708292
...
```

### Step 2: Read from Screenshot
From your provided screenshots, these emojis are already CORRECT in the code:
✅ loading, live, library, fav, error, eq, download, clear, autoplay

These might need updating (from screenshot 1):
❓ play, pause, stop, skip, prev, vol_up, vol_down, vol_max, mute, loop_all, loop_one, loop_off, music, artist, album, add, etc.

### Step 3: Update bot/utils/emojis.py
Open the file and check if the emoji IDs match your Discord portal.

If they don't, update them:

**Before (wrong):**
```python
PLAY = E("play", 1494517456844782842)  # ← Wrong ID
```

**After (correct):**
```python
PLAY = E("play", 1649451745684428282)  # ← Correct ID from Discord
```

### Step 4: Restart Bot
```bash
python3 -m bot.main
```

## I Can't Read the IDs from Screenshots

Run this to auto-extract:
```bash
# Make sure DISCORD_TOKEN is set
export DISCORD_TOKEN="your_bot_token"
python3 test_emoji_ids.py
```

This will fetch all emoji IDs and print the Python code you need.

---

## Common Issues

| Error | Solution |
|-------|----------|
| "Invalid emoji ID" | Emoji ID doesn't exist in Discord app - check Discord portal |
| "Emoji not found" | Emoji name doesn't match Discord - must be exact |
| "18 digit number expected" | Copy the full emoji ID without commas or spaces |

---

## Emoji Format Check

✅ Correct:
```python
PLAY = E("play", 1494517456844782842)
```

❌ Wrong:
```python
PLAY = E("play", "1494517456844782842")  # Don't use quotes!
PLAY = E("play", 1,494,517,456,844,782,842)  # Don't use commas!
PLAY = E("play", "play_emoji")  # Don't use emoji name!
```

---

Still stuck? Check EMOJI_FIX_GUIDE.md for detailed troubleshooting.
