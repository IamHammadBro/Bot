#!/usr/bin/env python3
"""
Simple Flask Backend for Spotify Premium Stream Bot
Executes the bot as subprocess to avoid import issues
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

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
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
            
            # Find the bot script
            bot_script = 'github_premium_bot.py'
            if not os.path.exists(bot_script):
                bot_script = '../github_premium_bot.py'
            if not os.path.exists(bot_script):
                raise Exception("github_premium_bot.py not found")
            
            # Start the bot process
            self.process = subprocess.Popen([
                sys.executable, bot_script, config_json
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.is_running = True
            self.add_log("✅ Bot subprocess started successfully", "success")
            
            # Start monitoring thread
            def monitor():
                try:
                    if self.process:
                        stdout, stderr = self.process.communicate()
                        
                        # Log output
                        if stdout:
                            for line in stdout.split('\n'):
                                if line.strip():
                                    self.add_log(line.strip(), "info")
                        
                        if stderr:
                            for line in stderr.split('\n'):
                                if line.strip():
                                    self.add_log(f"❌ {line.strip()}", "error")
                    
                except Exception as e:
                    self.add_log(f"❌ Monitor error: {str(e)}", "error")
                finally:
                    self.is_running = False
                    self.add_log("🔄 Bot session ended", "warning")
            
            thread = threading.Thread(target=monitor, daemon=True)
            thread.start()
            
        except Exception as e:
            self.add_log(f"❌ Failed to start bot: {str(e)}", "error")
            self.is_running = False
            raise
    
    def stop(self):
        """Stop the bot"""
        self.is_running = False
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.add_log("🛑 Bot stopped", "warning")
            except:
                pass
    
    def get_status(self):
        """Get session status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            'session_id': self.session_id,
            'is_running': self.is_running,
            'uptime': uptime,
            'logs': self.logs[-10:],  # Last 10 logs
            'config': {
                'playlist_url': self.config['playlist_url'],
                'username': self.config['username'][:3] + '***',
                'skip_probability': self.config.get('skip_probability', 0.55)
            }
        }

@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory('../frontend', 'index.html')

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
        
        # Create and start session
        session = SimpleBotSession(session_id, config)
        active_sessions[session_id] = session
        
        # Start the bot
        session.start()
        
        logger.info(f"Started bot session: {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Bot started successfully'
        })
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop-bot/<session_id>', methods=['POST'])
def stop_bot(session_id):
    """Stop a bot session"""
    try:
        if session_id not in active_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session = active_sessions[session_id]
        session.stop()
        del active_sessions[session_id]
        
        logger.info(f"Stopped bot session: {session_id}")
        
        return jsonify({
            'success': True,
            'message': 'Bot stopped successfully'
        })
        
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot-status/<session_id>')
def get_bot_status(session_id):
    """Get bot session status"""
    try:
        if session_id not in active_sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session = active_sessions[session_id]
        status = session.get_status()
        
        return jsonify({
            'session_id': session_id,
            'status': 'running' if status['is_running'] else 'stopped',
            'stats': {
                'songs_played': 0,  # Would need to parse from logs
                'songs_skipped': 0,
                'total_streams': 0,
                'errors': 0
            },
            'logs': status['logs'],
            'uptime': status['uptime']
        })
        
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    bot_file_exists = os.path.exists('github_premium_bot.py') or os.path.exists('../github_premium_bot.py')
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(active_sessions),
        'bot_file_exists': bot_file_exists
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Simple Spotify Bot Backend on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
