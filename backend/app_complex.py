#!/usr/bin/env python3
"""
Flask Backend for Spotify Premium Stream Bot
Handles bot execution, session management, and API endpoints
"""

import os
import sys
import asyncio
import threading
import uuid
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import subprocess
import signal
import psutil

# Add the parent directory to Python path so we can import the bot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import bot - if not found, we'll handle it gracefully
try:
    from github_premium_bot import PremiumSpotifyBot
except ImportError:
    # Try importing from backend directory
    try:
        from backend.github_premium_bot import PremiumSpotifyBot
    except ImportError:
        print("❌ Could not import PremiumSpotifyBot. Please ensure github_premium_bot.py is in the correct location.")
        PremiumSpotifyBot = None

app = Flask(__name__, static_folder='frontend', template_folder='frontend')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global session storage  
active_sessions: Dict[str, 'BotSession'] = {}
session_logs: Dict[str, List[Dict[str, Any]]] = {}

class BotSession:
    """Manages individual bot sessions"""
    
    def __init__(self, session_id: str, config: Dict[str, Any]):
        self.session_id = session_id
        self.config = config
        self.bot = None
        self.thread = None
        self.is_running = False
        self.start_time = datetime.now()
        self.stats = {
            'songs_played': 0,
            'songs_skipped': 0,
            'total_streams': 0,
            'errors': 0
        }
        self.logs = []
        
    def add_log(self, message: str, log_type: str = 'info'):
        """Add a log entry"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': log_type
        }
        self.logs.append(log_entry)
        
        # Keep only last 100 logs
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
            
        # Also store in global logs
        if self.session_id not in session_logs:
            session_logs[self.session_id] = []
        session_logs[self.session_id].append(log_entry)
        
        logger.info(f"[{self.session_id}] {message}")
    
    def update_stats(self, stat_name: str, value: int = 1):
        """Update session statistics"""
        if stat_name in self.stats:
            self.stats[stat_name] += value
    
    async def run_bot_async(self):
        """Run the bot asynchronously"""
        try:
            self.add_log("🚀 Initializing Spotify Premium Bot", "info")
            
            # Check if bot class is available
            if PremiumSpotifyBot is None:
                raise Exception("PremiumSpotifyBot class not available. Please check bot installation.")
            
            # Create bot configuration with unique ID
            bot_config = {
                'bot_id': f"web_bot_{self.session_id[:8]}",
                'username': self.config['username'],
                'password': self.config['password'],
                'playlist_url': self.config['playlist_url'],
                'headless': self.config.get('headless', True),
                'skip_probability': self.config.get('skip_probability', 0.55),
                'min_play_time': self.config.get('min_play_time', 32),
                'max_play_time': self.config.get('max_play_time', 45),
                'double_skip_probability': 0.15,
                'backward_skip_probability': 0.08
            }
            
            self.add_log(f"🔧 Bot configured: {bot_config['skip_probability']*100}% skip rate", "info")
            
            # Initialize the bot
            self.bot = PremiumSpotifyBot(bot_config)
            self.add_log("✅ Bot initialized successfully", "success")
            
            # Override bot's logger to capture logs
            self.setup_bot_logging()
            
            # Start the premium session
            self.add_log("🎵 Starting premium streaming session", "info")
            await self.bot.run_premium_session()
            
        except Exception as e:
            self.add_log(f"❌ Bot error: {str(e)}", "error")
            self.update_stats('errors')
            logger.error(f"Bot session {self.session_id} error: {e}")
        finally:
            self.is_running = False
            self.add_log("🔄 Bot session ended", "warning")
    
    def setup_bot_logging(self):
        """Setup bot logging to capture events"""
        if self.bot and hasattr(self.bot, 'logger'):
            # Create a custom handler to capture bot logs
            class SessionLogHandler(logging.Handler):
                def __init__(self, session):
                    super().__init__()
                    self.session = session
                    
                def emit(self, record):
                    msg = self.format(record)
                    
                    # Parse log level
                    log_type = 'info'
                    if record.levelno >= logging.ERROR:
                        log_type = 'error'
                        self.session.update_stats('errors')
                    elif record.levelno >= logging.WARNING:
                        log_type = 'warning'
                    elif '✅' in msg or 'successful' in msg.lower():
                        log_type = 'success'
                    
                    # Parse specific events for stats
                    if '⏭️' in msg or 'skip' in msg.lower():
                        self.session.update_stats('songs_skipped')
                    elif '🎶' in msg or 'playing' in msg.lower():
                        self.session.update_stats('songs_played')
                        self.session.update_stats('total_streams')
                    
                    self.session.add_log(msg, log_type)
            
            handler = SessionLogHandler(self)
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.bot.logger.addHandler(handler)
            self.bot.logger.setLevel(logging.INFO)
    
    def run_bot_thread(self):
        """Run the bot in a separate thread"""
        def thread_target():
            self.is_running = True
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.run_bot_async())
            except Exception as e:
                self.add_log(f"❌ Thread error: {str(e)}", "error")
                logger.error(f"Thread error for session {self.session_id}: {e}")
            finally:
                self.is_running = False
                
        self.thread = threading.Thread(target=thread_target, daemon=True)
        self.thread.start()
        self.add_log("🏃 Bot thread started", "info")
    
    def stop(self):
        """Stop the bot session"""
        self.is_running = False
        self.add_log("🛑 Stop requested", "warning")
        
        # Try to stop bot gracefully
        if self.bot and hasattr(self.bot, 'chrome_process'):
            try:
                self.bot.chrome_process.terminate()
                self.add_log("🔄 Chrome process terminated", "info")
            except:
                pass
        
        # Clean up thread
        if self.thread and self.thread.is_alive():
            # Thread will stop when is_running becomes False
            pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current session status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'session_id': self.session_id,
            'is_running': self.is_running,
            'uptime': uptime,
            'stats': self.stats,
            'config': {
                'playlist_url': self.config['playlist_url'],
                'username': self.config['username'][:3] + '***',  # Masked for security
                'skip_probability': self.config.get('skip_probability', 0.55),
                'headless': self.config.get('headless', True)
            },
            'recent_logs': self.logs[-10:]  # Last 10 logs
        }

@app.route('/')
def index():
    """Serve the main frontend"""
    return send_from_directory('frontend', 'index.html')

@app.route('/api/start-bot', methods=['POST'])
def start_bot():
    """Start a new bot session"""
    try:
        config = request.get_json()
        
        # Validate required fields
        required_fields = ['playlist_url', 'username', 'password']
        for field in required_fields:
            if not config.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate playlist URL
        if 'spotify.com/playlist/' not in config['playlist_url']:
            return jsonify({'error': 'Invalid Spotify playlist URL'}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create and start bot session(s)
        instances = config.get('instances', 1)
        session_ids = []
        
        for i in range(instances):
            instance_id = f"{session_id}_{i}" if instances > 1 else session_id
            
            # Create session
            session = BotSession(instance_id, config)
            active_sessions[instance_id] = session
            
            # Start the bot
            session.run_bot_thread()
            session_ids.append(instance_id)
            
            logger.info(f"Started bot session: {instance_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'session_ids': session_ids,
            'instances': instances,
            'message': f'Started {instances} bot instance(s)'
        })
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop-bot/<session_id>', methods=['POST'])
def stop_bot(session_id):
    """Stop a bot session"""
    try:
        stopped_sessions = []
        
        # Handle multiple instances
        for sid in list(active_sessions.keys()):
            if sid.startswith(session_id):
                session = active_sessions[sid]
                session.stop()
                stopped_sessions.append(sid)
                del active_sessions[sid]
                logger.info(f"Stopped bot session: {sid}")
        
        if stopped_sessions:
            return jsonify({
                'success': True,
                'stopped_sessions': stopped_sessions,
                'message': f'Stopped {len(stopped_sessions)} session(s)'
            })
        else:
            return jsonify({'error': 'Session not found'}), 404
            
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot-status/<session_id>')
def get_bot_status(session_id):
    """Get bot session status"""
    try:
        # Find sessions that match the session_id (handles multiple instances)
        matching_sessions = []
        for sid in active_sessions:
            if sid.startswith(session_id):
                matching_sessions.append(active_sessions[sid])
        
        if not matching_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        # Aggregate stats from all instances
        total_stats = {
            'songs_played': 0,
            'songs_skipped': 0,
            'total_streams': 0,
            'errors': 0
        }
        
        all_logs = []
        any_running = False
        
        for session in matching_sessions:
            status = session.get_status()
            
            # Aggregate stats
            for key in total_stats:
                total_stats[key] += status['stats'][key]
            
            # Collect recent logs
            all_logs.extend(status['recent_logs'])
            
            # Check if any instance is running
            if status['is_running']:
                any_running = True
        
        # Sort logs by timestamp
        all_logs.sort(key=lambda x: x['timestamp'])
        
        return jsonify({
            'session_id': session_id,
            'status': 'running' if any_running else 'stopped',
            'instances': len(matching_sessions),
            'stats': total_stats,
            'logs': all_logs[-20:],  # Last 20 logs
            'active_instances': [s.session_id for s in matching_sessions if s.is_running]
        })
        
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions')
def list_sessions():
    """List all active sessions"""
    try:
        sessions = []
        for session_id, session in active_sessions.items():
            sessions.append(session.get_status())
        
        return jsonify({
            'sessions': sessions,
            'total_active': len(sessions)
        })
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(active_sessions),
        'python_version': sys.version,
        'platform': sys.platform
    })

# Cleanup function for graceful shutdown
def cleanup_sessions():
    """Clean up all active sessions"""
    logger.info("Cleaning up active sessions...")
    for session_id in list(active_sessions.keys()):
        try:
            session = active_sessions[session_id]
            session.stop()
            del active_sessions[session_id]
            logger.info(f"Cleaned up session: {session_id}")
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {e}")

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    cleanup_sessions()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Spotify Bot Backend on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
    finally:
        cleanup_sessions()
