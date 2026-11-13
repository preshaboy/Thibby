import nextcord
from nextcord.ext import commands
import asyncio
import datetime
import os
import randomchicken

# --- MOBILE SECURE CONFIGURATION ---
# We use os.environ to keep your token hidden safely in Railway settings!
TOKEN = os.environ.get('DISCORD_TOKEN')

# Replace these numbers with your actual Discord IDs (keep them as numbers, no quotes)
TEXT_CHANNEL_ID = 1562785873261764635
VOICE_CHANNEL_ID = 1562785873429274624 
ROLE_TO_PING_ID = 1563428437513740418  

# YouTube links
PLAYLIST = [
    "https://ia601806.us.archive.org/35/items/meditation-0_202610/MEDITATION 0.mp3",
    "https://ia601600.us.archive.org/14/items/meditation-7/Meditation 7.mp3",
    "https://ia601600.us.archive.org/14/items/meditation-7/Meditation 8.mp3",
    "https://ia601800.us.archive.org/12/items/meditation-2_202610/MEDITATION 1.mp3",
    "https://ia601800.us.archive.org/12/items/meditation-2_202610/MEDITATION 2.mp3",
    "https://ia601800.us.archive.org/12/items/meditation-2_202610/MEDITATION 3.mp3",
    "httphttps://ia903108.us.archive.org/20/items/meditation-4/MEDITATION 4.mp3,
]

# Track playlist position
current_track_index = 0

intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin',
    'options': '-vn'
}

async def play_meditation():
    text_channel = bot.get_channel(TEXT_CHANNEL_ID)
    voice_channel = bot.get_channel(VOICE_CHANNEL_ID)
    
    if not text_channel or not voice_channel:
        print("Error: Could not find channels. Check your IDs.")
        return

    # 1. Ping role
    start_msg = await text_channel.send(f"Asé <@&1563428437513740418> 🌕. Daily meditation begins now. Join me in the voice channel...")

    # 2. Join voice channel
    try:
        vc = await voice_channel.connect()
    except Exception as e:
        print(f"Failed to join voice channel: {e}")
        return

    # 3. Stream all Internet Archive tracks back-to-back, repeating the list 2 times total
    try: 
        for loop_count in range(2):
            print(f"Starting playlist cycle {loop_count + 1} of 2...")
            
            for track_index in range(len(PLAYLIST)):
                # If the bot is manually kicked or stopped early, kill the loop instantly
                if not vc.is_connected():
                    print("The Avaturtle was disconnected from voice channel. Stopping playback.")
                    return
                    
                stream_url = PLAYLIST[track_index]
                audio_source = nextcord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)
                vc.play(audio_source)
                
                # Sleep and wait for the track to finish streaming completely
                while vc.is_playing(): 
                    await asyncio.sleep(1)
                if not vc.channel.members or len(vc.channel.members) <= 1: # Only the bot is left
                    vc.pause()
                    await asyncio.sleep(0.1)
                    vc.resume()
                # Tiny 2-second breathing window pause between files
                await asyncio.sleep(2)
                
        await vc.disconnect()
        
        # Delete the start announcement now that meditation is over
        if start_msg:
            try:
                await start_msg.delete()
            except Exception as e:
                print(f"Failed to delete start message: {e}")
                
        
        # ✨ CLOSING STATEMENT ADDED HERE ✨
        if text_channel:
            async with text_channel.typing():
                await asyncio.sleep(1)
                end_msg = await text_channel.send("🌑 Our journey is complete. May peace be upon your path! Asé.")
                
                # Wait 15 seconds so people can see it, then wipe it clean
                await asyncio.sleep(15)
                try:
                    await end_msg.delete()
                except Exception as e:
                    print(f"Failed to delete closing message: {e}")
            
    except Exception as e: 
        print(f"Error during playback: {e}")
        await text_channel.send("🌀 Couldn't load the meditation track today.")

    # 4. Disconnect cleanly when all cycles finish
    try:
        await vc.disconnect()
    except:
        pass

