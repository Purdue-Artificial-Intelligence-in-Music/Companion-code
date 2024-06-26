# -*- coding: utf-8 -*-

# This source code is licensed under the BSD-style license found in the
# LICENSE.rst file in the root directory of this source tree. 

# pyatsyn Copyright (c) <2023>, <Johnathan G Lyon>
# All rights reserved.

# Except where otherwise noted, ATSA and ATSH is Copyright (c) <2002-2004>
# <Oscar Pablo Di Liscia, Pete Moss, and Juan Pampin>


""" Main ATS Analysis Function

The analysis tracker is responsible for driving the analysis of an audio file 
into the .ats format. The system uses a Short Time Fourier Transform (STFT) as
is core analysis tool. Sound is analyzed using overlapping time windows and by
taking the STFT on each window. 

After converting to polar coordinates, a peak detection algorithm (:obj:`~pyatsyn.atsa.peak_detection`)
determines relevant spectral peaks in the data. At this point, pyschoacoustics 
are considered in the form of masking curve evaluation and computation of the 
Signal-to-Mask ratio (SMR) for each candidate peak. SMR data is store together with 
a corrected frequency, magnitude and phase.

The next step involves frame-to-frame tracking of peaks (:obj:`~pyatsyn.atsa.peak_tracking`) to connect peaks that
follow a similar spectral trajectory using both frequency and SMR data. The system 
uses a stable matching algorithm to pair candidate peaks, and is capable of interpolating
gaps in the tracks.

Once valid tracks are assembled, the results can be modeled with sinusoids (:obj:`~pyatsyn.atsa_synth`) and subtracted 
from the origin source sound to compute a residual. NOTE: This part of the ATS system is currently under
active research. For now, the residual analysis (:obj:`~pyatsyn.atsa.residual`) is modeled using a 
25 time-varying critical noise band energy model (consistent with the critical bands used during SMR evaluation). 
These noise bands can then be resynthesized using 25 correspoding banks of time-enveloped, band-limited noise.

Analysis is finally stored and abstracted as an :obj:`~pyatsyn.ats_structure.AtsSound` object.

"""

from numpy import zeros, roll, absolute, angle
from numpy.fft import fft, fftfreq
import soundfile as sf
import argparse

from pyatsyn.ats_structure import AtsSound

from pyatsyn.atsa.utils import db_to_amp, next_power_of_2, compute_frames, optimize_tracks
from pyatsyn.atsa.windows import make_fft_window, normalize_window, window_norm, VALID_FFT_WINDOW_DEFINITIONS
from pyatsyn.atsa.peak_detect import peak_detection
from pyatsyn.atsa.critical_bands import evaluate_smr
from pyatsyn.atsa.peak_tracking import update_track_averages, peak_tracking
from pyatsyn.atsa.residual import compute_residual, residual_analysis
from pyatsyn.ats_io import ats_save

