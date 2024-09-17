import pandas as pd
import numpy as np


def load_data(filepath: str) -> pd.DataFrame:
    """
    Load data from an Excel spreadsheet and return a pandas DataFrame.

    Parameters
    ----------
    filepath : str
        The path to the Excel spreadsheet.

    Returns
    -------
    pandas.DataFrame
        A dataframe with columns 'measure', 'live', and 'ref'.
    
    Raises
    ------
    ValueError
        If the required columns are not present in the spreadsheet.
    """
    # Load the Excel file into a pandas DataFrame
    df = pd.read_excel(filepath)

    # Ensure the required columns are present
    required_columns = ['measure', 'live', 'ref']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Missing one or more required columns: {required_columns}")

    # Return the dataframe with the required columns
    return df[required_columns]


def find_nearest(short_array: np.ndarray, long_array: np.ndarray) -> np.ndarray:
    """
    Find the indices of the nearest floats in the long_array for each float in the short_array.

    Parameters
    ----------
    short_array : numpy.ndarray
        The shorter array of floats.
    long_array : numpy.ndarray
        The longer array of floats.

    Returns
    -------
    numpy.ndarray
        An array of indices representing the nearest floats in the `long_array` for each float in the `short_array`.
    """

    differences = np.abs(short_array[:, np.newaxis] - long_array)

    # Find the index of the minimum difference for each value in array1
    nearest_indices = np.argmin(differences, axis=1)

    return nearest_indices


def calculate_accompaniment_error(df: pd.DataFrame, estimated_times: np.ndarray, accompanist_times: np.ndarray) -> pd.DataFrame:
    """
    Calculate the accompaniment error between estimated and accompanist times.
    
    This function computes the difference between the estimated times and 
    the accompanist's actual times, returning a DataFrame with the error 
    for each measure.

    Parameters
    ----------
    df : pd.DataFrame
        A DataFrame containing the 'measure', 'live', and 'ref' columns.
    estimated_times : np.ndarray
        A 1D array of time points representing the estimated timing for 
        the accompaniment.
    
    accompanist_times : np.ndarray
        A 1D array of time points representing the actual timing recorded 
        by the accompanist.

    Returns
    -------
    pd.DataFrame
        The original DataFrame with additional columns representing the estimated times, accompanist times, 
        and the calculated error (difference) between the two for each 
        time point.
    
    Raises
    ------
    ValueError
        If the shapes of `estimated_times` and `accompanist_times` do not match.

    Examples
    --------
    >>> data = {
    ...     'measure': [1, 2, 3, 4],
    ...     'live': [0.52, 1.08, 1.55, 2.10],
    ...     'ref': [0.50, 1.05, 1.50, 2.00]
    ... }
    >>> df = pd.DataFrame(data)
    >>> estimated = np.array([0.5, 1.0, 1.5, 2.0])
    >>> actual = np.array([0.45, 1.05, 1.52, 2.02])
    >>> result = calculate_accompaniment_error(df, estimated, actual)
    >>> print(result)
       measure  live   ref  estimated_times  accompanist_times  error
    0        1  0.52  0.50             0.50              0.45  -0.05
    1        2  1.08  1.05             1.00              1.05   0.05
    2        3  1.55  1.50             1.50              1.52   0.02
    3        4  2.10  2.00             2.00              2.02   0.02
    """
