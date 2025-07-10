# import pandas as pd
# import numpy as np


# def load_data(filepath: str) -> pd.DataFrame:
#     """
#     Load data from a CSV file and return a pandas DataFrame.

#     Parameters
#     ----------
#     filepath : str
#         The path to the CSV file.

#     Returns
#     -------
#     pandas.DataFrame
#         A dataframe with columns 'measure', 'live', and 'ref'.

#     Raises
#     ------
#     ValueError
#         If the required columns are not present in the CSV file.
#     """
#     # Load the Excel file into a pandas DataFrame
#     df = pd.read_csv(filepath)

#     # Ensure the required columns are present
#     required_columns = ["measure", "live", "ref"]
#     if not all(col in df.columns for col in required_columns):
#         raise ValueError(f"Missing one or more required columns: {required_columns}")

#     # Return the dataframe with the required columns
#     return df[required_columns]


# def find_nearest(short_array: np.ndarray, long_array: np.ndarray) -> np.ndarray:
#     """
#     Find the indices of the nearest floats in the long_array for each float in the short_array.

#     Parameters
#     ----------
#     short_array : numpy.ndarray
#         The shorter array of floats.
#     long_array : numpy.ndarray
#         The longer array of floats.

#     Returns
#     -------
#     numpy.ndarray
#         An array of indices representing the nearest floats in the `long_array`
#         for each float in the `short_array`.
#     """

#     differences = np.abs(short_array[:, np.newaxis] - long_array)

#     # Find the index of the minimum difference for each value in array1
#     nearest_indices = np.argmin(differences, axis=1)

#     return nearest_indices


# def calculate_accompaniment_error(
#     df: pd.DataFrame, estimated_times: np.ndarray, accompanist_times: np.ndarray
# ) -> pd.DataFrame:
#     """
#     Calculate accompaniment error and update DataFrame with new columns.

#     This function takes a DataFrame with 'measure', 'live', 'ref', 'estimated_ref',
#     and 'alignment_error' columns, and adds two new columns: 'accompaniment' and
#     'accompaniment_error'.

#     Parameters
#     ----------
#     df : pd.DataFrame
#         A DataFrame with at least the following columns:
#         - 'measure': Music measures.
#         - 'live': Time in seconds for each measure in the live recording.
#         - 'ref': Time in seconds for each measure in the reference recording.
#         - 'estimated_ref': Estimated reference times (should match some subset of `estimated_times`).
#         - 'alignment_error': Alignment error calculated as the difference between 'estimated_ref' and 'ref'.

#     estimated_times : np.ndarray
#         A 1D array of time points representing the estimated timing for the accompaniment. These
#         will be filtered to match the 'estimated_ref' column in the DataFrame.

#     accompanist_times : np.ndarray
#         A 1D array of time points representing the actual timing recorded by the accompanist.
#         These are mapped to the corresponding filtered `estimated_times`.

#     Returns
#     -------
#     pd.DataFrame
#         The original DataFrame updated with two new columns:
#         - 'accompaniment': The accompaniment times corresponding to the 'estimated_ref' values.
#         - 'accompaniment_error': The error calculated as the difference between 'estimated_ref' and 'accompaniment'.

#     Examples
#     --------
#     >>> data = {
#     ...     'measure': [1, 2, 3, 4],
#     ...     'live': [0.52, 1.08, 1.55, 2.10],
#     ...     'ref': [0.50, 1.05, 1.50, 2.00],
#     ...     'estimated_ref': [0.50, 1.00, 1.50, 2.00],
#     ...     'alignment_error': [0.00, -0.05, 0.00, 0.10]  # Existing column
#     ... }
#     >>> df = pd.DataFrame(data)
#     >>> estimated_times = np.array([0.45, 1.00, 1.50, 2.02])
#     >>> accompanist_times = np.array([0.46, 1.01, 1.52, 2.05])
#     >>> result = calculate_accompaniment_error(df, estimated_times, accompanist_times)
#     >>> print(result)
#        measure  live   ref  estimated_ref  alignment_error  accompaniment  accompaniment_error
#     0        1  0.52  0.50           0.50             0.00           0.46              -0.04
#     1        2  1.08  1.05           1.00            -0.05           1.01               0.01
#     2        3  1.55  1.50           1.50             0.00           1.52               0.02
#     3        4  2.10  2.00           2.00             0.10           2.05               0.05
#     """

#     ref = df["estimated_ref"].to_numpy()
#     nearest = find_nearest(ref, estimated_times)
#     nearest_acc = accompanist_times[nearest]
#     accompaniment_error = nearest_acc - ref
#     result = df.assign(
#         accompaniment=nearest_acc, accompaniment_error=accompaniment_error
#     )
#     return result


# if __name__ == "__main__":
#     data = {
#         "measure": [1, 2, 3, 4],
#         "live": [0.52, 1.08, 1.55, 2.10],
#         "ref": [0.50, 1.05, 1.50, 2.00],
#         "estimated_ref": [0.50, 1.00, 1.50, 2.00],
#         "alignment_error": [0.00, -0.05, 0.00, 0.10],
#     }
#     test_df = pd.DataFrame(data)
#     test_estimated_times = np.array([0.45, 1.00, 1.50, 2.02])
#     test_accompanist_times = np.array([0.46, 1.01, 1.52, 2.05])
#     test_result = calculate_accompaniment_error(
#         test_df, test_estimated_times, test_accompanist_times
#     )
#     print(test_result)
