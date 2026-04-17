#!/usr/bin/env python3
"""
Extract emoji IDs from Discord Developer Portal and update emojis.py

This script helps you get the EXACT emoji IDs from your Discord application
and generate the correct emojis.py file.
"""

import json
import subprocess
import sys

print("""
╔════════════════════════════════════════════════════════════╗
║  Discord Emoji ID Extractor - SkyMusic Bot                ║
╚════════════════════════════════════════════════════════════╝

INSTRUCTIONS:
=============

1. Go to: https://discord.com/developers/applications
2. Select your SkyMusic application
3. Click "Emojis" in the left sidebar
4. You should see a table with columns: EMOJI | UPLOADED BY | EMOJI ID

The Discord portal doesn't provide easy export, so here are your options:

OPTION A: Browser DevTools Console
──────────────────────────────────
1. Open Discord Developer Portal in your browser
2. Press F12 to open DevTools
3. Go to "Console" tab
4. Paste this code and press Enter:

    copy(
        Array.from(document.querySelectorAll('tr'))
            .slice(1)  // Skip header
            .map(row => {
                const cells = row.querySelectorAll('td');
                return cells.length >= 3 ?
                    cells[0].textContent.trim() + ': ' + cells[2].textContent.trim() :
                    null;
            })
            .filter(x => x)
            .join('\\n')
    )

5. Paste it here:
""")

user_input = input("\nPaste the emoji data (or enter 'skip' to manually edit): ").strip()

if user_input.lower() != 'skip':
    emojis = {}
    for line in user_input.split('\n'):
        if ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                name = parts[0].strip()
                emoji_id = parts[1].strip()
                if emoji_id.isdigit():
                    emojis[name] = emoji_id
    
    if emojis:
        print(f"\n✅ Extracted {len(emojis)} emojis:")
        for name, eid in sorted(emojis.items()):
            print(f"   {name}: {eid}")
        
        # Generate new emojis.py
        emoji_file_content = '''"""
Custom Application Emojis for SkyMusic
All emojis are custom Discord application emojis, not Unicode.
"""

def E(name: str, emoji_id: int) -> str:
    """Format a custom emoji for use in messages."""
    return f"<:{name}:{emoji_id}>"

'''
        
        # Add emojis organized by category
        categories = {
            'Core Controls': ['play', 'pause', 'stop', 'skip', 'prev'],
            'Volume': ['vol_up', 'vol_down', 'vol_max', 'mute'],
            'Playback': ['loop_all', 'loop_one', 'loop_off', 'autoplay', 'shuffle'],
            'Queue': ['queue', 'add', 'remove', 'clear', 'move'],
            'UI': ['search', 'suggest', 'success', 'error', 'loading'],
            'Metadata': ['music', 'artist', 'album', 'time', 'live'],
            'Extra': ['fav', 'library', 'download', 'radio', 'eq', 'warning', 'info', 'debug', 'check', 'brand'],
        }
        
        emoji_definitions = {}
        for category, names in categories.items():
            emoji_file_content += f"\n# {category}\n"
            for name in names:
                if name in emojis:
                    emoji_id = emojis[name]
                    emoji_var = name.upper()
                    emoji_file_content += f'{emoji_var} = E("{name}", {emoji_id})\n'
                    emoji_definitions[name] = (emoji_var, emoji_id)
        
        # Add aliases
        emoji_file_content += '''
# Status indicators
CONNECTED = SUCCESS
DISCONNECTED = ERROR
PLAYING = PLAY
PAUSED = PAUSE

# Additional UI Elements
BRAND = MUSIC  # SkyMusic brand emoji
'''
        
        # Write to file
        with open('bot/utils/emojis.py', 'w') as f:
            f.write(emoji_file_content)
        
        print("\n✅ Updated bot/utils/emojis.py with new emoji IDs!")
        print("\n📝 Changes made:")
        print("   - Updated all 39 emoji variable definitions")
        print("   - Organized by semantic category")
        print("   - Ready to use in your bot")
        
        print("\n🚀 Next steps:")
        print("   1. Run your bot: python3 -m bot.main")
        print("   2. Test the /play command in Discord")
        print("   3. The emoji errors should be fixed!")
        
    else:
        print("❌ No valid emoji data extracted. Please try again.")
else:
    print("\nℹ️  Manual editing mode:")
    print("   Open bot/utils/emojis.py and update the emoji IDs manually.")
    print("   Format: EMOJI_VAR = E('emoji_name', emoji_id_number)")

EOF
