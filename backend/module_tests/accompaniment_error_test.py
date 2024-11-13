import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch
from src.accompaniment_error import load_data, find_nearest, calculate_accompaniment_error

class TestAccompanimentFunctions(unittest.TestCase):
    @patch('pandas.read_csv')
    def test_load_data(self, mock_read_csv):
        # Mock data
        data = {
            'measure': [1, 2, 3, 4],
            'live': [0.52, 1.08, 1.55, 2.10],
            'ref': [0.50, 1.05, 1.50, 2.00]
        }
        mock_read_csv.return_value = pd.DataFrame(data)

        # Load data
        df = load_data('dummy_path.csv')

        # Verify the dataframe
        pd.testing.assert_frame_equal(df, pd.DataFrame(data))

    @patch('pandas.read_csv')
    def test_load_data_missing_columns(self, mock_read_csv):
        # Mock data with missing columns
        data = {
            'measure': [1, 2, 3, 4],
            'live': [0.52, 1.08, 1.55, 2.10]
        }
        mock_read_csv.return_value = pd.DataFrame(data)

        # Verify that ValueError is raised due to missing columns
        with self.assertRaises(ValueError) as context:
            load_data('dummy_path.csv')
        self.assertTrue('Missing one or more required columns' in str(context.exception))

    def test_find_nearest(self):
        # Define short and long arrays
        short_array = np.array([0.5, 1.0, 1.5])
        long_array = np.array([0.4, 0.9, 1.1, 1.4, 1.6])

        # Find nearest indices
        nearest_indices = find_nearest(short_array, long_array)

        # Expected result
        expected_indices = np.array([0, 1, 3])

        # Verify the result
        np.testing.assert_array_equal(nearest_indices, expected_indices)

    def test_calculate_accompaniment_error(self):
        # Mock data for the DataFrame
        data = {
            'measure': [1, 2, 3, 4],
            'live': [0.52, 1.08, 1.55, 2.10],
            'ref': [0.50, 1.05, 1.50, 2.00],
            'estimated_ref': [0.50, 1.00, 1.50, 2.00],
            'alignment_error': [0.00, -0.05, 0.00, 0.10]
        }
        df = pd.DataFrame(data)

        # Define estimated and accompanist times
        estimated_times = np.array([0.45, 1.00, 1.50, 2.02])
        accompanist_times = np.array([0.46, 1.01, 1.52, 2.05])

        # Calculate accompaniment error
        result_df = calculate_accompaniment_error(df, estimated_times, accompanist_times)

        # Expected result
        expected_data = {
            'measure': [1, 2, 3, 4],
            'live': [0.52, 1.08, 1.55, 2.10],
            'ref': [0.50, 1.05, 1.50, 2.00],
            'estimated_ref': [0.50, 1.00, 1.50, 2.00],
            'alignment_error': [0.00, -0.05, 0.00, 0.10],
            'accompaniment': [0.46, 1.01, 1.52, 2.05],
            'accompaniment_error': [-0.04, 0.01, 0.02, 0.05]
        }
        expected_df = pd.DataFrame(expected_data)

        # Verify the result
        pd.testing.assert_frame_equal(result_df, expected_df)

if __name__ == '__main__':
    unittest.main()