@echo off
echo Installing required packages...

REM Install matplotlib
pip install matplotlib

REM Install psutil
pip install psutil

REM Install gputil
pip install gputil

REM Install discord
pip install discord

cls
echo Installation complete.
echo Please setup config.ini
pause
