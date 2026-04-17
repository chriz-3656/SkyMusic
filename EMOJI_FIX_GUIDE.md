# 🎨 Fixing Invalid Emoji IDs - SkyMusic Bot

## Problem
Your Discord bot is showing this error:
```
❌ Invalid Form Body
In components.0.components.0.emoji.id: Invalid emoji
In components.0.components.1.emoji.id: Invalid emoji
```

This means the emoji IDs in `bot/utils/emojis.py` don't match the actual emoji IDs in your Discord application.

---

## Solution

You have **3 options** to fix this. Start with **Option 1** (easiest).

### ✅ Option 1: Automatic Detection (Recommended)

Run this command:
```bash
export DISCORD_TOKEN="your_bot_token_here"
python3 test_emoji_ids.py
```

This will:
1. Connect your bot to Discord
2. Fetch all emoji IDs from your Discord app
3. Print the exact Python code needed for `bot/utils/emojis.py`
4. Copy the output and paste it into the file

**Steps:**
1. Get your bot token from Discord Developer Portal
2. Run the command above (replace `your_bot_token_here` with the actual token)
3. Copy the output
4. Open `bot/utils/emojis.py`
5. Replace the emoji definitions with the output
6. Save and restart your bot

---

### 📋 Option 2: Manual Copy from Discord Portal

1. Go to: https://discord.com/developers/applications
2. Select your "SkyMusic" application
3. Click **Emojis** in the left sidebar
4. You'll see a table with columns: EMOJI | UPLOADED BY | EMOJI ID

5. For each emoji, copy the name and ID in this format:
   ```
   emoji_name: emoji_id
   play: 1494517456844782842
   pause: 1494517412678708292
   stop: 1494517441357942895
   ...etc
   ```

6. Run this script:
   ```bash
   python3 extract_emoji_ids.py
   ```

7. Paste your emoji data when prompted

---

### 🔧 Option 3: Browser DevTools (Advanced)

1. Open Discord Developer Portal in your browser
2. Navigate to your app's Emojis section
3. Press **F12** to open DevTools
4. Go to the **Console** tab
5. Paste this code:

```javascript
copy(
    Array.from(document.querySelectorAll('tr'))
        .slice(1)  // Skip header row
        .map(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 3) {
                const name = cells[0].textContent.trim();
                const id = cells[2].textContent.trim();
                return `${name}: ${id}`;
            }
            return null;
        })
        .filter(x => x)
        .join('\n')
)
```

6. This copies all emoji names and IDs to your clipboard
7. Paste into the `extract_emoji_ids.py` script or manually into `bot/utils/emojis.py`

---

## How to Identify Valid Emoji IDs

✅ **Valid Discord Emoji ID Format:**
- 18-19 digit number (Discord snowflake)
- Examples: `1494517456844782842`, `1649451750306048331`

❌ **Invalid Examples:**
- Text without numbers
- Numbers with letters (like: `1649451750306048f3f1`)
- Very short numbers (less than 15 digits)

---

## Testing After Fix

Once you've updated `bot/utils/emojis.py`:

1. Restart your bot:
   ```bash
   python3 -m bot.main
   ```

2. Watch for this message:
   ```
   ✅ Successfully synced 10 app commands with Discord
   ```

3. Test in Discord:
   - Use `/play` command
   - Check that buttons appear without errors
   - Verify emojis display correctly

---

## If You Still Get Errors

**Double-check:**
1. All emoji IDs are 18-19 digits long
2. No spaces in emoji ID
3. No commas or special characters
4. Check that ALL emojis exist in Discord (didn't get deleted)

**To verify emojis exist:**
- Go to Discord Developer Portal
- Click Emojis
- Search for the emoji name
- Confirm it's listed with an ID

**If emoji is missing:**
1. Upload it again to Discord
2. Copy the new ID
3. Update `bot/utils/emojis.py`

---

## Emoji Reference

Here are the emojis that must exist in your Discord app:

**Core Controls:**  
play, pause, stop, skip, prev

**Volume:**  
vol_up, vol_down, vol_max, mute

**Playback:**  
loop_all, loop_one, loop_off, autoplay, shuffle

**Queue:**  
queue, add, remove, clear, move

**UI:**  
search, suggest, success, error, loading

**Metadata:**  
music, artist, album, time, live

**Extra:**  
fav, library, download, radio, eq, warning, info, debug

---

## File Locations

- **Emoji Config:** `bot/utils/emojis.py`
- **Helper Script:** `test_emoji_ids.py` (auto-detect emoji IDs)
- **Manual Tool:** `extract_emoji_ids.py` (interactive tool)
- **Control Panel:** `bot/ui/control_panel.py` (uses emojis)

---

## Need Help?

If you're still stuck:

1. Check Discord's status - is the API working?
2. Verify your bot has the right permissions
3. Make sure the emoji names in Discord EXACTLY match the variable names in the code
4. Try running `test_emoji_ids.py` for automatic detection

Good luck! 🎵
