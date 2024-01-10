import subprocess

import psutil
import GPUtil

from console import loggable


@loggable
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

@loggable
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

@loggable
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

@loggable
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

@loggable
def workload_type() -> str:
    """Returns the salad workload type."""
    process_names = { "vmmem": "Vmmem", "t-rex.exe": "T-Rex", "xmrig": "XMRig"}
    
    for process in psutil.process_iter(['pid', 'name']):
        pid = process.info['pid']
        process_name = process.info['name']
        
        if psutil.pid_exists(pid) and process_name in process_names:
            return process_names[process_name]

    return "Unknown"
