# -*- coding: utf-8 -*-

# This source code is licensed under the BSD-style license found in the
# LICENSE.rst file in the root directory of this source tree. 

# pyatsyn Copyright (c) <2023>, <Johnathan G Lyon>
# All rights reserved.

# Except where otherwise noted, ATSA and ATSH is Copyright (c) <2002-2004>
# <Oscar Pablo Di Liscia, Pete Moss, and Juan Pampin>


"""Synthesizer Methods for Rendering .ats Files to Audio

"""

from numpy import zeros, matmul, arange, cos, linspace, cumsum, sin, pi, real
from numpy.fft import fft, ifft
from numpy.random import uniform
import soundfile as sf
from math import tau
import argparse

from pyatsyn.atsa.critical_bands import ATS_CRITICAL_BAND_EDGES
from pyatsyn.atsa.utils import compute_frames
from pyatsyn.ats_io import ats_load


def synth(ats_snd, normalize=False, compute_phase=True, 
            export_file=None, sine_pct = 1.0, noise_pct = 0.0, noise_bands = None, 
            normalize_sine = False, normalize_noise = False):    
    """Function to synthesize audio from :obj:`~pyatsyn.ats_structure.AtsSound`

    Sine generator bank and band-limited noise synthesizer for .ats files. When
    phase information is ignored phase is linearly interpolated between consecutive
    frequencies from an initial phase of 0.0 at the first non-zero amplitude for that partial.
    
    The method for cubic polynomial interpolation of phase used is credited to:

        MR. McAulay and T. Quatieri, "Speech analysis/Synthesis based on a 
        sinusoidal representation," in IEEE Transactions on Acoustics, 
        Speech, and Signal Processing, vol. 34, no. 4, pp. 744-754, 
        August 1986
        
        `doi: 10.1109/TASSP.1986.1164910 <https://doi.org/10.1109/TASSP.1986.1164910>`_.

    Parameters
    ----------
    ats_snd : :obj:`~pyatsyn.ats_structure.AtsSound`
        the .ats file used to synthesize
    normalize : bool, optional
        normalize sound to ±1 before output (default: False)
    compute_phase : bool, optional
        use cubic polynomial interpolation of phase information during synthesis, if available (default: True)
    export_file : str
        audio file path to write synthesis to, or None for no file output (default: None)
    sine_pct : float
        percentage of sine components to mix into output (default: 1.0)
    noise_pct : float
        percentage of noise components to mix into output (default: 0.0)
    noise_bands : ndarray[float]
        1D array of band edges to use for noise analysis. Currently using other than 25 bands 
        (i.e. 26 edges) is not fully supported. If None, 
        :obj:`~pyatsyn.atsa.critical_bands.ATS_CRITICAL_BAND_EDGES` will be used. (default: None)
    normalize_sine : bool
        normalize sine components to ±1 before mixing (default: False)
    normalize_noise : bool
        normalize noise componenets to ±1 before mixing (default: False)

    Returns
    -------
    ndarray[float]
        A 1D array of amplitudes representing the synthesized sound
    """
    sample_rate = ats_snd.sampling_rate
    out_size = int(ats_snd.dur * sample_rate)
    frame_size = ats_snd.frame_size
    frames = ats_snd.frames

    synthesized = zeros(out_size,"float64")

    frame_size_range = frame_size
    
    if sine_pct > 0.0:
        n_partials = ats_snd.partials    
        freq_to_radians_per_sample = tau / sample_rate
        
        has_pha = compute_phase and len(ats_snd.pha) > 0
        """
        for cubic polynomial interpolation of phase
        credit: McAulay & Quatieri (1986)
        """
        alpha_beta_coeffs = zeros([2,2], "float64")
        alpha_beta_coeffs[0][0] = 3 / (frame_size**2)
        alpha_beta_coeffs[0][1] = -1 / frame_size
        alpha_beta_coeffs[1][0] = -2 / (frame_size**3)
        alpha_beta_coeffs[1][1] = 1 / (frame_size**2)
        alpha_beta_terms = zeros([2,1],"float64")

        half_T = frame_size / 2

        samps = arange(frame_size, dtype='int64')
        samps_squared = samps ** 2
        samps_cubed = samps ** 3

        prior_partial_phases = None
        if not has_pha:
            prior_partial_phases = zeros(n_partials,"float64")

        fil_ptr = 0
        for frame_n in range(frames):
            
            # constrain number of samples we write at tail end of sound
            if fil_ptr + frame_size_range > out_size:
                frame_size_range = out_size - fil_ptr
            
            for partial in range(n_partials):
                if ats_snd.frq[partial][frame_n] == 0.0 and ats_snd.frq[partial][frame_n + 1] == 0.0:
                    continue

                # get amp step
                amp_0 = ats_snd.amp[partial][frame_n]
                amp_t = ats_snd.amp[partial][frame_n + 1]
                amp_step = (amp_t - amp_0) / frame_size

                # compute frequency/phase interpolation preliminaries
                w_0 = ats_snd.frq[partial][frame_n] * freq_to_radians_per_sample
                w_t = ats_snd.frq[partial][frame_n + 1] * freq_to_radians_per_sample
                
                if w_0 == 0.0:
                    w_0 = w_t
                elif w_t == 0.0:
                    w_t = w_0

                if has_pha:
                    pha_0 = ats_snd.pha[partial][frame_n]
                    pha_t = ats_snd.pha[partial][frame_n + 1]

                    """
                    cubic polynomial interpolation of phase
                    credit: McAulay & Quatieri (1986)
                    """
                    M = round((((pha_0 + (w_0 * frame_size) - pha_t) + (half_T * (w_t - w_0))) / tau))
                    alpha_beta_terms[0] = pha_t - pha_0 - (w_0 * frame_size) + (tau * M)
                    alpha_beta_terms[1] = w_t - w_0
                    alpha, beta = matmul(alpha_beta_coeffs, alpha_beta_terms)
                    synthesized[fil_ptr:fil_ptr + frame_size_range] += ((samps[:frame_size_range] * amp_step) + amp_0) * \
                                                                            cos(pha_0 + (w_0 * samps[:frame_size_range]) + 
                                                                                (alpha * samps_squared[:frame_size_range]) + 
                                                                                (beta * samps_cubed[:frame_size_range]))
                
                else:
                    # phaseless version
                    pha_0 = prior_partial_phases[partial]
                    w = cumsum(linspace(w_0, w_t, frame_size))
                    synthesized[fil_ptr:fil_ptr + frame_size_range] += ((samps[:frame_size_range] * amp_step) + amp_0) * \
                                                                            cos(w[:frame_size_range] + pha_0)
                    prior_partial_phases[partial] = pha_0 + w[-1]

            fil_ptr += frame_size

            if fil_ptr >= out_size:
                break

            if normalize_sine:
                gain = max(abs(synthesized))
                if gain != 1.0 and gain > 0.0:
                    synthesized /= gain

        synthesized *= sine_pct
        
    has_noi = noise_pct > 0.0 and len(ats_snd.band_energy) > 0

    if has_noi:
        # using white noise -> band-limited noise fft resynthesis method
        noise = zeros(out_size,"float64")
        
        window = sin(arange(sample_rate) * pi / sample_rate)**2 # using Hann window
        overlap = 0.5

        noise_hop = int(overlap * sample_rate)
        noise_M_over_2 = sample_rate // 2
        noise_frames = compute_frames(out_size, noise_hop)
        
        white_noise = uniform(-1,1, int(noise_frames * sample_rate / overlap) + 1)
        banded_noise = zeros([len(ats_snd.bands), out_size])

        # indices for refolding a symmetric fft after clearing freq bins
        bin_indices = zeros(sample_rate, "int64")
        for i in range(noise_M_over_2):
            bin_indices[i] = i
            bin_indices[-(i + 1)] = i

        # build band-limited noise
        if noise_bands is None:
            noise_bands = ATS_CRITICAL_BAND_EDGES
        for band in ats_snd.bands:
            lo = int(noise_bands[band])
            hi = int(noise_bands[band+1])
            
            in_ptr = 0
            out_ptr = -noise_M_over_2
            for frame_n in range(noise_frames):
                time_bins = white_noise[in_ptr:in_ptr+sample_rate] * window
                freq_bins = fft(time_bins)
                freq_bins[:lo] = 0.0
                freq_bins[hi+1:] = 0.0
                rev_fft = real(ifft(freq_bins[bin_indices]))

                front_pad = 0
                back_pad = 0
                if out_ptr < 0:
                    front_pad = -out_ptr
                if out_ptr + sample_rate >= out_size:
                    back_pad = out_ptr + sample_rate - out_size

                if not front_pad and not back_pad:    
                    banded_noise[band][out_ptr:out_ptr+sample_rate] += rev_fft
                else:
                    banded_noise[band][out_ptr+front_pad:out_ptr+sample_rate-back_pad] += rev_fft[front_pad:sample_rate-back_pad] 

                in_ptr += noise_hop
                out_ptr += noise_hop

                if out_ptr >= out_size:
                    break 

        # envelope bands
        fil_ptr = 0
        frame_size_range = frame_size
        for frame_n in range(frames):

            # constrain number of samples we write at tail end of sound
            if fil_ptr + frame_size_range > out_size:
                frame_size_range = out_size - fil_ptr
            for band in ats_snd.bands:
                if ats_snd.band_energy[band][frame_n] == 0.0 and ats_snd.band_energy[band][frame_n + 1] == 0.0:
                    continue

                # get amp step
                amp_0 = ats_snd.band_energy[band][frame_n]
                amp_t = ats_snd.band_energy[band][frame_n + 1]
                amp_step = (amp_t - amp_0) / frame_size
                noise[fil_ptr:fil_ptr + frame_size_range] += (amp_0 + (arange(frame_size_range) * amp_step)) * \
                                                                banded_noise[band][fil_ptr:fil_ptr + frame_size_range]

            fil_ptr += frame_size

            if fil_ptr >= out_size:
                break

        if normalize_noise:
            gain = max(abs(noise))
            if gain != 1.0 and gain > 0.0:
                noise /= gain

        synthesized += noise_pct * noise
    
    if normalize:
        gain = max(abs(synthesized))
        if gain != 1.0 and gain > 0.0:
            synthesized /= gain

    # export synthesized version to audio file
    if export_file is not None:
        sf.write(export_file, synthesized, ats_snd.sampling_rate)

    return synthesized  

