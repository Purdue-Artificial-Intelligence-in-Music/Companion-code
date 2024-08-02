def play_mic_data(self, mic_data, wav_data):
    """

    Parameters
    ----------
    mic_data : np.ndarray
        Array with shape (channels, num frames) containing microphone audio
        
    wav_data :
        Array with shape (channels, num_frames) containing WAV audio

    Returns
    -------
    np.ndarray
        Microphone audio
    """
    return mic_data

def play_wav_data(self, mic_data, wav_data):
    """

    Parameters
    ----------
    mic_data : np.ndarray
        Array with shape (channels, num frames) containing microphone audio
        
    wav_data :
        Array with shape (channels, num_frames) containing WAV audio

    Returns
    -------
    np.ndarray
        WAV audio
    """
    return wav_data

def play_all(self, mic_data, wav_data):
    """

    Parameters
    ----------
    mic_data : np.ndarray
        Array with shape (channels, num frames) containing microphone audio
        
    wav_data :
        Array with shape (channels, num_frames) containing WAV audio

    Returns
    -------
    np.ndarray
        Microphone and WAV audio
    """
    return mic_data + wav_data
