import numpy as np
from synchronizer import Synchronizer
from score_follower import ScoreFollower
from simple_pid import PID

#
# TODO: Pretty sure I need actual file paths for reference & accompaniment, those are just dummy paths right now
#

# Test case 1: Initialization of the Synchronizer Object
def test_synchronizer_initialization():
    reference = "path/to/score"
    synchronizer = Synchronizer(reference)
    
    assert synchronizer.sample_rate == 44100
    assert synchronizer.c == 10
    assert isinstance(synchronizer.score_follower, ScoreFollower)
    assert isinstance(synchronizer.PID, PID)

# Test case 2: Step Functionality
def test_synchronizer_step(mocker):
    reference = "path/to/score"
    synchronizer = Synchronizer(reference)
    frames = np.random.random((1, 8192))
    soloist_time = 8192/44100
    accompanist_time = 8192/44100

    # Ensure that score_follower.step returns the correct soloist_time
    mocker.patch.object(synchronizer.score_follower, 'step', return_value=soloist_time)
    
    # Spy on the live_buffer.write method
    spy_live_buffer_write = mocker.spy(synchronizer.live_buffer, 'write')

    playback_rate, estimated_time = synchronizer.step(frames, accompanist_time)

    # Assert that live_buffer.write was called with correct arguments
    spy_live_buffer_write.assert_called_once_with(frames)

    assert playback_rate == 1.0
    assert estimated_time == soloist_time

# Test case 3: Save Performance
def test_save_performance(mocker):
    # Mock the reference path to avoid file dependency
    reference = "path/to/score"
    synchronizer = Synchronizer(reference)

    # Mock any internal dependencies that rely on the reference being correct
    mocker.patch.object(synchronizer, 'score_follower')  # Assuming score_follower depends on the reference path
    # mocker.patch.object(synchronizer, 'live_buffer')  # Mock live_buffer in case it interacts with the reference

    # Spy on the live_buffer.save method
    spy_live_buffer_save = mocker.spy(synchronizer.live_buffer, 'save')

    # Call the method under test
    path = "path/to/save"
    synchronizer.save_performance(path)

    # Assert that live_buffer.save was called with the correct arguments
    spy_live_buffer_save.assert_called_once_with(path)

