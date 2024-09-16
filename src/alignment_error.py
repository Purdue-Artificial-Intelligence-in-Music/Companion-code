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
    """

    pass


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

    pass


def calculate_alignment_error(df: pd.DataFrame, warping_path: np.ndarray) -> pd.DataFrame:
    """
    Add estimated_ref and alignment_error columns to a pandas DataFrame.

    This function takes in a DataFrame with columns 'measure', 'live', and 'ref', 
    and returns a DataFrame with two additional columns: 'estimated_ref' and 'alignment_error'.

    Parameters
    ----------
    df : string
        Pandas DataFrame with columns 'measure', 'live', and 'ref'.
        Each row represents a measure in music, 'live' and 'ref' are the times in seconds when the measure starts
        in the live recording and reference recording, respectively.
    warping_path : numpy.ndarray
        The warping path calculated by the OTW algorithm. 
        It is a 2D array with shape (n, 2), where n is the number of points in the warping path. 
        The first column represents the estimated time in the reference recording. 
        The second column represents the time in the live recording.
        n is greater than the number of measures in the DataFrame.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with two additional columns:
        - 'estimated_ref': The estimated reference values for each measure based on the warping path.
        - 'alignment_error': The alignment error calculated based on the difference between 'estimated_ref' and 'ref' columns.
    """

    # Convert the live and ref columns of the DataFrame to numpy arrays
    # Convert the columns of the warping_path to numpy arrays: estimated_ref_times, live_times
    # For each live time in the warping path, find the nearest live time from the DataFrame and get its index
    # Create an array of these indices
    # Create an array estimated_ref_tmes[indices] to get the estimated reference times for each measure
    # Calculate the alignment error as the difference between the estimated reference times and the reference times
    # Add the estimated_ref and alignment_error columns to the DataFrame