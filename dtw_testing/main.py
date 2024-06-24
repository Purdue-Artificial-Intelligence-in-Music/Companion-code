import numpy as np
import matplotlib.pyplot as plt
import librosa
import time
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from soft_dtw_cuda import SoftDTW
import torch

def fast_dtw_test():
    y, sr = librosa.load(librosa.ex('brahms'), offset=10, duration=15)

    duration = librosa.get_duration(y=y, sr=sr)
    print(duration)

    X = librosa.feature.chroma_cens(y=y, sr=sr)
    noise = np.random.rand(X.shape[0], 200) # Random noise to vary Y from X
    Y = np.concatenate((noise, noise, X, noise), axis=1) # Y is X but with noise added

    X = X.T #Transpose (not sure if this is okay but it lets fastdtw run)
    Y = Y.T # Fast dtw needs second dimension to be the same
    print(X.shape)
    print("split")
    print(Y.shape)

    before = time.time()

    distance, path = fastdtw(X, Y, dist=euclidean)
    
    after = time.time()
    print(f"Distance: {distance}")
    #print(path)

    print(f"FastDTW calculations for DTW took {after - before} seconds for a time series of {duration} seconds")


def soft_dtw_test():
    batch_size, len_x, len_y, dims = 8, 15, 12, 5
    x = torch.rand((batch_size, len_x, dims), requires_grad=True)
    y = torch.rand((batch_size, len_y, dims))
    # Transfer tensors to the GPU
    # x = x.cuda()
    # y = y.cuda()

    # Create the "criterion" object
    before = time.time()
    sdtw = SoftDTW(use_cuda=False, gamma=0.1)

    # Compute the loss value
    loss = sdtw(x, y)  # Just like any torch.nn.xyzLoss()

    # Aggregate and call backward()
    loss.mean().backward()
    after = time.time()
    print(loss)
    print(f"Soft DTW calculations for DTW took {after - before} seconds for a time series of {batch_size} batch size")


def librosa_test(plot=True):

    y, sr = librosa.load(librosa.ex('brahms'), offset=10, duration=15)

    duration = librosa.get_duration(y=y, sr=sr)
    print(duration)

    X = librosa.feature.chroma_cens(y=y, sr=sr)
    noise = np.random.rand(X.shape[0], 200) # Random noise to vary Y from X
    Y = np.concatenate((noise, noise, X, noise), axis=1) # Y is X but with noise added

    
    print(X.shape)
    print("split")
    print(Y.shape)

    
    before = time.time()

    # D, wp, steps = librosa.sequence.dtw(X, Y, subseq=True, return_steps=True)

    #distance, path = fastdtw(X, Y, dist=euclidean)
    # print(distance)

    # sdtw = SoftDTW(use_cuda=False, gamma=0.1)
    # loss = sdtw(X, Y)

    after = time.time()
    
    print(steps)
    print(wp.shape)
    best_cost = D[wp[-1, 0], wp[-1, 1]]
    print(f"best cost: {best_cost}")
    
    
    print(f"Librosa calculations for DTW took {after - before} seconds for a time series of {duration} seconds")

    if plot:
        fig, ax = plt.subplots(nrows=2, sharex=True)
        img = librosa.display.specshow(D, x_axis='frames', y_axis='frames', ax=ax[0])

        ax[0].set(title='DTW cost', xlabel='Noisy sequence', ylabel='Target')
        ax[0].plot(wp[:, 1], wp[:, 0], label='Optimal path', color='y')
        ax[0].legend()

        fig.colorbar(img, ax=ax[0])
        ax[1].plot(D[-1, :] / wp.shape[0])
        ax[1].set(xlim=[0, Y.shape[1]], ylim=[0, 2], title='Matching cost function')

        plt.show()
        
        
fast_dtw_test()
# soft_dtw_test()
# librosa_test(True)