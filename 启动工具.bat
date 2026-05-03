@echo off
chcp 65001 >nul 2>&1
echo ==========================================
echo Offline Subtitle Generator Launcher
echo ==========================================
echo.

echo Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [OK] Python found
echo.

echo Checking dependencies...
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PyQt5...
    pip install PyQt5
)

python -c "import whisper" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing whisper...
    pip install openai-whisper
)

python -c "import torch" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing torch...
    pip install torch
)

echo.
echo [OK] All dependencies ready
echo.
echo ==========================================
echo Starting Subtitle Generator...
echo ==========================================
echo.

python main.py

pause
