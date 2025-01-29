import argparse
import threading
import queue
import numpy as np
import pyaudio
from typing import List, Tuple
from music21 import converter, note, chord
from time import sleep, time


# ----------------------- Synthesizer Function ----------------------- #

def synthesize_cello(frequency: float, duration: float, initial_phase: float = 0.0, sample_rate: int = 44100) -> Tuple[np.ndarray, float]:
    """
    Synthesize a cello note as a waveform (NumPy array) with phase continuity.

    Args:
        frequency (float): The frequency of the note (Hz).
        duration (float): Duration of the note in seconds.
        initial_phase (float): The initial phase in radians. Defaults to 0.0.
        sample_rate (int): Sampling rate in Hz. Defaults to 44100.

    Returns:
        Tuple[np.ndarray, float]: 
            - Waveform of the synthesized cello note.
            - Final phase in radians.
    """
    # Time vector
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Initialize waveform with the initial phase
    waveform = np.sin(2 * np.pi * frequency * t + initial_phase)

    # Add harmonics (approximation of cello sound)
    harmonics = [0.5, 0.3, 0.2, 0.1]  # Amplitude ratios for harmonics
    for i, amp in enumerate(harmonics, start=2):
        waveform += amp * np.sin(2 * np.pi * frequency * i * t + initial_phase)

    # Corrected Envelope (ADSR)
    attack_time = 0.05 * duration  # seconds
    release_time = 0.05 * duration  # seconds
    sustain_level = 0.7  # Amplitude level (0 to 1)

    attack_samples = int(attack_time * sample_rate)
    release_samples = int(release_time * sample_rate)
    sustain_samples = len(t) - attack_samples - release_samples

    if sustain_samples < 0:
        # Adjust the envelope if the note is too short
        attack_samples = int(0.3 * len(t))
        release_samples = int(0.3 * len(t))
        sustain_samples = len(t) - attack_samples - release_samples
        if sustain_samples < 0:
            attack_samples = release_samples = len(t) // 2
            sustain_samples = len(t) - attack_samples - release_samples

    envelope = np.concatenate([
        np.linspace(0, 1, attack_samples),  # Attack
        np.ones(sustain_samples) * sustain_level,  # Sustain
        np.linspace(sustain_level, 0, release_samples)  # Release
    ])
    envelope = envelope[:len(t)]  # Ensure envelope matches waveform length

    waveform *= envelope

    # Normalize waveform to prevent clipping
    max_amp = np.max(np.abs(waveform))
    if max_amp > 0:
        waveform /= max_amp

    # Calculate final phase
    final_phase = (2 * np.pi * frequency * duration + initial_phase) % (2 * np.pi)

    return waveform.astype(np.float32), final_phase

# ----------------------- MIDI Parsing Functions ----------------------- #

def list_instruments(midi_file_path: str) -> List[str]:
    """
    Parses the MIDI file and returns a list of instrument names with their indices.

    Args:
        midi_file_path (str): Path to the MIDI file.

    Returns:
        List[str]: List of instrument names.
    """
    # Parse the MIDI file
    try:
        midi_stream = converter.parse(midi_file_path)
    except Exception as e:
        print(f"Error parsing MIDI file: {e}")
        return []

    # Get all parts
    parts = midi_stream.parts

    instrument_names = []

    for i, part in enumerate(parts):
        # Attempt to get the instrument for the part
        instr = part.getInstrument(returnDefault=False)
        if instr:
            instr_name = instr.instrumentName
        else:
            # If no instrument is found, assign a default name
            instr_name = "Unknown Instrument"
        instrument_names.append(instr_name)

    # Print the list of instruments with their indices
    print("\nList of Instruments in the MIDI File:")
    for idx, name in enumerate(instrument_names):
        print(f"Index {idx}: {name}")

    return instrument_names