def tracker (   in_file, 
                start = 0.0, # analysis start point (in seconds)
                duration = None, # max duration to analyze (in seconds) or 'None' if analyze to end
                lowest_frequency = 20, # must be > 0
                highest_frequency = 20000.0,
                frequency_deviation = 0.1,
                window_cycles = 4,
                window_type = 'blackman-harris-4-1',
                hop_size = 0.25, # in fraction of window size
                fft_size = None, # None, or force an fft size
                amp_threshold = db_to_amp(-60),
                track_length = 3,
                min_gap_length = 3,
                min_segment_length = 3,
                last_peak_contribution = 0.0,
                SMR_continuity = 0.0,              
                residual_file = None,
                optimize = True,
                optimize_amp_threshold = None, # in amplitude
                force_M = None, # None, or a forced window length in samples
                force_window = None, # None, or a numpy.ndarray of floats
                window_alpha = 0.5,
                window_beta = 1.0,
                verbose = False,                
                ):    
    """Function to generates an Analysis-Transformation-Synthesis :obj:`~pyatsyn.ats_structure.AtsSound` from an audio file
    
    Parameters
    ----------
    in_file : str
        path to the audio file to analyze (must be single channel/mono)
    start : float
        timepoint (in s) in audiofile to begin analysis (default: 0.0)
    duration : float
        max duration (in s) in audiofile from start to end analysis or 'None' if analyze to end (default: None)
    lowest_frequency
        lowest frequency to analyze (must be > 0) (default: 20)
    highest_frequency : float
        highest frequency to analyze (capped to nyquist frequency and must be greater than `lowest_frequency`) (default: 20000.0)
    frequency_deviation : float
        maximum relative frequency deviation used to constrain peak tracking matches (default: 0.1)
    window_cycles : int
        lowest frequency to fit in analysis window; used to determine window size (default: 4)
    window_type : str
        type of window to use for FFT analysis (default: 'blackman-harris-4-1'). See :obj:`~pyatsyn.atsa.windows.VALID_FFT_WINDOW_DEFINITIONS`
    hop_size : float
        fraction of window size to shift from frame-to-frame (default: 0.25)
    fft_size : int
        None, or force an fft size (default: None)
    amp_threshold : float
        lowest amplitude used for peak detection (default: 0.001)
    track_length : int
        number of frames used to smooth frequency trajectories (default: 3)
    min_gap_length : int
        tracked partial gaps longer than this (in frames) will not be interpolated (default: 3)
    min_segment_length : int
        minimal size (in frames) of a track segment, otherwise it is pruned (default: 3)
    last_peak_contribution : float
        additional bias for the immediately prior frames values when calculating smoothing trajectories (default: 0.0)
    SMR_continuity : float
        percentage of SMR to use in cost calculations during peak tracking (default: 0.0)
    residual_file : str
        path to the audio file used to store residual analysis. 
        NOTE: noise calculation will not be performed in .ats file without this (default: None)
    optimize : bool
        whether to perform the post-peak tracking optimization on the :obj:`~pyatsyn.ats_structure.AtsSound` object (default: True)
    optimize_amp_threshold : float
        additional amplitude threshold used during optimization to prune tracks (default: None)
    force_M : int
        None, or a forced window length in samples (default: None)
    force_window : ndarray[float]
        None, or a 1D array describing a windowing curve (default: None)
    window_alpha : float
        parameter used for calculating tukey windows (default: 0.5)
    window_beta : float
        parameter used for calculating certain window types (default: 1.0)
    verbose : bool
        increase verbosity (default: False)

    Returns
    -------
    :obj:`~pyatsyn.ats_structure.AtsSound`
        the ats object that represents the analysis of the input audio file

    Raises
    ------
    ValueError
        if input file is not single channel/mono
    ValueError
        if `lowest_frequency` is < 0.0
    ValueError
        if `highest_frequency` is < `lowest_frequency`
    """
    # read input audio file
    in_sound, sample_rate = sf.read(in_file)

    if in_sound.ndim > 1:
        raise ValueError("Input audio file must be mono")
    
    # get first and last sample indices
    st = int(start * sample_rate)
    nd = in_sound.size
    if duration is not None:
        nd = st + int(duration * sample_rate)
    
    # calculate windowing parameters
    total_samps = nd - st
    analysis_duration = total_samps / sample_rate
    cycle_samps = int((1 / lowest_frequency) * window_cycles * sample_rate)

    M = force_M
    if M is None:
        # by default we want an odd length window centered at time 0.0
        if ( (cycle_samps % 2) == 0):
            M = cycle_samps + 1
        else:
            M = cycle_samps

    N = fft_size
    if N is None:
        # default fft size is next power of 2
        N = next_power_of_2(M)

    # instantiate window    
    window = force_window
    if window is None:
        if window_type is None:
            window_type='blackman-harris-4-1'
        window = make_fft_window(window_type, M, beta=window_beta, alpha=window_alpha)
      
    window = normalize_window(window)    
    hop = int(M * hop_size)
    # central point of the window
    M_over_2 = (M - 1) // 2
    frames = compute_frames(total_samps, hop)    

    # magic number for fft frequencies (frequency resolution)
    fft_mag = sample_rate / N

    l_frq = lowest_frequency
    if l_frq <= 0.0:
        raise ValueError('Lowest frequency must be greater than 0.0')
    
    h_frq = highest_frequency
    if h_frq > (sample_rate / 2.0):
        if verbose: print('WARNING: Capping highest frequency to Nyquist Frequency')
        h_frq = int(sample_rate / 2.0)
    if h_frq < l_frq:
        raise ValueError('Highest frequency must be greater than lowest frequency')

    # lowest/highest bins to read
    lowest_bin = int(l_frq / fft_mag)
    highest_bin = int(h_frq / fft_mag)

    # used to store central points of the windows
    win_samps = zeros(frames, "int64")
    # storage for lists of peaks
    analysis_frames = [None for _ in range(frames)]
    # set file pointer half a window from the first sample
    fil_ptr = st - M_over_2
    
    # guarantee that we have a valid minimum gap length
    if min_gap_length < 1:
        min_gap_length = 1

    fft_mags = None
    tracks = []

    if verbose:
        print(f"frames = {frames}")
        print(f"M = {M}; N = {N}")
        print(f"Beginning FFT -> peak tracking analysis...")
        report_every_x_percent = 10
    report_flag = 0

    for frame_n in range(frames):
        if verbose:
            done = frame_n * 100.0 / frames
            if done > report_flag:
                print(f"\t{done:.2f}% complete (tracking)")
                report_flag += report_every_x_percent
        
        # store in_sound sample at the middle of the window
        win_samps[frame_n] = fil_ptr + M_over_2

        ###################
        # WINDOWING + FFT #
        ###################

        # padding for window ranges that are out of the input file
        front_pad = 0
        back_pad = 0
        if fil_ptr < 0:
            front_pad = -fil_ptr
        if fil_ptr + M >= in_sound.size:
            back_pad = fil_ptr + M - in_sound.size

        data = zeros(N, "float64")
        if not front_pad and not back_pad:
            data[:M] = window * in_sound[fil_ptr:fil_ptr+M]
        else:
            data[front_pad:M-back_pad] = window[front_pad:M-back_pad] * in_sound[fil_ptr+front_pad:fil_ptr+M-back_pad]
                                                      
        # shift window by half of M so that phases in `data` are relatively accurate to midpoints
        data = roll(data, -M_over_2)

        # update file pointer
        fil_ptr += hop

        # get the DFT
        fd = fft(data)
        
        ##################
        # PEAK DETECTION #
        ##################

        fftfreqs = fftfreq(fd.size, 1 / sample_rate)                
        
        if front_pad or back_pad:
            # apply correction for frames that hang off the edge of the input file, thus downscaling the actual amplitude            
            # multiply by additional 2.0 to account for symmetric negative frequencies
            fft_mags = absolute(fd) * 2.0 * window_norm(window[front_pad:M-back_pad])
        else:
            # multiply by additional 2.0 to account for symmetric negative frequencies
            fft_mags = absolute(fd) * 2.0

        fftphases = angle(fd)

        peaks = peak_detection(fftfreqs, fft_mags, fftphases, lowest_bin, highest_bin, amp_threshold)         

        if peaks:
            # masking curve evaluation using a critical band based model
            evaluate_smr(peaks)

        #################
        # PEAK TRACKING #
        #################

        if len(tracks) > 0:
            update_track_averages(tracks, track_length, frame_n, analysis_frames, last_peak_contribution)
            peak_tracking(tracks, peaks, frame_n, analysis_frames, sample_rate, hop, frequency_deviation, SMR_continuity, min_gap_length)
        else:
            # otherwise instantiate tracks with the current frame's peaks, if any
            for pk_ind, pk in enumerate(peaks):
                pk.track = pk_ind
            tracks = [pk.clone() for pk in peaks]

        # store peaks for this current frame
        analysis_frames[frame_n] = peaks    

    ########################
    # INITIALIZE ATS SOUND #
    ########################
    pre_opt_track_len = len(tracks)
    if verbose:
        print(f"Tracker found {pre_opt_track_len} partial(s)")

    if optimize:
        if verbose:
            print("Optimizing...")
        tracks = optimize_tracks(tracks, analysis_frames, min_segment_length, optimize_amp_threshold, highest_frequency, lowest_frequency)
        if verbose:
            print(f"Optimization removed {pre_opt_track_len - len(tracks)} partial(s)")

    if verbose:
        print("Initializing AtsSound object...")
    ats_snd = AtsSound(sample_rate, hop, M, len(tracks), frames, analysis_duration, has_phase = True)

    if optimize:
        ats_snd.optimized = True
        amp_max = 0.0
        frq_max = 0.0
        for tk in tracks:
            ats_snd.frq_av[tk.track] = tk.frq
            ats_snd.amp_av[tk.track] = tk.amp
            amp_max = max(amp_max, tk.amp_max)
            frq_max = max(frq_max, tk.frq_max)
        ats_snd.amp_max = amp_max
        ats_snd.frq_max = frq_max

    # fill up with data
    for frame_n in range(frames):
        frame_time = (win_samps[frame_n] - st) / sample_rate
        ats_snd.time[frame_n] = frame_time
        for pk in analysis_frames[frame_n]:
            ats_snd.frq[pk.track][frame_n] = pk.frq
            ats_snd.amp[pk.track][frame_n] = pk.amp
            ats_snd.pha[pk.track][frame_n] = pk.pha     

    #####################
    # RESIDUAL ANALYSIS #
    #####################

    if residual_file:
        if verbose:
            print("Computing Residual...")
        residual = compute_residual(ats_snd, in_sound, st, nd, residual_file)

        if verbose:
            print("Analyzing Residual...")
        residual_analysis(residual, ats_snd, equalize=True, verbose=verbose)       

    if verbose:
        print("Tracking analysis complete")
    return ats_snd


