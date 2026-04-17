#!/usr/bin/env python3
"""
Test emoji IDs and help identify which ones are invalid in Discord.
"""

import sys
import asyncio
import discord
from discord.ext import commands
import os

# Get token from environment
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("❌ ERROR: DISCORD_TOKEN environment variable not set")
    print("   Set it with: export DISCORD_TOKEN='your_token_here'")
    sys.exit(1)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    """When bot is ready, test all emoji IDs."""
    print(f"\n🤖 Connected as: {bot.user}")
    print(f"📱 App ID: {bot.application_id}")
    
    # Get the application object to access emojis
    app = await bot.application_info()
    print(f"\n📊 Fetching emojis from your application...")
    
    # Try to get emojis via the bot's HTTP client
    try:
        # Make a raw request to get application emojis
        from discord.http import HTTPClient
        client = bot.http
        
        # Get emojis
        emojis = await client.get_app_emojis(bot.application_id)
        
        if emojis:
            print(f"\n✅ Found {len(emojis)} emojis in your Discord app:\n")
            
            # Organize by category for easy reading
            emoji_dict = {}
            for emoji in emojis:
                name = emoji['name']
                emoji_id = emoji['id']
                emoji_dict[name] = emoji_id
                print(f"  {name}: {emoji_id}")
            
            # Now check which ones are in our code
            print("\n" + "="*60)
            print("EMOJI ID MAPPING FOR bot/utils/emojis.py:")
            print("="*60 + "\n")
            
            # Generate the Python code
            print("# Core Controls")
            for name in ['play', 'pause', 'stop', 'skip', 'prev']:
                if name in emoji_dict:
                    print(f"{name.upper()} = E(\"{name}\", {emoji_dict[name]})")
            
            print("\n# Volume")
            for name in ['vol_up', 'vol_down', 'vol_max', 'mute']:
                if name in emoji_dict:
                    print(f"{name.upper()} = E(\"{name}\", {emoji_dict[name]})")
            
            print("\n# Playback")
            for name in ['loop_all', 'loop_one', 'loop_off', 'autoplay', 'shuffle']:
                if name in emoji_dict:
                    print(f"{name.upper()} = E(\"{name}\", {emoji_dict[name]})")
            
            print("\n# Queue")
            for name in ['queue', 'add', 'remove', 'clear', 'move']:
                if name in emoji_dict:
                    print(f"{name.upper()} = E(\"{name}\", {emoji_dict[name]})")
            
            print("\n# UI")
            for name in ['search', 'suggest', 'success', 'error', 'loading']:
                if name in emoji_dict:
                    print(f"{name.upper()} = E(\"{name}\", {emoji_dict[name]})")
            
            print("\n# Metadata")
            for name in ['music', 'artist', 'album', 'time', 'live']:
                if name in emoji_dict:
                    print(f"{name.upper()} = E(\"{name}\", {emoji_dict[name]})")
            
            print("\n# Extra")
            for name in ['fav', 'library', 'download', 'radio', 'eq', 'warning', 'info', 'debug']:
                if name in emoji_dict:
                    print(f"{name.upper()} = E(\"{name}\", {emoji_dict[name]})")
            
        else:
            print("⚠️  No emojis found. Make sure you've uploaded emojis to your app.")
            
    except Exception as e:
        print(f"❌ Error fetching emojis: {e}")
        import traceback
        traceback.print_exc()
    
    await bot.close()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Discord Emoji ID Tester - Get Current IDs from Your App  ║
╚══════════════════════════════════════════════════════════════╝

This script connects to Discord and fetches all your app's emojis,
then displays the Python code you need for bot/utils/emojis.py

""")
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Failed to connect to Discord: {e}")
        print("\nMake sure your DISCORD_TOKEN is correct.")
