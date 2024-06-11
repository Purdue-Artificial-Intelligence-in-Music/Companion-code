# -*- coding: utf-8 -*-

# This source code is licensed under the BSD-style license found in the
# LICENSE.rst file in the root directory of this source tree. 

# pyatsyn Copyright (c) <2023>, <Johnathan G Lyon>
# All rights reserved.

# Except where otherwise noted, ATSA and ATSH is Copyright (c) <2002-2004>, 
# <Oscar Pablo Di Liscia, Pete Moss, and Juan Pampin>


"""ATS File I/O

Functions for handling loading and saving of .ats files.

.ats files are written in binary format using double floats.

The expected structure of a .ats is:

+-------------------------------------------+
| ATS Header (all double floats)            |
+===========================================+
| :obj:`~pyatsyn.ats_io.ATS_MAGIC_NUMBER`   |
+-------------------------------------------+
| sampling-rate (samples/sec)               |
+-------------------------------------------+
| frame-size (samples)                      |
+-------------------------------------------+
| window-size (samples)                     |
+-------------------------------------------+
| partials (number)                         |
+-------------------------------------------+
| frames (number)                           |
+-------------------------------------------+
| ampmax (max. amplitude)                   |
+-------------------------------------------+
| frqmax (max. frequency)                   |
+-------------------------------------------+
| dur (duration)                            |
+-------------------------------------------+
| type (# specifying frame type, see below) |
+-------------------------------------------+

The frame data immediately follows the header, 
again all double floats, frame by frame, with a 
format matching the `type` (int) as specified in the header

ATS frames can be one of four different types:

+---------------------------------+---------------------------------+---------------------------------+---------------------------------+
| TYPE 1: NO phase & NO noise     | TYPE 2: WITH phase & NO noise   | TYPE 3: NO phase & WITH noise   | TYPE 4: WITH phase & WITH noise |
+=================================+=================================+=================================+=================================+
| time (frame starting time)      | time (frame starting time)      | time (frame starting time)      | time (frame starting time)      |
+---------------------------------+---------------------------------+---------------------------------+---------------------------------+
| amp (partial #0 amplitude)      | amp (partial #0 amplitude)      | amp (partial #0 amplitude)      | amp (partial #0 amplitude)      |
+---------------------------------+---------------------------------+---------------------------------+---------------------------------+
| frq (partial #0 frequency)      | frq (partial #0 frequency)      | frq (partial #0 frequency)      | frq (partial #0 frequency)      |
+---------------------------------+---------------------------------+---------------------------------+---------------------------------+
| ...                             | pha (partial #0 phase)          | ...                             | pha (partial #0 phase)          |
+---------------------------------+---------------------------------+---------------------------------+---------------------------------+
| amp (partial #n amplitude)      | ...                             | amp (partial #n amplitude)      | ...                             |
+---------------------------------+---------------------------------+---------------------------------+---------------------------------+
| frq (partial #n frequency)      | amp (partial #n amplitude)      | frq (partial #n frequency)      | amp (partial #n amplitude)      |
+---------------------------------+---------------------------------+---------------------------------+---------------------------------+
|                                 | frq (partial #n frequency)      | noise (band #0 energy)          | frq (partial #n frequency)      |
+---------------------------------+---------------------------------+---------------------------------+---------------------------------+
|                                 | pha (partial #n phase)          | ...                             | pha (partial #n phase)          |
+---------------------------------+---------------------------------+---------------------------------+---------------------------------+
|                                 |                                 | noise (band #n energy)          | noise (band #0 energy)          |
+---------------------------------+---------------------------------+---------------------------------+---------------------------------+
|                                 |                                 |                                 | ...                             |
+---------------------------------+---------------------------------+---------------------------------+---------------------------------+
|                                 |                                 |                                 | noise (band #n energy)          |
+---------------------------------+---------------------------------+---------------------------------+---------------------------------+

Attributes 
----------
ATS_MAGIC_NUMBER : float
    'magic' number used to validate and check endianness when using .ats files: 123.0
"""

from struct import pack, unpack, calcsize
from numpy import zeros, arange, mean
import argparse

from pyatsyn.ats_structure import AtsSound

ATS_MAGIC_NUMBER = 123.0

