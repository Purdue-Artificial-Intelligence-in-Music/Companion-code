from .score_follower import ScoreFollower
from .audio_buffer import AudioBuffer
from simple_pid import PID


class Synchronizer:
    """Synchronize microphone and accompaniment audio

    Parameters
    ----------
    reference : str
        Path to reference audio file
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
    sample_rate : int
        Sample rate for reference audio file and live audio
    c : int
        Search width for OTW
    score_follower : ScoreFollower
        ScoreFollower object to perform OTW
    PID : simple_pid.PID
        PID controller to adjust playback rate
    """

    def __init__(
        self,
        reference: str,
        Kp: int = 0.2,
        Ki: int = 0.00,
        Kd=0.0,
        sample_rate: int = 44100,
        channels: int = 1,
        win_length: int = 8192,
        hop_length: int = 2048,
        c: int = 10,
        max_run_count: int = 3,
        diag_weight: int = 0.4,
    ):
        self.sample_rate = sample_rate
        self.c = c

        # Create a score follower to track the soloist
        self.score_follower = ScoreFollower(
            reference=reference,
            c=c,
            max_run_count=max_run_count,
            diag_weight=diag_weight,
            sample_rate=sample_rate,
            win_length=win_length,
        )

        # Create an audio buffer to store the live soloist audio
        self.live_buffer = AudioBuffer(
            max_duration=600, sample_rate=sample_rate, channels=channels
        )

        # PID Controller to adjust playback rate
        self.PID = PID(
            Kp=Kp,
            Ki=Ki,
            Kd=Kd,
            setpoint=0,
            starting_output=1.0,
            output_limits=(1 / max_run_count, max_run_count),
            sample_time=win_length / sample_rate,
        )

    def step(self, frames, accompanist_time):
        """

        Parameters
        ----------
        frames : np.ndarray
            Audio frames from the soloist
        accompanist_time : float
            Time in the accompanist audio

        Returns
        -------
        playback_rate : float
            Playback rate for the accompanist audio
        estimated_time : float
            Estimated time in the soloist audio

        """
        self.live_buffer.write(frames)  # Save the live soloist audio
        estimated_time = self.score_follower.step(
            frames
        )  # Perform OTW on the live soloist audio

        error = accompanist_time - estimated_time
        playback_rate = self.PID(error)

        return playback_rate, estimated_time

    def get_live_time(self):
        """Get the timestamp in the live soloist audio"""
        return self.live_buffer.get_time()

    def save_performance(self, path):
        self.live_buffer.save(path)
