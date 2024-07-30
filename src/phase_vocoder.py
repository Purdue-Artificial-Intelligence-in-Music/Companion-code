import numpy as np
from typing import Any, Callable, Optional, Tuple, List, Union, overload
from typing_extensions import Literal
from librosa.core import convert
from librosa import util


def phase_vocoder(
    D: np.ndarray,
    *,
    rate: float,
    hop_length: Optional[int] = None,
    n_fft: Optional[int] = None,
) -> np.ndarray:
    """Phase vocoder.  Given an STFT matrix D, speed up by a factor of ``rate``

    Based on the implementation provided by [#]_.

    This is a simplified implementation, intended primarily for
    reference and pedagogical purposes.  It makes no attempt to
    handle transients, and is likely to produce many audible
    artifacts.  For a higher quality implementation, we recommend
    the RubberBand library [#]_ and its Python wrapper `pyrubberband`.

    .. [#] Ellis, D. P. W. "A phase vocoder in Matlab."
        Columbia University, 2002.
        https://www.ee.columbia.edu/~dpwe/resources/matlab/pvoc/

    .. [#] https://breakfastquay.com/rubberband/

    Examples
    --------
    >>> # Play at double speed
    >>> y, sr   = librosa.load(librosa.ex('trumpet'))
    >>> D       = librosa.stft(y, n_fft=2048, hop_length=512)
    >>> D_fast  = librosa.phase_vocoder(D, rate=2.0, hop_length=512)
    >>> y_fast  = librosa.istft(D_fast, hop_length=512)

    >>> # Or play at 1/3 speed
    >>> y, sr   = librosa.load(librosa.ex('trumpet'))
    >>> D       = librosa.stft(y, n_fft=2048, hop_length=512)
    >>> D_slow  = librosa.phase_vocoder(D, rate=1./3, hop_length=512)
    >>> y_slow  = librosa.istft(D_slow, hop_length=512)

    Parameters
    ----------
    D : np.ndarray [shape=(..., d, t), dtype=complex]
        STFT matrix

    rate : float > 0 [scalar]
        Speed-up factor: ``rate > 1`` is faster, ``rate < 1`` is slower.

    hop_length : int > 0 [scalar] or None
        The number of samples between successive columns of ``D``.

        If None, defaults to ``n_fft//4 = (D.shape[0]-1)//2``

    n_fft : int > 0 or None
        The number of samples per frame in D.
        By default (None), this will be inferred from the shape of D.
        However, if D was constructed using an odd-length window, the correct
        frame length can be specified here.

    Returns
    -------
    D_stretched : np.ndarray [shape=(..., d, t / rate), dtype=complex]
        time-stretched STFT

    See Also
    --------
    pyrubberband
    """
    if n_fft is None:
        n_fft = 2 * (D.shape[-2] - 1)

    if hop_length is None:
        hop_length = int(n_fft // 4)

    time_steps = np.arange(0, D.shape[-1], rate, dtype=np.float64)

    # Create an empty output array
    shape = list(D.shape)
    shape[-1] = len(time_steps)
    d_stretch = np.zeros_like(D, shape=shape)

    # Expected phase advance in each bin per frame
    phi_advance = hop_length * convert.fft_frequencies(sr=2 * np.pi, n_fft=n_fft)

    # Phase accumulator; initialize to the first sample
    phase_acc = np.angle(D[..., 0])

    # Pad 0 columns to simplify boundary logic
    padding = [(0, 0) for _ in D.shape]
    padding[-1] = (0, 2)
    D = np.pad(D, padding, mode="constant")

    for t, step in enumerate(time_steps):
        columns = D[..., int(step) : int(step + 2)]

        # Weighting for linear magnitude interpolation
        alpha = np.mod(step, 1.0)
        mag = (1.0 - alpha) * np.abs(columns[..., 0]) + alpha * np.abs(columns[..., 1])

        # Store to output array
        d_stretch[..., t] = util.phasor(phase_acc, mag=mag)

        # Compute phase advance
        dphase = np.angle(columns[..., 1]) - np.angle(columns[..., 0]) - phi_advance

        # Wrap to -pi:pi range
        dphase = dphase - 2.0 * np.pi * np.round(dphase / (2.0 * np.pi))

        # Accumulate phase
        phase_acc += phi_advance + dphase

    return d_stretch