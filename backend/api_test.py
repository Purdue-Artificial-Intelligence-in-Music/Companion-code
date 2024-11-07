import requests
import numpy as np
import soundfile as sf
import librosa 
import os
from src.alignment_error import load_data, calculate_alignment_error
from src.accompaniment_error import calculate_accompaniment_error

# Define the base URL for the Flask application
BASE_URL = "http://127.0.0.1:5000"

# Step 1: Get a session token from /start-session
start_session_url = f"{BASE_URL}/start-session"
try:
    start_response = requests.post(start_session_url)
    if start_response.status_code == 200:
        # Extract the session token from the response
        session_token = start_response.json().get('session_token')
        if session_token:
            print(f"Session Token Received: {session_token}")
        else:
            print("Failed to get session token")
            exit()
    else:
        print(f"Failed to start session. Status code: {start_response.status_code}, Message: {start_response.text}")
        exit()
except requests.RequestException as e:
    print(f"Exception occurred while starting session: {e}")
    exit()

# Step 2: List available music scores
scores_url = f"{BASE_URL}/scores"
try:
    scores_response = requests.get(scores_url)
    if scores_response.status_code == 200:
        scores = scores_response.json().get('files')
        if scores:
            print("Available Music Scores:")
            for score in scores:
                print(score)
        else:
            print("No music scores found")
    else:
        print(f"Failed to get music scores. Status code: {scores_response.status_code}, Message: {scores_response.text}")
except requests.RequestException as e:
    print(f"Exception occurred while getting music scores: {e}")

# Step 3: Fetch a specific music score
score_filename = input("Enter the name of the music score file to fetch: ")
score_url = f"{BASE_URL}/score/{score_filename}"
try:
    score_response = requests.get(score_url)
    if score_response.status_code == 200:
        with open(os.path.join('output', score_filename), 'wb') as f:
            f.write(score_response.content)
        print(f"Music score {score_filename} downloaded successfully")
    else:
        print(f"Failed to download music score. Status code: {score_response.status_code}, Message: {score_response.text}")
except requests.RequestException as e:
    print(f"Exception occurred while fetching music score: {e}")


# Step 4: Synthesize audio from the music score
tempo = input("Enter the tempo for audio synthesis: ")
synthesize_audio_url = f"{BASE_URL}/synthesize-audio/{score_filename}/{tempo}"
headers = {
    "session-token": session_token
}
try:
    audio_response = requests.get(synthesize_audio_url, headers=headers)
    if audio_response.status_code == 200:
        source_audio = audio_response.json().get('audio_data')
        sample_rate = audio_response.json().get('sample_rate')
        if source_audio:
            print("Audio data received successfully")
            # Process the audio data as needed
            source_audio = np.array(source_audio, dtype=np.float32)
            sf.write("output/synthesized_accompaniment.wav", source_audio, sample_rate)
        else:
            print("Failed to get audio data")
    else:
        print(f"Failed to synthesize audio. Status code: {audio_response.status_code}, Message: {audio_response.text}")
except requests.RequestException as e:
    print(f"Exception occurred while synthesizing audio: {e}")

# Step 5: Perform synchronization with live audio frames
synchronization_url = f"{BASE_URL}/synchronization"
headers = {
    "Content-Type": "application/json",
    "session-token": session_token
}

soloist_times = []
estimated_times = []
accompanist_times = []

# Load the solo audio file using librosa
source_file = os.path.join("data", "audio", score_filename.replace('.musicxml', ''), "live", "constant_tempo.wav")
source_audio, sample_rate = librosa.load(source_file, sr=44100)

accompanist_time = 0

input('Press Enter to start the performance')

for i in range(0, source_audio.shape[-1], 8192):
    frames = source_audio[i:i + 8192].tolist()
    soloist_time = i / sample_rate
    payload = {
        "frames": frames,
        "timestamp": accompanist_time
    }
    try:
        response = requests.post(synchronization_url, headers=headers, json=payload)
        if response.status_code == 200:
            playback_rate = response.json().get('playback_rate')
            estimated_time = response.json().get('estimated_position')
            accompanist_time += playback_rate * 8192 / sample_rate

            soloist_times.append(soloist_time)
            estimated_times.append(estimated_time)
            accompanist_times.append(accompanist_time)

            print(f'Soloist time: {soloist_time:.2f}, Estimated time: {estimated_time:.2f}, Accompanist time: {accompanist_time:.2f}, Playback rate: {playback_rate:.2f}')
        else:
            print(f"Error: {response.status_code}, Message: {response.text}")
    except requests.RequestException as e:
        print(f"Exception occurred while calling synchronization: {e}")
