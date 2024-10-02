from AudioBuffer import AudioBuffer
from otw import OnlineTimeWarping as OTW
import time
import numpy as np
import matplotlib.pyplot as plt
from features import ChromaMaker, file_to_np_cens


class ScoreFollower:
    """Performs online dynamic time warping (DTW) between reference audio and live microphone audio

    Parameters
    ----------
    reference : str
        Path to reference audio file
    source : str, optional
        Path to source audio file. If None, use microphone audio.
    c : int, optional
        Width of online DTW search
    max_run_count : int, optional
        Slope constraint for online DTW (1/max_run_count to max_run_count)
    diag_weight : int, optional
        Diagonal weight for OTW. Values less than 2 bias toward diagonal steps.
    sample_rate : int, optional
        Sample rate of the audio buffer
    win_length : int, optional
        Number of frames per chroma feature

    Attributes
    ----------
    sample_rate : int
        Sample rate of the audio buffer
    win_length : int
        Number of frames per chroma feature
    channels : int
        Number of channels
    frames_per_buffer : int
        Number of frames per buffer for PyAudio stream
    mic : int
        AudioBuffer object to store microphone audio
    chroma_maker : ChromaMaker
        ChromaMaker object to create CENS features
    ref_audio : np.ndarray
        Reference audio
    ref : np.ndarray
        Reference sequence of CENS feaures
    otw : OTW
        OTW object to align live features with reference sequence
    path : list
        Alignment path between live and reference sequences

    """
    def __init__(self, reference: str, source: str = None, c: int = 10, max_run_count: int = 3, diag_weight: int = 0.4, sample_rate: int = 44100, win_length: int = 8192, channels: int = 1, frames_per_buffer: int = 1024):

        self.sample_rate = sample_rate
        self.win_length = win_length

        # Create buffer for microphone audio
        self.mic = AudioBuffer(source=source,
                               max_duration=600,
                               sample_rate=sample_rate,
                               channels=channels,
                               frames_per_buffer=frames_per_buffer)

        # Instantiate ChromaMaker object
        self.chroma_maker = ChromaMaker(sr=sample_rate, n_fft=win_length)
        
        # Params for OTW
        params = {
        "sr": sample_rate,
        "n_fft": win_length,
        "ref_hop_len": win_length,
        "c": c,
        "max_run_count": max_run_count,
        "diag_weight": diag_weight
        }

        self.ref = file_to_np_cens(filepath=reference, params=params)

        # Initialize OTW object
        self.otw = OTW(ref=self.ref, params=params)

        # Online DTW alignment path
        self.path = []

    def get_chroma(self, audio):
        """

        Parameters
        ----------
        audio : np.ndarray
            Audio frames to convert to a chroma feature

        Returns
        -------
        np.ndarray
            Chroma feature
        """
        # If the number of frames is too small, pad with zeros
        if audio.shape[-1] < self.win_length:
            audio = np.pad(audio, ((0, 0), (0, self.win_length - audio.shape[-1])), mode='constant', constant_values=((0, 0), (0, 0)))
        
        # Return a chroma feature for the audio
        return self.chroma_maker.insert(audio)

    def step(self):
        """Calculate next step in the alignment path between the microphone and reference audio """
        
        # While the number of unread frames is less than the window length
        while self.mic.count < self.win_length:
            # If the mic is not active, return the last position in the reference audio
            if not self.mic.is_active():
                print("Microphone is no longer active and all audio has been processed.")
                return None
            # If the mic is active, wait for more audio frames
            time.sleep(0.01)

        # Read audio frames from the buffer
        audio = self.mic.read(self.win_length)

        # Generate chroma feature
        chroma = self.get_chroma(audio)

        # Calculate position in reference audio
        ref_index = self.otw.insert(chroma)

        # Record position in alignment path
        self.path.append((ref_index, self.otw.live_index))

        # Return position in reference audio
        return ref_index

    def start(self):
        """Start the microphone input stream. """
        self.mic.start()

    def pause(self):
        self.mic.pause()

    def unpause(self):
        self.mic.unpause()

    def stop(self):
        """Stop the microphone input stream. """
        self.mic.stop()

    def is_active(self):
        """Return True if the microphone input stream is active and we have not reached the end of the otw buffer"""
        return self.mic.is_active() and self.otw.live_index < self.otw.live.shape[-1] - 1
    
    def get_estimated_time(self):
        # TODO: Check that this formula is correct
        return self.otw.ref_index * self.win_length / self.sample_rate

    def get_backwards_path(self, b):
        cost_matrix = self.otw.accumulated_cost
        ref_index = self.otw.ref_index # row index
        live_index = self.otw.live_index # column index

        j = ref_index
        t = live_index
        backwards_path = []

        while j > ref_index - b and (0, 0) not in backwards_path:
            down, left, diagonal = cost_matrix[j-1, t], cost_matrix[j, t-1], cost_matrix[j-1, t-1]
            minimum_cost = min(down, left, diagonal)
            if minimum_cost == down:
                backwards_path.append((j-1, t))
                j -= 1
            elif minimum_cost == left:
                backwards_path.append((j, t-1))
                t -= 1
            else:
                backwards_path.append((j-1, t-1))
                j -= 1
                t -= 1
        
        return backwards_path
    
    def get_path_difference(self, back_path):
        return [x for x in self.path if x not in back_path]

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import os
    reference = os.path.join('data', 'audio', 'bach', 'synthesized', 'solo.wav')
    source = os.path.join('data', 'audio', 'bach', 'live', 'variable_tempo.wav')
    score_follower = ScoreFollower(reference=reference,
                                   source=None,
                                   c=10,
                                   max_run_count=3,
                                   diag_weight=0.5,
                                   sample_rate=44100,
                                   win_length=8192,
                                   channels=1,
                                   frames_per_buffer=2048)

    score_follower.start()

    while not score_follower.is_active():
        time.sleep(0.01)

    try:
        while score_follower.is_active():
            ref_index = score_follower.step()
            print(f'Live index: {score_follower.otw.live_index}, Ref index: {ref_index}')
    except KeyboardInterrupt:
        score_follower.stop()

    # cost_matrix = score_follower.otw.accumulated_cost
    # indices = np.asarray(score_follower.path).T
    # cost_matrix[(indices[0], indices[1])] = np.inf

    # t = score_follower.otw.live_index
    # j = (score_follower.otw.ref_index)/(score_follower.ref.shape[-1] - 1)

    # if t > j:
    #     back_path = score_follower.get_backwards_path(t)
    # else:
    #     back_path = score_follower.get_backwards_path(j)

    # print(f'Backwards path: {back_path}')
    # print(f'Forward path: {score_follower.path}')
    # print(f'Difference: {score_follower.get_path_difference(back_path)}')

    # plt.figure()
    # plt.imshow(cost_matrix)
    # plt.title('OTW Cost Matrix')
    # plt.xlabel('Live Sequence')
    # plt.ylabel('Reference Sequence')
    # plt.show()
    # plt.close()
    
    from librosa.display import specshow, waveshow
    fig, ax = plt.subplots(nrows=2, sharex=False, sharey=True)
    specshow(score_follower.otw.live[:, :score_follower.otw.live_index], y_axis='chroma', x_axis='time', 
             sr=score_follower.sample_rate, hop_length=score_follower.win_length, 
             win_length=score_follower.win_length, ax=ax[0])
    specshow(score_follower.otw.ref[:, :score_follower.otw.ref_index], y_axis='chroma', x_axis='time', 
            sr=score_follower.sample_rate, hop_length=score_follower.win_length, 
            win_length=score_follower.win_length, ax=ax[1])
    plt.show()

    from alignment_error import load_data, calculate_alignment_error
    
    df = load_data('data\\alignments\\variable_tempo.csv')
    warping_path = np.asarray(score_follower.path, dtype=np.float32)
    warping_path = warping_path * score_follower.win_length / score_follower.sample_rate
    df = calculate_alignment_error(df, warping_path)
    df.to_csv('output\\variable_tempo_live.csv', index=False)

    