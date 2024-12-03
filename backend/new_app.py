from flask import Flask, request, jsonify, send_file
import os
from flask_cors import CORS
import librosa
import numpy as np
import io
import base64
import soundfile as sf
import secrets
from src.audio_generator import AudioGenerator
from src.synchronizer import Synchronizer

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # setting a constant base directory
MUSICXML_FOLDER = os.path.join(BASE_DIR, 'data', 'musicxml')
SESSIONS = {}

def generate_session_token():
    return secrets.token_hex(32)  # Generates a 64-character hexadecimal string

@app.route('/start-session', methods=['POST'])
def start_session():
    try:
        # Generate a new session token
        session_token = generate_session_token()
        # Return the session token to the client
        return jsonify({'session_token': session_token}), 200
    except Exception as e:
        return str(e), 500

@app.route('/scores', methods=['GET'])
def get_scores():
    try:
        files = [f for f in os.listdir(MUSICXML_FOLDER) if f.endswith('.musicxml')]
        return jsonify({'files': files}), 200
    except Exception as e:
        return str(e), 500

@app.route('/score/<filename>', methods=['GET'])
def get_score(filename):
    try:
        file_path = os.path.join(MUSICXML_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='application/xml'), 200
        else:
            return 'File not found', 404
    except Exception as e:
        return str(e), 500

@app.route('/synthesize-audio/<filename>/<int:tempo>', methods=['GET'])
def synthesize_audio(filename, tempo):
    # Get the session token from the request headers
    print("synthesize start")
    session_token = request.headers.get('session-token')
    if not session_token:
        return 'Missing or invalid session token', 401
    
    # Check if the MusicXML file exists
    file_path = os.path.join(MUSICXML_FOLDER, filename)
    print("file_path", file_path)
    if not os.path.exists(file_path):
        return 'MusicXML file not found', 404
    
    # Generate the solo and accompaniment audio files
    generator = AudioGenerator(file_path)
    output_dir = os.path.join(BASE_DIR, 'data', 'audio', filename.replace('.musicxml', ''))
    print(output_dir)
    generator.generate_audio(output_dir, tempo)

    # Create a synchronizer object
    reference = os.path.join(output_dir, 'instrument_0.wav')

    synchronizer = Synchronizer(reference=reference,
                                Kp=0.05,
                                Ki=0.0,
                                Kd=0.0,
                                sample_rate=44100,
                                channels=1,
                                win_length=8192,
                                hop_length=2048,
                                c=50,
                                max_run_count=3,
                                diag_weight=0.4)
    # Store the synchronizer in the SESSIONS dictionary
    SESSIONS[session_token] = {'synchronizer': synchronizer}

    # Return the accompaniment audio data to the client
    accompaniment, sr = librosa.load(os.path.join(output_dir, 'instrument_1.wav'), sr=44100, mono=True, dtype=np.float32)
    accompaniment = accompaniment.tolist()
    # print(accompaniment)
    
    # Converting accompaniment buffer into an encoded format
    buffer_io = io.BytesIO()
    sf.write(buffer_io, accompaniment, sr, format='WAV')
    buffer_io.seek(0)
    
    #need to return the audio buffer in base64 format for compatability with native audio players
    audio_base64 = base64.b64encode(buffer_io.read()).decode('utf-8')
    
    # print(audio_base64)
    data = {
        "buffer" : audio_base64,
        "sr" : sr
    }
    return jsonify(data), 200

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

    synchronizer: Synchronizer = session_data['synchronizer']

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

@app.route('/stop-session', methods=['POST'])
def stop_session():
    # Get the session token from the request headers
    session_token = request.headers.get('session-token')
    if not session_token:
        return 'Missing or invalid session token', 401
    
    try:
        # Remove the session data from the SESSIONS dictionary
        if session_token in SESSIONS:
            del SESSIONS[session_token]
        
        return 'Session stopped', 200
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