def tracker_CLI():
    """Command line wrapper for :obj:`~pyatsyn.atsa.tracker.tracker`

    Example
    ------- 
    Display usage details with help flag   

    ::

        $ pyatsyn-atsa -h

    Analyze a wav file

    ::

        $ pyatsyn-atsa example.wav example.ats

    Analyze a wav file and compute the residual and increase verbosity

    ::
    
        $ pyatsyn-atsa example.wav example.ats -v -r example-residual.wav

    """
    parser = argparse.ArgumentParser(
        description = "Generates an Analysis-Transformation-Synthesis (.ats) file from an audio file"
        
    )
    parser.add_argument("audio_file_in", help="path to the audio file to analyze")
    parser.add_argument("ats_file_out", help=".ats file path to output to")

    parser.add_argument("-v", "--verbose", help="increase verbosity", action="store_true")
    parser.add_argument("-r","--residual_file", help="path to the audio file used to store residual analysis. \
                            NOTE: noise calculation will not be performed in .ats file without this", default=None)

    parser.add_argument("-s", "--start", type=float, help="timepoint (in s) in audiofile to begin analysis (default 0.0)", default=0.0)
    parser.add_argument("-d", "--duration", type=float, help="max duration (in s) in audiofile from start to end analysis (default duration of file)", default=None)
    parser.add_argument("--low_freq", type=float, help="lowest frequency to analyze (must be > 0) (default 20)", default=20)
    parser.add_argument("--hi_freq", type=float, help="highest frequency to analyze (default 20000)", default=20000)
    parser.add_argument("--amp_threshold", type=float, help="lowest amplitude used for peak detection (default 0.001)", default=0.001)
    parser.add_argument("--freq_dev", type=float, help="frequency deviation; used to constrain peak tracking matches (default 0.1)", default=0.1)    
    parser.add_argument("--SMR_continuity", type=float, help="percentage of SMR to use in cost calculations during peak tracking (default 0.0)", default=0.0)
    
    valid_fft_win_str = "[ " + ' | '.join(VALID_FFT_WINDOW_DEFINITIONS) + " ]"
    parser.add_argument("--win_type", type=ascii, 
        help=f"type of window to use for FFT analysis (default: blackman-harris-4-1); Supported types: {valid_fft_win_str}", default=None)

    parser.add_argument("--win_alpha", type=float, help="parameter used for calculating tukey windows (default 0.5)", default=0.5)
    parser.add_argument("--win_beta", type=float, help="parameter used for calculating certain window types (default 1.0)", default=1.0)
    

    parser.add_argument("--hop_size", type=float, help="fraction of window size to shift from frame-to-frame (default 0.25)", default=0.25)
    parser.add_argument("--fft_size", type=int, help="force an fft_size", default=None)
    parser.add_argument("--win_cycles", type=float, help="lowest frequency to fit in analysis window; used to determine window size (default 4)", default=4)
    parser.add_argument("--force_M", type=int, help="forced window length in samples", default=None)


    parser.add_argument("--track_length", type=int, help="number of frames used to smooth frequency trajectories (default 3)", default=3)
    parser.add_argument("--last_peak_contribution", type=float, help="aadditional bias for the immediately prior frames values when calculating smoothing trajectories (default 0.0)", default=0.0)

    parser.add_argument("--min_gap_length", type=int, help="tracked partial gaps longer than this (in frames) will not be interpolated (default 3)", default=3)
    parser.add_argument("--min_segment_length", type=int, help="minimize size (in frames) of a track segment, otherwise it is pruned (default 3)", default=3)
    
    parser.add_argument("--opt_amp_threshold", type=float, help="additional amplitude threshold used during optimization to prune tracks (default 0.001)", default=None)
    parser.add_argument("--no_optimize", help="skip pre-output optimization of .ats file", action="store_true")
    
    args = parser.parse_args()

    ats_save(tracker(   args.audio_file_in,
                        start = args.start,
                        duration = args.duration,
                        lowest_frequency = args.low_freq,
                        highest_frequency = args.hi_freq,
                        frequency_deviation = args.freq_dev,
                        window_cycles = args.win_cycles,
                        window_type = args.win_type,
                        hop_size = args.hop_size,                
                        fft_size = args.fft_size,
                        amp_threshold = args.amp_threshold,
                        track_length = args.track_length,
                        min_gap_length = args.min_gap_length,
                        min_segment_length = args.min_segment_length,
                        last_peak_contribution = args.last_peak_contribution,
                        SMR_continuity = args.SMR_continuity,
                        optimize_amp_threshold = args.opt_amp_threshold,
                        residual_file = args.residual_file,
                        optimize = not args.no_optimize,
                        force_M = args.force_M,
                        window_alpha = args.win_alpha,
                        window_beta = args.win_beta,
                        verbose = args.verbose,  
                    ),
                args.ats_file_out)                

