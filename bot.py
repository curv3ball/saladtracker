import asyncio
import time
import psutil
from datetime import datetime, timedelta

import discord
import configparser
from discord.ext import commands, tasks

from console import *
from data import Globals, WebData, Settings
import system

bot = commands.Bot(
    command_prefix = '.',
    intents = discord.Intents.all()
)

@tasks.loop(seconds=1.5)
async def send_embed():
    """Task to send an embed periodically."""
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

    print(uptime_timedelta)

    #balance
    current_balance = WebData.CURRENT_BALANCE

    # embed object
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
    embed.set_footer(text=f"{os_version} ({os_build.rsplit('.', 1)[-1]})")

# PLACEHOLDER
def foo(x):
    while True:
        print(x)
        time.sleep(1)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    Globals.SCRIPT_START_TIME = datetime.datetime.now()
    log('Discord bot online', clear=True)
    send_embed.start()

    # PLACEHOLDER
    # Gather and await the results of the wrapper function
    await asyncio.gather(
        await asyncio.to_thread(
            foo,
            "Test"
        )
    )

if __name__ == '__main__':
    try:
        # Check if Salad.exe is running
        if not any(process.info['name'] == 'Salad.exe' for process in psutil.process_iter(['pid', 'name'])):
            raise SaladNotRunningException

        # Read configuration from config.ini
        config = configparser.ConfigParser()
        config.read('config.ini')

        # Populate settings from configuration
        Settings.EMAIL = config['General']['Email']
        Settings.DEBUG = config.getboolean('General', 'Debug')
        Settings.BOT_TOKEN = config['Bot']['Token']
        
        # Run the Discord bot
        bot.run(Settings.BOT_TOKEN)

    except Exception as e:
        log(f"Error: {e}")

