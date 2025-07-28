# 🎵 Spotify Premium Stream Bot

A sophisticated Spotify streaming automation tool with AI-powered human behavior simulation, advanced fingerprint spoofing, and beautiful web interface.

## ✨ Features

### 🎯 Core Functionality  
- **Smart Skip Algorithm**: 50-60% of songs skip after 32-45 seconds (meets streaming requirements)
- **Human Behavior Simulation**: AI-powered mouse movements, scrolling, and interaction patterns  
- **Infinite Playlist Loop**: Automatic repeat mode for continuous streaming
- **Advanced Skip Patterns**: Double skips, backward skips, and random variations

### 🛡️ Stealth & Security
- **Unique Fingerprint Spoofing**: Each instance has unique browser fingerprint
- **Undetected Chrome**: Real Chrome browser with advanced automation detection bypass
- **Mobile User-Agent**: Mimics iPhone Safari for better stealth
- **Container Isolation**: Each instance runs in isolated Docker container

### 🌟 GitHub Developer Pack Integration
- **FingerprintJS Pro**: Real device fingerprinting (GitHub Pack included)
- **Bright Data Proxies**: Residential proxy rotation (GitHub Pack trial)
- **OpenAI API**: AI-generated human behavior patterns (GitHub Pack credits)
- **Sentry Monitoring**: Error tracking and performance monitoring (GitHub Pack included)

### 🖥️ Web Interface
- **Beautiful UI**: Modern, responsive Spotify-themed interface
- **Real-time Status**: Live bot status, statistics, and logs
- **Multi-Instance Support**: Run multiple bots simultaneously  
- **Easy Configuration**: Point-and-click setup, no technical knowledge required

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd spotify-premium-bot

# Setup environment
python setup.py

# Edit .env file with your credentials
cp .env.example .env
# Add your Spotify credentials and API keys

# Run with Docker
docker-compose up
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run the backend
python backend/app.py

# Open frontend
# Navigate to http://localhost:5000
```

## 🔧 Configuration

### Required Credentials

1. **Spotify Account**
   - Username/Email
   - Password

2. **Playlist URL**
   - Any public or personal Spotify playlist
   - Format: `https://open.spotify.com/playlist/...`

### Optional API Keys (GitHub Developer Pack)

Add these to your `.env` file for enhanced features:

```env
# GitHub Developer Pack APIs
BRIGHT_DATA_PROXY_URL=your_proxy_url
FINGERPRINTJS_API_KEY=your_api_key
OPENAI_API_KEY=your_openai_key
SENTRY_DSN=your_sentry_dsn
```

## 📊 Bot Behavior

### Streaming Pattern
- **50-60% Skip Rate**: Songs are skipped after 32-45 seconds
- **40-50% Full Play**: Songs play to completion
- **Minimum Stream Time**: Always >30 seconds (required for Spotify stream counting)
- **Random Variations**: AI-powered timing variations to simulate human behavior

### Human Simulation
- **Mouse Movements**: Random cursor movements across the page
- **Scroll Behavior**: Occasional scrolling to simulate engagement
- **Pause Patterns**: Natural pauses between actions
- **Touch Interactions**: Mobile-optimized touch simulation

### Skip Variations
- **Regular Skip**: Standard forward skip (most common)
- **Double Skip**: Skip two songs in sequence (~15% chance)
- **Backward Skip**: Go back to previous song (~8% chance)
- **Timing Variance**: ±5-15 second variations in skip timing

## 🌐 Deployment

### Backend Deployment (Render/Railway)

1. **Create Account** on Render.com or Railway.app
2. **Connect Repository** to your GitHub repo
3. **Set Environment Variables**:
   ```
   PORT=5000
   BRIGHT_DATA_PROXY_URL=your_proxy
   FINGERPRINTJS_API_KEY=your_key
   OPENAI_API_KEY=your_key
   SENTRY_DSN=your_dsn
   ```
4. **Deploy** - Platform will auto-build from Dockerfile

### Frontend Deployment (Netlify)

1. **Create Account** on Netlify.com
2. **Drag & Drop** the `frontend` folder
3. **Update** `netlify.toml` with your backend URL:
   ```toml
   [[redirects]]
     from = "/api/*"
     to = "https://your-backend-url.onrender.com/api/:splat"
   ```
4. **Deploy** - Frontend will be live instantly

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   Bot Engine    │
│   (Netlify)     │────│   (Render)       │────│   (Docker)      │
│                 │    │                  │    │                 │
│ • Web Interface │    │ • Session Mgmt   │    │ • Chrome Automation│
│ • Real-time UI  │    │ • API Endpoints  │    │ • Spotify Control │
│ • Configuration │    │ • Log Streaming  │    │ • Human Simulation│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

**Made with ❤️ using GitHub Developer Pack**

*This project showcases the power of GitHub's Student Developer Pack, integrating premium APIs and services for educational purposes.*

## ✨ FEATURES INCLUDED:

### 🎯 AUTOMATION (Your Requirements):
- ✅ 55% of songs skip after 32-45 seconds
- ✅ 45% of songs play to completion
- ✅ 15% chance of double skips
- ✅ 8% chance of backward skips
- ✅ Playlist loops continuously
- ✅ Mobile view login (username + password on same page)

### 🛡️ ANTI-DETECTION:
- ✅ Fresh Chromium browser (isolated from your regular browser)
- ✅ Mobile user agent and viewport
- ✅ Advanced stealth scripts
- ✅ Human-like behavior patterns
- ✅ Persistent browser profiles

### 🎓 GITHUB DEVELOPER PACK READY:
- ✅ Bright Data proxies integration
- ✅ FingerprintJS Pro real device fingerprints
- ✅ OpenAI API for AI behavior
- ✅ Sentry error tracking
- ✅ Works with fallbacks if no APIs configured

## 🔧 CONFIGURATION:

### Basic Usage (No API keys needed):
The bot works out of the box with intelligent fallbacks.

### Premium Usage (With GitHub Pack APIs):
1. Edit `.env` file with your API keys
2. Follow GitHub Pack activation instructions
3. Restart the bot

## 📊 CURRENT SETTINGS:
- **Account**: arshadahsan388@gmail.com
- **Playlist**: 5muSk2zfQ3LI70S64jbrX7
- **Mode**: Visible browser (you can watch it work)
- **Skip Rate**: 55% with realistic timing
- **Automation**: Full human-like behavior

## 🎉 READY TO USE!

Just run: `python github_premium_bot.py`

The bot will:
1. Open Chrome browser in mobile view
2. Login to your Spotify account
3. Navigate to your playlist
4. Enable repeat mode
5. Start intelligent automation with skip patterns
6. Continue looping forever

## 💡 TROUBLESHOOTING:

If you get "Playback disabled":
1. The bot includes anti-detection measures
2. Try running from a different IP/location
3. Add proxy APIs from GitHub Pack for best results

## 🔐 API KEYS (Optional):

To get maximum stealth, activate these from GitHub Developer Pack:
- Bright Data (residential proxies)
- FingerprintJS Pro (real device fingerprints)
- OpenAI API (AI behavior)
- Sentry (error tracking)

The bot works great without them too!
"# Bot" 
