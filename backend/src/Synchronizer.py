from PhaseVocoder import PhaseVocoder
from ScoreFollower import ScoreFollower
from AudioBuffer import AudioBuffer
# from VoiceCommandThread import VoiceAnalyzerThread
from simple_pid import PID
import soundfile
import numpy as np


class Synchronizer:
    """Synchronize microphone and accompaniment audio

    Parameters
    ----------
    score : str
        Path to score
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
    def __init__(self, reference: str, accompaniment: str, Kp: int = 0.2, Ki: int = 0.00, Kd=0.05, 
                 sample_rate: int = 44100, win_length: int = 8192, hop_length: int = 8192, c: int = 10, max_run_count: int = 3, diag_weight: int=0.4, channels: int = 1):

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
        
        self.accompaniment_buffer = AudioBuffer(sample_rate=sample_rate, channels=channels)

        # PID Controller
        self.PID = PID(Kp=Kp, Ki=Ki, Kd=Kd, setpoint=0, starting_output=1.0, 
                       output_limits=(1 / max_run_count, max_run_count), 
                       sample_time = win_length / sample_rate)
        
        # Voice Command thread
        # self.listener = VoiceAnalyzerThread(name="Listener", buffer=self.score_follower.mic, player=self.player)
    

    def step(self, frames):
        """Update the audio player playback rate  """
        ref_index = self.score_follower.step(frames)
        self.soloist_buffer.write(frames)
        if ref_index is None:
            return False

        accompanist_time = self.accompanist_time()
        error = accompanist_time - self.estimated_time()
        playback_rate = self.PID(error)

        if ref_index > self.c:
            self.phase_vocoder.set_playback_rate(playback_rate)

        return self.phase_vocoder.get_next_frames(), self.score_follower.get_estimated_time()
    
    def soloist_time(self):
        return self.soloist_buffer.get_time()

    def estimated_time(self):
        return self.score_follower.get_estimated_time()
    
    def accompanist_time(self):
        return self.phase_vocoder.get_time()
    
    def save_performance(self, path):
        # Get the audio logs
        mic_log = self.score_follower.input_buffer.get_audio()
        player_log = self.phase_vocoder.output_log

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
        
    # def get_warping_path(self):
    #     return self.score_follower.path
