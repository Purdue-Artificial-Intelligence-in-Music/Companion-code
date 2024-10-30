import unittest
import pandas as pd
import numpy as np
from src.accompaniment_error import load_data, find_nearest, calculate_accompaniment_error

class TestAccompanimentError(unittest.TestCase):
    def setUp(self):
        self.sample_data = {
        'measure': [1, 2, 3, 4],
        'live': [0.52, 1.08, 1.55, 2.10],
        'ref': [0.50, 1.05, 1.50, 2.00],
        'estimated_ref': [0.50, 1.00, 1.50, 2.00],
        'alignment_error': [0.00, -0.05, 0.00, 0.10]
    }
        self.df = pd.DataFrame(self.sample_data)
        self.estimated_times = np.array([0.45, 1.00, 1.50, 2.02])
        self.accompanist_times = np.array([0.46, 1.01, 1.52, 2.05])
        self.final_data = {
        'measure': [1, 2, 3, 4],
        'live': [0.52, 1.08, 1.55, 2.10],
        'ref': [0.50, 1.05, 1.50, 2.00],
        'estimated_ref': [0.50, 1.00, 1.50, 2.00],
        'alignment_error': [0.00, -0.05, 0.00, 0.10],
        'accompaniment': [0.46, 1.01, 1.52, 2.05],
        'accompaniment_error': [-0.04, 0.01, 0.02, 0.05]
    }
        self.final_df = pd.DataFrame(self.final_data)
        self.expected_nearest = [0, 1, 2, 3]
    
    def test_load_data(self):
        expected = pd.DataFrame({'measure':[1, 2, 3, 4, 5], 'ref':[0, 4, 8, 12, 16], 'live':[0, 2.5, 9.12, 12, 16.05]})
        result = load_data('test_tempo.xlsx')
        pd.testing.assert_frame_equal(result, expected)
    
    def test_accompaniment_error(self):
        result = calculate_accompaniment_error(df, self.estimated_times, self.accompanist_times)
        pd.testing.assert_frame_equal(result, self.final_data)
    
    def test_find_nearest(self):
        ref = self.df['estimated_ref'].to_numpy()
        result = find_nearest(ref, self.estimated_times)
        self.assertEqual(result, self.expected_nearest)
