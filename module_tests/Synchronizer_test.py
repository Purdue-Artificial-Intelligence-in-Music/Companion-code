import pytest
import numpy as np
import soundfile
from Synchronizer import Synchronizer
from ScoreFollower import ScoreFollower
from AudioPlayer import AudioPlayer
from simple_pid import PID

#
# TODO: Pretty sure I need actual file paths for reference & accompaniment, those are just dummy paths right now
#

# Test case 1: Initialization of the Synchronizer Object
def test_synchronizer_initialization():
    reference = "path/to/score"
    accompaniment = "path/to/accompaniment"
    synchronizer = Synchronizer(reference, accompaniment)
    
    assert synchronizer.sample_rate == 44100
    assert synchronizer.c == 10
    assert isinstance(synchronizer.score_follower, ScoreFollower)
    assert isinstance(synchronizer.player, AudioPlayer)
    assert isinstance(synchronizer.PID, PID)

# Test case 2: Start Functionality
def test_synchronizer_start(mocker):
    reference = "path/to/score"
    accompaniment = "path/to/accompaniment"
    synchronizer = Synchronizer(reference, accompaniment)
    
    mocker.patch.object(synchronizer.score_follower, 'start')
    mocker.patch.object(synchronizer.player, 'start')
    
    synchronizer.start()
    
    synchronizer.score_follower.start.assert_called_once()
    synchronizer.player.start.assert_called_once()

# Test case 3: Pause and Unpause Functionality
def test_synchronizer_pause_unpause(mocker):
    reference = "path/to/score"
    accompaniment = "path/to/accompaniment"
    synchronizer = Synchronizer(reference, accompaniment)
    
    mocker.patch.object(synchronizer.score_follower, 'pause')
    mocker.patch.object(synchronizer.player, 'pause')
    mocker.patch.object(synchronizer.score_follower, 'unpause')
    mocker.patch.object(synchronizer.player, 'unpause')
    
    synchronizer.pause()
    synchronizer.score_follower.pause.assert_called_once()
    synchronizer.player.pause.assert_called_once()
    
    synchronizer.unpause()
    synchronizer.score_follower.unpause.assert_called_once()
    synchronizer.player.unpause.assert_called_once()

# Test case 4: Stop Functionality
def test_synchronizer_stop(mocker):
    reference = "path/to/score"
    accompaniment = "path/to/accompaniment"
    synchronizer = Synchronizer(reference, accompaniment)
    
    mocker.patch.object(synchronizer.score_follower, 'stop')
    mocker.patch.object(synchronizer.player, 'stop')
    
    synchronizer.stop()
    
    synchronizer.score_follower.stop.assert_called_once()
    synchronizer.player.stop.assert_called_once()

# Test case 5: Update Functionality
def test_synchronizer_update(mocker):
    reference = "path/to/score"
    accompaniment = "path/to/accompaniment"
    synchronizer = Synchronizer(reference, accompaniment)
    
    mocker.patch.object(synchronizer.score_follower, 'step', return_value=5)
    mocker.patch.object(synchronizer, 'accompanist_time', return_value=5.0)
    mocker.patch.object(synchronizer, 'estimated_time', return_value=4.0)
    
    synchronizer.update()
    
    error = synchronizer.accompanist_time() - synchronizer.estimated_time()
    playback_rate = synchronizer.PID(error)
    assert synchronizer.player.playback_rate == playback_rate

# Test case 6: Is Active Functionality
def test_synchronizer_is_active(mocker):
    reference = "path/to/score"
    accompaniment = "path/to/accompaniment"
    synchronizer = Synchronizer(reference, accompaniment)
    
    mocker.patch.object(synchronizer.score_follower, 'is_active', return_value=True)
    mocker.patch.object(synchronizer.player, 'is_active', return_value=True)
    
    assert synchronizer.is_active() is True

    synchronizer.score_follower.is_active.return_value = False
    assert synchronizer.is_active() is False

# Test case 7: Save Performance
def test_save_performance(mocker):
    reference = "path/to/score"
    accompaniment = "path/to/accompaniment"
    synchronizer = Synchronizer(reference, accompaniment)
    
    mock_mic_log = np.random.random((1, 1000))
    mock_player_log = np.random.random((1, 1000))
    
    mocker.patch.object(synchronizer.score_follower.mic, 'get_audio', return_value=mock_mic_log)
    synchronizer.player.output_log = mock_player_log
    mocker.patch('soundfile.write')

    synchronizer.save_performance('path/to/output.wav')
    
    soundfile.write.assert_called_once()
