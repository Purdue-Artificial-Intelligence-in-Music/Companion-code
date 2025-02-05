
import fluidsynth
from typing import List, Tuple
from music21 import converter, note, chord
from time import sleep, time
import math

# Initialize the synthesizer
fs = fluidsynth.Synth(samplerate=44100)
fs.start()  # you can pass a specific audio driver if needed

# Load a SoundFont (ensure you have a high-quality one with cello sounds)
sfid = fs.sfload("soundfonts\FluidR3_GM.sf2")
fs.program_select(0, sfid, 0, 42)  # the last number (42 here) is the MIDI program number for a cello (may vary by SoundFont)

def midi_to_notes(
    midi_file_path: str,
    tempo_bpm: float,
    instrument_index: int
) -> List[Tuple[float, float, float]]:
    """
    Parse a MIDI file and extract note information from a specified instrument.

    This function reads a MIDI file, extracts notes from the given instrument index,
    and returns a list of tuples. Each tuple contains the frequency in Hertz, duration
    in seconds, and timestamp in seconds for a note. In the case of chords, each note
    in the chord is processed individually.

    Parameters
    ----------
    midi_file_path : str
        The path to the MIDI file.
    tempo_bpm : float
        The tempo of the piece in beats per minute (BPM).
    instrument_index : int
        The index of the instrument (part) from which to extract the notes.
        An IndexError is raised if the index is out of range.

    Returns
    -------
    List[Tuple[float, float, float]]
        A list where each element is a tuple containing:
        - frequency (float): The frequency of the note in Hertz.
        - duration (float): The duration of the note in seconds.
        - timestamp (float): The starting time of the note in seconds.

    Notes
    -----
    - If an error occurs during MIDI file parsing, an error message is printed and
      an empty list is returned.
    - Tied notes within the MIDI file are merged to form a single note duration.
    """
    # Parse the MIDI file
    try:
        midi_stream = converter.parse(midi_file_path)
    except Exception as e:
        print(f"Error parsing MIDI file: {e}")
        return []

    # Get all parts
    parts = midi_stream.parts

    # Validate instrument_index
    if instrument_index < 0 or instrument_index >= len(parts):
        raise IndexError(f"Instrument index {instrument_index} is out of range. "
                         f"Please choose between 0 and {len(parts)-1}.")

    # Select the specified part
    selected_part = parts[instrument_index]

    # Attempt to get the instrument name
    instr = selected_part.getInstrument(returnDefault=False)
    if instr:
        instr_name = instr.instrumentName
    else:
        instr_name = "Unknown Instrument"

    print(f"\nExtracting notes from Instrument Index {instrument_index}: {instr_name}\n")

    # Flatten the selected part to simplify iteration
    flat_part = selected_part.flat

    # Handle ties to merge long notes
    flat_part = flat_part.stripTies()  # This merges tied notes into single notes

    freq_dur_timestamp_list = []

    # Calculate the duration of one quarter note in seconds
    quarter_note_duration_sec = 60.0 / tempo_bpm

    # Iterate through all notes and chords in the flat part
    for element in flat_part.notes:
        # Determine the start time (offset) in quarter lengths
        offset_quarter = element.offset
        timestamp_sec = offset_quarter * quarter_note_duration_sec

        # If the element is a Note, extract its frequency and duration
        if isinstance(element, note.Note):
            frequency = element.pitch.frequency
            duration_sec = element.duration.quarterLength * quarter_note_duration_sec
            freq_dur_timestamp_list.append(
                (frequency, duration_sec, timestamp_sec))

        # If the element is a Chord, handle each note in the chord
        elif isinstance(element, chord.Chord):
            for pitch in element.pitches:
                frequency = pitch.frequency
                duration_sec = element.duration.quarterLength * quarter_note_duration_sec
                freq_dur_timestamp_list.append(
                    (frequency, duration_sec, timestamp_sec))

    return freq_dur_timestamp_list

def frequency_to_midi(frequency: float) -> int:
    """
    Convert a frequency in Hz to the corresponding MIDI note number.

    Parameters
    ----------
    frequency : float
        Frequency in Hertz.

    Returns
    -------
    int
        The MIDI note number (0-127).
    """
    midi_note = 69 + 12 * math.log2(frequency / 440.0)
    return int(round(midi_note))

# Assuming 'fs' is your FluidSynth synthesizer object.
def play_note(frequency: float, duration: float):
    """
    Play a note using FluidSynth by converting the given frequency to a MIDI note number.

    Parameters
    ----------
    frequency : float
        The frequency of the note in Hz.
    duration : float
        Duration to hold the note (in seconds).
    """
    midi_note = frequency_to_midi(frequency)
    
    fs.noteon(0, midi_note, 100)  # channel 0, note, velocity 100
    sleep(duration)
    fs.noteoff(0, midi_note)


MIDI_FILE = 'data/midi/air.mid'
TEMPO = 60
INSTRUMENT = 1

notes = midi_to_notes(MIDI_FILE, TEMPO, INSTRUMENT)

start_time = time()
for n in notes:
    freq, dur, ts = n
    if time() - start_time < ts:
        sleep(ts - (time() - start_time))
    play_note(freq, dur)
    print(f"Playing note: {freq:.2f} Hz for {dur:.2f} seconds")

fs.delete()