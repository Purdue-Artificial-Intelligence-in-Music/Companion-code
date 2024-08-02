import librosa
import audioflux as af
import numpy as np
import matplotlib.pyplot as plt

Both = 0
Column = 1
Row = 2

audio, sr = librosa.load('audio_files/moonlight_sonata.wav')
stretched_audio = librosa.effects.time_stretch(audio, rate = 1.1)
# cqt_obj = af.CQT(num=84, samplate=sr, slide_length=1024)
# cqt_arr = cqt_obj.cqt(audio)
# chroma_features = cqt_obj.chroma(cqt_arr)
# chroma_features = chroma_features.reshape((-1, 12))

chroma_features = librosa.feature.chroma_cens(y=audio, sr=sr, hop_length=1024, win_len_smooth=1024).T
stretched_chroma_features = librosa.feature.chroma_cens(y=stretched_audio, sr=sr, hop_length=1024, win_len_smooth=1024).T
t = 0  # current position in u
j = 0  # current position in v
v = chroma_features  # known sequence
u = stretched_chroma_features  # partially unknown sequence
previous = None

c = 200
runCount = 0
MaxRunCount = 2

D = np.ones((len(u), len(v))) * np.inf

def d(i, j):
    diff = u[i] - v[j]
    return np.sqrt(np.dot(diff, diff))

def EvaluatePathCost(i, j):
    global D

    # Base Case
    if i == 0 and j == 0:
        D[i, j] = d(i, j)
        return
    
    # Recursive Case
    if j == 0:
        below = np.inf
    else:
        below = D[i, j-1] + d(i, j)

    if i == 0:
        left = np.inf
    else:
        left = D[i-1, j] + d(i, j)

    if i == 0 or j ==  0:
        diagonal = np.inf
    else:
        diagonal = D[i-1, j-1] + 2*d(i, j)
    
    D[i, j] = np.min((below, left, diagonal))

def GetInc(t, j):
    global c, runCount, MaxRunCount

    if t < c:
        return Both
    
    if runCount > MaxRunCount:
        if previous == Row:
            return Column
        else:
            return Row
        
    x1, y1 = t, np.argmin(D[t, :])
    x2, y2 = np.argmin(D[:, j]), j

    if D[x1, y1] <= D[x2, y2]:
        x, y = x1, y1
    else:
        x, y = x2, y2

    if x < t:
        return Row
    elif y < j:
        return Column
    else:
        return Both
    

EvaluatePathCost(t, j)

while True:
    inc = GetInc(t, j)
    if inc != Column:
        t = t + 1
        if t >= len(u):
            break
        for k in range (j - c + 1, j + 1, 1):
            if k > 0:
                EvaluatePathCost(t, k)
    if inc != Row:
        j = j + 1
        if j >= len(v):
            break
        for k in range(t - c + 1, t + 1, 1):
            if k > 0:
                EvaluatePathCost(k, j)
    if inc == previous:
        runCount = runCount + 1
    else:
        runCount = 1
    if inc != Both:
        previous = inc

plt.imshow(D)
plt.show()