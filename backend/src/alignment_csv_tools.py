from music21 import converter, instrument, note, stream
import music21
import math
import pandas as pd
import pretty_midi

def create_alignment_csv(csv_out_uri, ref_mxml_uri):
    mxml_baseline = converter.parse(ref_mxml_uri)
    
    beat = []
    pitch = []
    duration = []
    tie = []
    midi = []

    ref_ts = []
    live_ts = []

    mxml_parts = _extract_all_parts(mxml_baseline)
    for part in mxml_parts:
        part_notes = part.flatten().notes
        for n in part_notes:
            tie_type = n.tie.type if n.tie else "no"

            beat.append(n.getOffsetInHierarchy(part))
            pitch.append(n.pitch)
            duration.append(n.quarterLength)
            tie.append(tie_type)
            midi.append(n.pitch.midi)
            ref_ts.append(None)
            live_ts.append(None)


    df = pd.DataFrame(
        {
            "beat": beat,
            "duration": duration,
            "pitch": pitch,
            "tie": tie,
            "midi": midi,
            "ref_ts": ref_ts,
            "live_ts": live_ts,
        }
    )

    df.to_csv(csv_out_uri, sep=",", index=False)

def populate_alignment_csv(csv_uri, ref_midi_uri, live_midi_uri=None):
    df = pd.read_csv(csv_uri)

    midi_ref = pretty_midi.PrettyMIDI(ref_midi_uri)
    df["ref_ts"] = _align_midi_mxml(df, midi_ref)

    if live_midi_uri:
        midi_live = pretty_midi.PrettyMIDI(live_midi_uri)
        df["live_ts"] = _align_midi_mxml(df, midi_live)

    df.to_csv(csv_uri, sep=",", index=False)

    
def convert_old_csv(csv_uri, out_uri, ref_mxml_uri):
    create_alignment_csv(out_uri, ref_mxml_uri)

    df_old = pd.read_csv(csv_uri)
    df_new = pd.read_csv(out_uri)

    ref_ts = df_old["baseline_time"]
    live_ts = df_old["altered_time"]

    df_new["ref_ts"] = ref_ts
    df_new["live_ts"] = live_ts

    df_new.to_csv(out_uri, sep=",", index=False)

def mirror_alignment_csv(csv_uri):    
    df = pd.read_csv(csv_uri)
    if "ref_ts" not in df:
        raise ValueError("No ref_ts column to mirror!")
    df["live_ts"] = df["ref_ts"]
    
    df.to_csv(csv_uri, sep=",", index=False)

def _extract_all_parts(m21obj):
    parts = []

    if isinstance(m21obj, stream.Part): # type: ignore
        parts.append(m21obj)

    elif isinstance(m21obj, (stream.Score, stream.Opus)): # type: ignore
        for sub in m21obj:
            parts.extend(_extract_all_parts(sub))

    elif isinstance(m21obj, stream.Stream): # type: ignore
        for sub in m21obj:
            parts.extend(_extract_all_parts(sub))

    return parts

def _align_midi_mxml(mxml_df: pd.DataFrame, midi_pm: pretty_midi.PrettyMIDI):
    mxml_idx = 0
    midi_ts_seq = []

    for instruments in midi_pm.instruments:
        for midi_idx in range(0, len(instruments.notes)):
            note = instruments.notes[midi_idx]
            
            if mxml_df["tie"][mxml_idx] == "start":
                mxml_dur = 0.0
                mxl_tie_durs = []
                
                while True:
                    mxml_dur += mxml_df["duration"][mxml_idx]
                    mxl_tie_durs.append(mxml_df["duration"][mxml_idx])
                    if mxml_df["tie"][mxml_idx] == "stop":
                        break
                    mxml_idx += 1

                mxl_tie_ratios = [td / mxml_dur for td in mxl_tie_durs]
                print(mxl_tie_ratios)
                nxt_note = instruments.notes[midi_idx + 1]
                midi_dur = nxt_note.start - note.start
                interp_start = note.start
                
                for tie_ratio in mxl_tie_ratios:
                    midi_ts_seq.append(interp_start)
                    interp_start += midi_dur * tie_ratio

                if (not math.isclose(interp_start, nxt_note.start)):
                    raise ValueError("Tie fragmentation failed", interp_start, nxt_note.start)
            else:
                if note.pitch != mxml_df["midi"][mxml_idx]:
                    raise ValueError(f"MIDI doesn't match MusicXML at idx ${mxml_idx}: {note.pitch} vs {mxml_df['midi'][mxml_idx]}")
                mxml_idx += 1
                midi_ts_seq.append(note.start)

    return midi_ts_seq


if __name__ == "__main__":
    mxl = "data/musicxml/schumann_melody.musicxml"
    out = "data/alignments/schumann_melody_100bpm.csv"
    create_alignment_csv(out, mxl)

    # mxl = "data/musicxml/schumann_melody.musicxml"
    # out = "data/alignments/schumann_melody_new_excerpt.csv"
    # mirror_alignment_csv(out)

    populate_alignment_csv(out, "data/midi/ode_to_joy_baseline.mid", "data/midi/ode_to_joy_altered.mid")