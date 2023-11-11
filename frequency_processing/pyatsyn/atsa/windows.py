# -*- coding: utf-8 -*-

# This source code is licensed under the BSD-style license found in the
# LICENSE.rst file in the root directory of this source tree. 

# pyatsyn Copyright (c) <2023>, <Johnathan G Lyon>
# All rights reserved.

# Except where otherwise noted, ATSA and ATSH is Copyright (c) <2002-2004>
# <Oscar Pablo Di Liscia, Pete Moss, and Juan Pampin>


"""Functions to Generate FFT Windows

A collection of window utilies to generate several useful window types: 

+---------------------+---------------------+---------------------+
| blackman-exact      | kaiser              | cauchy              |
+---------------------+---------------------+---------------------+
| blackman            | gaussian            | connes              |
+---------------------+---------------------+---------------------+
| blackman-harris-3-1 | poisson             | exponential         |
+---------------------+---------------------+---------------------+
| blackman-harris-3-2 | cauchy              | bartlett            |
+---------------------+---------------------+---------------------+
| blackman-harris-4-1 | connes              | riemann             |
+---------------------+---------------------+---------------------+
| blackman-harris-4-2 | welch               | tukey               |
+---------------------+---------------------+---------------------+
| rectangular         | kaiser              | hamming             |
+---------------------+---------------------+---------------------+
| parzen              | gaussian            | hann                |
+---------------------+---------------------+---------------------+
| welch               | poisson             | hann-poisson        |
+---------------------+---------------------+---------------------+

Most equations are adapted from the following two papers:

F. J. Harris, "On the use of windows for harmonic analysis with the 
discrete Fourier transform," in Proceedings of the IEEE, vol. 66, 
no. 1, pp. 51-83, Jan. 1978.

    `doi: 10.1109/PROC.1978.10837 <https://doi.org/10.1109/PROC.1978.10837>`_.

A. Nuttall, "Some windows with very good sidelobe behavior," in IEEE 
Transactions on Acoustics, Speech, and Signal Processing, vol. 29, 
no. 1, pp. 84-91, February 1981

    `doi: 10.1109/TASSP.1981.1163506 <https://doi.org/10.1109/TASSP.1981.1163506>`_.

Attributes 
----------
VALID_FFT_WINDOW_DEFINITIONS : list[str]
    a list of supported window types
ATS_BLACKMAN_WINDOW_COEFF_LABELS : dict[str : list[float]]
    A dictionary to match blackman window type strings to their coefficients
"""

from numpy import zeros, cos, sin, log, exp, sqrt, absolute, ones, pi
from math import tau

VALID_FFT_WINDOW_DEFINITIONS = [
    'blackman-exact',
    'blackman',
    'blackman-harris-3-1',
    'blackman-harris-3-2',
    'blackman-harris-4-1',
    'blackman-harris-4-2',
    'rectangular',
    'parzen',
    'welch',
    'kaiser',
    'gaussian',
    'poisson',
    'cauchy',
    'connes',
    'welch',
    'kaiser',
    'gaussian',
    'poisson',
    'cauchy',
    'connes',
    'exponential',
    'bartlett',
    'riemann',
    'tukey',
    'hamming',
    'hann',
    'hann-poisson',
]  


# Window coefficients (a0, a1, a2, a3)
ATS_BLACKMAN_WINDOW_COEFF_LABELS = {
    'blackman-exact': [0.42659, -0.49656, 0.07685, 0],              # Exact Blackman (-51 dB)
    'blackman': [0.42, -0.5, 0.08, 0],                              # Blackman (rounded coeffs) (-58 dB)
    'blackman-harris-3-1': [0.42323, -0.49755, 0.07922, 0],         # 3-term Blackman-Harris 1 (-67 dB)
    'blackman-harris-3-2': [0.44959, -0.49364, 0.05677, 0],         # 3-term Blackman-Harris 2 (-61 dB)
    'blackman-harris-4-1': [0.35875, -0.48829, 0.14128, -0.01168],  # 4-term Blackman-Harris 1 (-92 dB)
    'blackman-harris-4-2': [0.40217, -0.49703, 0.09392, -0.00183]   # 4-term Blackman-Harris 2 (-71 dB)
    }


