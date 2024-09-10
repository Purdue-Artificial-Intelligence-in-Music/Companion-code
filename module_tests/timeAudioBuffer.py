import sys
import os

# importing AudioBuffer to this script
directory = r'C:\Users\Nick\github\Nick-Ko-Companion-code\src'
assert os.path.exists(directory), f"{directory} does not exists"
sys.path.append(directory)
print(directory in sys.path)

try:
    from AudioBuffer import AudioBuffer
except:
    print("remember to use SET PYTHONPATH=\"C:\\Users\\Nick\\github\\Nick-Ko-Companion-code\\src\"")
    print("on Windows machines")
    exit(1)

import time
import numpy as np
import matplotlib.pyplot as plt

DURATION_UPPER_LIMIT = 10**4

def measure_elapsed_time(maxDuration: int)->float:
    # when calling this function, vary maxDuration only to change buffer size
    if maxDuration <= 0:
        maxDuration = 600
    currTime = time.perf_counter()  #current time stamp
    # init AudioBuffer: testing empty 
    myAudioBuffer = AudioBuffer(max_duration=maxDuration)
    timeElapsed = time.perf_counter() - currTime
    return timeElapsed


def main()->None:
    # set up values
    durationValues = np.array([i for i in range(600, DURATION_UPPER_LIMIT, 100)])
    bufferSizes = np.array([value * 1024 for value in durationValues])
    measuredTime = np.array([measure_elapsed_time(time) for time in durationValues])

    # plotting
    fig, ax = plt.subplots()
    ax.plot(durationValues, measuredTime)
    ax.set_xlabel('bufferSizes', fontweight ='bold')
    ax.set_ylabel('elapsed_time measured in ns')
    ax.grid(True)
    
    ax.set_title('bufferSize vs elapsed_time', fontsize = 14, fontweight ='bold')
    plt.savefig('AuioBufferInitTime.png')

if __name__ == '__main__':
    main()