async def meditation_scheduler(): 
    await bot.wait_until_ready()
    print("Scheduler tracking system activated...")
    
    # Trackers to block duplicate alerts in the same minute
    last_triggered_minute = ""
    last_warning_minute = ""
    last_15min_warning_minute = ""
    
    active_reminders = []
    
    while not bot.is_closed(): 
        now = datetime.datetime.now().strftime("%H:%M")
        text_channel = bot.get_channel(TEXT_CHANNEL_ID)
        
        reminder_message = None # Store reference globally or inside your scheduler
        
        # 📢 30-Minute Early Reminder Check (Fires at 08:30, 16:30, 00:30 UTC)
        if now in ["17:30", "01:30"]:
            if last_warning_minute != now:
                last_warning_minute = now
                if text_channel:
                    async with text_channel.typing():
                        await asyncio.sleep(1.5)
                        msg = await text_channel.send(f"""🔔 Reminder <@&1563428437513740418>: Our collective meditation starts in **30 Minutes**! Empty your mind.  

Our session lasts about an hour. Do not worry if you missed it, my disciple. Just type "*!ase*". 🌌""")
                        active_reminders.append(msg)

        # 📢 15-Minute Early Reminder Check
        if now in ["17:45", "01:45"]:
            if last_15min_warning_minute != now:
                last_15min_warning_minute = now
                if text_channel:
                    msg = await text_channel.send(f"🔔 Reminder <@&1563428437513740418>: Meditation starts in **15 minutes**! Let us elevate Earth's resonance collectively.")
                    active_reminders.append(msg)

        
        # 🧘‍♂️ Session Commencement Check (Fires at 09:00, 17:00, 01:00 UTC)
        if now in ["18:00", "02:00"]:
            if last_triggered_minute != now:
                last_triggered_minute = now
                
                 # Delete the reminder message if it exists
                for msg in active_reminders:
                    try:
                        await msg.delete()
                    except Exception as e:
                        print(f"Failed to delete reminder message: {e}")
                active_reminders.clear() # Clear out the list
                
                await play_meditation()
                
        # Reset memory arrays once time coordinates shift
        if now not in ["18:00", "02:00"]:
            last_triggered_minute = ""
        if now not in ["17:30", "01:30"]:
            last_warning_minute = ""
        if now not in ["17:45", "01:45"]:
            last_15min_warning_minute = ""
            
        await asyncio.sleep(15)
        
@bot.command()
async def ase(ctx, *, channel_name: str = None):
    # 1. Delete the user's command message instantly for clean chat
    try:
        await ctx.message.delete()
    except Exception as e:
        print(f"Failed to delete user command message: {e}")

    # 2. Determine which voice channel to join
    voice_channel = None
    if channel_name:
        # If you typed a room name (e.g., "!ase planetary"), look for it in the server
        for vc in ctx.guild.voice_channels:
            if channel_name.lower() in vc.name.lower():
                voice_channel = vc
                break
        if not voice_channel:
            await ctx.send(f"🧿 I could not find a voice channel matching '{channel_name}', seeker.", delete_after=5)
            return
    else:
        # Otherwise, default to your hardcoded meditation channel
        voice_channel = bot.get_channel(VOICE_CHANNEL_ID)

    if not voice_channel: 
        await ctx.send("🧿 I could not find the voice channel, seeker.")
        return

    # 3. Send Thibby's start response and save it to a variable
    start_msg = await ctx.send(f"🌕 Asé seeker. Come meditate with me in **{voice_channel.name}** and elevate Earth's resonance.")

    # Clean connection join
    try:
        if bot.voice_clients:
            for client in bot.voice_clients:
                if client.guild == voice_channel.guild:
                    await client.disconnect(force=True)
        vc = await voice_channel.connect()
    except Exception as e: 
        await ctx.send(f"🧿 I could not connect to the voice channel: {e}")
        return

    # Stream Track 1, Track 2, and Track 3 back-to-back (1 Full Loop)
    try: 
        for track_index in range(len(PLAYLIST)):
            # If you type !stop early during testing, kill the loop instantly
            if not vc.is_connected():
                print("Asé. 🪬 Our session ended early. I will return.")
                return
                
            stream_url = PLAYLIST[track_index]
            audio_source = nextcord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)
            vc.play(audio_source)
            
            while vc.is_playing(): 
                await asyncio.sleep(1)
            if not vc.channel.members or len(vc.channel.members) <= 1: # Only the bot is left
                vc.pause()
                await asyncio.sleep(0.1)
                vc.resume()
                
            # Small 2-second breathing pause between tracks
            await asyncio.sleep(2)
            
    except Exception as e: 
        await ctx.send(f"⛔️ Audio streaming error occurred during session: {e}")

    # Leave voice channel cleanly when the full loop finishes
    try:
        await vc.disconnect()
        
        # Delete Thibby's initial start announcement
        if start_msg:
            try:
                await start_msg.delete()
            except Exception as e:
                print(f"Failed to delete start message: {e}")

        # Send and auto-wipe the closing statement after 15 seconds
        end_msg = await ctx.send("🌑 Our journey is complete. May peace be upon your path! Asé.")
        await asyncio.sleep(60)
        try:
            await end_msg.delete()
        except Exception as e:
            print(f"Failed to delete closing message: {e}")
            
    except:
        pass
    
