import numpy as np
# from .file_utils import load_wav

def pitch_freqs(start_pitch = 0, end_pitch = 128) :
    """Returns the center frequency for each MIDI pitch in the range [start_pitch:end_pitch].
    
    :param start_pitch: starting pitch
    :param end_pitch: one more than the last pitch value
    
    :returns: a numpy array of length end_pitch-start_pitch of frequencies
    """
    p = np.arange(start_pitch, end_pitch)
    kTRT = 2**(1/12.)
    return 440 * (kTRT ** (p - 69.))


def spec_to_pitch_mtx(fs, fft_len, tuning = 0.) :
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
    pitch_edges  = pitch_freqs(-0.5+tuning, 128.5+tuning) 

    def _func(f1, f2, f3, x):
        f = np.linspace(f1, f3, 128)
        h = np.hanning(128)
        return np.interp(x, f, h)

    for p in range(128):
        out[p:] = _func(pitch_edges[p], pitch_center[p], pitch_edges[p+1], bin_f)

    return out


class ChromaMaker(object):
    def __init__(self, sr, n_fft):
        '''Streaming implementation of wave to chroma. Initialize with parameters sr, n_fft. Then
        call cm.insert(y) to insert an audio buffer which must be of length n_fft'''

        super(ChromaMaker, self).__init__()
        
        self.sr = sr
        self.n_fft = n_fft
        
        # create one time parameters:
        tuning = 0
        self.window = np.hanning(self.n_fft)
        c_fp = spec_to_pitch_mtx(self.sr, self.n_fft, tuning)
        c_pc = np.tile(np.identity(12), 11)[:, 0:128]
        self.c_fc = np.dot(c_pc, c_fp)
        
    def reset(self):
        pass

    def insert(self, y):
        'insert new audio. Return length 12 CENS chroma vector'

        # apply window, apply FFT, convert to chroma
        sig = y * self.window
        X = np.abs(np.fft.rfft(sig)).reshape(-1, 1)
        chroma = np.dot(self.c_fc, X ** 2)[:,0]
        
        # CENS operations:
        
        # 1) normalize by L1
        length = np.linalg.norm(chroma, ord=1)
        if length == 0:
            chroma[:] = 1
            length = 12
        chroma = chroma / length
        
        # 2) quantize according to logarithmic scheme. Resulting values span [0:5]
        quant  = np.zeros(12)
        values = [1, 2, 3, 4]
        thresholds = [0.05, .1, .2, .4, 1]
        for i, v in enumerate(values):
            span = np.logical_and(chroma > thresholds[i], chroma <= thresholds[i+1])
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

    # length of live features; create output
    M = (len(y) - n_fft) // hop_len + 1
    out = np.zeros((12, M))
    
    cm = ChromaMaker(sr, n_fft)
    for m in range(M):
        window = y[m*hop_len:m*hop_len+n_fft]
        out[:,m] = cm.insert(window)

    return out

# def file_to_np_cens(filepath, params):
#     'Load a file and convert to an np-cens chromagram based on params'

#     y = load_wav(filepath)
#     sr = params['sr']
#     n_fft = params['n_fft']
#     hop_len = params['ref_hop_len']

#     return audio_to_np_cens(y, sr, n_fft, hop_len)

