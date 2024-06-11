# -*- coding: utf-8 -*-

# This source code is licensed under the BSD-style license found in the
# LICENSE.rst file in the root directory of this source tree. 

# pyatsyn Copyright (c) <2023>, <Johnathan G Lyon>
# All rights reserved.

# Except where otherwise noted, ATSA and ATSH is Copyright (c) <2002-2004>
# <Oscar Pablo Di Liscia, ,and Juan Pampin>

"""Functions to Compute and Analyze Residual Signals

The reisidual signal is computed by taking the time-domain difference between the orignal sound 
and the sinusoidal synthesis of the spectral trajectories. NOTE: this section is under active research.
Currently, this noise signal is analyzed using the STFT to obtain time-varying energy at 
25 critical bands (see :obj:`~pyatsyn.atsa.critical_bands.ATS_CRITICAL_BAND_EDGES`)

"""

from numpy import zeros, mean, roll, arange, absolute, asarray
from numpy.fft import fft
import soundfile as sf

from pyatsyn.ats_synth import synth

from pyatsyn.atsa.utils import next_power_of_2, db_to_amp, ATS_NOISE_THRESHOLD
from pyatsyn.atsa.critical_bands import ATS_CRITICAL_BAND_EDGES


def compute_residual(   ats_snd, 
                        in_sound,
                        start_sample,
                        end_sample,
                        residual_file = None,
                                ):
    """Function to computes the time domain difference between the sinusoidal synthesis of spectral trajectories in an ats_snd, 
    and the original sound data

    Parameters
    ----------
    
    ats_snd : :obj:`~pyatsyn.ats_structure.AtsSound`
        the input ats object to compute the residual for
    in_sound : ndarray[float]
        the original sound signal from which to extract the residual
    start_sample : int
        sample in `in_sound` where the `ats_snd` begins
    end_sample : int
        sample in `in_sound` where  the `ats_snd` ends
    residual_file : str, optional
        path to audio file to output residual signal to. None if no file output. (Default: None)

    Returns
    -------
    residual : ndarray[float]
        a 1D array of floats containing the amplitudes of the computed residual in the time domain
    """ 
    synthesized = synth(ats_snd)
    residual = in_sound[start_sample:end_sample] - synthesized

    # export residual to audio file
    if residual_file is not None:
        sf.write(residual_file, residual, ats_snd.sampling_rate)

    return residual


