@echo off
REM reset-lab.bat — Reset the demo lab between sessions (Windows)
cd /d "%~dp0"

set PYTHON=.venv\Scripts\python.exe
if not exist "%PYTHON%" set PYTHON=python

%PYTHON% scripts\reset_lab.py
pause
