#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import time
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, Any

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gemstone-iv-bot-monitor'

# Initialize SocketIO with CORS enabled
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# In-memory storage for character states
character_states: Dict[str, Dict[str, Any]] = {}
INACTIVE_THRESHOLD_SECONDS = 20

@app.route('/')
def dashboard():
    """Serve the main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/character/update', methods=['POST'])
def update_character():
    """REST endpoint to receive character status updates from Lich scripts"""
    try:
        data = request.get_json()
        
        if not data or 'character' not in data or 'name' not in data['character']:
            return jsonify({'error': 'Invalid character data'}), 400
        
        character_name = data['character']['name']
        
        # Add server timestamp
        data['server_timestamp'] = time.time()
        
        # Store the character state
        character_states[character_name] = data
        
        # Emit real-time update to all connected clients
        socketio.emit('character_update', {
            'character_name': character_name,
            'data': data
        })
        
        return jsonify({
            'status': 'success',
            'message': f'Character {character_name} updated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/characters', methods=['GET'])
def get_active_characters():
    """Return all characters that have been updated within the last 20 seconds"""
    current_time = time.time()
    active_characters = {}
    
    for char_name, char_data in character_states.items():
        last_update = char_data.get('server_timestamp', 0)
        if current_time - last_update <= INACTIVE_THRESHOLD_SECONDS:
            active_characters[char_name] = char_data
    
    return jsonify(active_characters)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    # Send current state to newly connected client
    emit('characters_state', character_states)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

def cleanup_inactive_characters():
    """Background task to clean up very old character data"""
    while True:
        current_time = time.time()
        # Remove characters that haven't been updated in over 5 minutes
        chars_to_remove = []
        
        for char_name, char_data in character_states.items():
            last_update = char_data.get('server_timestamp', 0)
            if current_time - last_update > 300:  # 5 minutes
                chars_to_remove.append(char_name)
        
        for char_name in chars_to_remove:
            del character_states[char_name]
            socketio.emit('character_removed', {'character_name': char_name})
        
        time.sleep(60)  # Run cleanup every minute

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_inactive_characters, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False, log_output=True)