def make_blackman_window(window_type, size):
    """Helper function to build Blackman windows

    Parameters
    ----------
    window_type : str
        the type of blackman window (supported types are defined in :obj:`~pyatsyn.atsa.windows.ATS_BLACKMAN_WINDOW_COEFF_LABELS)`
    size : int
        the size of the window to generate

    Returns
    -------
    ndarray[float]
        a 1D array of floats representing the window
    """
    if window_type not in ATS_BLACKMAN_WINDOW_COEFF_LABELS.keys():
        raise Exception('Specified Blackman Window Type not Defined')

    coeffs =  ATS_BLACKMAN_WINDOW_COEFF_LABELS[window_type]

    two_pi_over_size = tau / size
    a0 = coeffs[0]
    a1 = coeffs[1]
    a2 = coeffs[2]
    a3 = coeffs[3]
    win = zeros(size,'float64')
    for count in range(0,size):
        coeff4 = 0
        if (a3 != 0):
            coeff4 = a3 * cos(3 * two_pi_over_size * count)
        win[count] = a0 + (a1 * cos(two_pi_over_size * count)) + (a2 * cos(2 * two_pi_over_size * count)) + coeff4
    return win
 

def make_fft_window(window_type, size, beta=1.0, alpha=0.5):
    """Function to build the specified window

    Parameters
    ----------
    window_type : str
        the type of window (supported types are defined in :obj:`~pyatsyn.atsa.windows.VALID_FFT_WINDOW_DEFINITIONS`)
    size : int
        the size of the window to generate
    beta : float, optional
        parameter used in certain window calculations (float: 1.0)
    alpha : float, optional
        parameter used in tukey window calculation (float: 0.5)

    Returns
    -------
    ndarray[float]
        a 1D array of floats representing the window

    Raises
    ------
    ValueError
        if `window_type` is not one of the supported window types in :obj:`~pyatsyn.atsa.windows.VALID_FFT_WINDOW_DEFINITIONS`
    """
    if (window_type.startswith('blackman')):
        return make_blackman_window(window_type, size)

    midn = size // 2

    if window_type == 'rectangular':
        return ones(size, dtype="float64")
    elif window_type == 'parzen' or window_type == 'welch' or window_type == 'kaiser' or \
            window_type == 'gaussian' or window_type == 'poisson' or window_type == 'cauchy' \
                or window_type == 'connes':
        window = zeros(size, 'float64')        
        midp1 = (size + 1) // 2
        win_fun = lambda x: 1.0 - abs( (x - midn) / midp1) # parzen
        if window_type == 'welch':
            win_fun = lambda x: 1.0 - pow(((x - midn) / midp1), 2)
        elif window_type == 'kaiser':
            win_fun = lambda x: bes_i0((beta * (sqrt(1.0 - pow((midn - x) / midn, 2))))) / bes_i0(beta)
        elif window_type == 'gaussian':
            win_fun = lambda x: exp( -0.5 * pow((beta * ((midn - x)/ midn)), 2))
        elif window_type == 'poisson':
            win_fun = lambda x: exp( -beta * ((midn - x) / midn))
        elif window_type == 'cauchy':
            win_fun = lambda x: 1.0 / (1.0 + pow(((beta * (midn - x)) / midn), 2))
        elif window_type == 'connes':
            win_fun = lambda x: pow((1.0 - pow( ((x - midn) / midp1), 2)), 2)
        for i in range(0, midn + 1):
            val = win_fun(i)
            window[i] = val
            window[-(i+1)] = val            
        return window
    elif window_type == 'exponential':
        window = zeros(size, 'float64')
        expsum = 1.0
        expn = (1.0 + (log(2) / midn))
        for i in range(0, midn + 1):
            val = expsum - 1.0
            expsum *= expn
            window[i] = val
            window[-(i+1)] = val 
        return window 
    elif window_type == 'bartlett':
        window = zeros(size, 'float64')
        rate = 1.0 / midn
        angle = 0.0
        for i in range(0, midn + 1):
            val = angle
            angle += rate
            window[i] = val
            window[-(i+1)] = val                  
        return window
    elif window_type == 'riemann':
        window = zeros(size, 'float64')
        sr = tau / size
        for i in range(0, midn): 
            val = sin(sr * (midn - i)) / (sr * (midn - i))
            window[i] = val
            window[-(i+1)] = val
        window[midn] = 1                
        return window        
    elif window_type == 'tukey':        
        window = zeros(size, 'float64')
        knee = alpha * size // 2
        for i in range(0, midn + 1):
            if i >= knee:
                val = 1.0
            else:
                val = 0.5 * (1.0 - cos( (pi * i) / knee))
            window[i] = val
            window[-(i+1)] = val            
        return window
    elif window_type == 'hamming' or window_type == 'hann' or window_type == 'hann-poisson':
        window = zeros(size, 'float64')
        freq = tau / size
        angle = 0.0
        win_fun = lambda x: 0.54 - (0.46 * x) # hamming
        if window_type == 'hann':
            win_fun = lambda x: 0.5 - (0.5 * x)
        elif window_type == 'hann-poisson':
            win_fun = lambda x: (0.5 - (0.5 * cx)) * exp( -beta * ((midn - i) / midn))
        for i in range(0, midn + 1):
            cx = cos(angle)
            val = win_fun(cx)
            window[i] = val
            window[-(i+1)] = val 
            angle += freq           
        return window
    else:
        raise ValueError('Specified Window Type not Defined')


