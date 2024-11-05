from phase_vocoder import PhaseVocoder
from score_follower import ScoreFollower
from audio_buffer import AudioBuffer
from simple_pid import PID
import soundfile
import numpy as np


class Synchronizer:
    """Synchronize microphone and accompaniment audio

    Parameters
    ----------
    reference : str
        Path to reference audio file
    accompaniment : str
        Path to accompaniment audio file
    Kp : int, optional
        Proportional gain for PID controller
    Ki : int, optional
        Integral gain for PID controller
    Kd : int, optional
        Derivative gain for PID controller
    sample_rate : int, optional
        Sample rate for audio file
    channels : int, optional
        Number of channels for audio file
    win_length : int, optional
        Window length for CENS feature generation
    hop_length : int, optional
        Hop length for phase vocoder
    c : int, optional
        Search width for OTW
    max_run_count : int, optional
        Slope constraint for OTW
    diag_weight : int, optional
        Diagonal weight for OTW. Values less than 2 bias toward diagonal steps.

    Attributes
    ----------
    window_length : int
        Window length for CENS feature generation
    c : int
        Search width for OTW
    score_follower : ScoreFollower
        ScoreFollower object to perform OTW
    player : AudioPlayer
        AudioPlayer object to play accompaniment
    PID : simple_pid.PID
        PID controller to adjust playback rate
    """

    def __init__(self, reference: str, accompaniment: str, Kp: int = 0.2, Ki: int = 0.00, Kd=0.05,
                 sample_rate: int = 44100, channels: int = 1, win_length: int = 8192, hop_length: int = 2048, c: int = 10, max_run_count: int = 3, diag_weight: int = 0.4):

        self.sample_rate = sample_rate
        self.c = c

        # ScoreFollower needs soloist audio
        self.score_follower = ScoreFollower(reference=reference,
                                            c=c,
                                            max_run_count=max_run_count,
                                            diag_weight=diag_weight,
                                            sample_rate=sample_rate,
                                            win_length=win_length,
                                            channels=channels)

        self.soloist_buffer = AudioBuffer(max_duration=600,
                                          sample_rate=sample_rate,
                                          channels=channels)

        self.phase_vocoder = PhaseVocoder(path=accompaniment,
                                          playback_rate=1.0,
                                          sample_rate=sample_rate,
                                          channels=channels,
                                          n_fft=win_length,
                                          hop_length=hop_length)

        self.accompaniment_buffer = AudioBuffer(
            sample_rate=sample_rate, channels=channels)

        # PID Controller
        self.PID = PID(Kp=Kp, Ki=Ki, Kd=Kd, setpoint=0, starting_output=1.0,
                       output_limits=(1 / max_run_count, max_run_count),
                       sample_time=win_length / sample_rate)

    def step(self, frames):
        """Update the audio player playback rate  """
        self.soloist_buffer.write(frames)
        ref_index = self.score_follower.step(frames)
        if ref_index is None:
            return False
        
        error = self.accompanist_time() - self.estimated_time()
        playback_rate = self.PID(error)

        if ref_index > self.c:
            self.phase_vocoder.set_playback_rate(playback_rate)

        accompaniment_frames = self.phase_vocoder.get_next_frames()
        if accompaniment_frames is not None:
            self.accompaniment_buffer.write(accompaniment_frames)
        return accompaniment_frames, self.score_follower.get_estimated_time()

    def soloist_time(self):
        return self.soloist_buffer.get_time()

    def estimated_time(self):
        return self.score_follower.get_estimated_time()

    def accompanist_time(self):
        return self.phase_vocoder.get_time()

    def save_performance(self, path):
        # Get the audio logs
        soloist_audio = self.soloist_buffer.get_audio()
        accompanist_audio = self.accompaniment_buffer.get_audio()

        # Trim the audio logs to be the same length
        length = min(soloist_audio.shape[-1], accompanist_audio.shape[-1])
        print(soloist_audio.shape, accompanist_audio.shape)
        soloist_audio = soloist_audio[:, :length]
        accompanist_audio = accompanist_audio[:, :length]

        # Normalize and combine logs
        soloist_audio /= np.max(np.abs(soloist_audio))
        accompanist_audio /= np.max(np.abs(accompanist_audio))

        audio = soloist_audio + accompanist_audio
        audio /= np.max(np.abs(audio))
        audio = audio.reshape((-1, ))

        # Save performance to wave file
        soundfile.write(path, audio, self.sample_rate)
