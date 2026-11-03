@echo off
title Balloon Pop - Rainbow Challenge

cd /d "%~dp0"

echo Installing required libraries...
python -m pip install -r requirements.txt

echo.
echo Starting Balloon Pop Game...
python main.py

echo.
echo Game closed.
pause