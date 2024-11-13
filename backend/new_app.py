from flask import Flask, request, jsonify, send_file
import os
from src.audio_generator import AudioGenerator
import librosa
import numpy as np

app = Flask(__name__)

# Assuming the MusicXML files are stored in a folder called 'musicxml_files'
MUSICXML_FOLDER = os.path.join('data', 'musicxml')
SESSIONS = {}

@app.route('/scores', methods=['GET'])
def get_scores():
    try:
        files = [f for f in os.listdir(MUSICXML_FOLDER) if f.endswith('.musicxml')]
        return jsonify({'files': files}), 200
    except Exception as e:
        return str(e), 500

@app.route('/score/<filename>', methods=['GET'])
def get_score(filename):
    session_token = request.headers.get('session-token')
    SESSIONS[session_token] = filename
    file_path = os.path.join(MUSICXML_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='application/xml'), 200
    else:
        return 'File not found', 404

@app.route('/synthesize-audio/<filename>/<int:tempo>', methods=['GET'])
def synthesize_audio(filename, tempo):
    session_token = request.headers.get('session-token')
    if not session_token or session_token not in SESSIONS:
        return 'Missing or invalid session token', 401

    file_path = os.path.join(MUSICXML_FOLDER, filename)
    if not os.path.exists(file_path):
        return 'MusicXML file not found', 404
    
    SESSIONS[session_token] = filename

    generator = AudioGenerator(file_path)
    output_dir = os.path.join('data', 'audio', filename.replace('.musicxml', '.wav'))
    generator.generate_audio(output_dir, tempo)
    accompaniment, _ = librosa.load(os.path.join(output_dir, 'insturment_1.wav'))
    accompaniment = accompaniment.tolist()  # Makes it possible to send through JSON
    return jsonify({'audio_data': accompaniment}), 200

@app.route('/synchronization', methods=['POST'])
def synchronization():
    session_token = request.headers.get('session-token')
    if not session_token:
        return 'Missing or invalid session token', 401

    if not request.is_json:
        return 'Invalid request data', 400

    data = request.get_json()
    frames = data.get('frames')
    timestamp = data.get('timestamp')

    if frames is None or timestamp is None:
        return 'Invalid request data', 400

    # Placeholder for synchronization logic
    # Here we would estimate the soloist's position and calculate the playback rate
    # For now, we'll just return a mock response
    playback_rate = 1.0  # Mock playback rate
    estimated_position = timestamp + 1.0  # Mock estimated position
    return jsonify({'playback_rate': playback_rate, 'estimated_position': estimated_position}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
