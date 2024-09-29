import unittest
from unittest.mock import Mock, patch, MagicMock
from textTesting import classify_command
try:
    from src.VoiceCommandThread.py import VoiceAnalyzerThread
except:
    print("something went wrong with importing")
    exit(1)
import numpy as np

# Test cases for classify_command
class TestClassifyCommand(unittest.TestCase):

    @patch('builtins.input', lambda *args: None)  # Patch input to prevent waiting for user input
    @patch('transformers.pipeline')  # Mock the pipeline to avoid model inference in tests
    def setUp(self, mock_pipeline):
        # Define a mock output for the pipeline to simulate model behavior
        self.mock_classifier = mock_pipeline.return_value
        self.mock_classifier.return_value = {
            'labels': ['The action is: The action involves increasing speed.'],
            'scores': [0.95]
        }

    def test_direct_action_mapping(self):
        # Test direct action phrases
        self.assertEqual(classify_command("too fast"), "slow down")
        self.assertEqual(classify_command("too loud"), "volume down")
        self.assertEqual(classify_command("stop playing"), "stop")
        self.assertEqual(classify_command("go"), "start")
        self.assertEqual(classify_command("halt"), "stop")

    def test_negation_adjustment(self):
        # Test negations handling
        self.assertEqual(classify_command("don't stop"), "start")
        self.assertEqual(classify_command("do not stop"), "start")
        self.assertEqual(classify_command("never go"), "stop")
        self.assertEqual(classify_command("don't listen"), "deafen")

    # def test_extended_buffer(self):
    #     # Test for result when the given prompt extends mutliple commands
    #     # Should return the result that fits the newest command
    #     self.assertEqual(classify_command("go stop too fast go too slow stop go"), "start")

    def test_classifier_fallback(self):
        # Test that it falls back on the classifier when no negation or action phrase is found
        with patch('transformers.pipeline') as mock_pipeline:
            # Mock the classifier's result for an arbitrary input
            mock_pipeline.return_value.return_value = {
                'labels': ['The action is: The action involves increasing speed.'],
                'scores': [0.95]
            }
            self.assertEqual(classify_command("Increase the tempo"), "speed up")

    def test_classifier_multi_label(self):
        # Test multi-label classification case
        with patch('transformers.pipeline') as mock_pipeline:
            # Simulate the output from the multi-label classification
            mock_pipeline.return_value.return_value = {
                'labels': [
                    'The action is: The action involves increasing speed.',
                    'The action is: The action involves increasing volume.'
                ],
                'scores': [0.8, 0.6]
            }
            self.assertEqual(classify_command("Get things moving"), "speed up")

    def test_ambiguous_classification(self):
        # Test ambiguous phrases that might be harder to classify
        with patch('transformers.pipeline') as mock_pipeline:
            mock_pipeline.return_value.return_value = {
                'labels': ['The action is: The action involves decreasing speed.'],
                'scores': [0.9]
            }
            self.assertEqual(classify_command("It's too slow"), "speed up")

    def test_no_special_case(self):
        # Test a phrase that doesn't match any predefined action or negation, triggering the model
        with patch('transformers.pipeline') as mock_pipeline:
            # Mock the classifier's result for fallback
            mock_pipeline.return_value.return_value = {
                'labels': ['The action is: The action involves decreasing speed.'],
                'scores': [0.85]
            }
            self.assertEqual(classify_command("Reduce the speed"), "slow down")

