import unittest
from unittest.mock import patch

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

    def test_extended_buffer(self):
        # Test for result when the given prompt extends mutliple commands
        # Should return the result that fits the newest command
        self.assertEqual(classify_command("go stop too fast go too slow stop go"), "start")

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

if __name__ == '__main__':
    unittest.main()