def window_norm (window):
    """Function to compute the norm of a window

    :math:`norm = \\frac{1}{\\sum | x |}` where :math:`x` are the window samples

    Parameters
    ----------
    window : ndarray[float]
        the window from which to calculate a norm

    Returns
    -------
    float
        the norm of the window
    """
    norm_factor = absolute(window).sum()
    if norm_factor == 0.0:
        raise Exception('Cannot normalize window with absolute sum of 0.0')
    return 1.0 / norm_factor


def normalize_window(window):
    """Function to normalize a window

    Normalization here means that the window will integrate to 1.0 (i.e., total area of 1)

    Parameters
    ----------
    window : ndarray[float]
        the window to normalize

    Returns
    -------
    ndarray[float]
        a normalized version of the input window
    """
    out_window = zeros(window.size, "float64")
    window_sum = sum(window)
    if window_sum == 0.0:
        out_window = window + (1 / len(window))
    else:
        out_window = window / window_sum
    return out_window


def bes_i0 (x):
    """Modified Bessel Function of the First Kind from "Numerical Recipes in C"

    Parameters
    ----------
    x : float
        Bessel function input

    Returns
    -------
    float
        Bessel function output
    """
    if (abs(x) < 3.75):
        y = pow( (x / 3.75), 2)
        return (1.0 + (y * (3.5156229 + (y * (3.0899414 + \
            (y * (1.2067492 + (y * (0.2659732 + (y * \
            (0.360768e-1 + (y * 0.45813e-2))))))))))))
    else:
        ax = abs(x)
        y = 3.75 / ax
        return ( (exp(ax) / sqrt(ax)) * (0.39894228 + \
            (y * (0.1328592e-1 + (y * (0.225319e-2 + (y * \
            (-0.157565e-2 + (y * (0.916281e-2 + (y * \
            (-0.2057706e-1 + (y * (0.2635537e-1 + (y * \
            (-0.1647633e-1 + (y * 0.392377e-2)))))))))))))))))
