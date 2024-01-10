import asyncio
import psutil
from datetime import timedelta

import discord
import configparser
from discord.ext import commands, tasks

from console import *
from data import Globals, WebData, Settings
import system
import webscraper

bot = commands.Bot(
    command_prefix = '.',
    intents = discord.Intents.all()
)

@tasks.loop(seconds = 1.5)
async def send_embed():
    """Send system information as an embedded message to a Discord channel."""

    # Retrieve system information
    cpu_clockspeed, cpu_name, _, _, cpu_status = system.cpu()
    gpu_name, gpu_memory, gpu_load, _ = system.gpu()
    ram_total, ram_used, ram_clockspeed, ram_manufacturer, ram_partnumber = system.ram()
    os_version, os_build = system.os()
    workload = system.workload_type()

    # Format strings for Google search queries
    cpu_search = f"{cpu_name} @ {cpu_clockspeed}GHz".replace(' ', '+')
    gpu_search = f"{gpu_name} @ {gpu_memory}GB".replace(' ', '+')
    ram_search = f"{ram_manufacturer} {ram_partnumber} {ram_total}GB @ {ram_clockspeed}MHz".replace(' ', '+')

    # Convert elapsed time to a timedelta object and format
    elapsed_time = datetime.datetime.now() - Globals.SCRIPT_START_TIME
    uptime_timedelta = timedelta(seconds=elapsed_time.total_seconds())
    days, seconds = divmod(uptime_timedelta.seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    formatted_uptime = f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}" # dd:hh:mm:ss

    # Balance
    current_balance = WebData.CURRENT_BALANCE

    # Embed object
    embed = discord.Embed(colour=0x009afa)

    # CPU information
    embed.add_field(
        name="",
        value=f"[CPU](https://www.google.com/search?q={cpu_search})\n**{cpu_status}**",
        inline=True
    )

    # GPU information
    embed.add_field(
        name="",
        value=f"[GPU](https://www.google.com/search?q={gpu_search})\n**{gpu_load}%**",
        inline=True
    )

    # RAM information
    embed.add_field(
        name="",
        value=f"[RAM](https://www.google.com/search?q={ram_search})\n**{int((ram_used / ram_total) * 100)}%**",
        inline=True
    )

    # Workload information
    embed.add_field(
        name="Workload",
        value=f"**{workload}**",
        inline=True
    )

    # Bot information
    embed.add_field(
        name="Uptime",
        value=f"**{formatted_uptime}**",
        inline=True
    )

    # Salad balance
    embed.add_field(
        name="Balance",
        value=f"**${current_balance}**",
        inline=True
    )

    # Windows version (footer)
    embed.set_footer(text = f"{os_version} ({os_build.rsplit('.', 1)[-1]})")

    # Send the embed to the specified Discord channel
    channel = bot.get_channel(Settings.BOT_CHANNEL)

    # Send message if no previous message, else edit old one
    if Globals.LAST_MESSAGE_ID is not None:
        try:
            message = await channel.fetch_message(Globals.LAST_MESSAGE_ID)
            await message.edit(embed = embed)
        except Exception:
            message = await channel.send(embed = embed)
            Globals.LAST_MESSAGE_ID = message.id
    else:
        message = await channel.send(embed = embed)
        Globals.LAST_MESSAGE_ID = message.id

@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    log('Discord Bot Online', clear = True)

    send_embed.start()

    Globals.SCRIPT_START_TIME = datetime.datetime.now()
    # Gather and await the results of the wrapper function
    await asyncio.gather(
        await asyncio.to_thread(
            webscraper.input_email, # function
            Settings.EMAIL          # args
        )
    )

if __name__ == '__main__':
    try:
        # Check if Salad.exe is running
        if not any(process.info['name'] == 'Salad.exe' for process in psutil.process_iter(['pid', 'name'])):
            raise SaladNotRunningException

        log('[ Bot ]', clear = True)
        # Config object
        config = configparser.ConfigParser()
        config.read('config.ini')

        # Populate settings from config.ini
        log('  - importing settings')
        Settings.EMAIL = config['General']['Email']
        Settings.DEBUG = config.getboolean('General', 'Debug')
        Settings.BOT_TOKEN = config['Bot']['Token']
        Settings.BOT_CHANNEL = config.getint('Bot', 'Channel')
        
        # Run the Discord bot
        log('  - loading bot')
        bot.run(Settings.BOT_TOKEN)

    except Exception as e:
        log(f"Error: {e}")

