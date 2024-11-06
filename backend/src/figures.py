import numpy as np
import librosa
from librosa.display import specshow, waveshow
import matplotlib.pyplot as plt

sr = 16000
window_length = 8192
hop_length = window_length

live_audio, _ = librosa.load(
    'data/bach/live/constant_tempo.wav', sr=sr, mono=True)
ref_audio, _ = librosa.load(
    'data/bach/synthesized/track0.wav', sr=sr, mono=True)
comp_audio, _ = librosa.load(
    'data/bach/synthesized/track1.wav', sr=sr, mono=True)

live_audio /= np.max(live_audio)
ref_audio /= np.max(ref_audio)
comp_audio /= np.max(comp_audio)

live_chroma = librosa.feature.chroma_cens(
    y=live_audio, sr=sr, hop_length=hop_length, win_len_smooth=None)
ref_chroma = librosa.feature.chroma_cens(
    y=ref_audio, sr=sr, hop_length=hop_length, win_len_smooth=None)

plt.rcParams.update({'font.size': 18})
figsize = (18, 6)
dpi = 400
pad_inches = 0.1

fig, ax = plt.subplots(nrows=2, sharex=True, figsize=figsize)
waveshow(y=ref_audio, x_axis='time', sr=sr, ax=ax[0])
waveshow(y=comp_audio, x_axis='time', sr=sr, ax=ax[1])
ax[0].set_title('Solo Audio')
ax[0].set_xlabel('')
ax[0].set_ylabel('Amplitude')
ax[0].set_yticks(np.array([-1, -0.5, 0, 0.5, 1]))
ax[1].set_title('Accompaniment Audio')
ax[1].set_ylabel('Amplitude')
ax[1].set_yticks(np.array([-1, -0.5, 0, 0.5, 1]))
fig.subplots_adjust(hspace=0.25)
fig.savefig('data/bach/figures/audio.png', bbox_inches='tight',
            pad_inches=pad_inches, dpi=dpi)
plt.close(fig)

# Figure showing mic audio and chroma features
fig, ax = plt.subplots(nrows=2, sharex=True, figsize=figsize)
waveshow(y=live_audio, x_axis='time', sr=sr, ax=ax[0])
img = specshow(live_chroma, y_axis='chroma', x_axis='time', sr=sr,
               hop_length=window_length, win_length=window_length, ax=ax[1])
ax[0].set_title('Live Audio')
ax[0].set_xlabel('')
ax[0].set_ylabel('Amplitude')
ax[0].set_yticks(np.array([-1, -0.5, 0, 0.5, 1]))
ax[1].set_title('Live Features')
fig.subplots_adjust(hspace=0.25)
fig.colorbar(img, ax=ax)
fig.savefig('data/bach/figures/live_chroma.png',
            bbox_inches='tight', pad_inches=pad_inches, dpi=dpi)
plt.close(fig)

# Figure showing reference audio and chroma features
fig, ax = plt.subplots(nrows=2, sharex=True, figsize=figsize)
waveshow(y=ref_audio, x_axis='time', sr=sr, ax=ax[0])
img = specshow(ref_chroma, y_axis='chroma', x_axis='time', sr=sr,
               hop_length=hop_length, win_length=window_length, ax=ax[1])
ax[0].set_title('Reference Audio')
ax[0].set_xlabel('')
ax[0].set_ylabel('Amplitude')
ax[0].set_yticks(np.array([-1, -0.5, 0, 0.5, 1]))
ax[1].set_title('Reference Features')
fig.subplots_adjust(hspace=0.25)
fig.colorbar(img, ax=ax)
fig.savefig('data/bach/figures/ref_chroma.png',
            bbox_inches='tight', pad_inches=pad_inches, dpi=dpi)
plt.close(fig)

# Figure showing chroma features
fig, ax = plt.subplots(nrows=2, sharex=True, sharey=True, figsize=figsize)
img = specshow(live_chroma, y_axis='chroma', x_axis='time', ax=ax[0], sr=sr,
               hop_length=hop_length, win_length=window_length)
specshow(ref_chroma, y_axis='chroma', x_axis='time', ax=ax[1], sr=sr,
         hop_length=hop_length, win_length=window_length)
ax[0].set_title('Live Features')
ax[0].set_xlabel('')
ax[1].set_title('Reference Features')
fig.subplots_adjust(hspace=0.25)
fig.colorbar(img, ax=ax)
fig.savefig('data/bach/figures/live_ref_chroma.png',
            bbox_inches='tight', pad_inches=pad_inches, dpi=dpi)
plt.close(fig)
