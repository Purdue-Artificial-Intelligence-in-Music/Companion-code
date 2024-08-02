import sys
import numpy as np
import wave

from js import Blob, document, window


def load_wav(filepath, t_start=0, t_end=sys.maxsize):
    """Load a wave file, which must be 16bit and must be either mono or stereo.
    :param filepath: audio file
    :param t_start: start time when loading a portion of the file (in seconds)
    :param t_end: end time when loading a portion of the file (in seconds)
    :return: a numpy floating-point array with a range of [-1, 1]
    """

    wf = wave.open(filepath)
    num_channels, sampwidth, fs, end, comptype, compname = wf.getparams()

    # for now, we will only accept 16 bit files
    assert sampwidth == 2

    # start frame, end frame, and duration in frames
    f_start = int(t_start * fs)
    f_end = min(int(t_end * fs), end)
    frames = f_end - f_start

    wf.setpos(f_start)
    raw_bytes = wf.readframes(frames)

    # convert raw data to numpy array, assuming int16 arrangement
    samples = np.frombuffer(raw_bytes, dtype=np.int16)

    # convert from integer type to floating point, and scale to [-1, 1]
    samples = samples.astype(np.float32)
    samples *= 1 / 32768.0

    if num_channels == 1:
        return samples

    elif num_channels == 2:
        return 0.5 * (samples[0::2] + samples[1::2])

    else:
        raise ("Can only handle mono or stereo wave files")


def save_from_browser(file, filename):
    "pass numpy array out of the Pyodide in-memory filesystem to save to disk from browser"
    np.set_printoptions(threshold=np.inf)
    blob = Blob.new(
        [np.array2string(file, separator=",", suppress_small=True)[1:-1]],
        {type: "text/csv"},
    )
    url = window.URL.createObjectURL(blob)

    downloadLink = document.createElement("a")
    downloadLink.href = url
    downloadLink.download = filename
    document.body.appendChild(downloadLink)
    downloadLink.click()
