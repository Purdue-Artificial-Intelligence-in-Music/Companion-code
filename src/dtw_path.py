from fastdtw import fastdtw
import librosa
import numpy as np

def get_dtw_path(wav_audio: np.array, mic_audio: np.array):
    chroma_wav = librosa.feature.chroma_cqt(y=wav_audio)
    chroma_mic = librosa.feature.chroma_cqt(y=mic_audio)
    #print(chroma_mic.shape)
    padding = np.zeros((chroma_mic.shape[0], chroma_mic.shape[1], chroma_wav.shape[2] - chroma_mic.shape[2])) # to make fastdtw work
    #print(padding.shape)
    chroma_mic = np.concatenate((chroma_mic, padding), axis=2)
    #print(chroma_mic.shape)
    dist, path = fastdtw(chroma_wav, chroma_mic)
    return path