def residual_analysis(  residual, 
                        ats_snd, 
                        min_fft_size = 4096,
                        equalize = False,
                        pad_factor = 2,
                        band_edges = None,
                        par_energy = False,
                        verbose = False,                                               
                        ):
    """Function to compute noise energy in a residual signal across 25 critical bands

    Noise energy in each critical band is evaluated in the following way:

    :math:`E[i] = \\frac{1}{K} \\sum^{k_{i0} + K - 1}_{k= k_{i0}} |X(k)|^2`

    where :math:`i` is the band number (0 to 24), :math:`K` is the number of bins
    of the STFT where the band :math:`i` has frequency information. :math:`k_{i0}`
    is the lowest STFT bin where band :math:`i` has information, and :math:`X` is the
    amplitude data for a given bin :math:`k`.

    The algorithm evaluates the noise energy at each step of the Bark scale.

    Parameters
    ----------
    residual : ndarray[float]
        a 1D array of floats containing the amplitudes of the residual signal in the time domain
    ats_snd : :obj:`~pyatsyn.ats_structure.AtsSound`
        the input ats object to store the residual analysis in
    min_fft_size : int, optional
        restricts the minimum size of the FFT window (default: 4096)
    equalize : bool, optional
        equalize noise energy in the frequency domain to the time domain energy using Parseval's Theorem (default: False)
    pad_factor : int, optional
        multiplicative window padding relative to `ats_snd.window_size` for calculating FFT window size (default: 2)
    band_edges : ndarray[float]
        1D array containing 26 frequencies that distinguish the default 25 critical bands. 
        If None, will use :obj:`~pyatsyn.atsa.cricital_bands.ATS_CRITICAL_BAND_EDGES` (default: None)
    par_energy : bool
        whether to transfer noise energy to partials. NOTE: currently not fully supported; only for legacy support (default: False)
    verbose : bool, optional
        increase verbosity (default: False)
    """ 
    hop = ats_snd.frame_size
    M = ats_snd.window_size
    M_over_2 = (M - 1) // 2

    threshold = db_to_amp(ATS_NOISE_THRESHOLD)

    N = residual_N(M, min_fft_size, pad_factor)

    frames = ats_snd.frames
    fft_mag = ats_snd.sampling_rate / N

    # sub band limits
    if band_edges is None:
        band_edges = ATS_CRITICAL_BAND_EDGES
    band_limits = residual_get_band_limits(fft_mag, band_edges)
    n_bands = len(band_limits) - 1
    band_energy = zeros([n_bands,frames],"float64")

    if verbose:
        print(f"Beginning Residual FFT... [frames = {frames}; M = {M}; N = {N}]")
        report_every_x_percent = 10
    report_flag = 0

    fft_mags = None
    t_domain_energy = 0.0
    fil_ptr = -M_over_2

    for frame_n in range(frames):

        if verbose:
            done = frame_n * 100.0 / frames
            if done > report_flag:
                print(f"\t{done:.2f}% complete (residual analysis)")
                report_flag += report_every_x_percent
        
        # padding for window ranges that are out of the input file
        front_pad = 0
        back_pad = 0
        if fil_ptr < 0:
            front_pad = -fil_ptr
        if fil_ptr + M >= residual.size:
            back_pad = fil_ptr + M - residual.size
        
        data = zeros(N, "float64")

        # pull in data
        data[front_pad:M-back_pad] = residual[fil_ptr+front_pad:fil_ptr+M-back_pad]                    
        if equalize:
            # store the time domain energy for equalization
            t_domain_energy = sum(data[front_pad:M-back_pad]**2)
        
        # shift window by half of M so that phases in `data` are relatively accurate to midpoints
        data = roll(data, -M_over_2)
        
        # update file pointer
        fil_ptr += hop

        # DC Block
        data = data - mean(data)

        # FFT
        fd = fft(data)

        fft_mags = absolute(fd) * 2.0

        residual_compute_band_energy(fft_mags, band_limits, band_energy, frame_n)

        if equalize:
            # re-scale frequency band energy to the energy in the time domain                 
            f_domain_energy = sum(band_energy[:,frame_n])
            
            eq_ratio = 1.0
            if f_domain_energy > 0.0:
                eq_ratio = t_domain_energy / f_domain_energy
            band_energy[:,frame_n] *= eq_ratio
            
    # apply noise threshold
    band_energy[band_energy < threshold] = 0.0
    
    # store in ats object
    ats_snd.band_energy = band_energy
    ats_snd.bands = arange(n_bands, dtype='int64')

    if par_energy:
        if verbose:
            print("Transferring noise band energy to partials...")
        band_to_energy(ats_snd, band_edges)
        remove_bands(ats_snd, ATS_NOISE_THRESHOLD)


def residual_N(M, min_fft_size, factor = 2):
    """Function to compute an FFT window size for residual analysis

    Parameters
    ----------
    M : int
        target window size
    min_fft_size : int
        restricts the minimum size of the FFT window 
    factor : int, optional
        multiplicative window padding relative to `M` for calculating FFT window size(default: 2)

    Returns
    -------
    int
        power-of-2 window size
    """ 
    if M * factor > min_fft_size:
        return next_power_of_2(M * factor)
    else:
        return next_power_of_2(min_fft_size)


def residual_get_band_limits(fft_mag, band_edges):
    """Function to convert band edges to FFT bin indices

    Parameters
    ----------
    fft_mag : float
        FFT magic number - sampling rate / FFT window size
    band_edges : ndarray[float]
        1D array of band edge frequencies (in Hz)

    Returns
    -------
    band_limits : ndarray[int]
        1D array of bin indicies mapping band edge frequencies to bins in FFT frequency domain
    """ 
    band_limits = zeros(len(band_edges),"int64")
    for ind, band in enumerate(band_edges):
        band_limits[ind] = band / fft_mag
    return band_limits


