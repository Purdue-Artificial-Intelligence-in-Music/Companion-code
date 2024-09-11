from AudioPlayer import AudioPlayer
from ScoreFollower import ScoreFollower
from VoiceCommandThread import VoiceAnalyzerThread
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
    listener : VoiceCommandThread
        VoiceAnalyzerThread object to update settings on the fly
    """
    def __init__(self, reference: str, accompaniment: str, source: str = None, Kp: int = 0.2, Ki: int = 0.00, Kd=0.05, 
                 sample_rate: int = 16000, win_length: int = 4096, hop_length: int = 1024, c: int = 10, max_run_count: int = 3, diag_weight: int=0.5, **kwargs):

        self.sample_rate = sample_rate
        self.c = c

        # ScoreFollower needs soloist audio
        self.score_follower = ScoreFollower(reference=reference,
                                            source=source,
                                            c=c,
                                            max_run_count=max_run_count,
                                            diag_weight=diag_weight,
                                            sample_rate=sample_rate,
                                            win_length=win_length,
                                            **kwargs)
        
        # AudioPlayer needs accompanist audio
        self.player = AudioPlayer(path=accompaniment, playback_rate=1.0, hop_length=hop_length, **kwargs)
        
        # PID Controller
        self.PID = PID(Kp=Kp, Ki=Ki, Kd=Kd, setpoint=0, starting_output=1.0, 
                       output_limits=(1 / max_run_count, max_run_count), 
                       sample_time = win_length / sample_rate)
        
        # Voice Command thread
        self.listener = VoiceAnalyzerThread(name="Listener", buffer=self.score_follower.mic, player=self.player)
        
        self.accompanist_time_log = []

    def start(self):
        """Start the score follower and audio player. """
        self.score_follower.start()
        self.player.start()

    def pause(self):
        self.score_follower.pause()
        self.player.pause()

    def unpause(self):
        self.score_follower.unpause()
        self.player.unpause()

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
        error = accompanist_time - self.estimated_time()
        playback_rate = self.PID(error)

        if ref_index > self.c:
            self.player.playback_rate = playback_rate

        return self.is_active()

    def is_active(self):
        """Return True if score follower and audio player are both active. False otherwise. """
        return self.score_follower.is_active() and self.player.is_active()
    
    def soloist_time(self):
        return self.score_follower.mic.get_time()

    def estimated_time(self):
        return self.score_follower.get_estimated_time()
    
    def accompanist_time(self):
        return self.player.get_time()
    
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
