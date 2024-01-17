import os
import re
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.dates import DateFormatter, DayLocator
import asyncio
import time
import psutil
import threading
import subprocess
import GPUtil
import discord
import configparser
from discord.ext import commands, tasks

bot = commands.Bot(
    command_prefix='.',
    intents=discord.Intents.all()
)

matplotlib.use('Agg')  # Use Agg backend for Matplotlib

class globals:
    SCRIPT_START_TIME = None
    LAST_MESSAGE_ID = None

class logdata:
    CURRENT_BALANCE: float = 0.00

class settings:
    BOT_TOKEN: str = ''
    BOT_CHANNEL: int = 0

class system:
    def ram() -> tuple:
        """
        Retrieve information about system RAM.

        Returns:
            tuple: total, used, clockspeed, manufacturer, partnumber
        """
        
        ram = psutil.virtual_memory()
        command = 'wmic memorychip get configuredclockspeed, manufacturer, partnumber'
        query = subprocess.check_output(command, shell=True, text=True)

        result = [
            item for item in [
                entry.strip() for entry in query.strip().split('\n') if entry.strip()
            ][1].split('  ') if item
        ]

        # Convert values to gigabytes and format as integers
        items = (
            int(ram.total / (1024 ** 3) + 1),
            int(ram.used / (1024 ** 3)),
            result[0],  # ConfiguredClockSpeed
            result[1],  # Manufacturer
            result[2],  # PartNumber
        )

        items_converted = tuple(item for item in items)
        return items_converted

    def cpu() -> tuple:
        """
        Retrieve information about the CPU.

        Returns:
            tuple: clockspeed, name, totalcores, enabledcores, status
        """
        command = 'wmic cpu get name, numberofcores, numberofenabledcore, currentclockspeed, status'
        query = subprocess.check_output(command, shell=True, text=True)

        result = [
            entry.strip() for entry in query.strip().split('\n')[2].split('  ') if entry.strip()
        ]

        # Extract relevant CPU information
        items = (
            f'{int(result[0]) / 1000:.2f}',  # CurrentClockSpeed
            result[1],  # Name
            result[2],  # NumberOfCores
            result[3],  # NumberOfEnabledCore
            result[4],  # Status
        )

        items_converted = tuple(item for item in items)
        return items_converted

    def gpu() -> tuple:
        """
        Retrieve information about the GPU.

        Returns:
            tuple: name, vram, load, status
        """
        card: GPUtil.GPU = GPUtil.getGPUs()[0]

        command = 'wmic path win32_videocontroller get status'
        query = subprocess.check_output(command, shell=True, text=True)

        result = [
            entry.strip() for entry in query.strip().split('\n') if entry.strip()
        ]

        # Convert GPU memory values to gigabytes and format as integers
        items = (
            card.name,
            f'{int(card.memoryTotal / (1024) // 1 + 1)}',
            f'{int(round(card.load * 100, 2))}',
            f'{result[1]}'  # Status
        )

        items_converted = tuple(item for item in items)
        return items_converted

    def os() -> tuple:
        """
        Retrieve information about the OS.

        Returns:
            tuple: windowsversion, buildnumber
        """
        command = 'wmic os get caption, version'
        query = subprocess.check_output(command, shell=True, text=True)

        result = [
            entry.strip() for entry in query.strip().split('\n') if entry.strip()
        ][1].split('  ')

        items = (
            f'{result[0]}',                     # Caption
            f'{result[1]}'.rsplit('.', 1)[-1]   # Version
        )

        items_converted = tuple(item for item in items)
        return items_converted

    def workload_type() -> str:
        """Returns the salad workload type."""
        process_names = { "vmmem": "Vmmem", "t-rex.exe": "T-Rex", "xmrig": "XMRig"}
        
        for process in psutil.process_iter(['pid', 'name']):
            pid = process.info['pid']
            process_name = process.info['name']
            
            if psutil.pid_exists(pid) and process_name in process_names:
                return process_names[process_name]

        return "Unknown"

