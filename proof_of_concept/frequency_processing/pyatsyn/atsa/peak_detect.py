# -*- coding: utf-8 -*-

# This source code is licensed under the BSD-style license found in the
# LICENSE.rst file in the root directory of this source tree. 

# pyatsyn Copyright (c) <2023>, <Johnathan G Lyon>
# All rights reserved.

# Except where otherwise noted, ATSA and ATSH is Copyright (c) <2002-2004>, 
# <Oscar Pablo Di Liscia, Pete Moss, and Juan Pampin>


"""Single-Frame Peak Detection from FFT Data

Functions to process FFT data and extract peaks

"""

from numpy import pi
from math import tau

from pyatsyn.ats_structure import AtsPeak
from pyatsyn.atsa.utils import amp_to_db, db_to_amp


def peak_detection (fftfreqs, fftmags, fftphases, 
                    lowest_bin=None, highest_bin=None, lowest_magnitude=None):
    """Function to detect peaks from FFT data

    This function scans for peaks in FFT frequency data,
    returning found peaks that pass constraint criteria.
    Because FFT data is restricted to discrete bins, interpolation
    is used to provide a more precise estimation of amplitude, phase, and frequency.

    Parameters
    ----------
    fftfreqs : ndarray[float64]
        A 1D array of frequency labels (in Hz) corresponding to `fftmags` and `fftphases`
    fftmags : ndarray[float64]
        A 1D array of FFT magnitudes for each frequency in `fftfreqs`; this is the data where we search for the peaks.
    fftphases : ndarray[float64]
        A 1D array of FFT phases (in radians) for each index in `fftfreqs` and `fftmags`
    lowest_bin : int, optional
        Lower limit bin index used to restrict what bins of `fftfreqs` are searched (default: None)
    highest_bin : int, optional
        Upper limit bin index used to restrict what bins of `fftfreqs` are searched (default: None)
    lowest_magnitude : float, optional
        Minimum amplitude threshold that must be exceeded for a peak to validly detected (default: None)

    Returns
    -------
    list[:obj:`~pyatsyn.ats_structure.AtsPeak`]
        A list of :obj:`~pyatsyn.ats_structure.AtsPeak` constructed from detected peaks
    """
    peaks = []

    N = highest_bin
    if N is None:
        N = fftfreqs.size - 1
    
    first_bin = lowest_bin
    if first_bin is None or first_bin < 1:
        first_bin = 1
    
    frqs = fftfreqs[first_bin-1:N + 1]
    mags = fftmags[first_bin-1:N + 1]
    phs = fftphases[first_bin-1:N + 1]
    fq_scale = frqs[1] - frqs[0]

    for k in range(1, N - first_bin):

        left = mags[k-1]
        center = mags[k]
        right = mags[k+1]

        if center > lowest_magnitude and center > right and center > left:
            pk = AtsPeak()
            offset, pk.amp = parabolic_interp(left, center, right)
            pk.frq = frqs[k] + (fq_scale * offset)
            if (offset > 0):
                pk.pha = phase_correct(phs[k-1], phs[k], offset)
            else:
                pk.pha = phase_correct(phs[k], phs[k+1], offset)
            peaks.append(pk)

    return peaks


def parabolic_interp(alpha, beta, gamma):
    """Function to obtain a parabolically modeled maximum from 3 points    

    Given 3 evenly-spaced points, a parabolic interpolation 
    scheme is used to calculate a coordinate frequency offset
    and maximum amplitude at the estimated parabolic apex.

    Expected: `alpha` <= `beta` <= `gamma`

    Parameters
    ----------
    alpha : float
        Amplitude at lower frequency
    beta : float
        Amplitude at center frequency
    gamma : float
        Amplitude at upper frequency

    Returns
    -------
    offset : float
        Frequency offset (in samples) relative to center frequency bin
    height : float
        Amplitude of estimated parabolic apex
    """
    dB_alpha = amp_to_db(alpha)
    dB_beta = amp_to_db(beta)
    dB_gamma = amp_to_db(gamma)
    dB_alpha_minus_gamma = dB_alpha - dB_gamma
    offset = 0.5 * dB_alpha_minus_gamma / (dB_alpha + dB_gamma + (-2 * dB_beta))
    height = db_to_amp(dB_beta - (0.25 * dB_alpha_minus_gamma * offset))
    return offset, height

def phase_correct(left, right, offset):
    """Function for angular interpolation of phase

    Parameters
    ----------
    left : float
        Phase value (in radians) to interpolate between
    right : float
        Other phase value (in radians) to interpolate between
    offset : float
        Phase offset (in samples) between left and right at which to calculate

    Returns
    -------
    float
        interpolated phase (in radians)
    """
    if left - right > 1.5 * pi:
        return (left + (offset * (right - left + tau)))
    elif right - left > 1.5 * pi:
        return (left + (offset * (right - left - tau)))
    else:
        return (left + (offset * (right - left)))