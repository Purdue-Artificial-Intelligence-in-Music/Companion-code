import skfuzzy as fuzz
import skfuzzy.control as ctrl
import soundfile
import numpy as np
from AudioPlayer import AudioPlayer
from ScoreFollower import ScoreFollower

class KalmanFilter:
    def __init__(self, process_variance: float, measurement_variance: float, estimated_error: float, initial_estimate: float):
        self.process_variance = process_variance  # Variance in the process
        self.measurement_variance = measurement_variance  # Variance in the measurement
        self.estimated_error = estimated_error  # Estimation error
        self.current_estimate = initial_estimate  # Current estimate
        self.kalman_gain = 0  # Kalman gain

    def update(self, measurement: float) -> float:
        # Kalman gain calculation
        self.kalman_gain = self.estimated_error / (self.estimated_error + self.measurement_variance)
        # Update the current estimate
        self.current_estimate = self.current_estimate + self.kalman_gain * (measurement - self.current_estimate)
        # Update the estimation error
        self.estimated_error = (1 - self.kalman_gain) * self.estimated_error + abs(self.current_estimate) * self.process_variance
        return self.current_estimate


class FuzzyLogicController:
    """Fuzzy logic controller for adjusting playback rate."""

    def __init__(self):
        # Define fuzzy variables
        self.error = ctrl.Antecedent(np.arange(-1.5, 1.5, 0.01), 'error')  # Extended range for error
        self.playback_rate = ctrl.Consequent(np.arange(0.3, 1.8, 0.01), 'playback_rate')  # Extended range for playback rate

        # Define fuzzy membership functions for error
        self.error['negative_very_large'] = fuzz.trapmf(self.error.universe, [-1.5, -1.5, -1.0, -0.5])
        self.error['negative_large'] = fuzz.trapmf(self.error.universe, [-1.0, -0.5, -0.3, -0.1])
        self.error['negative_small'] = fuzz.trimf(self.error.universe, [-0.3, -0.1, 0])
        self.error['zero'] = fuzz.trimf(self.error.universe, [-0.1, 0, 0.1])
        self.error['positive_small'] = fuzz.trimf(self.error.universe, [0, 0.1, 0.3])
        self.error['positive_large'] = fuzz.trapmf(self.error.universe, [0.1, 0.3, 0.5, 1.0])
        self.error['positive_very_large'] = fuzz.trapmf(self.error.universe, [0.5, 1.0, 1.5, 1.5])

        # Define fuzzy membership functions for playback rate
        self.playback_rate['very_slow'] = fuzz.trapmf(self.playback_rate.universe, [0.3, 0.3, 0.5, 0.7])
        self.playback_rate['slow'] = fuzz.trimf(self.playback_rate.universe, [0.5, 0.7, 1.0])
        self.playback_rate['normal'] = fuzz.trimf(self.playback_rate.universe, [0.8, 1.0, 1.2])
        self.playback_rate['fast'] = fuzz.trimf(self.playback_rate.universe, [1.0, 1.2, 1.5])
        self.playback_rate['very_fast'] = fuzz.trapmf(self.playback_rate.universe, [1.3, 1.5, 1.8, 1.8])

        # Define fuzzy rules
        rule1 = ctrl.Rule(self.error['negative_very_large'], self.playback_rate['very_fast'])
        rule2 = ctrl.Rule(self.error['negative_large'], self.playback_rate['fast'])
        rule3 = ctrl.Rule(self.error['negative_small'], self.playback_rate['normal'])
        rule4 = ctrl.Rule(self.error['zero'], self.playback_rate['normal'])
        rule5 = ctrl.Rule(self.error['positive_small'], self.playback_rate['normal'])
        rule6 = ctrl.Rule(self.error['positive_large'], self.playback_rate['slow'])
        rule7 = ctrl.Rule(self.error['positive_very_large'], self.playback_rate['very_slow'])

        # Create control system
        self.playback_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7])
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
            'negative_very_large': fuzz.interp_membership(self.error.universe, self.error['negative_very_large'].mf, error),
            'negative_large': fuzz.interp_membership(self.error.universe, self.error['negative_large'].mf, error),
            'negative_small': fuzz.interp_membership(self.error.universe, self.error['negative_small'].mf, error),
            'zero': fuzz.interp_membership(self.error.universe, self.error['zero'].mf, error),
            'positive_small': fuzz.interp_membership(self.error.universe, self.error['positive_small'].mf, error),
            'positive_large': fuzz.interp_membership(self.error.universe, self.error['positive_large'].mf, error),
            'positive_very_large': fuzz.interp_membership(self.error.universe, self.error['positive_very_large'].mf, error)
        }

        # Determine which membership has the highest degree
        error_type = max(membership_degrees, key=membership_degrees.get)
        return error_type


class Synchronizer:
    """Synchronize microphone and accompaniment audio using fuzzy logic controller."""

    def __init__(self, reference: str, accompaniment: str, source: str = None, 
                 sample_rate: int = 16000, win_length: int = 4096, hop_length: int = 1024, c: int = 10, max_run_count: int = 3, diag_weight: float = 0.5, **kwargs):
        
        self.sample_rate = sample_rate
        self.c = c

        # ScoreFollower setup to follow soloist
        self.score_follower = ScoreFollower(reference=reference,
                                            source=source,
                                            c=c,
                                            max_run_count=max_run_count,
                                            diag_weight=diag_weight,
                                            sample_rate=sample_rate,
                                            win_length=win_length,
                                            **kwargs)

        # AudioPlayer for accompanist audio
        self.player = AudioPlayer(path=accompaniment, playback_rate=1.0, hop_length=hop_length, sample_rate=sample_rate, **kwargs)

        # Fuzzy Logic Controller for dynamic playback rate adjustment
        self.fuzzy_controller = FuzzyLogicController()

        # Kalman Filter for error smoothing
        self.kalman_filter = KalmanFilter(process_variance=1e-6, measurement_variance=1e-2, estimated_error=1e-1, initial_estimate=0)

        # Time log to keep track of accompanist time
        self.accompanist_time_log = []

    def start(self):
        """Start the score follower and audio player."""
        self.score_follower.start()
        self.player.start()

    def update(self):
        """Update the audio player playback rate dynamically."""
        ref_index = self.score_follower.step()

        if ref_index is None:
            return False

        accompanist_time = self.accompanist_time()
        self.accompanist_time_log.append(accompanist_time)

        # Calculate the timing error between the soloist and accompanist
        raw_error = accompanist_time - self.estimated_time()

        # Smooth the error using Kalman Filter
        smoothed_error = self.kalman_filter.update(raw_error)

        # Adjust playback rate based on fuzzy logic control
        playback_rate = self.fuzzy_controller.get_playback_rate(smoothed_error)
        self.player.playback_rate = playback_rate

        return self.is_active()

    def is_active(self):
        """Check if the score follower and audio player are both active."""
        return self.score_follower.is_active() and self.player.is_active()

    def estimated_time(self):
        """Return the estimated soloist time from the score follower."""
        return self.score_follower.get_estimated_time()

    def accompanist_time(self):
        """Return the current time of the accompanist's playback."""
        return self.player.get_time()
    
    def soloist_time(self):
        """Return the current soloist time from the score follower."""
        return self.score_follower.mic.get_time()
