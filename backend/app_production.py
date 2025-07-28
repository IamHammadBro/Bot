#!/usr/bin/env python3
"""
Production Flask Backend for Spotify Premium Stream Bot
Optimized for Render.com deployment
"""

import os
import sys
import json
import subprocess
import threading
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Import configuration
try:
    from config import config
except ImportError:
    # Fallback configuration if config.py is not found
    class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
        DEBUG = False
        PORT = int(os.environ.get('PORT', 10000))
        FRONTEND_URL = os.environ.get('FRONTEND_URL', '*')
    config = {'production': Config, 'default': Config}

# Get environment
env = os.environ.get('FLASK_ENV', 'production')
app_config = config.get(env, config['default'])

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(app_config)

# Configure CORS properly for production
CORS(app, origins=[
    "https://*.netlify.app",
    "https://*.netlify.com", 
    "http://localhost:3000",
    "http://127.0.0.1:3000"
])

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global session storage
active_sessions = {}

class SimpleBotSession:
    """Simple bot session that runs the bot as subprocess"""
    
    def __init__(self, session_id: str, config: Dict[str, Any]):
        self.session_id = session_id
        self.config = config
        self.process = None
        self.is_running = False
        self.start_time = datetime.now()
        self.logs = []
        
    def add_log(self, message: str, log_type: str = 'info'):
        """Add a log entry"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': log_type
        }
        self.logs.append(log_entry)
        
        # Keep only last 50 logs
        if len(self.logs) > 50:
            self.logs = self.logs[-50:]
        
        logger.info(f"[{self.session_id}] {message}")
    
    def start(self):
        """Start the bot subprocess"""
        try:
            self.add_log("🚀 Starting Spotify Premium Bot", "info")
            
            # Create config for the bot
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
            
            # Convert config to JSON string
            config_json = json.dumps(bot_config)
            
            # Find the bot script - check multiple locations
            bot_script_paths = [
                'github_premium_bot.py',
                '../github_premium_bot.py',
                os.path.join(os.path.dirname(__file__), '..', 'github_premium_bot.py'),
                '/app/github_premium_bot.py'  # For containerized deployment
            ]
            
            bot_script = None
            for path in bot_script_paths:
                if os.path.exists(path):
                    bot_script = path
                    break
            
            if not bot_script:
                raise FileNotFoundError("Could not find github_premium_bot.py")
            
            # Start subprocess
            cmd = [sys.executable, bot_script, '--config', config_json]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.is_running = True
            self.add_log("✅ Bot subprocess started successfully", "success")
            
            # Start thread to monitor subprocess
            monitor_thread = threading.Thread(target=self._monitor_subprocess)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Failed to start bot: {str(e)}"
            self.add_log(error_msg, "error")
            logger.error(f"[{self.session_id}] {error_msg}")
            return False
    
    def _monitor_subprocess(self):
        """Monitor subprocess output and status"""
        try:
            while self.process and self.process.poll() is None:
                if self.process.stdout:
                    output = self.process.stdout.readline()
                    if output:
                        self.add_log(output.strip(), "bot")
                
                if self.process.stderr:
                    error = self.process.stderr.readline()
                    if error:
                        self.add_log(f"Error: {error.strip()}", "error")
        except Exception as e:
            self.add_log(f"Monitor error: {str(e)}", "error")
        finally:
            self.is_running = False
            self.add_log("🔴 Bot subprocess ended", "info")
    
    def stop(self):
        """Stop the bot subprocess"""
        try:
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
                
                self.is_running = False
                self.add_log("🛑 Bot stopped successfully", "info")
                return True
        except Exception as e:
            error_msg = f"❌ Error stopping bot: {str(e)}"
            self.add_log(error_msg, "error")
            logger.error(f"[{self.session_id}] {error_msg}")
            return False
    
    def get_status(self):
        """Get bot status"""
        return {
            'session_id': self.session_id,
            'is_running': self.is_running,
            'start_time': self.start_time.isoformat(),
            'uptime': str(datetime.now() - self.start_time),
            'logs': self.logs[-10:],  # Last 10 logs
            'config': {
                'playlist_url': self.config.get('playlist_url', ''),
                'skip_probability': self.config.get('skip_probability', 0.55),
                'min_play_time': self.config.get('min_play_time', 32),
                'max_play_time': self.config.get('max_play_time', 45)
            }
        }

# Routes
@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Spotify Premium Bot Backend is running',
        'active_sessions': len(active_sessions),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/start-bot', methods=['POST'])
def start_bot():
    """Start a new bot session"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'password', 'playlist_url']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create bot session
        session = SimpleBotSession(session_id, data)
        
        # Start the bot
        if session.start():
            active_sessions[session_id] = session
            logger.info(f"Started bot session: {session_id}")
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'message': 'Bot started successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start bot'
            }), 500
            
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stop-bot/<session_id>', methods=['POST'])
def stop_bot(session_id):
    """Stop a bot session"""
    try:
        session = active_sessions.get(session_id)
        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        if session.stop():
            del active_sessions[session_id]
            logger.info(f"Stopped bot session: {session_id}")
            
            return jsonify({
                'success': True,
                'message': 'Bot stopped successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to stop bot'
            }), 500
            
    except Exception as e:
        logger.error(f"Error stopping bot: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bot-status/<session_id>', methods=['GET'])
def get_bot_status(session_id):
    """Get bot session status"""
    try:
        session = active_sessions.get(session_id)
        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        return jsonify({
            'success': True,
            'status': session.get_status()
        })
        
    except Exception as e:
        logger.error(f"Error getting bot status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all active sessions"""
    try:
        sessions = []
        for session_id, session in active_sessions.items():
            sessions.append(session.get_status())
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'total': len(sessions)
        })
        
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Simple Spotify Bot Backend on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
