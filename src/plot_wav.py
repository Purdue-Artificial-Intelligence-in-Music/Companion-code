import librosa
import matplotlib.pyplot as plt

y_orig, sr_orig = librosa.load("new_src/hunt.wav")
y_new, sr_new = librosa.load("src/wav_output.wav")
L = min(len(y_orig), len(y_new))

assert sr_orig == sr_new

# plt.plot(y_orig)
# plt.plot(y_new)
plt.plot(y_orig[0:L] - y_new[0:L])
plt.show()