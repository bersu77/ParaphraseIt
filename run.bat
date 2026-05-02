@echo off
REM Launcher for Windows
cd /d "%~dp0"

if not exist "venv" (
    echo Setting up virtual environment...
    python -m venv venv
    venv\Scripts\pip install -r requirements.txt
)

venv\Scripts\python paraphrase.py
pause
