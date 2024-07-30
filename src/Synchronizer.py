from AudioPlayer import AudioPlayer
from ScoreFollower import ScoreFollower
from simple_pid import PID
import soundfile
import numpy as np


class Synchronizer:
    """Synchronize microphone and accompaniment audio

    Parameters
    ----------
    score : str
        Path to score
    source : str, optional
        Path to soloist recording. If None, use mic audio.
    output : str, optional
        Path to output file for performance recording. If None, use score title.
    sample_rate : int, optional
        Sample rate for audio file
    channels : int, optional
        Number of channels for audio file
    frames_per_buffer : int, optional
        Number of frames per buffer for PyAudio stream
    window_length : int, optional
        Window length for CENS feature generation
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
    def __init__(self, reference: str, accompaniment: str, source: str = None, sample_rate: int = 16000, channels: int = 1, frames_per_buffer: int = 1024, 
                 window_length: int = 4096, c: int = 10, max_run_count: int = 3, diag_weight: int = 2, Kp: int = 0.2, Ki: int = 0.00, Kd=0.05):

        self.sample_rate = sample_rate
        self.window_length = window_length
        self.c = c
            
        # ScoreFollower needs soloist audio
        self.score_follower = ScoreFollower(reference=reference,
                                            source=source,
                                            sample_rate=sample_rate,
                                            channels=channels,
                                            frames_per_buffer=frames_per_buffer,
                                            window_length=window_length,
                                            c=c,
                                            max_run_count=max_run_count,
                                            diag_weight=diag_weight)
        
        # AudioPlayer needs accompanist audio
        self.player = AudioPlayer(path=accompaniment,
                                  sample_rate=sample_rate,
                                  channels=channels,
                                  frames_per_buffer=frames_per_buffer,
                                  playback_rate=1.0)

        # PID Controller
        self.PID = PID(Kp=Kp, Ki=Ki, Kd=Kd, setpoint=0, starting_output=1.0, 
                       output_limits=(1 / max_run_count, max_run_count), sample_time = window_length / sample_rate)
        
        self.accompanist_time_log = []

    def start(self):
        """Start the score follower and audio player. """
        self.score_follower.start()
        self.player.start()

    def stop(self):
        """Stop the score follower and audio player """
        self.score_follower.stop()
        self.player.stop()

    def update(self):
        """Update the audio player playback rate  """

        ref_index = self.score_follower.step()

        if ref_index is None:
            return False

        accompanist_time = self.accompanist_time()
        self.accompanist_time_log.append(accompanist_time)
        error = accompanist_time - self.predicted_time()
        playback_rate = self.PID(error)

        if ref_index > self.c:
            self.player.playback_rate = playback_rate

        return self.is_active()

    def is_active(self):
        """Return True if score follower and audio player are both active. False otherwise. """
        return self.score_follower.is_active() and self.player.is_active()
    
    def soloist_time(self):
        return self.score_follower.mic.write_index / self.score_follower.mic.sample_rate

    def predicted_time(self):
        return self.score_follower.otw.j * self.window_length / self.sample_rate
    
    def accompanist_time(self):
        return self.player.index / self.player.sample_rate
    
    def save_performance(self, path):
        # Get the audio logs
        mic_log = self.score_follower.mic.get_audio()
        player_log = self.player.output_log

        # Trim the audio logs to be the same length
        length = min(mic_log.shape[-1], player_log.shape[-1])
        mic_log = mic_log[:, :length]
        player_log = player_log[:, :length]

        # Normalize and combine logs
        mic_log /= np.max(mic_log)
        player_log /= np.max(player_log)
        audio = mic_log + player_log
        audio /= np.max(audio)
        audio = audio.reshape((-1, ))

        # Save performance to wave file
        soundfile.write(path, audio, self.sample_rate)
