# -*- coding: utf-8 -*-

# This source code is licensed under the BSD-style license found in the
# LICENSE.rst file in the root directory of this source tree. 

# pyatsyn Copyright (c) <2023>, <Johnathan G Lyon>
# All rights reserved.

# Except where otherwise noted, ATSA and ATSH is Copyright (c) <2002-2004>
# <Oscar Pablo Di Liscia, Pete Moss, and Juan Pampin>

"""Utility Functions for ATS Analysis

Attributes
----------
MAX_DB_SPL : float
    maximum DB_SPL level; used for converting amplitude units
ATS_MIN_SEGMENT_LENGTH : int
    default minimum segment length
ATS_AMP_THRESHOLD : float
    default amp threshold
ATS_NOISE_THRESHOLD : float
    default noise threshold
"""

from numpy import inf, ceil, log2, log10


###################
# UTILITY CONSTANTS
###################

MAX_DB_SPL = 100.0
ATS_MIN_SEGMENT_LENGTH = 3
ATS_AMP_THRESHOLD = -60
ATS_NOISE_THRESHOLD = -120


###################
# UTILITY FUNCTIONS
###################

def db_to_amp(db):
    """Function to convert decibels to amplitude: :math:`10^{dB / 20.0}`

    Parameters
    ----------
    db : float
        a decibel value

    Returns
    -------
    float
        the converted amplitude value
    """
    if (db == -inf):
        return 0.0
    return pow(10, (db / 20.0))


def amp_to_db(amp):
    """Function to convert amplitude to decibels: :math:`20 * \\log_{10}{amp}`

    Parameters
    ----------
    amp : float
        an amplitude value

    Returns
    -------
    float
        the converted decibel value
    """
    return 20 * log10(amp)


def amp_to_db_spl(amp):
    """Function to convert amplitude to decibel sound pressure level (dB SPL)

    Parameters
    ----------
    amp : float
        an amplitude value

    Returns
    -------
    float
        the converted dB SPL value
    """
    return MAX_DB_SPL + amp_to_db(amp)


def next_power_of_2(num):
    """Function to return the closest power of 2 integer more than or equal to an input

    Parameters
    ----------
    num : int
        a positive integer

    Returns
    -------
    int
        the closest power of 2 integer more than or equal to `num`
    """
    return int(2**ceil(log2(num)))


def compute_frames(total_samps, hop):
    """Function to compute the number frames to use in the specified analysis.

    Calculates an extra frame to prevent attenuation during windowing at the tail and to allow 
    for interpolation at the end of the soundfile.

    Parameters
    ----------
    total_samps : int
        number of samples in analyzed sound duration
    hop : int
        interframe distance in samples

    Returns
    -------
    int
        number of frames to use for STFT analysis
    """
    return int(ceil(total_samps / hop)) + 1
        

def optimize_tracks(tracks, analysis_frames, min_segment_length, 
                        amp_threshold, highest_frequency, lowest_frequency):
    """Function to run optimization routines on the established tracks.

    The optimizations performed are:
        * trim short partials
        * calculate and store maximum and average frq and amp
        * prune tracks below amplitude threshold
        * prune tracks outside frequency constraints
        * sort and renumber tracks and peaks in analysis_frames according to average frq    

    NOTE: directly updates analysis_frames, pruning peaks corresponding to pruned tracks.

    Parameters
    ----------
    tracks : Iterable[:obj:`~pyatsyn.ats_structure.AtsSound`]
        collection of established tracks
    analysis_frames : Iterable[Iterable[:obj:`~pyatsyn.ats_structure.AtsPeak`]]
        a collection storing the :obj:`~pyatsyn.ats_structure.AtsPeak` objects at each frame in time
    min_segment_length : int
        minimal size (in frames) of a valid track segment, otherwise it is pruned
    amp_threshold : float
        amplitude threshold used to prune tracks. If None, will default to :obj:`~pyatsyn.atsa.utils.ATS_AMP_THRESHOLD` converted to amplitude.
    highest_frequency : float
        upper frequency threshold, tracks with maxima above this will be pruned
    lowest_frequency : float
        lower frequency threshold, tracks with minima below this will be pruned

    Returns
    -------
    tracks : Iterable[:obj:`pyatsyn.ats_structure.AtsPeak`]
        the optimized subset of input tracks
    """
    if min_segment_length < 1:
        min_segment_length = ATS_MIN_SEGMENT_LENGTH

    # NOTE: amp_threshold is expected in amps
    if amp_threshold == None:
        amp_threshold = db_to_amp(ATS_AMP_THRESHOLD)
    
    tracks_for_removal = set()

    # trim short partials
    for tk in tracks:
        if tk.duration < min_segment_length:
            tracks_for_removal.add(tk.track)
        else:
            # zero amp & frq for averages
            tk.frq = 0.0
            tk.amp = 0.0
    
    # get max & average values (store data on tracks)
    for frame_n in range(len(analysis_frames)):
        for pk in analysis_frames[frame_n]:
            tk_ind = pk.track
            if tk_ind not in tracks_for_removal:
                tk = tracks[tk_ind]
                tk.amp_max = max(tk.amp_max, pk.amp)
                tk.frq_max = max(tk.frq_max, pk.frq)
                tk.frq_min = min(tk.frq_min, pk.frq)
                
                # rolling averages                     
                alpha = 1 / tk.duration
                tk.frq += pk.frq * alpha
                tk.amp += pk.amp * alpha

    # process tracks again for amp & freq thresholds
    for tk in tracks:
        if tk.amp_max < amp_threshold or tk.frq_max > highest_frequency or tk.frq_min < lowest_frequency:
            tracks_for_removal.add(tk.track)
    
    renumbering_tracks = [None] * len(tracks)
    
    # prune invalid tracks        
    tracks = [tk for tk in tracks if tk.track not in tracks_for_removal]
    
    # sort tracks by average freq and build renumbering map and renumber tracks
    tracks.sort(key=lambda tk: tk.frq)
    for ind, tk in enumerate(tracks):
        renumbering_tracks[tk.track] = ind
        tk.track = ind
    
    # renumber and prune peaks
    for frame_n in range(len(analysis_frames)):
        new_frame = []
        for pk in analysis_frames[frame_n]:
            if renumbering_tracks[pk.track] is not None:
                pk.track = renumbering_tracks[pk.track]
                new_frame.append(pk)
        analysis_frames[frame_n] = new_frame
    
    return tracks

