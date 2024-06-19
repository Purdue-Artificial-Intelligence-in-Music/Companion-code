from dtw import *
import librosa
import audioflux as af
import matplotlib.pyplot as plt

def to_chroma(audio, sr):
    cqt_obj = af.CQT(num=84, samplate=sr)
    cqt_arr = cqt_obj.cqt(audio)
    chroma_cqt_arr = cqt_obj.chroma(cqt_arr)
    return chroma_cqt_arr

audio, sr = librosa.load('audio_files\\moonlight_sonata.wav', mono=True)
start = 0
end = 22050
ref = audio[start:end]
query = librosa.effects.time_stretch(ref, rate=0.5)


ref_chroma = to_chroma(ref, sr)
query_chroma = to_chroma(query, sr) 

ref_chroma = ref_chroma.T
query_chroma = query_chroma.T

alignment = dtw(query_chroma, ref_chroma, open_begin=False, open_end=False)
alignment.plot(type='alignment')
plt.show()
