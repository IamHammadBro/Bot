#!/usr/bin/env python3
"""
Simple Flask Backend that executes the bot as a subprocess
This avoids import issues by running the bot directly
"""

import os
import sys
import asyncio
import threading
import uuid
import logging
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import signal
import psutil

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global session storage  
active_sessions: Dict[str, 'BotSession'] = {}
session_logs: Dict[str, List[Dict[str, Any]]] = {}

class BotSession:
    """Manages individual bot sessions using subprocess"""
    
    def __init__(self, session_id: str, config: Dict[str, Any]):
        self.session_id = session_id
        self.config = config
        self.process = None
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
    
    def create_bot_config_file(self):
        """Create a temporary config file for the bot"""
        config_file = f"temp_config_{self.session_id}.json"
        
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
        
        with open(config_file, 'w') as f:
            json.dump(bot_config, f)
        
        return config_file
    
    def run_bot_subprocess(self):
        """Run the bot as a subprocess"""
        def thread_target():
            self.is_running = True
            try:
                self.add_log("🚀 Starting Spotify Premium Bot as subprocess", "info")
                
                # Create config file
                config_file = self.create_bot_config_file()
                
                # Create a modified version of the bot that accepts config file
                bot_script = self.create_bot_script(config_file)
                
                # Start the bot subprocess
                self.process = subprocess.Popen([
                    sys.executable, bot_script
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                self.add_log("✅ Bot subprocess started", "success")
                
                # Monitor the process
                while self.is_running and self.process.poll() is None:
                    # Read output
                    if self.process.stdout:
                        line = self.process.stdout.readline()
                        if line:
                            self.parse_bot_output(line.strip())
                    
                    # Check for errors
                    if self.process.stderr:
                        error_line = self.process.stderr.readline()
                        if error_line:
                            self.add_log(f"❌ {error_line.strip()}", "error")
                
                # Clean up
                if os.path.exists(config_file):
                    os.remove(config_file)
                if os.path.exists(bot_script):
                    os.remove(bot_script)
                    
            except Exception as e:
                self.add_log(f"❌ Subprocess error: {str(e)}", "error")
                logger.error(f"Subprocess error for session {self.session_id}: {e}")
            finally:
                self.is_running = False
                self.add_log("🔄 Bot session ended", "warning")
                
        self.thread = threading.Thread(target=thread_target, daemon=True)
        self.thread.start()
        self.add_log("🏃 Bot subprocess thread started", "info")
    
    def create_bot_script(self, config_file):
        """Create a temporary bot script that uses the config file"""
        script_path = f"temp_bot_{self.session_id}.py"
        
        # Read the original bot file
        original_bot_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'github_premium_bot.py')
        
        if not os.path.exists(original_bot_path):
            # Try current directory
            original_bot_path = 'github_premium_bot.py'
        
        if not os.path.exists(original_bot_path):
            raise Exception("Could not find github_premium_bot.py")
        
        with open(original_bot_path, 'r') as f:
            bot_code = f.read()
        
        # Modify the main function to use our config
        modified_code = bot_code.replace(
            'async def main():',
            f'''async def main():
    import json
    with open('{config_file}', 'r') as f:
        config = json.load(f)'''
        ).replace(
            'config = {',
            '''# Using config from file
    # config = {'''
        ).replace(
            'bot = PremiumSpotifyBot(config)',
            '''# Use the config from file
    bot = PremiumSpotifyBot(config)'''
        )
        
        # Write the modified script
        with open(script_path, 'w') as f:
            f.write(modified_code)
        
        return script_path
    
    def parse_bot_output(self, line: str):
        """Parse bot output and extract relevant information"""
        # Look for specific patterns in bot output
        if '✅' in line or 'success' in line.lower():
            self.add_log(line, "success")
        elif '❌' in line or 'error' in line.lower():
            self.add_log(line, "error")
            self.update_stats('errors')
        elif '⏭️' in line or 'skip' in line.lower():
            self.add_log(line, "info")
            self.update_stats('songs_skipped')
        elif '🎶' in line or 'playing' in line.lower():
            self.add_log(line, "info")
            self.update_stats('songs_played')
            self.update_stats('total_streams')
        else:
            self.add_log(line, "info")
    
    def stop(self):
        """Stop the bot session"""
        self.is_running = False
        self.add_log("🛑 Stop requested", "warning")
        
        # Try to stop the subprocess gracefully
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.add_log("🔄 Bot process terminated", "info")
            except:
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
        
        # Check if bot file exists
        bot_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'github_premium_bot.py')
        if not os.path.exists(bot_file):
            bot_file = 'github_premium_bot.py'
        if not os.path.exists(bot_file):
            return jsonify({'error': 'Bot file not found. Please ensure github_premium_bot.py exists.'}), 500
        
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
            session.run_bot_subprocess()
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

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    bot_file_exists = os.path.exists('github_premium_bot.py') or os.path.exists('../github_premium_bot.py')
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(active_sessions),
        'python_version': sys.version,
        'platform': sys.platform,
        'bot_file_exists': bot_file_exists
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
