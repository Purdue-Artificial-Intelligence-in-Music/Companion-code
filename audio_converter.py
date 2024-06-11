import librosa
import numpy as np
import soundfile as sf
import scipy.io.wavfile

input_file = 'test_audio/imperial_march.wav'
output_file = 'test_audio/imperial_march.wav'

y, sr = librosa.load(input_file, sr=22050, mono=False, dtype=np.float64)
print(sr)
y = (y/np.max(y) * (2 ** 31 - 1))

y = y.astype(np.int32)
scipy.io.wavfile.write(output_file, sr, y)
