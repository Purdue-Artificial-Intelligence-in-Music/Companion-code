import fluidsynth
from typing import List, Tuple
from music21 import converter, note, chord
from time import sleep, time
import math

# ---------------------------
# Initialize FluidSynth
# ---------------------------
fs = fluidsynth.Synth(samplerate=44100)
fs.start()  # Optionally specify an audio driver

# Load a SoundFont (ensure you have a high-quality one with cello sounds)
sfid = fs.sfload(r"soundfonts\FluidR3_GM.sf2")
fs.program_select(0, sfid, 0, 42)  # channel 0, bank 0, program 42 (adjust as needed)

# ---------------------------
# Function: Extract notes in quarter-note units
# ---------------------------
def midi_to_notes_quarter(
    midi_file_path: str,
    instrument_index: int
) -> List[Tuple[float, float, float]]:
    """
    Parse a MIDI file and extract note information from a specified instrument,
    returning timing in quarter note units.

    Returns a list of tuples (frequency, quarter_duration, quarter_offset) where:
      - frequency (Hz)
      - quarter_duration: note duration in quarter note lengths (beats)
      - quarter_offset: note start time in quarter note units (beats)
    """
    try:
        midi_stream = converter.parse(midi_file_path)
    except Exception as e:
        print(f"Error parsing MIDI file: {e}")
        return []

    parts = midi_stream.parts
    if instrument_index < 0 or instrument_index >= len(parts):
        raise IndexError(f"Instrument index {instrument_index} is out of range. "
                         f"Please choose between 0 and {len(parts)-1}.")

    selected_part = parts[instrument_index]
    instr = selected_part.getInstrument(returnDefault=False)
    instr_name = instr.instrumentName if instr else "Unknown Instrument"
    print(f"\nExtracting notes from Instrument Index {instrument_index}: {instr_name}\n")

    flat_part = selected_part.flat.stripTies()  # merge tied notes

    notes_list = []
    for element in flat_part.notes:
        quarter_offset = element.offset           # offset in quarter note units (beats)
        quarter_duration = element.duration.quarterLength  # duration in beats
        if isinstance(element, note.Note):
            frequency = element.pitch.frequency
            notes_list.append((frequency, quarter_duration, quarter_offset))
        elif isinstance(element, chord.Chord):
            for pitch in element.pitches:
                frequency = pitch.frequency
                notes_list.append((frequency, quarter_duration, quarter_offset))
    return notes_list

# ---------------------------
# Helper: Convert frequency (Hz) to MIDI note number
# ---------------------------
def frequency_to_midi(frequency: float) -> int:
    midi_note = 69 + 12 * math.log2(frequency / 440.0)
    return int(round(midi_note))

# ---------------------------
# Function: Play a note via FluidSynth using MIDI
# ---------------------------
def play_note(frequency: float, duration: float):
    """
    Play a note using FluidSynth by converting frequency to a MIDI note.
    
    Parameters:
      frequency : float
          The frequency of the note in Hz.
      duration : float
          The duration (in seconds) to hold the note.
    """
    midi_note = frequency_to_midi(frequency)
    fs.noteon(0, midi_note, 100)  # channel 0, note, velocity 100
    sleep(duration)
    fs.noteoff(0, midi_note)

# ---------------------------
# Global tempo and tempo update logic
# ---------------------------
# Start with an initial tempo (BPM)
current_tempo = 60  # BPM

# For demonstration, we simulate a tempo change after a set time.
# In a real scenario, you could update this variable in response to external input.
TEMPO_CHANGE_TIME = 10  # seconds after performance start to change tempo
NEW_TEMPO = 90          # New BPM after the change

# ---------------------------
# Main performance loop
# ---------------------------
MIDI_FILE = r'data/midi/air.mid'
INSTRUMENT = 1

# Extract notes as (frequency, quarter_duration, quarter_offset)
notes = midi_to_notes_quarter(MIDI_FILE, INSTRUMENT)
# Sort by quarter note offset
notes.sort(key=lambda n: n[2])

print("Starting performance...")

performance_start = time()

for freq, quarter_duration, quarter_offset in notes:
    # Before scheduling each note, check if we need to update the tempo.
    elapsed = time() - performance_start
    if elapsed > TEMPO_CHANGE_TIME and current_tempo != NEW_TEMPO:
        current_tempo = NEW_TEMPO
        print(f"\nTempo changed to {current_tempo} BPM at elapsed time {elapsed:.2f} sec\n")
    
    # Compute scheduled onset (in seconds) using the current tempo.
    # (60 / current_tempo) gives the length of one beat in seconds.
    scheduled_time = quarter_offset * (60 / current_tempo)
    
    # Wait until it is time to play the note.
    while time() - performance_start < scheduled_time:
        sleep(0.001)
    
    # Compute note duration in seconds using the current tempo.
    note_duration = quarter_duration * (60 / current_tempo)
    
    play_note(freq, note_duration)
    print(f"Playing note: {freq:.2f} Hz for {note_duration:.2f} sec (quarter offset {quarter_offset})")

print("Performance complete.")

fs.delete()