DOUBLE_SIZE = calcsize('d')
DOUBLE_BIG_ENDIAN = '>d'
DOUBLE_LIL_ENDIAN = '<d'

def ats_save(sound, file, save_phase=True, save_noise=True):
    """Function to save an :obj:`~pyatsyn.ats_structure.AtsSound` to a file

    Parameters
    ----------
    sound : :obj:`~pyatsyn.ats_structure.AtsSound`
        ats sound object to save
    file : str
        file path to save to
    save_phase : bool, optional
        whether to include phase data in file output (default: True)
    save_noise : bool, optional
        whether to include noise band energy data in file output (default: True)
    """
    has_pha = save_phase and len(sound.pha) > 0
    has_noi = save_noise and (len(sound.energy) > 0 or len(sound.band_energy) > 0)

    if has_noi and len(sound.bands) != 25:
        print("WARNING: outputing noise energies with other than the expected 25 critical bands")

    ats_type = 1
    if has_pha and has_noi:
        ats_type = 4
    elif not has_pha and has_noi:
        ats_type = 3
    elif has_pha and not has_noi:
        ats_type = 2

    with open(file, 'wb') as fil:
        # write header
        fil.write(pack('d',ATS_MAGIC_NUMBER))
        fil.write(pack('d',sound.sampling_rate))
        fil.write(pack('d',sound.frame_size))
        fil.write(pack('d',sound.window_size))
        fil.write(pack('d',sound.partials))
        fil.write(pack('d',sound.frames))
        fil.write(pack('d',sound.amp_max))
        fil.write(pack('d',sound.frq_max))
        fil.write(pack('d',sound.dur))
        fil.write(pack('d',ats_type))

        for frame_n in range(sound.frames):
            fil.write(pack('d',sound.time[frame_n]))
            for partial in range(sound.partials):
                fil.write(pack('d',sound.amp[partial][frame_n]))
                fil.write(pack('d',sound.frq[partial][frame_n]))
                if has_pha:
                    fil.write(pack('d',sound.pha[partial][frame_n]))
            
            if has_noi:
                for band in range(len(sound.bands)):
                    fil.write(pack('d',sound.band_energy[band][frame_n]))                    


