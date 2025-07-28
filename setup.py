#!/usr/bin/env python3
"""
Quick setup script for Spotify Premium Bot
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    required_tools = {
        'python': 'python --version',
        'docker': 'docker --version',
        'git': 'git --version'
    }
    
    missing = []
    for tool, cmd in required_tools.items():
        result = run_command(cmd, f"Checking {tool}")
        if result is None:
            missing.append(tool)
    
    if missing:
        print(f"❌ Missing required tools: {', '.join(missing)}")
        print("Please install them before continuing.")
        return False
    
    print("✅ All requirements satisfied")
    return True

def setup_environment():
    """Setup environment files"""
    print("🔧 Setting up environment...")
    
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your actual API keys")
    else:
        print("ℹ️  Environment file already exists")

def install_dependencies():
    """Install Python dependencies"""
    if not run_command('pip install -r requirements.txt', 'Installing Python dependencies'):
        return False
    
    # Install Playwright browsers
    if not run_command('playwright install chromium', 'Installing Playwright browsers'):
        return False
    
    return True

def build_docker():
    """Build Docker image"""
    return run_command('docker build -t spotify-bot .', 'Building Docker image')

def main():
    print("🎵 Spotify Premium Bot Setup")
    print("=" * 40)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Build Docker image
    print("\n🐳 Building Docker image...")
    if not build_docker():
        print("❌ Failed to build Docker image")
        print("ℹ️  You can still run the bot locally without Docker")
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run locally: python backend/app.py")
    print("3. Or with Docker: docker-compose up")
    print("4. Open http://localhost:5000 in your browser")
    
    print("\nFor deployment:")
    print("- Backend: Deploy to Render/Railway/DigitalOcean")
    print("- Frontend: Deploy to Netlify/Vercel")
    print("- Update netlify.toml with your backend URL")

if __name__ == "__main__":
    main()
