@echo off
echo ========================================
echo  Building ParaphraseIt for Windows
echo ========================================
echo.

cd /d "%~dp0"

:: Step 1: Setup venv
if not exist "venv" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
    echo [1/4] Installing dependencies...
    venv\Scripts\pip install -r requirements.txt
) else (
    echo [1/4] Virtual environment found.
)

:: Step 2: Build .exe
echo [2/4] Building ParaphraseIt.exe...
venv\Scripts\pyinstaller ^
    --onefile ^
    --windowed ^
    --name "ParaphraseIt" ^
    --icon "assets\icon.ico" ^
    --add-data "assets;assets" ^
    --add-data ".env;." ^
    paraphrase.py

if not exist "dist\ParaphraseIt.exe" (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo [3/4] .exe built successfully: dist\ParaphraseIt.exe

:: Step 3: Build installer (if Inno Setup is installed)
where iscc >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [4/4] Building installer with Inno Setup...
    iscc installer.iss
    echo.
    echo ========================================
    echo  BUILD COMPLETE!
    echo  Installer: installer_output\ParaphraseIt_Setup.exe
    echo ========================================
) else (
    echo [4/4] Inno Setup not found. Skipping installer.
    echo      Install from: https://jrsoftware.org/isinfo.php
    echo      Then re-run this script to create the installer.
    echo.
    echo ========================================
    echo  BUILD COMPLETE!
    echo  Standalone: dist\ParaphraseIt.exe
    echo  (You can run this directly, no installer needed)
    echo ========================================
)

echo.
pause