def ats_load(   file, 
                optimize=False, 
                min_gap_size = None,
                min_segment_length = None,                     
                amp_threshold = None, 
                highest_frequency = None,
                lowest_frequency = None):
    """Function to load a .ats file into python

    Loads a .ats file into python and provides routines to re-optimize the 
    :obj:`~pyatsyn.ats_structure.AtsSound` data if required.

    Parameters
    ----------
    file : str
        filepath to .ats file to load
    optimize : bool, optional
        determined whether to call :obj:`~pyatsyn.ats_structure.AtsSound.optimize` upon load (default: True)
    min_gap_size : int, optional
        when optimizing, tracked partial gaps smaller than or equal to this (in frames) will be 
        interpolated and filled. If None, no gap filling will occur (default: None)
    amp_threshold : float, optional
        minimum amplitude threshold used during optimization to prune tracks. 
        If None, no amplitude thresholding will occur (default: None)
    highest_frequency : float, optional
        maximum frequency threshold used during optimization to prune tracks.
        If None, no maximum frequency thresholding will occur (default: None)
    lowest_frequency : float, optional
        minimum frequency threshold used during optimization to prune tracks.
        If None, no minimum frequency thresholding will occur (default: None)
        
    
    Returns
    -------
    :obj:`~pyatsyn.ats_structure.AtsSound`
        the loaded ats data

    Raises
    ------
    ValueError
        if file is not a compatible ATS format (i.e., the ATS magic number was not decodable)
    """
    with open(file, 'rb') as fil:
        
        # check ATS_MAGIC_NUMBER and set endian order
        check_magic_number_raw = fil.read(DOUBLE_SIZE)
        ordered_double = None        
        if unpack(DOUBLE_BIG_ENDIAN,check_magic_number_raw)[0] == ATS_MAGIC_NUMBER:
            ordered_double = DOUBLE_BIG_ENDIAN
        elif unpack(DOUBLE_LIL_ENDIAN,check_magic_number_raw)[0] == ATS_MAGIC_NUMBER:
            ordered_double = DOUBLE_LIL_ENDIAN
        else:
            raise ValueError("File is not a compatible ATS format (ATS magic number was not accurate)")
        
        sampling_rate = int(unpack(ordered_double, fil.read(DOUBLE_SIZE))[0])
        frame_size = int(unpack(ordered_double, fil.read(DOUBLE_SIZE))[0])
        window_size = int(unpack(ordered_double, fil.read(DOUBLE_SIZE))[0])
        partials = int(unpack(ordered_double, fil.read(DOUBLE_SIZE))[0])
        frames = int(unpack(ordered_double, fil.read(DOUBLE_SIZE))[0])
        amp_max = unpack(ordered_double, fil.read(DOUBLE_SIZE))[0]
        frq_max = unpack(ordered_double, fil.read(DOUBLE_SIZE))[0]
        dur = unpack(ordered_double, fil.read(DOUBLE_SIZE))[0]
        ats_type = int(unpack(ordered_double, fil.read(DOUBLE_SIZE))[0])

        has_noise = False
        if ats_type == 3 or ats_type == 4:
            has_noise = True
        has_phase = False
        if ats_type == 2 or ats_type == 4:
            has_phase = True

        ats_snd = AtsSound(sampling_rate, frame_size, window_size, 
                                partials, frames, dur, has_phase=has_phase)

        ats_snd.amp_max = amp_max
        ats_snd.frq_max = frq_max

        ats_snd.frq_av = zeros(partials, "float64")
        ats_snd.amp_av = zeros(partials, "float64")
        ats_snd.time = zeros(frames, "float64")
        ats_snd.frq = zeros([partials,frames], "float64")
        ats_snd.amp = zeros([partials,frames], "float64")
        if has_phase:
            ats_snd.pha = zeros([partials,frames], "float64")
        if has_noise:
            # NOTE: hard-coded for expected number of critical bands
            ats_snd.bands = arange(25)
            ats_snd.band_energy = zeros([25, frames], "float64")

        for frame_n in range(ats_snd.frames):
            ats_snd.time[frame_n] = unpack(ordered_double, fil.read(DOUBLE_SIZE))[0]
            for partial in range(ats_snd.partials):
                ats_snd.amp[partial][frame_n] = unpack(ordered_double, fil.read(DOUBLE_SIZE))[0]
                ats_snd.frq[partial][frame_n] = unpack(ordered_double, fil.read(DOUBLE_SIZE))[0]
                if has_phase:
                    ats_snd.pha[partial][frame_n] = unpack(ordered_double, fil.read(DOUBLE_SIZE))[0]
            if has_noise:
                for band in range(len(ats_snd.bands)):
                    ats_snd.band_energy[band][frame_n] = unpack(ordered_double, fil.read(DOUBLE_SIZE))[0]
        
        # load frq/amp averages
        for partial in range(ats_snd.partials):
            ats_snd.frq_av[partial] = mean(ats_snd.frq[partial][ats_snd.frq[partial] > 0.0])
            ats_snd.amp_av[partial] = mean(ats_snd.amp[partial][ats_snd.amp[partial] > 0.0])

        if optimize:
            ats_snd.optimize(min_gap_size, min_segment_length, amp_threshold, highest_frequency, lowest_frequency)
        
        return ats_snd


