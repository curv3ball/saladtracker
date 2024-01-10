from discord.ext import commands, tasks
from console import *
import configparser
import discord
import psutil

bot = commands.Bot(
    command_prefix='.',
    intents=discord.Intents.all()
)

SCRIPT_START_TIME = None
LAST_MESSAGE_ID = None

class Settings:
    """Class for storing and managing settings."""
    email       : str = ''
    bot_token   : str = ''
    debug       : bool = False

@tasks.loop(seconds=1.5)
async def send_embed():
    """Task to send an embed periodically."""
    pass

@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    log('Discord bot online', clear=True)
    send_embed.start()

if __name__ == '__main__':
    try:
        # Check if Salad.exe is running
        if not any(process.info['name'] == 'Salad.exe' for process in psutil.process_iter(['pid', 'name'])):
            raise SaladNotRunningException

        # Read configuration from config.ini
        config = configparser.ConfigParser()
        config.read('config.ini')

        # Populate settings from configuration
        Settings.email = config['General']['Email']
        Settings.debug = config.getboolean('General', 'Debug')
        Settings.bot_token = config['Bot']['Token']

        # Run the Discord bot
        bot.run(Settings.bot_token)

    except Exception as e:
        log(f"Error: {e}")
