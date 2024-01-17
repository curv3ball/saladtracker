@echo off
echo Installing required Python packages...

pip install matplotlib
pip install asyncio
pip install psutil
pip install discord.py
pip install configparser
pip install gputil

echo Installation complete. Please setup config.ini
pause