@bot.command()
async def stop(ctx):
    try: 
        await ctx.message.delete()
    except:
        pass
    
    async with ctx.channel.typing():
        await asyncio.sleep(1)
        if ctx.voice_client:
           await ctx.voice_client.disconnect()
           msg = await ctx.send("🪬 Asé. Our journey ended early. The Avaturtle will return.")
        else:
           msg = await ctx.send("🧿 I could not find a voice channel, seeker.")
    
    await asyncio.sleep(20)
    try:
        await msg.delete()
    except:
        pass

@bot.command()
# 1. 
async def sleep(ctx, *, channel_name: str = None):
    # 2. DELETE USER COMMAND MESSAGE INSTANTLY
    try:
        await ctx.message.delete()
    except Exception as e:
        print(f"Failed to delete user message: {e}")

    # 3. CHOOSE CHANNEL: Custom room if typed, otherwise your hardcoded default
    voice_channel = None
    if channel_name:
        for vc in ctx.guild.voice_channels:
            if channel_name.lower() in vc.name.lower():
                voice_channel = vc
                break
        if not voice_channel:
            await ctx.send(f"🧿 I could not find a voice channel matching '{channel_name}', seeker.", delete_after=5)
            return
    else:
        voice_channel = bot.get_channel(VOICE_CHANNEL_ID)

    if not voice_channel: 
        await ctx.send("🧿 I could not find a voice channel, seeker.")
        return

    async with ctx.channel.typing():
        await asyncio.sleep(1)
        # 4. Save start message reference into "start_msg" so we can delete it later
        start_msg = await ctx.send(f"🧞 Asé seeker. We will begin our 8-hour continuous harmonic resonance field in **{voice_channel.name}**. Join me...")

    try:
        if bot.voice_clients:
            for client in bot.voice_clients:
                if client.guild == voice_channel.guild:
                    await client.disconnect(force=True)
        vc = await voice_channel.connect()
    except Exception as e: 
        await ctx.send(f"❌ Failed to join voice: {e}")
        return

    # Stream the playlist continuously for ~15 full cycles (~8 hours)
    try: 
        for loop_count in range(32):
            print(f"Starting 8-hour playlist cycle {loop_count + 1} of 32...")
            
            for track_index in range(len(PLAYLIST)):
                if not vc.is_connected():
                    print("Asé. 🪬 Our sleep journey ended early.")
                    return
                    
                stream_url = PLAYLIST[track_index]
                audio_source = nextcord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)
                vc.play(audio_source)
                
                while vc.is_playing(): 
                    await asyncio.sleep(1)
                if not vc.channel.members or len(vc.channel.members) <= 1: # Only the bot is left
                    vc.pause()
                    await asyncio.sleep(0.1)
                    vc.resume()
                    
                await asyncio.sleep(2)
            
    except Exception as e: 
        await ctx.send(f"My Avaturtle duties await. Until next time, seeker.: {e}")

    # 5. CLEAN UP MESSAGES WHEN FINISHED
    try:
        await vc.disconnect()
        
        # Delete the start announcement
        if start_msg:
            try:
                await start_msg.delete()
            except Exception as e:
                print(f"Failed to delete start message: {e}")

        # Send closing message and auto-delete it after 15 seconds
        end_msg = await ctx.send("🌗 Our deep night journey is complete. May you rest peacefully! Asé.")
        await asyncio.sleep(60)
        try:
            await end_msg.delete()
        except Exception as e:
            print(f"Failed to delete closing message: {e}")
            
    except:
        pass

@bot.event
async def on_message(message):
    # Always let the bot process commands properly first
    await bot.process_commands(message)

    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

        # Check if the user's ID is mentioned in the message text
    if bot.user in message.mentions or "thibby" in message.content.lower():
        try:
            reactions = ["💜", "🌌", "🪻", "🪷", "🔮",]
            
            chosen_emoji = random.choice(reactions)
           
            await message.add_reaction(chosen_emoji)
            
        except Exception as e:
            print(f"Failed to add reaction: {e}")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    bot.loop.create_task(meditation_scheduler())

bot.run(TOKEN)
