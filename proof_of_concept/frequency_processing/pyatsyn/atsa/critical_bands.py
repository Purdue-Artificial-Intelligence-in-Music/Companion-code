# -*- coding: utf-8 -*-

# This source code is licensed under the BSD-style license found in the
# LICENSE.rst file in the root directory of this source tree. 

# pyatsyn Copyright (c) <2023>, <Johnathan G Lyon>
# All rights reserved.

# Except where otherwise noted, ATSA and ATSH is Copyright (c) <2002-2004>, 
# <Oscar Pablo Di Liscia, Pete Moss, and Juan Pampin>


"""Critical Bands and Signal-to-Mask Ratio Evaluation

This module is used to evaluate critical band masking for signal-to-mask ratio calculations

Attributes
----------
ATS_CRITICAL_BAND_EDGES : ndarray[float]
    1D array containing 26 frequencies that distinguish the default 25 critical bands
"""

from numpy import log10, array

from pyatsyn.atsa.utils import amp_to_db_spl


ATS_CRITICAL_BAND_EDGES = array([0.0,100.0,200.0,300.0, 400.0,
                                510.0, 630.0, 770.0, 920.0, 1080.0,
                                1270.0, 1480.0, 1720.0, 2000.0, 2320.0, 
                                2700.0, 3150.0, 3700.0, 4400.0, 5300.0, 
                                6400.0, 7700.0, 9500.0, 12000.0, 15500.0, 
                                20000.0], dtype="float64")


def evaluate_smr(peaks, slope_l = -27.0, delta_db = -50):    
    """Function to evaluate signal-to-mask ratio for the given peaks

    This function evaluates masking values (SMR) for :obj:`~pyatsyn.ats_structure.AtsPeak` in list `peaks`
    Iteratively the parameters will be use to generate a triangular mask 
    with a primary vertex at the frequency of, and at delta_dB below the amplitude 
    of the masker. 
    
    .. image:: _static/img/smr.png
        :width: 350
        :alt: graphic depiction of smr calculation

    All other peaks are evaluated based on the triangular
    edges descending from the primary vertex according to slope_l for lower 
    frequencies, and a calculated slope for higher frequencies. Maskee amplitudes
    proportions above this edge are then assigned to the maskee peak's smr property.
    By the end of the iteration, the largest smr seen as maskee is kept in the peak's
    smr property.

    Parameters
    ----------
    peaks : Iterable[:obj:`~pyatsyn.ats_structure.AtsPeak`]
        An iterable collection of AtsPeaks that will have their `smr` attributes updated
    slope_l : float, optional
        A float (in dB/bark) to dictate the slope of the left side of the mask (default: -27.0)
    delta_db : float, optional
        A float (in dB) that sets the amplitude threshold for the masking curves
        Must be (<= 0dB) (default: -50)

    Raises
    ------
    ValueError
        If `delta_db` is not less than or equal to 0.
    """
    if delta_db > 0:
        raise ValueError("delta_db must be <= 0")

    n_peaks = len(peaks)
    if n_peaks == 1:
        peaks[0].smr = amp_to_db_spl(peaks[0].amp)    
    else:
        for p in peaks:
            p.barkfrq = frq_to_bark(p.frq)
            p.db_spl = amp_to_db_spl(p.amp)
            p.slope_r = compute_slope_r(p.db_spl, slope_l)        

        for maskee_ind, maskee in enumerate(peaks):

            for masker_ind in [ i for i in range(n_peaks) if i != maskee_ind]:
                masker = peaks[masker_ind]                
                
                mask_term = masker.db_spl + delta_db + (masker.slope_r * abs(maskee.barkfrq - masker.barkfrq))
                if mask_term > maskee.smr:
                    maskee.smr = mask_term

            maskee.smr = maskee.db_spl - maskee.smr


def frq_to_bark(freq):
    """Function to convert frequency from Hz to bark scale

    This function will convert frequency from Hz to bark scale, a psychoacoustical scale used 
    for subjective measurements of loudness.

    Parameters
    ----------
    freq : float
        A frequency (in Hz) to convert to bark scale

    Returns
    -------
    float
        the frequency in bark scale 

    """
    if freq <= 0.0:
        return 0.0
    elif freq <= 400.0:
        return freq * 0.01
    elif freq >= 20000.0:
        return None
    else:
        band = find_band(freq)
        low = ATS_CRITICAL_BAND_EDGES[band]
        high = ATS_CRITICAL_BAND_EDGES[band+1]
        return 1 + band + abs(log10(freq/low) / log10(low/high))


def find_band(freq):
    """Function to retrieve lower band edge in :obj:`~pyatsyn.atsa.critical_bands.ATS_CRITICAL_BAND_EDGES`

    Parameters
    ----------
    freq : float
        A frequency (in Hz) to find the related band in :obj:`~pyatsyn.atsa.critical_bands.ATS_CRITICAL_BAND_EDGES` for
    
    Returns
    ----------
    int
        index into :obj:`~pyatsyn.atsa.critical_bands.ATS_CRITICAL_BAND_EDGES` that marks the lower band edge for the given freq

    Raises
    ----------
    LookupError
        if the frequency given is outside the range of the lowest or highest edge in :obj:`~pyatsyn.atsa.critical_bands.ATS_CRITICAL_BAND_EDGES`

    """
    if freq < ATS_CRITICAL_BAND_EDGES[0]:
        raise LookupError("Frequency is below range of ATS_CRITICAL_BAND_EDGES")
    if freq > ATS_CRITICAL_BAND_EDGES[-1]:
        raise LookupError("Frequency is above range of ATS_CRITICAL_BAND_EDGES")

    for ind in range(len(ATS_CRITICAL_BAND_EDGES)-2,0,-1):
        if freq > ATS_CRITICAL_BAND_EDGES[ind]:
            return ind
    return 0


def compute_slope_r(masker_amp_db, slope_l = -27.0):
    """Function to compute right slope of triangular mask

    Computes the right slope of mask, dependent on the level of the masker

    Parameters
    ----------
    masker_amp_db : float
        Amplitude (in dB) of the masker peak

    slope_l : float, optional
        slope (in dB / bark) of the lower frequency side of the masking triangle

    """
    return slope_l + (max(masker_amp_db - 40.0, 0.0) * 0.37)