def ats_info(file, partials_info=False):
    """Function to print information about a .ats to the stdout
    
    Parameters
    ----------
    file : str
        an .ats file to print information about
    partials_info : bool, optional
        whether to include frq and amp averages about each partial in the output (default: False)    
    """
    if not partials_info:
        with open(file, 'rb') as fil:

            # check ATS_MAGIC_NUMBER and set endian order
            check_magic_number_raw = fil.read(DOUBLE_SIZE)
            ordered_double = None        
            if unpack(DOUBLE_BIG_ENDIAN,check_magic_number_raw)[0] == ATS_MAGIC_NUMBER:
                ordered_double = DOUBLE_BIG_ENDIAN
                print(f"BIG ENDIAN: ", ATS_MAGIC_NUMBER)
            elif unpack(DOUBLE_LIL_ENDIAN,check_magic_number_raw)[0] == ATS_MAGIC_NUMBER:
                ordered_double = DOUBLE_LIL_ENDIAN
                print(f"LITTLE ENDIAN: ", ATS_MAGIC_NUMBER)
            else:
                print("File is not a compatible ATS format (ATS magic number was not accurate)")
                return
            
            sampling_rate = int(unpack(ordered_double, fil.read(DOUBLE_SIZE))[0])
            frame_size = int(unpack(ordered_double, fil.read(DOUBLE_SIZE))[0])
            window_size = int(unpack(ordered_double, fil.read(DOUBLE_SIZE))[0])
            partials = int(unpack(ordered_double, fil.read(DOUBLE_SIZE))[0])
            frames = int(unpack(ordered_double, fil.read(DOUBLE_SIZE))[0])
            amp_max = unpack(ordered_double, fil.read(DOUBLE_SIZE))[0]
            frq_max = unpack(ordered_double, fil.read(DOUBLE_SIZE))[0]
            dur = unpack(ordered_double, fil.read(DOUBLE_SIZE))[0]
            ats_type = int(unpack(ordered_double, fil.read(DOUBLE_SIZE))[0])

            print(f"sampling rate (samples/s):", sampling_rate)
            print(f"frame size:", frame_size)
            print(f"window size:", window_size)
            print(f"n partials:", partials)
            print(f"n frames:", frames)
            print(f"maximum amplitude:", amp_max)
            print(f"maximum frequency (Hz):", frq_max)
            print(f"duration (s):", dur)
            print(f"ATS frame type: ", ats_type)            
    else:
        with open(file, 'rb') as fil:
            # check ATS_MAGIC_NUMBER and set endian order
            check_magic_number_raw = fil.read(DOUBLE_SIZE)
            ordered_double = None        
            if unpack(DOUBLE_BIG_ENDIAN,check_magic_number_raw)[0] == ATS_MAGIC_NUMBER:
                ordered_double = DOUBLE_BIG_ENDIAN
                print(f"BIG ENDIAN: ", ATS_MAGIC_NUMBER)
            elif unpack(DOUBLE_LIL_ENDIAN,check_magic_number_raw)[0] == ATS_MAGIC_NUMBER:
                ordered_double = DOUBLE_LIL_ENDIAN
                print(f"LITTLE ENDIAN: ", ATS_MAGIC_NUMBER)
            else:
                print("File is not a compatible ATS format (ATS magic number was not accurate)")
                return

        ats_snd = ats_load(file)

        print(f"sampling rate (samples/s):", ats_snd.sampling_rate)
        print(f"frame size:", ats_snd.frame_size)
        print(f"window size:", ats_snd.window_size)
        print(f"n partials:", ats_snd.partials)
        print(f"n frames:", ats_snd.frames)
        print(f"maximum amplitude:", ats_snd.amp_max)
        print(f"maximum frequency (Hz):", ats_snd.frq_max)
        print(f"duration (s):", ats_snd.dur)

        has_noise = False
        if len(ats_snd.bands) > 0 and len(ats_snd.band_energy) > 0:
            has_noise = True
        has_phase = False
        if ats_snd.pha is not None:
            has_phase = True

        ats_type = 1
        if has_phase and has_noise:
                ats_type = 4
        elif not has_phase and has_noise:
            ats_type = 3
        elif has_phase and not has_noise:
            ats_type = 2
        print(f"ATS frame type: ", ats_type)

        print(f"\nPartial Information:")
        for partial in range(ats_snd.partials):
            print(f"\tpartial #{partial}:\t\tfrq_av {ats_snd.frq_av[partial]:.2f}\t\tamp_av {ats_snd.amp_av[partial]:.5f}")
        
def ats_info_CLI():
    """Command line wrapper for :obj:`~pyatsyn.ats_io.ats_info`
    
    Example
    -------
    Display usage details with help flag

    ::

        $ pyatsyn-info -h

    Print the header information of a .ats file

    ::

        $ pyatsyn-info example.ats

    Print the header information and partials information of a .ats file

    ::

        $ pyatsyn-info example.ats -p

    """
    parser = argparse.ArgumentParser(
        description = "Print information about an .ats file"        
    )
    parser.add_argument("ats_file", help="the path to the .ats file to print information about")
    parser.add_argument("-p", "--partials", help="include a summary for each partial in the output", action="store_true")
    args = parser.parse_args()
    ats_info(args.ats_file, args.partials)