class TestVoiceAnalyzerThread(unittest.TestCase):

    def setUp(self):
        # Mocking AudioBuffer and AudioPlayer classes
        self.mock_buffer = Mock()
        self.mock_player = Mock()

        # Create an instance of the VoiceAnalyzerThread
        self.voice_thread = VoiceAnalyzerThread(name="test_thread", buffer=self.mock_buffer, player=self.mock_player)

    def test_int_or_str_int(self):
        # Testing when input can be converted to an integer
        result = self.voice_thread.int_or_str('123')
        self.assertEqual(result, 123)

    def test_int_or_str_str(self):
        # Testing when input cannot be converted to an integer
        result = self.voice_thread.int_or_str('abc')
        self.assertEqual(result, 'abc')

    @patch('queue.Queue.put')
    def test_callback(self, mock_put):
        # Test if callback puts data in the queue
        indata = np.zeros(100, dtype=np.int16)
        frames = 1024
        time = Mock()
        status = None
        
        # Call the callback method
        self.voice_thread.callback(indata, frames, time, status)

        # Check if the data was put in the queue
        mock_put.assert_called_once_with(bytes(indata))

    @patch('sys.stderr', new_callable=MagicMock)
    @patch('queue.Queue.put')
    def test_callback_with_status(self, mock_put, mock_stderr):
        # Test if callback prints status when it's not None
        indata = np.zeros(100, dtype=np.int16)
        frames = 1024
        time = Mock()
        status = "Some Error Status"
        
        # Call the callback method
        self.voice_thread.callback(indata, frames, time, status)

        # Check if the error status was printed to stderr
        mock_stderr.write.assert_called_once_with("Some Error Status\n")

        # Check if the data was still put in the queue
        mock_put.assert_called_once_with(bytes(indata))

    def test_run_command_deafen(self):
        # Test deafen command which toggles canHear
        initial_can_hear = self.voice_thread.canHear
        
        # Call run_command with 'deafen'
        self.voice_thread.run_command('deafen')
        
        # Check if canHear has been toggled
        self.assertEqual(self.voice_thread.canHear, not initial_can_hear)

    def test_run_command_start(self):
        # Test the start command which unpauses the buffer and player
        self.voice_thread.run_command('start')

        # Ensure that unpause is called on both the buffer and player
        self.mock_buffer.unpause.assert_called_once()
        self.mock_player.unpause.assert_called_once()

    def test_run_command_stop(self):
        # Test the stop command which pauses the buffer and player
        self.voice_thread.run_command('stop')

        # Ensure that pause is called on both the buffer and player
        self.mock_buffer.pause.assert_called_once()
        self.mock_player.pause.assert_called_once()

    def test_run_command_exit(self):
        # Test the exit command which stops the buffer, player and sets stop_request to True
        self.voice_thread.run_command('exit')

        # Ensure that stop is called on both the buffer and player
        self.mock_buffer.stop.assert_called_once()
        self.mock_player.stop.assert_called_once()

        # Check if stop_request is set to True
        self.assertTrue(self.voice_thread.stop_request)

    def test_run_command_speed_up(self):
        # Set initial playback rate for the player
        self.mock_player.playback_rate = 1.0

        # Call run_command with 'speed up'
        self.voice_thread.run_command('speed up')

        # Check if the playback rate has increased by 10%
        self.assertEqual(self.mock_player.playback_rate, 1.1)

    def test_run_command_slow_down(self):
        # Set initial playback rate for the player
        self.mock_player.playback_rate = 1.0

        # Call run_command with 'slow down'
        self.voice_thread.run_command('slow down')

        # Check if the playback rate has decreased by 10%
        self.assertEqual(self.mock_player.playback_rate, 0.9)

    @patch('argparse.ArgumentParser')
    @patch('sounddevice.RawInputStream')
    @patch('vosk.Model')
    @patch('vosk.KaldiRecognizer')
    @patch('json.loads')
    @patch('VoiceAnalyzerThread.classify_command')
    def test_run(self, mock_classify_command, mock_json_loads, mock_KaldiRecognizer, mock_Model, mock_RawInputStream, mock_ArgumentParser):
        # This is a simplified test for the run method. It mocks out various external dependencies.
        mock_parser = mock_ArgumentParser.return_value
        mock_parser.parse_known_args.return_value = (Mock(), [])
        mock_stream = mock_RawInputStream.return_value.__enter__.return_value
        mock_rec = mock_KaldiRecognizer.return_value
        mock_rec.AcceptWaveform.return_value = True
        mock_json_loads.return_value = {"text": "some command"}
        mock_classify_command.return_value = "start"

        # Mock stop request to simulate early termination of the loop
        self.voice_thread.stop_request = True

        # Run the thread's run method
        self.voice_thread.run()

        # Check if classify_command was called with the expected result
        mock_classify_command.assert_called_with("some command")

        # Ensure the command was run (start in this case)
        self.mock_buffer.unpause.assert_called_once()
        self.mock_player.unpause.assert_called_once()

if __name__ == '__main__':
    unittest.main()
