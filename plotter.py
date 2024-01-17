import os
import re
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.dates import DateFormatter, DayLocator
import asyncio
import time
from data import LogData
from console import log, loggable

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
                    timestamp = parse_timestamp_with_timezone(match.group(1), '-0500')
                    data_value = data_transform(match.group(2).strip())
                    data_list.append((timestamp, data_value))

async def process_files(files, base_dir, patterns):
    """Process multiple log files concurrently."""
    tasks = [process_file(os.path.join(base_dir, file), patterns) for file in files]
    await asyncio.gather(*tasks)

async def process_files_parallel(files, base_dir, patterns):
    loop = asyncio.get_event_loop()
    tasks = [process_file(os.path.join(base_dir, file), patterns) for file in files]
    await asyncio.gather(*tasks)

async def get_balance() -> None:
    """Set LogData.CURRENT_BALANCE to the last found balance in the log files."""
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

        # Set LogData.CURRENT_BALANCE to the last found balance
        if wallet_data:
            _, last_balance = max(wallet_data, key=lambda x: x[0])  # Get the entry with the latest timestamp
            LogData.CURRENT_BALANCE = last_balance * 3
            print(f"[Wallet] => {LogData.CURRENT_BALANCE}")

async def generate_graph(debug = False):
    """Generate and save graphs for bandwidth, container earnings, and wallet data."""
    while True:
        if debug:
            start_time = time.time()

        # Set the theme
        print("[Plotter] => Setting theme") if debug else None
        plt.style.use('dark_background')

        # Initialize data structures
        print("[Plotter] => Initialize data structures") if debug else None
        earnings_data = []
        wallet_data = []

        # Define patterns for data extraction
        print("[Plotter] => Pattern setup") if debug else None
        patterns = [
            (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?Predicted Earnings Report: ([\d.]+)', float, earnings_data),
            (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?Wallet: Current\(([\d.]+)\)', float, wallet_data),
        ]

        # Get all files in the base directory
        print("[Plotter] => Getting log files") if debug else None
        base_dir = 'C:\\ProgramData\\Salad\\logs'
        all_files = [file for file in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, file))]

        # Sample data
        max_points = 50

        print("[Plotter] => Processing log files") if debug else None
        # Process files concurrently
        await process_files_parallel(all_files, base_dir, patterns)

        # Sort and sample data
        print("[Plotter] => Sorting sample data") if debug else None
        earnings_data.sort()
        wallet_data.sort()

        earnings_data = sample_data(earnings_data, max_points)
        wallet_data = sample_data(wallet_data, max_points)

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
        print("[Plotter] => Adjusting layout") if debug else None
        plt.tight_layout()

        # Save the plot to a PNG file
        print("[Plotter] => Saving to file") if debug else None
        plt.savefig('graph.png')

        print("[Plotter] => Graph generation time:", time.time() - start_time) if debug else None

if __name__ == '__main__':
    # asyncio.run(generate_graph(True))
    asyncio.run(get_balance())