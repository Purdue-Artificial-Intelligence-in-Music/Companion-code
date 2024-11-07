from flask import Flask, request, jsonify, send_file
from flask_session import Session
import os
import librosa
import numpy as np
import redis
import secrets
import pickle
from src.audio_generator import AudioGenerator
from src.synchronizer import Synchronizer

app = Flask(__name__)

# Configure session to use Redis

# Initialize Redis connection for other operations
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Assuming the MusicXML files are stored in a folder called 'musicxml_files'
MUSICXML_FOLDER = os.path.join('data', 'musicxml')
SESSIONS = {}

def generate_session_token():
    return secrets.token_hex(32)  # Generates a 64-character hexadecimal string

@app.route('/start-session', methods=['POST'])
def start_session():
    # Generate a new session token
    session_token = generate_session_token()

    # Return the session token to the client
    return jsonify({'session_token': session_token}), 200

@app.route('/scores', methods=['GET'])
def get_scores():
    try:
        files = [f for f in os.listdir(MUSICXML_FOLDER) if f.endswith('.musicxml')]
        return jsonify({'files': files}), 200
    except Exception as e:
        return str(e), 500

@app.route('/score/<filename>', methods=['GET'])
def get_score(filename):
    file_path = os.path.join(MUSICXML_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='application/xml'), 200
    else:
        return 'File not found', 404

@app.route('/synthesize-audio/<filename>/<int:tempo>', methods=['GET'])
def synthesize_audio(filename, tempo):
    session_token = request.headers.get('session-token')
    if not session_token:
        return 'Missing or invalid session token', 401

    file_path = os.path.join(MUSICXML_FOLDER, filename)
    if not os.path.exists(file_path):
        return 'MusicXML file not found', 404

    generator = AudioGenerator(file_path)
    output_dir = os.path.join('data', 'audio', filename.replace('.musicxml', ''))
    print(output_dir)
    generator.generate_audio(output_dir, tempo)

    # Create a synchronizer object for this session
    synchronizer = Synchronizer(reference=os.path.join(output_dir, 'instrument_0.wav'))

    # Store the synchronizer
    SESSIONS[session_token] = {'synchronizer': synchronizer}

    accompaniment, _ = librosa.load(os.path.join(output_dir, 'instrument_1.wav'), sr=44100, mono=True, dtype=np.float32)
    accompaniment = accompaniment.tolist()
    return jsonify({'audio_data': accompaniment}), 200

@app.route('/synchronization', methods=['POST'])
def synchronization():
    # Get the session token from the request headers
    session_token = request.headers.get('session-token')
    if not session_token:
        return 'Missing or invalid session token', 401
    
    # Retrieve the session data from the SESSIONS dictionary
    session_data = SESSIONS.get(session_token)
    if not session_data:
        return 'Session not found or expired', 404
    
    # Get the synchronizer object

    synchronizer = session_data['synchronizer']
    if not synchronizer:
        return 'Synchronizer not found', 404
    
    # Parse the incoming data
    if not request.is_json:
        return 'Invalid request data', 400

    data = request.get_json()
    frames = data.get('frames')
    timestamp = data.get('timestamp')

    if frames is None or timestamp is None:
        return 'Invalid request data', 400

    frames = np.asarray(frames, np.float32)
    frames = frames.reshape((1, -1))
    print(frames.shape)
    print(timestamp)
    playback_rate, estimated_position = synchronizer.step(frames, timestamp)
    return jsonify({'playback_rate': playback_rate, 'estimated_position': estimated_position}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