class plotter:
    def bytes_to_mbits(bytes_val):
        """Convert bytes to Mbits."""
        if isinstance(bytes_val, str):
            bytes_val = int(bytes_val)
        return (bytes_val / 1024 / 1024) * 8

    def parse_timestamp_with_timezone(timestamp_str, timezone_str):
        """Parse timestamp with timezone."""
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        timezone_offset = int(timezone_str[:3]), int(timezone_str[3:])
        return timestamp - timedelta(hours=timezone_offset[0], minutes=timezone_offset[1])

    def sample_data(data, max_points):
        """Sample data to ensure unique dates."""
        sampled_data = []
        unique_dates = set()
        for timestamp, value in data:
            date_str = timestamp.strftime('%d-%m')
            if date_str not in unique_dates:
                unique_dates.add(date_str)
                sampled_data.append((timestamp, value))
        if len(sampled_data) > max_points:
            step = len(sampled_data) // max_points
            return sampled_data[::step]
        return sampled_data

    async def process_file(filepath, patterns):
        """Process a single log file."""
        data = []
        with open(filepath, 'r') as f:
            for line in f:
                for pattern, data_transform, data_list in patterns:
                    match = re.search(pattern, line)
                    if match:
                        timestamp = plotter.parse_timestamp_with_timezone(match.group(1), '-0500')
                        data_value = data_transform(match.group(2).strip())
                        data_list.append((timestamp, data_value))

    async def process_files(files, base_dir, patterns):
        """Process multiple log files concurrently."""
        tasks = [plotter.process_file(os.path.join(base_dir, file), patterns) for file in files]
        await asyncio.gather(*tasks)

    async def process_files_parallel(files, base_dir, patterns):
        loop = asyncio.get_event_loop()
        tasks = [plotter.process_file(os.path.join(base_dir, file), patterns) for file in files]
        await asyncio.gather(*tasks)

    async def get_balance() -> None:
        """Set logdata.CURRENT_BALANCE to the last found balance in the log files."""
        while True:
            # Initialize data structure
            wallet_data = []
            # Define pattern for extracting wallet data
            wallet_pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?Wallet: Current\(([\d.]+)\)')

            logs_directory = 'C:\\ProgramData\\Salad\\logs'
            # Get all files in the logs directory
            all_files = [file for file in os.listdir(logs_directory) if os.path.isfile(os.path.join(logs_directory, file))]

            # Process log files
            for file_name in all_files:
                file_path = os.path.join(logs_directory, file_name)
                # Process lines and extract wallet data
                with open(file_path, 'r') as file:
                    for line in file:
                        match = wallet_pattern.match(line)
                        if match:
                            timestamp, balance = match.groups()
                            wallet_data.append((timestamp, float(balance)))

            # Set logdata.CURRENT_BALANCE to the last found balance
            if wallet_data:
                _, last_balance = max(wallet_data, key=lambda x: x[0])  # Get the entry with the latest timestamp
                logdata.CURRENT_BALANCE = last_balance

    async def generate_graph(debug = False):
        """Generate and save graphs for bandwidth, container earnings, and wallet data."""
        while True:
            if debug:
                start_time = time.time()

            # Set the theme
            console.log("[Plotter] => Setting theme") if debug else None
            plt.style.use('dark_background')

            # Initialize data structures
            console.log("[Plotter] => Initialize data structures") if debug else None
            earnings_data = []
            wallet_data = []

            # Define patterns for data extraction
            console.log("[Plotter] => Pattern setup") if debug else None
            patterns = [
                (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?Predicted Earnings Report: ([\d.]+)', float, earnings_data),
                (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?Wallet: Current\(([\d.]+)\)', float, wallet_data),
            ]

            # Get all files in the base directory
            console.log("[Plotter] => Getting log files") if debug else None
            base_dir = 'C:\\ProgramData\\Salad\\logs'
            all_files = [file for file in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, file))]

            # Sample data
            max_points = 50

            console.log("[Plotter] => Processing log files") if debug else None
            # Process files concurrently
            await plotter.process_files_parallel(all_files, base_dir, patterns)

            # Sort and sample data
            console.log("[Plotter] => Sorting sample data") if debug else None
            earnings_data.sort()
            wallet_data.sort()

            earnings_data = plotter.sample_data(earnings_data, max_points)
            wallet_data = plotter.sample_data(wallet_data, max_points)

            # Clear the plots
            plt.clf()

            # Create date formatter for 24-hour time format
            date_formatter = DateFormatter('%d-%m')

            # Plotting the Container Earnings graph
            times, earnings = zip(*earnings_data) if earnings_data else ([], [])
            plt.subplot(2, 1, 1)
            plt.plot(times, earnings, label='Container Earnings')
            plt.legend()
            plt.gca().xaxis.set_major_formatter(date_formatter)
            plt.gca().xaxis.set_major_locator(DayLocator())

            # Plotting the Wallet graph
            times, wallets = zip(*wallet_data) if wallet_data else ([], [])
            plt.subplot(2, 1, 2)
            plt.plot(times, wallets, label='Wallet Balance')
            plt.legend()
            plt.gca().xaxis.set_major_formatter(date_formatter)
            plt.gca().xaxis.set_major_locator(DayLocator())

            # Adjust layout
            console.log("[Plotter] => Adjusting layout") if debug else None
            plt.tight_layout()

            # Save the plot to a PNG file
            console.log("[Plotter] => Saving to file") if debug else None
            plt.savefig('graph.png')

            console.log("[Plotter] => Graph generation time:", time.time() - start_time) if debug else None

