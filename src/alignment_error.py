import pandas as pd
import numpy as np


def load_data(filepath: str) -> pd.DataFrame:
    """
    Load data from a csv file and return a pandas DataFrame.

    Parameters
    ----------
    filepath : str
        The path to the csv file.

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
    df = pd.read_csv(filepath)

    # Ensure the required columns are present
    required_columns = ['measure', 'live', 'ref']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Missing one or more required columns: {required_columns}")

    # Return the dataframe with the required columns
    return df[required_columns]


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

    # I convert the live and ref columns of the passed dataframe to numpy arrays
    live_times = df['live'].to_numpy()
    ref_times = df['ref'].to_numpy()

    # Below, we convert the columns from the 2D warping_path array to 1D numpy arrays
    estimated_ref_times = warping_path[:, 0]
    live_times_from_warping = warping_path[:, 1]

    closest_indices = []

    # In the loop below, we find the closest indices in the warping path for each live time in the given dataframe
    for time in live_times:
        difference = np.abs(live_times_from_warping - time)
        closest_index = np.argmin(difference)
        closest_indices.append(closest_index)

    estimated_ref = estimated_ref_times[closest_indices]

    alignment_error = estimated_ref - ref_times

    df['estimated_ref'] = estimated_ref
    df['alignment_error'] = alignment_error

    return df
