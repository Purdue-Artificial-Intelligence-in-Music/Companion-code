from score_follower import ScoreFollower
from audio_buffer import AudioBuffer
from filterpy.kalman import KalmanFilter
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np

class Synchronizer:
    """Synchronize microphone and accompaniment audio with Kalman filter and fuzzy logic controller"""

    def __init__(self, reference: str, sample_rate: int = 44100, channels: int = 1, 
                 win_length: int = 8192, hop_length: int = 2048, c: int = 10, 
                 max_run_count: int = 3, diag_weight: int = 0.4):

        self.sample_rate = sample_rate
        self.c = c

        # Initialize score follower
        self.score_follower = ScoreFollower(reference=reference,
                                            c=c,
                                            max_run_count=max_run_count,
                                            diag_weight=diag_weight,
                                            sample_rate=sample_rate,
                                            win_length=win_length)

        # Initialize audio buffer
        self.live_buffer = AudioBuffer(max_duration=600,
                                       sample_rate=sample_rate,
                                       channels=channels)

        # Initialize Kalman Filter
        self.kf = KalmanFilter(dim_x=2, dim_z=1)  # 2 states (error, change in error), 1 measurement
        self.kf.x = np.array([[0.], [0.]])  # Initial state
        self.kf.F = np.array([[1., 1.], [0., 1.]])  # State transition matrix
        self.kf.H = np.array([[1., 0.]])  # Measurement function
        self.kf.P *= 1000.  # Covariance matrix
        self.kf.R = 5  # Measurement noise
        self.kf.Q = np.array([[0.1, 0.1], [0.1, 0.1]])  # Process noise

        # Fuzzy controller setup
        error = ctrl.Antecedent(np.arange(-10, 10, 1), 'error')
        playback_rate = ctrl.Consequent(np.arange(0.5, 1.5, 0.1), 'playback_rate')

        error['small'] = fuzz.trimf(error.universe, [-1, 0, 1])
        error['large'] = fuzz.trimf(error.universe, [-10, 0, 10])

        playback_rate['steady'] = fuzz.trimf(playback_rate.universe, [0.9, 1, 1.1])
        playback_rate['increase'] = fuzz.trimf(playback_rate.universe, [1.1, 1.25, 1.5])
        playback_rate['decrease'] = fuzz.trimf(playback_rate.universe, [0.5, 0.75, 0.9])

        # Define rules with modified logic
        rule1 = ctrl.Rule(error['small'], playback_rate['steady'])
        rule2 = ctrl.Rule(error['large'], playback_rate['increase'])
        rule3 = ctrl.Rule(error['large'], playback_rate['decrease'])

        playback_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
        self.playback_sim = ctrl.ControlSystemSimulation(playback_ctrl)

    def step(self, frames, accompanist_time):
        """Step function to update Kalman filter and fuzzy logic playback rate controller"""
        
        self.live_buffer.write(frames)
        estimated_time = self.score_follower.step(frames)
        
        # Kalman filter prediction and update
        self.kf.predict()
        self.kf.update(accompanist_time - estimated_time)

        # Pass error to fuzzy controller
        error = self.kf.x[0][0]  # Estimated error from Kalman filter
        self.playback_sim.input['error'] = error
        self.playback_sim.compute()
        playback_rate = self.playback_sim.output['playback_rate']

        return playback_rate, estimated_time

    def get_live_time(self):
        """Get the timestamp in the live soloist audio"""
        return self.live_buffer.get_time()

    def save_performance(self, path):
        """Save the performance audio"""
        self.live_buffer.save(path)