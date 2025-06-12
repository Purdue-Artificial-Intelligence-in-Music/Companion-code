"""
Copyright (c) 2024 Matthew Caren

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from .features import Features

import numpy as np

def pitch_freqs(start_pitch=0, end_pitch=128):
    """Returns the center frequency for each MIDI pitch in the range [start_pitch:end_pitch].

    :param start_pitch: starting pitch
    :param end_pitch: one more than the last pitch value

    :returns: a numpy array of length end_pitch-start_pitch of frequencies
    """
    p = np.arange(start_pitch, end_pitch)
    kTRT = 2**(1/12.)
    return 440 * (kTRT ** (p - 69.))


def spec_to_pitch_mtx(fs, fft_len, tuning=0.):
    """Create a conversion matrix from a FT vector to a MIDI pitch vector.
    Is also the conversion matrix from a spectrogram to a pitch-o-gram.
    AKA, log-frequency spectrum.

    :param fs: the sample rate
    :param fft_len: the length of the FFT
    :param tuning: an optional MIDI pitch adjustment parameter for alternate tunings, in units of semi-tones

    :returns: a matrix of shape (128, num_bins), where num_bins corresponds to the number of bins in the first half of the FFT
    """

    num_bins = fft_len // 2 + 1
    out = np.zeros((128, num_bins))

    # frequncies for each bin in the fft
    bin_f = np.arange(fft_len / 2. + 1) * fs / fft_len

    # frequency ranges for each pitch in 0-128. Range is pitch_f[p] to pitch_f[p+1]
    pitch_center = pitch_freqs(0.+tuning, 128.+tuning)
    pitch_edges = pitch_freqs(-0.5+tuning, 128.5+tuning)

    def _func(f1, f2, f3, x):
        f = np.linspace(f1, f3, 128)
        h = np.hanning(128)
        return np.interp(x, f, h)

    for p in range(128):
        out[p:] = _func(pitch_edges[p], pitch_center[p],
                        pitch_edges[p+1], bin_f)

    return out


class CENSFeatures(Features):
    FEATURE_LEN = 12
    
    def __init__(self, sr, n_fft):
        '''Streaming implementation of wave to chroma. Initialize with parameters sr, n_fft. Then
        call cm.insert(y) to insert an audio buffer which must be of length n_fft'''

        super().__init__(sr=sr, win_len=n_fft)

        self.sr = sr
        self.n_fft = n_fft

        # create one time parameters:
        tuning = 0
        self.window = np.hanning(self.n_fft)
        c_fp = spec_to_pitch_mtx(self.sr, self.n_fft, tuning)
        c_pc = np.tile(np.identity(12), 11)[:, 0:128]
        self.c_fc = np.dot(c_pc, c_fp)

    def compare_features(self, other, i, j):
        return np.dot(self.get_feature(i), other.get_feature(j))

    def make_feature(self, y):
        'Convert new audio to length 12 CENS chroma vector'
        # apply window, apply FFT, convert to chroma
        sig = y * self.window
        X = np.abs(np.fft.rfft(sig)).reshape(-1, 1)
        chroma = np.dot(self.c_fc, X ** 2)[:, 0]

        # CENS operations:

        # 1) normalize by L1
        length = np.linalg.norm(chroma, ord=1)
        if length == 0:
            chroma[:] = 1
            length = 12
        chroma = chroma / length

        # 2) quantize according to logarithmic scheme. Resulting values span [0:5]
        quant = np.zeros(12)
        values = [1, 2, 3, 4]
        thresholds = [0.05, .1, .2, .4, 1]
        for i, v in enumerate(values):
            span = np.logical_and(
                chroma > thresholds[i], chroma <= thresholds[i+1])
            quant[span] = v

        # 3) smoothing would go here, but ignoring that for now.
        chroma = quant

        # 4) normalize by L2 norm
        length = np.linalg.norm(chroma, ord=2)
        if length == 0:
            chroma[:] = 1
            length = 12**(0.5)
        chroma = chroma / length

        return chroma

def audio_to_np_cens(y, sr, n_fft, hop_len):
    'Use ChromaMaker to create an np-cens chromagram from the given audio'
    obj = CENSFeatures.from_audio(y, sr, n_fft, hop_len)
    return obj.get_featuregram()


def file_to_np_cens(filepath, params):
    'Load a file and convert to an np-cens chromagram based on params'

    sr = params['sr']
    n_fft = params['n_fft']
    hop_len = params['ref_hop_len']

    obj = CENSFeatures.from_file(filepath, sr, n_fft, hop_len)
    return obj.get_featuregram()
