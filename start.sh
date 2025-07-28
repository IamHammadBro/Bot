#!/bin/bash
echo "🎵 Spotify Premium Stream Bot"
echo "================================"

echo "🔍 Checking requirements..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python 3.8+"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found! Please install pip"
    exit 1
fi

echo "✅ Python found"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install flask flask-cors playwright aiohttp sentry-sdk psutil requests gunicorn python-dotenv
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python3 -m playwright install chromium
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Playwright browsers"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "🔧 Creating .env file..."
    cp ".env.example" ".env"
    echo "⚠️  Please edit .env file with your API keys before continuing"
    echo "📝 Edit .env file: nano .env"
    read -p "Press Enter when you've configured .env file..."
fi

echo "🚀 Starting Spotify Bot Backend..."
echo "🌐 Open http://localhost:5000 in your browser"
echo "🛑 Press Ctrl+C to stop the bot"

python3 backend/app.py
