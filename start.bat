@echo off
echo 🎵 Spotify Premium Stream Bot
echo ================================

echo 🔍 Checking requirements...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

:: Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip not found! Please reinstall Python with pip
    pause
    exit /b 1
)

echo ✅ Python found

:: Install dependencies
echo 📦 Installing dependencies...
pip install flask flask-cors playwright aiohttp sentry-sdk psutil requests gunicorn python-dotenv
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

:: Install Playwright browsers
echo 🌐 Installing Playwright browsers...
python -m playwright install chromium
if errorlevel 1 (
    echo ❌ Failed to install Playwright browsers
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

:: Check if .env exists
if not exist ".env" (
    echo 🔧 Creating .env file...
    copy ".env.example" ".env"
    echo ⚠️  Please edit .env file with your API keys before continuing
    echo 📝 Opening .env file for editing...
    notepad .env
    pause
)

echo 🚀 Starting Spotify Bot Backend...
echo 🌐 Open http://localhost:5000 in your browser
echo 🛑 Press Ctrl+C to stop the bot

python backend/app.py

pause
