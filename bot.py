import asyncio
import psutil
import shutil
from datetime import datetime, timedelta

import discord
import configparser
from discord.ext import commands, tasks

from console import log, SaladNotRunningException
from data import Globals, WebData, Settings
import system
import webscraper

bot = commands.Bot(
    command_prefix='.',
    intents=discord.Intents.all()
)

@tasks.loop(seconds=1)
async def send_embed():
    """Send system information as an embedded message to a Discord channel."""
    try:
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
        elapsed_time = datetime.now() - Globals.SCRIPT_START_TIME
        uptime_timedelta = timedelta(seconds=elapsed_time.total_seconds())
        days, seconds = divmod(uptime_timedelta.seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        formatted_uptime = f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"  # dd:hh:mm:ss
        Globals.SCRIPT_UP_TIME = formatted_uptime

        # Balance
        current_balance = f'{WebData.CURRENT_BALANCE:.2f}'

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
        embed.set_footer(text=f"{os_version} ({os_build.rsplit('.', 1)[-1]})")

        # Send the embed to the specified Discord channel
        channel = bot.get_channel(Settings.BOT_CHANNEL)

        # Send message if no previous message, else edit old one
        if Globals.LAST_MESSAGE_ID is not None:
            try:
                message = await channel.fetch_message(Globals.LAST_MESSAGE_ID)
                await message.edit(embed=embed)
            except Exception:
                message = await channel.send(embed=embed)
                Globals.LAST_MESSAGE_ID = message.id
        else:
            message = await channel.send(embed=embed)
            Globals.LAST_MESSAGE_ID = message.id

    except Exception as e:
        log(f"Error in send_embed: {e}")

@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    try:
        log(f'[ Bot ] Discord bot online | Channel: {Settings.BOT_CHANNEL}', clear=True)

        send_embed.start()

        Globals.SCRIPT_START_TIME = datetime.now()
        # Gather and await the results of the wrapper function
        await asyncio.gather(
            await asyncio.to_thread(
                webscraper.input_email,  # function
                Settings.EMAIL  # args
            )
        )

    except Exception as e:
        log(f"Error in on_ready: {e}")

if __name__ == '__main__':
    try:
        log('[ Bot ] => searching for salad process', clear=True)
        # Check if Salad.exe is running
        if not any(process.info['name'] == 'Salad.exe' for process in psutil.process_iter(['pid', 'name'])):
            raise SaladNotRunningException

        log('[ Bot ] => loading config object', clear=True)
        # Config object
        config = configparser.ConfigParser()
        config.read('config.ini')

        # Populate settings from config.ini
        log('[ Bot ] => importing settings')
        Settings.EMAIL = config['General']['Email']
        Settings.DEBUG = config.getboolean('General', 'Debug')
        Settings.BOT_TOKEN = config['Bot']['Token']
        Settings.BOT_CHANNEL = config.getint('Bot', 'Channel')

        # Run the Discord bot
        log('[ Bot ] => loading discord bot')
        bot.run(Settings.BOT_TOKEN)

    except Exception as e:
        log(f"Error: {e}")
