import os
import glob
from pathlib import Path
import pretty_midi
import numpy as np
import librosa
from audio_generator import AudioGenerator

def get_bpm(midi_path: str) -> float:
    pm = pretty_midi.PrettyMIDI(midi_path)
    # returns two arrays: times (s) and tempi (BPM)
    _, tempi = pm.get_tempo_changes()
    if len(tempi) == 0:
        # no explicit tempo → default 120 BPM
        return 120.0
    # return the initial tempo
    return float(tempi[0])

def calculate_piano_roll_fps(columns_per_beat: int, BPM: float) -> float:
    """
    Calculate frames per second (fps) for a piano roll given a resolution in columns per beat
    and a tempo in beats per minute (BPM).

    Parameters:
        columns_per_beat (int): The number of columns per beat.
        BPM (float): Tempo in beats per minute.

    Returns:
        float: Frames per second (columns per second) for the piano roll.
    """
    beats_per_second = BPM / 60.0
    fps = columns_per_beat * beats_per_second
    return fps

def midi_to_piano_roll(midi_path: str) -> np.ndarray:
    """
    Convert a MIDI file into a piano roll representation.

    Parameters
    ----------
    midi_path : str
        Path to the MIDI file.

    Returns
    -------
    np.ndarray
        A 2D numpy array representing the piano roll.
    """
    # Load the MIDI file
    pm = pretty_midi.PrettyMIDI(midi_path)

    # Get the solo instrument (first instrument in the MIDI file)
    solo: pretty_midi.Instrument = pm.instruments[0]

    # Get the tempo in BPM
    BPM = get_bpm(midi_path)

    # Calculate the frames per second (fps) for the piano roll
    fps = calculate_piano_roll_fps(columns_per_beat=4, BPM=BPM)

    # Get the piano roll representation
    # The piano roll is a 2D array where rows correspond to MIDI pitches and columns to time frames
    # The values in the array are the velocities of the notes at that time frame
    piano_roll = solo.get_piano_roll(fs=fps)  # fs is the sampling rate (frames per second)

    return piano_roll

def synthesize_midi_to_audio(midi_path: str, output_path: str) -> None:
    print(f"Generating audio from {midi_path}")
    print(f"Output path: {output_path}")
    generator = AudioGenerator(midi_path, soundfont_path='..\..\soundfonts\FluidR3_GM.sf2')  # Placeholder, will be set in process_piece
    generator.generate_audio(output_path, tempo=None, sample_rate=22050)  # Generate audio from MIDI

def create_spectrogram(audio_path: str, n_fft: int = 2048, hop_length: int = 512) -> np.ndarray:
     # Define audio processing parameters
        sr = 22050                   # Sample rate in Hz
        n_fft = 2048                 # FFT window size
        spec_fps = 20                     # Frames per second
        hop_length = int(sr / spec_fps)   # Hop length; ~1102 samples per frame
        n_mels = 78                  # Number of mel bins (log-frequency bands)
        fmin = 60                    # Minimum frequency (Hz)
        fmax = 6000                  # Maximum frequency (Hz)

        # Load audio and compute its spectrogram
        audio, _ = librosa.load(audio_path, sr=sr)
        spec = librosa.feature.melspectrogram(
                            y=audio,
                            sr=sr,
                            n_fft=n_fft,
                            hop_length=hop_length,
                            n_mels=n_mels,
                            fmin=fmin,
                            fmax=fmax
                        )
        # Convert the power spectrogram to a logarithmic (dB) scale
        spectrogram = librosa.power_to_db(spec, ref=np.max)

        return spectrogram


def process_piece(piece_dir: Path, output_dir: Path):
    """
    piece_dir/
      piece_name_vn_vn/
        piece_name_altered_solos/
          solo_baseline.mid
          solo_accelerando.mid
          ...
        piece_name_analysis/
          solo_note_timings.csv
    """
    name = piece_dir.name.replace("_vn_vn", "")
    altered_dir = piece_dir / f"{name}_altered_pieces"
    analysis_dir = piece_dir / f"{name}_analysis"
    out_piece = output_dir / name
    out_piece.mkdir(parents=True, exist_ok=True)

    # 1) Baseline piano roll
    baseline_midi = altered_dir / "baseline.mid"
    # ---- CALL YOUR PIANO-ROLL FUNCTION ----
    piano_roll = midi_to_piano_roll(str(baseline_midi))
    np.save(out_piece/"piano_roll.npy", piano_roll)

    # 2) Synth & spectrogram for each altered solo
    for midi_path in sorted(altered_dir.glob("*.mid")):
        tag = midi_path.stem.replace("solo_", "")  # e.g. "accelerando"
        audio_dir = out_piece
        spec_path  = out_piece / f"spec_{tag}.npy"

        # ---- CALL YOUR SYNTHESIS FUNCTION ----
        synthesize_midi_to_audio(str(midi_path), str(audio_dir))

        # ---- CALL YOUR SPECTROGRAM FUNCTION ----
        spec = create_spectrogram(str(audio_dir / "instrument_0.wav"))
        # Save the spectrogram
        np.save(spec_path, spec)

    # 3) Copy or preprocess the analysis CSV if you need it
    csv_in  = analysis_dir / "solo_note_timings.csv"
    csv_out = out_piece   / "solo_note_timings.csv"
    if csv_in.exists():
        # simply copy it, or parse it yourself here
        import shutil
        shutil.copy(csv_in, csv_out)
    else:
        print(f"⚠️  Missing analysis CSV for {name}")

def main(data_root: str, output_root: str):
    data_root   = Path(data_root)
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    for piece_dir in sorted(data_root.iterdir()):
        print(f"Checking {piece_dir.name}...")
        if not piece_dir.is_dir():
            print(f"⚠️  {piece_dir.name} is not a directory")
            continue
        piece_name = piece_dir.name.replace("_vn_vn", "")
        # quick sanity check
        if not (piece_dir / f"{piece_name}_altered_solos").exists():
            print(f"⚠️  Missing altered solos for {piece_name}")
            continue

        print(f"Processing {piece_name}...")
        process_piece(piece_dir, output_root)

if __name__ == "__main__":
    # import argparse

    # p = argparse.ArgumentParser()
    # p.add_argument("data_root",  help="root folder containing all piece subfolders")
    # p.add_argument("output_root", help="where to store piano rolls & spectrograms")
    # args = p.parse_args()

    main("URMP_altered", "dataset")
