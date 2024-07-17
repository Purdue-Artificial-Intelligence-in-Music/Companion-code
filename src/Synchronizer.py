from AudioPlayer import AudioPlayer
from ScoreFollower import ScoreFollower
from AudioGenerator import AudioGenerator
from simple_pid import PID
from threading import Thread
from midi_ddsp.utils.audio_io import save_wav
import soundfile
import os
import numpy as np
import librosa


def calculate_slope(x, y):
    if len(x) != len(y):
        raise ValueError("The lengths of x and y must be equal.")
    
    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
    
    if denominator == 0:
        raise ValueError("Variance of x is zero, slope cannot be calculated.")
    
    slope = numerator / denominator
    return slope


class Synchronizer(Thread):
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
    def __init__(self, score, source=None, sample_rate=16000, channels=1, frames_per_buffer=1024, window_length=4096, c=10, max_run_count=3, diag_weight=2,
                 Kp=0.2, Ki=0.00, Kd=0.05):
        # Initialize parent class
        super(Synchronizer, self).__init__(daemon=True)

        self.sample_rate = sample_rate
        self.window_length = window_length
        self.c = c

        # Check that musicxml score was provided
        if not (score.endswith('.musicxml') or score.endswith('mid')):
            raise Exception("Error: Synchronizer path must be uncompressed MusicXML score (.musicxml) or MIDI file (.mid)")
        
        # Create an AudioGenerator object
        generator = AudioGenerator(path=score)

        # Get the title of the score
        title = os.path.basename(score)[:-9]

        # Path to soloist audio
        self.output_dir = os.path.join('audio', title)
        soloist_path = os.path.join(self.output_dir, 'track0.wav')
        accompanist_path = os.path.join(self.output_dir, 'track1.wav')

        
        # If the soloist audio does not exist, generate it
        if not (os.path.exists(soloist_path) and os.path.exists(accompanist_path)):

            # If there is a source audio file
            if source is not None:
                # calculate the length of the audio file
                frames, _ = librosa.load(source, mono=True, sr=sample_rate)
                num_frames = frames.shape[-1]
                target_length = num_frames / sample_rate
            else:
                target_length = None
            
            # Synthesize audio from midi file
            generator.generate_audio(output_dir=self.output_dir, target_length=target_length)
            
        # ScoreFollower needs soloist audio
        self.score_follower = ScoreFollower(path=soloist_path,
                                            source=source,
                                            sample_rate=sample_rate,
                                            channels=channels,
                                            frames_per_buffer=frames_per_buffer,
                                            window_length=window_length,
                                            c=c,
                                            max_run_count=max_run_count,
                                            diag_weight=diag_weight)
        
        # AudioPlayer needs accompanist audio
        self.player = AudioPlayer(path=accompanist_path, 
                                  sample_rate=sample_rate,
                                  channels=channels,
                                  frames_per_buffer=frames_per_buffer,
                                  playback_rate=1.0)
        

        ref_audio, _ = librosa.load(soloist_path, sr=sample_rate, mono=True)
        ref_tempo = librosa.beat.tempo(ref_audio, sr=sample_rate)
        print("Reference tempo:", ref_tempo)
        # PID Controller
        self.PID = PID(Kp=Kp, Ki=Ki, Kd=Kd, setpoint=0, starting_output=1.0, 
                       output_limits=(1 / max_run_count, max_run_count), sample_time = window_length / sample_rate)
        # self.PID.output_limits = (1/max_run_count, max_run_count)
        # self.PID.sample_time = window_length / sample_rate
        self.accompaniment_error = []

    def run(self):
        """Start the score follower and audio player. """
        self.score_follower.start()
        self.player.start()

    def stop(self):
        """Stop the score follower and audio player """
        self.score_follower.stop()
        self.player.stop()
        self.score_follower.join()
        self.player.join()

    def update(self):
        """Update the audio player playback rate  """
        ref_index, live_index = self.score_follower.step()

        librosa.beat.tempo(self.score_follower.mic[:, self.score_follower.mic])
        error = self.accompanist_time() - self.predicted_time()
        playback_rate = self.PID(error)
        # if len(self.score_follower.path) >= 5:
            # points = self.score_follower.path[-5:]
            # print(points)
            # ref_indices, live_indices = np.asarray(points).T
            # slope = calculate_slope(x=live_indices, y=ref_indices)
            # print("slope:", slope)
            # slope = max(slope, 0.33)
            # slope = min(slope, 3)
        if live_index > self.c:
            # self.player.index = ref_index * self.score_follower.window_length
            self.player.playback_rate = playback_rate

    def is_active(self):
        """Return True if score follower and audio player are both active. False otherwise. """
        return self.score_follower.is_active() # and self.player.is_active()
    
    def soloist_time(self):
        return self.score_follower.mic.total / self.score_follower.mic.sample_rate

    def predicted_time(self):
        return self.score_follower.otw.j * self.window_length / self.sample_rate
    
    def accompanist_time(self):
        return self.player.index / self.player.sample_rate
    
    def save_performance(self):
        # Get the audio logs
        mic_log = self.score_follower.mic.audio_log
        player_log = self.player.audio_log

        # Trim the audio logs to be the same length
        length = min(mic_log.shape[-1], player_log.shape[-1])
        mic_log = mic_log[:, :length]
        player_log = player_log[:, :length]

        # Normalize and combine logs
        mic_log /= np.max(mic_log)
        player_log /= np.max(player_log)
        audio = mic_log + player_log
        audio = audio.reshape((-1, ))

        # Save performance to wave file
        output_path = os.path.join(self.output_dir, 'performance.wav')
        soundfile.write(output_path, audio, self.sample_rate)
