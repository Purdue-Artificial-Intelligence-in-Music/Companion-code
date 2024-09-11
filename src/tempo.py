import librosa

def tempo(wav_file):
    return librosa.feature.tempo(y=wav_file)[0]