class console:
    class SaladNotRunningException(Exception):
        """Exception raised when Salad.exe is not running."""
        def __init__(self, message="Salad.exe must be running, please run Salad before running this program."):
            """
            Initializes the SaladNotRunningException.

            Args:
                message (str): Custom error message (default is a generic message).

            """
            self.message = message
            super().__init__(self.message)

    def log(msg: str, clear: bool = False):
        """
        Prints a log message and optionally clears the console.

        Args:
            msg (str): The log message to be printed.
            clear (bool): Whether to clear the console before printing (default is False).

        """
        if clear:
            console.cls()

        print(msg)

    def cls():
        """Clears the console buffer."""
        os.system('cls')

@tasks.loop(seconds=5)
async def send_embed():
    """Send system information as an embedded message to a Discord channel."""


    """ HOW IT WILL LOOK IN THE EMBED:
    -------------------------------------------
    | Salad Tracker [BOT]                     |
    |                                         |
    | CPU         GPU                RAM      |
    | OK          99%                75%      |

    | Workload    Uptime             Balance  |
    | Unknown     00:00:00:00        $0.00    |
    |  _____________________________________  |
    | |                                     | |
    | |  _________________________________  | |
    | | |                                 | | |
    | | |    Container Earnigns Chart     | | |
    | | |                                 | | |
    | | |_________________________________| | |
    | |  _________________________________  | |
    | | |                                 | | |
    | | |      Wallet Balance Chart       | | |
    | | |                                 | | |
    | | |_________________________________| | |
    | |_____________________________________| |
    |                                         |
    | Microsoft Windows 10 Home (19045)       |
    -------------------------------------------
    """
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
        ram_percent = f"{int((ram_used / ram_total) * 100)}%"

        # Convert elapsed time to a timedelta object and format
        elapsed_time = datetime.now() - globals.SCRIPT_START_TIME
        uptime_timedelta = timedelta(seconds=elapsed_time.total_seconds())
        days, seconds = divmod(uptime_timedelta.seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        formatted_uptime = f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"  # dd:hh:mm:ss

        # Balance
        current_balance = f'{logdata.CURRENT_BALANCE:.2f}'

        # Embed object
        embed = discord.Embed(colour=discord.colour.Color.from_rgb(0, 0, 0))

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
            value=f"[RAM](https://www.google.com/search?q={ram_search})\n**{ram_percent}**",
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

        file_path = 'graph.png'
        
        # Check if the file exists
        file = None
        if os.path.exists(file_path):
            file = discord.File(file_path, filename=file_path)
            embed.set_image(url=f'attachment://graph.png')

        # Windows version (footer)
        embed.set_footer(text=f"{os_version} ({os_build.rsplit('.', 1)[-1]})")

        # Send the embed to the specified Discord channel
        channel = bot.get_channel(settings.BOT_CHANNEL)

        # Check if there's a previous message
        if globals.LAST_MESSAGE_ID is not None:
            try:
                # Fetch the old message and delete it
                old_message = await channel.fetch_message(globals.LAST_MESSAGE_ID)
                await old_message.delete()

                # Send the new embed with the updated file
                new_message = await channel.send(embed=embed, file=file)
                globals.LAST_MESSAGE_ID = new_message.id
            except Exception as e:
                console.log(f"Error updating message: {e}")
        else:
            # Send a new message with the embed and file
            message = await channel.send(embed=embed, file=file)
            globals.LAST_MESSAGE_ID = message.id

        max_length = max(len(cpu_name), len(gpu_name), len(ram_manufacturer))

        # Define a fixed width for the left part
        fixed_width = 15

        cpu_info = f"CPU: {cpu_name} {cpu_clockspeed}".ljust(max_length + fixed_width) + f"[ {cpu_status} ]"
        gpu_info = f"GPU: {gpu_name} {gpu_memory}".ljust(max_length + fixed_width) + f"[ {gpu_load} ]"
        ram_info = f"RAM: {ram_manufacturer} {ram_partnumber}".ljust(max_length + fixed_width) + f"[ {ram_percent} ]"

        console.log(f"""
        [ SYSTEM ]
        {cpu_info}
        {gpu_info}
        {ram_info}

        [ SALAD ]
        Balance: {logdata.CURRENT_BALANCE}
        """, clear=True)

    except Exception as e:
        console.log(f"Error in send_embed: {e}")

def plotter_wrapper(debug = False):
    """Wrapper for generating graphs."""
    loop1 = asyncio.new_event_loop()
    asyncio.set_event_loop(loop1)
    loop1.run_until_complete(plotter.generate_graph(debug))

def balance_wrapper():
    """Wrapper for getting the current balance."""
    loop2 = asyncio.new_event_loop()
    asyncio.set_event_loop(loop2)
    loop2.run_until_complete(plotter.get_balance())

@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    try:
        console.log(f'[ Bot ] Discord bot online | Channel: {settings.BOT_CHANNEL}', clear=True)
        globals.SCRIPT_START_TIME = datetime.now()

        plotter_thread = threading.Thread(target=plotter_wrapper, args=(False,))
        balance_thread = threading.Thread(target=balance_wrapper)
        plotter_thread.start()
        balance_thread.start()
        send_embed.start()

    except Exception as e:
        console.log(f"Error in on_ready: {e}")

if __name__ == '__main__':
    try:
        console.log('[ Bot ] => searching for salad process', clear=True)
        # Check if Salad.exe is running
        if not any(process.info['name'] == 'Salad.exe' for process in psutil.process_iter(['pid', 'name'])):
            raise console.SaladNotRunningException

        console.log('[ Bot ] => loading config object', clear=True)
        # Config object
        config = configparser.ConfigParser()
        config.read('config.ini')

        # Populate settings from config.ini
        console.log('[ Bot ] => importing settings')
        settings.BOT_TOKEN = config['Bot']['Token']
        settings.BOT_CHANNEL = config.getint('Bot', 'Channel')

        # Run the Discord bot
        console.log('[ Bot ] => loading discord bot')
        bot.run(settings.BOT_TOKEN)

    except Exception as e:
        console.log(f"Error: {e}")