def synth_CLI():    
    """Command line wrapper for :obj:`~pyatsyn.ats_synth.synth`

    Example
    ------- 
    Display usage details with help flag   

    ::

        $ pyatsyn-synth -h

    Generate a wav file from a sine generator bank from an ats file

    ::

        $ pyatsyn-synth example.ats example.wav

    Generate a wav file from a sine generator bank and band-limited noise using from an ats file

    ::
    
        $ pyatsyn-synth example.ats example.wav --noise 1.0

    """
    parser = argparse.ArgumentParser(
        description = "Sine generator bank and band-limited noise synthesizer for .ats files"        
    )
    parser.add_argument("ats_file_in", help="the path to the .ats file to synthesize")
    parser.add_argument("audio_file_out", help="audio file path to synthesize to")
    parser.add_argument("-n", "--normalize", help="normalize sound to ±1 before output", action="store_true")
    parser.add_argument("--sine", type=float, help="percentage of sine components to mix (default 1.0)", default=1.0)
    parser.add_argument("--noise", type=float, help="percentage of noise components to mix (default 0.0)", default=0.0)
    parser.add_argument("--normalize_sine", help="normalize sine components to ±1 before mixing", action="store_true")
    parser.add_argument("--normalize_noise", help="normalize noise componenets to ±1 before mixing", action="store_true")
    parser.add_argument("--ignore_phase", help="ignore phase information during synthesis", action="store_true")
    args = parser.parse_args()
    synth(  ats_load(args.ats_file_in, args.ats_file_in), 
            normalize = args.normalize,
            compute_phase = not args.ignore_phase,
            export_file = args.audio_file_out,
            sine_pct = args.sine,
            noise_pct = args.noise,
            normalize_sine = args.normalize_sine,
            normalize_noise = args.normalize_noise
            )