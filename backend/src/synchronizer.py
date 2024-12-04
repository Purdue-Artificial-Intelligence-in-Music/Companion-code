import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl
from .score_follower import ScoreFollower
from .audio_buffer import AudioBuffer
from filterpy.kalman import KalmanFilter


class FuzzyLogicController:
    """Fuzzy logic controller for adjusting playback rate."""

    def __init__(self):
        # Define fuzzy variables
        self.error = ctrl.Antecedent(np.arange(-1.5, 1.5, 0.01), 'error')
        self.playback_rate = ctrl.Consequent(np.arange(0.3, 1.8, 0.01), 'playback_rate')

        # Define fuzzy membership functions for error
        self.error['negative_large'] = fuzz.trapmf(self.error.universe, [-1.5, -1.5, -0.7, -0.3])
        self.error['negative_small'] = fuzz.trimf(self.error.universe, [-0.5, -0.1, 0])
        self.error['zero'] = fuzz.trimf(self.error.universe, [-0.1, 0, 0.1])
        self.error['positive_small'] = fuzz.trimf(self.error.universe, [0, 0.1, 0.5])
        self.error['positive_large'] = fuzz.trapmf(self.error.universe, [0.3, 0.7, 1.5, 1.5])

        # Define fuzzy membership functions for playback rate
        self.playback_rate['very_slow'] = fuzz.trapmf(self.playback_rate.universe, [0.3, 0.3, 0.5, 0.7])
        self.playback_rate['slow'] = fuzz.trimf(self.playback_rate.universe, [0.5, 0.7, 1.0])
        self.playback_rate['normal'] = fuzz.trimf(self.playback_rate.universe, [0.8, 1.0, 1.2])
        self.playback_rate['fast'] = fuzz.trimf(self.playback_rate.universe, [1.0, 1.2, 1.5])
        self.playback_rate['very_fast'] = fuzz.trapmf(self.playback_rate.universe, [1.3, 1.5, 1.8, 1.8])

        # Define fuzzy rules
        rule1 = ctrl.Rule(self.error['negative_large'], self.playback_rate['very_fast'])
        rule2 = ctrl.Rule(self.error['negative_small'], self.playback_rate['fast'])
        rule3 = ctrl.Rule(self.error['zero'], self.playback_rate['normal'])
        rule4 = ctrl.Rule(self.error['positive_small'], self.playback_rate['slow'])
        rule5 = ctrl.Rule(self.error['positive_large'], self.playback_rate['very_slow'])

        # Create control system
        self.playback_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
        self.playback = ctrl.ControlSystemSimulation(self.playback_ctrl)

    def get_playback_rate(self, error):
        """Compute the playback rate based on fuzzy logic."""
        
        self.playback.input['error'] = error
        self.playback.compute()
        return self.playback.output['playback_rate']
    
    def print_error_membership(self, error):
        """Return the type of error based on its fuzzy membership."""

        # Calculate the membership degrees for each fuzzy set
        membership_degrees = {
            'negative_large': fuzz.interp_membership(self.error.universe, self.error['negative_large'].mf, error),
            'negative_small': fuzz.interp_membership(self.error.universe, self.error['negative_small'].mf, error),
            'zero': fuzz.interp_membership(self.error.universe, self.error['zero'].mf, error),
            'positive_small': fuzz.interp_membership(self.error.universe, self.error['positive_small'].mf, error),
            'positive_large': fuzz.interp_membership(self.error.universe, self.error['positive_large'].mf, error),
        }

        # Determine which membership has the highest degree
        error_type = max(membership_degrees, key=membership_degrees.get)
        return error_type


class Synchronizer:
    """Synchronize microphone and accompaniment audio with Kalman filter and fuzzy logic controller."""

    def __init__(self, reference: str, sample_rate: int = 44100, channels: int = 1,
                 win_length: int = 8192, hop_length: int = 2048, c: int = 10,
                 max_run_count: int = 3, diag_weight: int = 0.4):
        self.sample_rate = sample_rate
        self.c = c

        # Initialize score follower
        self.score_follower = ScoreFollower(
            reference=reference,
            c=c,
            max_run_count=max_run_count,
            diag_weight=diag_weight,
            sample_rate=sample_rate,
            win_length=win_length
        )

        # Initialize audio buffer
        self.live_buffer = AudioBuffer(
            max_duration=600,
            sample_rate=sample_rate,
            channels=channels
        )

        self.kf = KalmanFilter(dim_x=3, dim_z=1)

        # Initial state
        self.kf.x = np.array([0., 0., 0.])  # [position, velocity, acceleration]

        # State transition matrix (F)
        dt = 1  # Time step
        self.kf.F = np.array([[1., dt, 0.5 * dt**2],
                              [0., 1., dt],
                              [0., 0., 1.]])

        # Measurement matrix (H) - measuring position only
        self.kf.H = np.array([[1., 0., 0.]])

        # Covariance matrix (P)
        self.kf.P = np.diag([10, 1, 0.5])  # Higher uncertainty for position

        # Measurement noise covariance (R)
        self.kf.R = 0.5  # Adjust based on measurement noise variance

        # Process noise covariance (Q)
        self.kf.Q = np.array([[0.01, 0., 0.],
                              [0., 0.01, 0.],
                              [0., 0., 0.01]])  # Reduced process noise

        self.fuzzy_controller = FuzzyLogicController()

    def step(self, frames, accompanist_time):
        """Step function to update Kalman filter and fuzzy logic playback rate controller."""
        self.live_buffer.write(frames)
        estimated_time = self.score_follower.step(frames)
        raw_error = accompanist_time - estimated_time

        self.kf.predict()
        self.kf.update([raw_error])
        smoothed_error = self.kf.x[0]

        playback_rate = self.fuzzy_controller.get_playback_rate(smoothed_error)
        playback_rate = max(0.3, min(1.8, playback_rate))  # Clamp playback rate for keeping playback rate within 0.3 and 1.8

        return playback_rate, estimated_time

    def get_live_time(self):
        """Get the timestamp in the live soloist audio."""
        return self.live_buffer.get_time()

    def save_performance(self, path):
        """Save the performance audio."""
        self.live_buffer.save(path)