def residual_compute_band_energy(fft_mags, band_limits, band_energy, frame_n):
    """Function to compute the band energy

    Energy in each band is evaluated in the following way:

    :math:`E[i] = \\frac{1}{K} \\sum^{k_{i0} + K - 1}_{k= k_{i0}} |X(k)|^2`

    where :math:`i` is the band number (0 to 24), :math:`K` is the number of bins
    of the STFT where the band :math:`i` has frequency information. :math:`k_{i0}`
    is the lowest STFT bin where band :math:`i` has information, and :math:`X` is the
    amplitude data for a given bin :math:`k`.

    NOTE: band_energy is updated directly

    Parameters
    ----------
    fft_mags : ndarray[float]
        1D array of frequency domain amplitudes
    band_limits : ndarray[int]
        1D array of bin indicies mapping band edge frequencies to bins in FFT frequency domain
    band_energy : ndarray[float]
        2D array to store band energies for each band at each frame
    frame_n : int
        the current frame
    """ 
    for band in range(len(band_limits) - 1):
        low = band_limits[band]
        if low < 0:
            low = 0
        high = band_limits[band + 1]
        if high > fft_mags.size // 2:
            high = fft_mags.size // 2

        band_energy[band][frame_n] = sum(fft_mags[low:high]**2) / fft_mags[low:high].size


def band_to_energy(ats_snd, band_edges, use_smr = False):
    """Function to transfer band energies into partials

    NOTE: Currently not fully supported. Included for legacy purposes.

    Parameters
    ----------
    ats_snd : :obj:`~pyatsyn.ats_structure.AtsSound`
        the ats object containing band energies
    band_edges : ndarray[float]
        1D array of band edge frequencies (in Hz)        
    use_smr : bool, optional
        whether to use smr instead of amplitude for scaling energy across partials (default: False)
    """     
    bands = len(ats_snd.bands)
    partials = ats_snd.partials
    frames = ats_snd.frames
    par_energy = zeros([partials,frames],"float64")
    partial_ind = 0

    for frame_n in range(frames):
        for band in range(bands):

            # get frame's partials that are within the subband
            lo_frq = band_edges[band]
            hi_frq = band_edges[band + 1]
            par = []
            while (partial_ind < partials):
                check = ats_snd.frq[partial_ind][frame_n]
                if check < lo_frq:
                    partial_ind += 1
                elif check >= lo_frq and check <= hi_frq:
                    par.append(partial_ind)
                    partial_ind += 1
                else:
                    break
            
            if par and ats_snd.band_energy[band][frame_n] > 0.0:
                
                amp_source = ats_snd.amp
                if use_smr:
                    amp_source = ats_snd.smr

                # get the current energy of the subband
                par_amp_sum = 0.0
                for p_ind in par:
                    par_amp_sum += amp_source[p_ind][frame_n]
                
                if par_amp_sum > 0.0:
                    # if the sub-band is active store band energy proportionally among activate partials
                    for p in par:
                        par_energy[p][frame_n] = amp_source[p][frame_n] * ats_snd.band_energy[band][frame_n] / par_amp_sum
                else:
                    # otherwise spread the energy across the inactive partials
                    energy_per_partial = ats_snd.band_energy[band][frame_n] / len(par)
                    for p in par:
                        par_energy[p][frame_n] = energy_per_partial
        
                # clear energy redistributed to partials from band
                ats_snd.band_energy[band][frame_n] = 0.0

    ats_snd.energy = par_energy
            
            
def remove_bands(ats_snd, threshold):
    """Function to remove bands and band_energies below a threshold

    NOTE: ats_snd is updated directly

    Parameters
    ----------
    ats_snd : :obj:`~pyatsyn.ats_structure.AtsSound`
        the ats object storing band energies to threshold
    threshold : float
        energy threshold used to prune band energies and bands
    """ 
    frames = ats_snd.frames
    threshold = db_to_amp(threshold)
    
    valid_bands = []
    for band in ats_snd.bands:
        if mean(ats_snd.band_energy[band][ats_snd.band_energy[band] > 0.0]) >= threshold:
            valid_bands.append(band)
    
    if valid_bands:
        ats_snd.band_energy = ats_snd.band_energy[valid_bands,:]
        ats_snd.bands = asarray(valid_bands, 'int64')
    else:
        ats_snd.band_energy = []
        ats_snd.bands = []