#!/usr/bin/env python3
"""
Quick installation script for required dependencies
"""

import subprocess
import sys

def install_dependencies():
    """Install all required dependencies"""
    print("🚀 Installing Spotify Bot Dependencies...")
    print("=" * 50)
    
    dependencies = [
        "playwright",
        "aiohttp", 
        "python-dotenv",
        "sentry-sdk"
    ]
    
    for dep in dependencies:
        try:
            print(f"📦 Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing {dep}: {e}")
    
    # Install Playwright browsers
    try:
        print("🌐 Installing Playwright browsers...")
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        print("✅ Playwright browsers installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing browsers: {e}")
    
    print("\n🎉 Installation Complete!")
    print("🚀 Run the bot: python github_premium_bot.py")

if __name__ == "__main__":
    install_dependencies()
