import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch
import sys
import os

sys.path = [os.path.join(os.path.dirname(os.path.abspath(__file__)), '../src')]

from alignment_error import load_data, calculate_alignment_error

class TestAlignmentFunctions(unittest.TestCase):

    def setUp(self):
        self.sample_data = {
            'measure': range(1, 37),
            'ref': [
                0, 4, 8, 12, 16, 20, 24, 28, 32, 36,
                40, 44, 48, 52, 56, 60, 64, 68, 72, 76,
                80, 84, 88, 92, 96, 100, 104, 108, 112, 116,
                120, 124, 128, 132, 136, 140
            ],
            'live': [
                0, 3.9, 8.15, 12.01, 16, 20.11, 24.05, 28.2, 32.12, 36.08,
                39.75, 43.93, 48.1, 51.95, 56.01, 60.15, 64.04, 67.55, 71.85, 76.1,
                80.21, 84.1, 87.8, 91.68, 95.96, 100.01, 104.05, 108.04, 112.05, 115.7,
                120.01, 124.09, 127.83, 131.94, 135.9, 140.12
            ]
        }
        # we construct this df manually first (to compare with the df load_data sets up from 'alignment.xlsx')
        self.df = pd.DataFrame(self.sample_data)

        # this is taken as mock data from 'alignment.xlsx'; it is actually generated from a time warping algo
        self.warping_path = np.array([
            [0, 0], [4, 3.9], [8, 8.15], [12, 12.01], [16, 16],
            [20, 20.11], [24, 24.05], [28, 28.2], [32, 32.12], [36, 36.08],
            [40, 39.75], [44, 43.93], [48, 48.1], [52, 51.95], [56, 56.01],
            [60, 60.15], [64, 64.04], [68, 67.55], [72, 71.85], [76, 76.1],
            [80, 80.21], [84, 84.1], [88, 87.8], [92, 91.68], [96, 95.96],
            [100, 100.01], [104, 104.05], [108, 108.04], [112, 112.05], [116, 115.7],
            [120, 120.01], [124, 124.09], [128, 127.83], [132, 131.94], [136, 135.9],
            [140, 140.12]
        ])

    @patch('pandas.read_excel')
    def test_load_data(self, mock_read_excel):
        mock_read_excel.return_value = self.df
        result_df = load_data('alignment.xlsx')
        pd.testing.assert_frame_equal(result_df, self.df)

    @patch('pandas.read_excel')
    def test_load_data_missing_columns(self, mock_read_excel):
        missing_column_df = pd.DataFrame({'measure': [1, 2, 3], 'ref': [0, 4, 8]})
        mock_read_excel.return_value = missing_column_df
        with self.assertRaises(ValueError):
            load_data('alignment.xlsx')

    def test_calculate_alignment_error(self):
        result_df = calculate_alignment_error(self.df, self.warping_path)

        # expected results
        exp_estimated_ref = self.warping_path[:, 0]
        ref_numpy = self.df['ref'].to_numpy()
        exp_alignment_error = exp_estimated_ref - ref_numpy

        pd.testing.assert_series_equal(result_df['estimated_ref'], pd.Series(exp_estimated_ref, name='estimated_ref'))
        pd.testing.assert_series_equal(result_df['alignment_error'], pd.Series(exp_alignment_error, name='alignment_error'))

    def test_calculate_alignment_error_empty_df(self):
        # empty dataframe test
        empty_df = pd.DataFrame(columns=['measure', 'ref', 'live'])

        result_empty_df = calculate_alignment_error(empty_df, self.warping_path)

        # result should be an empty dataframe with additional columns; we check below
        self.assertTrue(result_empty_df.empty)
        self.assertTrue(all(col in result_empty_df.columns for col in ['estimated_ref', 'alignment_error']))

if __name__ == '__main__':
    unittest.main()
