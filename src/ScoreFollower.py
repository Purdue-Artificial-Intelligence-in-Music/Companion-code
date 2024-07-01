from buffer import AudioBuffer
import librosa
from otw import OTW
from threading import Thread
import time
import numpy as np
import matplotlib.pyplot as plt
from features import ChromaMaker, audio_to_np_cens


class ScoreFollower(Thread):
    """ """
    def __init__(self, path, sample_rate=22050, channels=1, frames_per_buffer=1024, window_length=4096, c=10, max_run_count=3, diag_weight=0.4):
        super(ScoreFollower, self).__init__()

        self.sample_rate = sample_rate
        self.channels = channels
        self.frames_per_buffer = frames_per_buffer
        self.window_length = window_length
        self.daemon = True

        self.mic = AudioBuffer(sample_rate=sample_rate,
                               channels=channels,
                               frames_per_buffer=frames_per_buffer,
                               num_chunks=100)

        ref_audio, _ = librosa.load(path, sr=22050)
        self.chroma_maker = ChromaMaker(sr=sample_rate, n_fft=window_length)

        self.ref = audio_to_np_cens(y=ref_audio, sr=sample_rate, n_fft=window_length, hop_len=window_length)

        print(self.ref.shape)
        params = {
        "c": c,
        "max_run_count": max_run_count,
        "diag_weight": diag_weight
        }

        self.otw = OTW(ref=self.ref, params=params)
        self.path = []
        print(self.otw.live.shape)

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
        if audio.shape[-1] < self.window_length:
            audio = np.pad(audio, ((0, 0), (0, self.window_length - audio.shape[-1])), mode='constant', constant_values=((0, 0), (0, 0)))
        
        return self.chroma_maker.insert(audio)

    def step(self):
        """Calculate next step in the alignment path between the microphone and reference audio """
        while self.mic.count < self.window_length:
            if not self.mic.is_active():
                return self.otw.j
            time.sleep(0.01)
        audio = self.mic.read(self.window_length)
        # print(f'Read index: {self.mic.read_index}, Write index: {self.mic.write_index}, Count: {self.mic.count}')
        chroma = self.get_chroma(audio)
        j = self.otw.insert(chroma)
        self.path.append((j, self.otw.t))
        return j

    def run(self):
        """Start the microphone input stream. """
        self.mic.start()

    def stop(self):
        """Stop the microphone input stream. """
        self.mic.stop()

    def is_active(self):
        """Return true if the microphone input stream is active """
        return self.mic.is_active()

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    follower = ScoreFollower(path='soloist.wav')

    follower.start()

    while not follower.is_active():
        time.sleep(0.01)

    try:
        while follower.is_active():
            follower.step()
    except KeyboardInterrupt:
        follower.stop()

    indices = np.asarray(follower.path).T
    follower.otw.D[(indices[1], indices[0])] = np.inf
    plt.imshow(follower.otw.D)
    plt.show()