def midi_to_notes(
    midi_file_path: str,
    tempo_bpm: float,
    instrument_index: int
) -> List[Tuple[float, float, float]]:
    """
    Parses a MIDI file and returns a list of tuples containing
    (frequency in Hz, duration in seconds, timestamp in seconds)
    for each note from the specified instrument.

    Args:
        midi_file_path (str): Path to the MIDI file.
        tempo_bpm (float): Tempo in Beats Per Minute (BPM).
        instrument_index (int): Index of the instrument to extract notes from.

    Returns:
        List[Tuple[float, float, float]]: List of (frequency, duration, timestamp) tuples.
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

# ----------------------- Synthesizer and Playback ----------------------- #

def synthesize_notes(notes: List[Tuple[float, float, float]], audio_queue: queue.Queue, sample_rate: int = 44100, stop_event: threading.Event = None):
    """
    Synthesizes notes and writes them to the audio queue based on their timestamps.

    Args:
        notes (List[Tuple[float, float, float]]): List of (frequency, duration, timestamp) tuples.
        audio_queue (queue.Queue): Queue to hold synthesized audio frames.
        sample_rate (int): Sampling rate in Hz.
        stop_event (threading.Event): Event to signal thread termination.
    """
    if not notes:
        return

    # Sort notes by timestamp to ensure correct order
    notes = sorted(notes, key=lambda x: x[2])

    # Initialize phase
    current_phase = 0.0

    # Reference start time
    start_time = time()

    for i, (freq, dur, ts) in enumerate(notes):
        if stop_event and stop_event.is_set():
            print("Synthesizer thread received stop signal.")
            break

        # Calculate the scheduled time for this note
        scheduled_time = start_time + ts

        # Current time
        now = time()

        # Time to wait before synthesizing this note
        wait_time = scheduled_time - now

        if wait_time > 0:
            sleep(wait_time)

        # Synthesize the note
        waveform, final_phase = synthesize_cello(freq, dur, initial_phase=current_phase, sample_rate=sample_rate)

        # Split the waveform into smaller frames (e.g., 1024 samples)
        frame_size = 1024
        num_full_frames = len(waveform) // frame_size
        remaining_samples = len(waveform) % frame_size

        # Enqueue full frames
        for j in range(num_full_frames):
            frame = waveform[j*frame_size : (j+1)*frame_size]
            try:
                audio_queue.put(frame, timeout=1.0)  # Block if queue is full
            except queue.Full:
                print("Warning: Audio queue is full. Dropping frame.")
                if stop_event and stop_event.is_set():
                    break

        # Enqueue remaining samples as a smaller frame
        if remaining_samples > 0 and (not stop_event or not stop_event.is_set()):
            frame = waveform[-remaining_samples:]
            try:
                audio_queue.put(frame, timeout=1.0)
            except queue.Full:
                print("Warning: Audio queue is full. Dropping remaining samples.")

        # Update the phase for the next note
        current_phase = final_phase

    print("Synthesizer thread has finished processing notes.")

def callback(in_data, frame_count, time_info, status, audio_queue: queue.Queue, stop_event: threading.Event):
    """
    PyAudio callback function to stream audio data.

    Args:
        in_data: Input data (unused).
        frame_count (int): Number of frames to read.
        time_info: Time information.
        status: Status flags.
        audio_queue (queue.Queue): Queue to read audio data from.
        stop_event (threading.Event): Event to signal callback termination.

    Returns:
        Tuple[bytes, int]: Audio data and flag indicating whether to continue.
    """
    try:
        # Attempt to retrieve data from the queue
        data = audio_queue.get(timeout=0.1)
    except queue.Empty:
        # If no data is available, output silence
        data = np.zeros(frame_count, dtype=np.float32)
    else:
        # If data is longer than frame_count, split it and put the rest back
        if len(data) > frame_count:
            remaining = data[frame_count:]
            data = data[:frame_count]
            try:
                audio_queue.put_nowait(remaining)
            except queue.Full:
                print("Warning: Audio queue overflow. Dropping excess audio data.")

        elif len(data) < frame_count:
            # If data is shorter, pad with zeros
            data = np.pad(data, (0, frame_count - len(data)), 'constant')

    if stop_event.is_set() and audio_queue.empty():
        return (data.tobytes(), pyaudio.paComplete)
    else:
        return (data.tobytes(), pyaudio.paContinue)

def main():
    parser = argparse.ArgumentParser(description='Real-time Cello Synthesizer')
    parser.add_argument('midi_file', type=str, help='Path to the MIDI file')
    parser.add_argument('--tempo', type=float, default=120.0, help='Tempo in BPM')
    parser.add_argument('--instrument', type=int, default=0, help='Instrument index')
    args = parser.parse_args()

    midi_file = args.midi_file
    tempo = args.tempo
    instrument_index = args.instrument

    # Parse MIDI and get notes
    try:
        notes = midi_to_notes(midi_file, tempo, instrument_index)
    except Exception as e:
        print(f"Error extracting notes: {e}")
        return

    if not notes:
        print("No notes found for the selected instrument.")
        return

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Define buffer parameters
    BUFFER_SIZE = 100  # Increased buffer size to accommodate more frames
    AUDIO_BUFFER_SIZE = 1024  # Number of frames per buffer read

    # Create a queue to hold audio frames
    audio_queue = queue.Queue(maxsize=BUFFER_SIZE)

    # Create a stop event
    stop_event = threading.Event()

    # Open audio stream
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=44100,
                    output=True,
                    frames_per_buffer=AUDIO_BUFFER_SIZE,
                    stream_callback=lambda in_data, frame_count, time_info, status: callback(in_data, frame_count, time_info, status, audio_queue, stop_event))

    # Start the stream
    stream.start_stream()

    # Start the synthesizer thread
    synth_thread = threading.Thread(target=synthesize_notes, args=(notes, audio_queue, 44100, stop_event))
    synth_thread.start()

    print("Synthesizing and playing notes in real-time... Press Ctrl+C to stop.")

    try:
        while stream.is_active():
            sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping playback...")
        stop_event.set()
    finally:
        # Wait for the synthesizer thread to finish
        synth_thread.join()

        # Allow some time for remaining audio to play
        sleep(1)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()

        # Terminate PyAudio
        p.terminate()

        print("Playback finished.")

if __name__ == "__main__":
    main()
