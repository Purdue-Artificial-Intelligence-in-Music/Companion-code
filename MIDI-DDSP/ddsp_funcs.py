import numpy as np
import midi_ddsp
import pretty_midi
import numpy as np
import librosa
import matplotlib.pyplot as plt
import tensorflow.compat.v2 as tf
from IPython.display import Javascript
import IPython.display as ipd
import pandas as pd
import music21

from midi_ddsp import load_pretrained_model
from midi_ddsp.utils.training_utils import set_seed, get_hp
from midi_ddsp.hparams_synthesis_generator import hparams as hp
from midi_ddsp.modules.get_synthesis_generator import get_synthesis_generator, get_fake_data_synthesis_generator
from midi_ddsp.modules.expression_generator import ExpressionGenerator, get_fake_data_expression_generator
from midi_ddsp.utils.audio_io import save_wav
from midi_ddsp.utils.midi_synthesis_utils import synthesize_mono_midi, synthesize_bach, note_list_to_sequence
from midi_ddsp.midi_ddsp_synthesize import synthesize_midi
from midi_ddsp.utils.inference_utils import ensure_same_length, expression_generator_output_to_conditioning_df, conditioning_df_to_audio, get_process_group
from midi_ddsp.data_handling.instrument_name_utils import INST_NAME_TO_ID_DICT, INST_NAME_LIST, INST_NAME_TO_MIDI_PROGRAM_DICT,MIDI_PROGRAM_TO_INST_ID_DICT,MIDI_PROGRAM_TO_INST_NAME_DICT

EDIT_DF_NAME_ORDER = ['volume', 'vol_fluc', 'vol_peak_pos', 'vibrato', 'brightness', 'attack', 'pitch', 'note_length']

COND_DF_NAME_ORDER = ['volume', 'vol_fluc', 'vibrato', 'brightness', 'attack', 'vol_peak_pos', 'pitch', 'onset', 'offset', 'note_length']

GAIN_ADJUST_DB_DICT = {    
    'string_set': {    
        'Soprano': 2,
        'Alto': 2,
        'Tenor': -1,
        'Bass': -1,
    },
    'woodwind_set': {    
        'Soprano': 1.5,
        'Alto': 1.2,
        'Tenor': 0,
        'Bass': 1.8,
    },
    'brasswind_set': {    
        'Soprano': 2,
        'Alto': 2,
        'Tenor': 5.6,
        'Bass': 2.9,
    },

}

def plot_spec(wav, sr, title='', play=True, vmin=-8, vmax=1, save_path=None):
    D = np.log(np.abs(librosa.stft(wav, n_fft=512 + 256)))
    librosa.display.specshow(D, sr=sr, vmin=vmin, vmax=vmax, cmap='magma')
    plt.title(title)
    wav = np.clip(wav, -1, 1)
    if play:
        ipd.display(ipd.Audio(wav, rate=sr))
    if save_path:
        plt.savefig(save_path)
        plt.close()

def conditioning_df_to_edit_df(conditioning_df):
  edit_df = conditioning_df.copy()
  return edit_df[EDIT_DF_NAME_ORDER]

def edit_df_to_conditioning_df(edit_df):
  conditioning_df = edit_df.copy()
  note_length = conditioning_df['note_length'].values
  offset = np.cumsum(note_length)
  onset = np.concatenate([[0],offset[:-1]])
  conditioning_df['onset']=onset
  conditioning_df['offset']=offset
  return conditioning_df[COND_DF_NAME_ORDER]

def get_t(bend):
    return int(bend.time * 250.0)

def apply_mult(vals_to_change, bend_val, total_bend=2):
    semitones = np.float32(bend_val) / 8192 * total_bend
    mult = np.power(2, semitones / 12)
    vals_to_change *= mult
    return vals_to_change


def gen_pitch_bend(f0_ori, midi, inst=0):
    out = f0_ori.numpy()
    bends = midi.instruments[inst].pitch_bends
    if len(bends) == 0:
        return f0_ori
    bends.sort(key=(lambda x : x.time))
    if bends[0].time != 0:
        bends.insert(0, pretty_midi.PitchBend(pitch=0, time=0))
    last_good_idx = -1
    for i in range(len(bends) - 1):
        bend1 = bends[i]
        bend2 = bends[i+1]
        idx1 = get_t(bend1)
        idx2 = get_t(bend2)
        if idx1 - last_good_idx > 0:
            last_good_idx = idx1
            if idx2 - idx1 == 0:
                out[idx1] = apply_mult(f0_ori[idx1], bend1.pitch)
            else:
                out[idx1:idx2] = apply_mult(f0_ori[idx1:idx2], bend1.pitch)
    out[get_t(bends[len(bends)-1]):] = apply_mult(f0_ori[get_t(bends[len(bends)-1]):], bends[len(bends)-1].pitch)
    out = tf.convert_to_tensor(out)
    out = out[tf.newaxis, ..., tf.newaxis]
    return out

def resynth_audio(midi, midi_synth_params, synthesis_generator, instrument_id):
    f0_ori = midi_synth_params['f0_hz'][0,...,0]
    amps_ori = midi_synth_params['amplitudes'].numpy()[0,...,0]
    noise_ori = midi_synth_params['noise_magnitudes'].numpy()
    hd_ori = midi_synth_params['harmonic_distribution'].numpy()

    f0_changed = gen_pitch_bend(f0_ori, midi)

    amps_changed = amps_ori
    amps_changed = amps_changed[tf.newaxis, ..., tf.newaxis]
    noise_changed = noise_ori
    hd_changed = hd_ori

    # Resynthesis the audio using DDSP
    processor_group = get_process_group(midi_synth_params['amplitudes'].shape[1], use_angular_cumsum=True)
    midi_audio_changed = processor_group({'amplitudes': amps_changed,
                            'harmonic_distribution': noise_changed,
                            'noise_magnitudes': hd_changed,
                            'f0_hz': f0_changed,},
                            verbose=False)
    if synthesis_generator.reverb_module is not None:
        midi_audio_changed = synthesis_generator.reverb_module(midi_audio_changed, reverb_number=instrument_id, training=False)
    
    return midi_audio_changed

def get_closest_prev_time(list, idx):
    '''
    Inputs:
    - list: a list of pretty_midi.ControlChange events
    - idx: a float representing a time value
    Returns:
    - An element of list which is the event that occurs closest to but before time idx
    '''
    if len(list) == 0:
        return None
    for j in range(len(list)):
        if abs(list[j].time - idx) < 1e-4:
            return list[j]
        elif list[j].time > idx:
            if j == 0:
                return None
            return list[j - 1]
    return None

def get_notes_with_artic(midi, conditioning_df, inst=0, midi_cc=20):
    '''
    Inputs:
    - midi: PrettyMIDI object
    - conditioning_df: MIDI-DDSP-generated conditioning Pandas dataframe
    - inst: the instrument number
    - midi_cc: the midi_cc number to check
            case "staccato": midi_cc = 20
            case "tenuto": midi_cc = 21
            case "marcato": midi_cc = 22
            case "accent": midi_cc = 23
            case "slur": midi_cc = 24
    - idx: a float representing a time value
    Returns:
    - note_idx_list: a list of row indices in conditioning_df which are played when midi_cc is HIGH (>64)
    '''
    cc_list = []
    for ccs in midi.instruments[inst].control_changes:
        if ccs.number == 24 and ccs.value == 0:
            ccs.time += 1e-2
    for ccs in midi.instruments[inst].control_changes:
        if ccs.number == midi_cc:
            cc_list.append(ccs)
    note_idx_list = []
    for i in range(len(conditioning_df)):
        if conditioning_df.loc[i, "volume"] > 1e-3:
            x = get_closest_prev_time(cc_list, np.float64(conditioning_df.loc[i, "onset"])/250.0)
            if x is not None and x.value > 64:
                note_idx_list.append(i)
    return note_idx_list

def modify_params_with_artic(midi, conditioning_df, inst=0, midi_cc=20, param_name="volume", func=(lambda x : x)):
    '''
    This function takes in the below inputs, and modifies the values in conditioning_df's column param_name by running them through func.
    Inputs:
    - midi: PrettyMIDI object
    - conditioning_df: MIDI-DDSP-generated conditioning Pandas dataframe
    - inst: the instrument number
    - midi_cc: the midi_cc number to check
    - param_name: a name of a column in conditioning_df
    - func: a processing function pointer
    Returns:
    - Nothing
    How to get output:
    - Stored in conditioning_df
    '''
    note_idx_list = get_notes_with_artic(midi, conditioning_df, inst=inst, midi_cc=midi_cc)
    for idx in note_idx_list:
        conditioning_df.loc[idx, param_name] = func(conditioning_df.loc[idx, param_name])

def make_excessive_amount_of_vibrato(conditioning_df, start, end, vibrato_val):
    start = int(start * 250)
    end = int(end * 250)
    for i in range(len(conditioning_df)):
        s = conditioning_df.loc[i, "onset"]
        e = conditioning_df.loc[i, "offset"]
        if s >= start and e <= end:
            conditioning_df.loc[i, "vibrato"] = vibrato_val

def modify_params_with_artic_full(midi, conditioning_df, inst_id, synthesis_generator, inst=0, add_pitch_bends_slurs = True):
    '''
    This function takes in the below inputs, and modifies the values in conditioning_df's column param_name by running them through func.
    Inputs:
    - midi: PrettyMIDI object
    - conditioning_df: MIDI-DDSP-generated conditioning Pandas dataframe
    - inst: the instrument number
    - func: a processing function pointer
    Returns:
    - Nothing
    How to get output:
    - Stored in conditioning_df
        case "staccato": midi_cc = 20
        case "tenuto": midi_cc = 21
        case "marcato": midi_cc = 22
        case "accent": midi_cc = 23
        case "slur": midi_cc = 24
    '''

    stacc_list = get_notes_with_artic(midi, conditioning_df, inst=inst, midi_cc=20)
    tenuto_list = get_notes_with_artic(midi, conditioning_df, inst=inst, midi_cc=21)
    marc_list = get_notes_with_artic(midi, conditioning_df, inst=inst, midi_cc=22)
    accent_list = get_notes_with_artic(midi, conditioning_df, inst=inst, midi_cc=23)
    slur_list = get_notes_with_artic(midi, conditioning_df, inst=inst, midi_cc=24)
    rows_to_add = []
    rows_to_remove = []
    for idx in stacc_list:
        conditioning_df.loc[idx, "brightness"] = conditioning_df.loc[idx, "brightness"] / 3.0
        conditioning_df.loc[idx, "vibrato"] = conditioning_df.loc[idx, "vibrato"] / 5.0
        conditioning_df.loc[idx, "attack"] = min(max(conditioning_df.loc[idx, "attack"], 0.2) * 1.2, 1)
        shorten_length = int(float(conditioning_df.loc[idx, "note_length"]) / 4.0)
        if conditioning_df.loc[idx+1, "volume"] == 0 and conditioning_df.loc[idx+1, "pitch"] == 0:
            conditioning_df.loc[idx, "offset"] = max(conditioning_df.loc[idx, "onset"], conditioning_df.loc[idx, "offset"] - shorten_length)
            conditioning_df.loc[idx, "note_length"] = conditioning_df.loc[idx, "offset"] - conditioning_df.loc[idx, "onset"]
            conditioning_df.loc[idx+1, "onset"] = conditioning_df.loc[idx, "offset"]
            conditioning_df.loc[idx+1, "note_length"] = conditioning_df.loc[idx+1, "offset"] - conditioning_df.loc[idx+1, "onset"]
        else:
            blank_row = conditioning_df.loc[0].copy()
            blank_row.loc["offset"] = conditioning_df.loc[idx, "offset"]
            conditioning_df.loc[idx, "offset"] = min(conditioning_df.loc[idx, "onset"], conditioning_df.loc[idx, "offset"] - shorten_length)
            conditioning_df.loc[idx, "note_length"] = min(0, conditioning_df.loc[idx, "note_length"] - shorten_length)
            blank_row.loc["onset"] = conditioning_df.loc[idx, "offset"]
            blank_row.loc["note_length"] = blank_row.loc["offset"] - blank_row.loc["onset"]
            rows_to_add.append(idx, blank_row)
    for idx in marc_list:
        conditioning_df.loc[idx, "brightness"] = max(conditioning_df.loc[idx, "brightness"] * 1.1, 1.0)
        conditioning_df.loc[idx, "vibrato"] = conditioning_df.loc[idx, "vibrato"] / 5.0
        conditioning_df.loc[idx, "attack"] = min(max(conditioning_df.loc[idx, "attack"], 0.2) * 1.2, 1)
        shorten_length = int(float(conditioning_df.loc[idx, "note_length"]) / 3.0)
        if conditioning_df.loc[idx+1, "volume"] == 0 and conditioning_df.loc[idx+1, "pitch"] == 0:
            conditioning_df.loc[idx, "offset"] = max(conditioning_df.loc[idx, "onset"], conditioning_df.loc[idx, "offset"] - shorten_length)
            conditioning_df.loc[idx, "note_length"] = conditioning_df.loc[idx, "offset"] - conditioning_df.loc[idx, "onset"]
            conditioning_df.loc[idx+1, "onset"] = conditioning_df.loc[idx, "offset"]
            conditioning_df.loc[idx+1, "note_length"] = conditioning_df.loc[idx+1, "offset"] - conditioning_df.loc[idx+1, "onset"]
        else:
            blank_row = conditioning_df.loc[0].copy()
            blank_row.loc["offset"] = conditioning_df.loc[idx, "offset"]
            conditioning_df.loc[idx, "offset"] = min(conditioning_df.loc[idx, "onset"], conditioning_df.loc[idx, "offset"] - shorten_length)
            conditioning_df.loc[idx, "note_length"] = min(0, conditioning_df.loc[idx, "note_length"] - shorten_length)
            blank_row.loc["onset"] = conditioning_df.loc[idx, "offset"]
            blank_row.loc["note_length"] = blank_row.loc["offset"] - blank_row.loc["onset"]
            rows_to_add.append(idx, blank_row)
    for idx in accent_list:
        conditioning_df.loc[idx, "brightness"] = min(conditioning_df.loc[idx, "brightness"] * 1.1, 1.0)
        conditioning_df.loc[idx, "attack"] = min(max(conditioning_df.loc[idx, "attack"], 0.2) * 1.2, 1)
    for idx in slur_list:
        if conditioning_df.loc[idx+1, "volume"] == 0 and conditioning_df.loc[idx+1, "pitch"] == 0:
            if slur_list.count(idx+2) > 0:
                conditioning_df.loc[idx, "offset"] = conditioning_df.loc[idx+1, "offset"]
                conditioning_df.loc[idx, "note_length"] = conditioning_df.loc[idx, "offset"] - conditioning_df.loc[idx, "onset"]
                rows_to_remove.append(idx+1)
    for idx in tenuto_list:
        conditioning_df.loc[idx, "vibrato"] = conditioning_df.loc[idx, "vibrato"] / 2.0
        conditioning_df.loc[idx, "attack"] = conditioning_df.loc[idx, "attack"] * 0.8
    for idx in rows_to_remove:
        for elem in rows_to_add:
            if idx == elem[0]:
                rows_to_add.remove(elem[0])
            elif idx < elem[0]:
                elem[0] -= 1
        conditioning_df.drop(idx)
    for elem in rows_to_add:
        for elem2 in rows_to_add:
            if elem2[0] > elem[0]:
                elem2[0] += 1
        conditioning_df = pd.concat([conditioning_df.loc[:elem[0]], elem[1], conditioning_df.loc[elem[0]:]]).reset_index(drop=True)
    
    df_copy = conditioning_df.copy()

    midi_audio, _, midi_synth_params = conditioning_df_to_audio(synthesis_generator, conditioning_df, tf.constant([inst_id]), display_progressbar=True)

    if not add_pitch_bends_slurs:
        midi_audio_changed = midi_audio
        f0_changed = None
    else:
        slur_list = get_notes_with_artic(midi, conditioning_df, inst=inst, midi_cc=24)

        conditioning_df

        curr_chain = []
        list_chains = []
        rows_to_remove = []
        for i in range(len(slur_list)):
            if curr_chain == []:
                curr_chain.append(slur_list[i])
            elif slur_list[i] == slur_list[i-1]+1:
                curr_chain.append(slur_list[i])
                rows_to_remove.append(slur_list[i])
            else:
                list_chains.append(curr_chain)
                curr_chain = []
        if curr_chain != []:
            list_chains.append(curr_chain)
        for chain in list_chains:
            if len(chain) == 1:
                continue
            first_idx = chain[0]
            orig_pitch = conditioning_df.loc[chain[0], "pitch"]
            conditioning_df.loc[first_idx, "offset"] = conditioning_df.loc[chain[len(chain)-1], "offset"]
            conditioning_df.loc[first_idx, "note_length"] = conditioning_df.loc[first_idx, "offset"] - conditioning_df.loc[first_idx, "onset"]
        
        conditioning_temp = conditioning_df.drop(rows_to_remove)

        _, _, midi_synth_params = conditioning_df_to_audio(synthesis_generator, conditioning_temp, tf.constant([inst_id]), display_progressbar=True)

        f0_ori = midi_synth_params['f0_hz'][0,...,0]
        f0_changed = f0_ori.numpy()

        bends = midi.instruments[inst].pitch_bends
        if len(bends) != 0:
            bends.sort(key=(lambda x : x.time))
            if bends[0].time != 0:
                bends.insert(0, pretty_midi.PitchBend(pitch=0, time=0))
            last_good_idx = -1
            for i in range(len(bends) - 1):
                bend1 = bends[i]
                bend2 = bends[i+1]
                idx1 = get_t(bend1)
                idx2 = get_t(bend2)
                if idx1 - last_good_idx > 0:
                    last_good_idx = idx1
                    if idx2 - idx1 == 0:
                        f0_changed[idx1] = apply_mult(f0_ori[idx1], bend1.pitch)
                    else:
                        f0_changed[idx1:idx2] = apply_mult(f0_ori[idx1:idx2], bend1.pitch)
            f0_changed[get_t(bends[len(bends)-1]):] = apply_mult(f0_ori[get_t(bends[len(bends)-1]):], bends[len(bends)-1].pitch)
        
        for chain in list_chains:
            for idx in chain[1:]:
                p_off = conditioning_df.loc[idx, "pitch"] - orig_pitch
                mult = np.power(2, float(p_off) / 12.0)
                start = conditioning_df.loc[idx, "onset"]
                end = conditioning_df.loc[idx, "offset"]
                f0_changed[start:end] *= mult
            for i in range(len(chain) - 1):
                print(min(70, conditioning_df.loc[chain[i], "note_length"] * 0.3))
                start = int(conditioning_df.loc[chain[i], "onset"] + conditioning_df.loc[chain[i], "offset"] - min(70, conditioning_df.loc[chain[i], "note_length"] * 0.3))
                end = conditioning_df.loc[chain[i], "offset"]
                l = end - start + 1
                if l > 0:
                    f0_changed[start:end+1] = np.linspace(f0_changed[start], f0_changed[end], l)
        
        f0_changed = tf.convert_to_tensor(f0_changed)    
        f0_changed = f0_changed[tf.newaxis, ..., tf.newaxis]

        # Resynthesis the audio using DDSP
        processor_group = get_process_group(midi_synth_params['amplitudes'].shape[1], use_angular_cumsum=True)
        midi_audio_changed = processor_group({'amplitudes': midi_synth_params['amplitudes'],
                                'harmonic_distribution': midi_synth_params['harmonic_distribution'],
                                'noise_magnitudes': midi_synth_params['noise_magnitudes'],
                                'f0_hz': f0_changed,},
                                verbose=False)
        if synthesis_generator.reverb_module is not None:
            midi_audio_changed = synthesis_generator.reverb_module(midi_audio_changed, reverb_number=inst_id, training=False)
    
    return midi_audio_changed, conditioning_temp, df_copy, midi_synth_params, f0_changed
def print_important_things(midi, conditioning_df):
    for note in midi.instruments[0].notes:
        # Prints notes in the first instrument of midi
        print(note)

    for ccs in midi.instruments[0].control_changes:
        # Prints ControlChange msgs in the first instrument of midi
        print(ccs)

    for pb in midi.instruments[0].pitch_bends:
        # Prints ControlChange msgs in the first instrument of midi
        print(pb)

    print(midi.estimate_tempo())

    print(conditioning_df)

def calculate_coeffs(n: float, p: float, q: float):
    assert 0 < n < 1
    assert 0 < p <= 1
    assert 0 <= q <= 1
    assert n <= p
    a = 1/(n*n - n) * (q-1 - n*(1-p)/(n-1))
    b = (1-p)/(n-1) - (n+1)*a
    c = p-b-a
    return a,b,c

def cubic(x, a=0, b=0, c=0, d=0):
    return a * np.power(x, 3) + b * np.power(x, 2) + c * x + d

def cubic_bounded(x, a=0, b=0, c=0, d=0):
    return min(max(cubic(x, a, b, c, d), 0.0), 1.0)

def cubic_interp(x, n, p, q):
    a, b, c = calculate_coeffs(n, p, q)
    return cubic_bounded(x, a, b, c, 0)

def dB_to_val(dB):
    return np.power(10.0, dB / 10.0)

def val_to_dB(val, eps=1e-8):
    if val < 0.0:
        val = eps
    return 10.0 * np.log10(val)

def get_midi_cc_list(midi, inst_num, cc_num):
    cc_out = []
    for cc in midi.instruments[inst_num].control_changes:
        if cc.number == cc_num:
            cc_out.append(cc)
    return cc_out

def get_closest_prev_time_or_return_first(list, idx):
    '''
    Inputs:
    - list: a list of pretty_midi.ControlChange events
    - idx: a float representing a time value
    Returns:
    - An element of list which is the event that occurs closest to but before time idx
    '''
    if len(list) == 0:
        return None
    for j in range(len(list)):
        if abs(list[j].time - idx) < 1e-4:
            return list[j]
        elif list[j].time > idx:
            if j == 0:
                return list[0]
            return list[j - 1]
    return list[0]

def bad_func(x):
    return 1

def apply_cresc_desc(midi, midi_synth_params, synthesis_generator, inst_id, f0_changed=None, eps=1e-8, breath_cc = 2, inst_num = 0, fs=250.0, deriv=0.7):
    cc_list = get_midi_cc_list(midi, inst_num, breath_cc)
    if len(cc_list) == 0:
        amps_changed = midi_synth_params['amplitudes']
    else:
        amps_ori = midi_synth_params['amplitudes'].numpy()[0,...,0]
        amps_new = np.zeros_like(amps_ori)
        eps=1e-8
        for i in range(len(amps_new)):
            curr_amp = amps_ori[i]
            curr_abs_amp = dB_to_val(curr_amp)
            desired_breath = get_closest_prev_time_or_return_first(cc_list, i/250.0)
            desired_abs_amp = desired_breath.value / 128.0
            if i < 10:
                print((curr_abs_amp, desired_abs_amp))
            interp = cubic_interp(curr_abs_amp, desired_abs_amp, 1, 0.7)
            if interp == 0:
                interp = eps
            amps_new[i] = val_to_dB(interp)
        amps_changed = tf.convert_to_tensor(amps_new)    
        amps_changed = amps_changed[tf.newaxis, ..., tf.newaxis]

    processor_group = get_process_group(midi_synth_params['amplitudes'].shape[1], use_angular_cumsum=True)
    if f0_changed is not None:
        midi_audio_changed = processor_group({'amplitudes': amps_changed,
                                'harmonic_distribution': midi_synth_params['harmonic_distribution'],
                                'noise_magnitudes': midi_synth_params['noise_magnitudes'],
                                'f0_hz':  f0_changed,},
                                verbose=False)
    else:
        midi_audio_changed = processor_group({'amplitudes': amps_changed,
                                'harmonic_distribution': midi_synth_params['harmonic_distribution'],
                                'noise_magnitudes': midi_synth_params['noise_magnitudes'],
                                'f0_hz':  midi_synth_params['f0_hz'],},
                                verbose=False)
    
    if synthesis_generator.reverb_module is not None:
        midi_audio_changed = synthesis_generator.reverb_module(midi_audio_changed, reverb_number=inst_id, training=False)

    return midi_audio_changed
    

def mono_midi_to_note_sequence(midi_data, instrument_id, inst_num=0, pitch_offset=0,
                               speed_rate=1):
  """Convert a mono MIDI file to note sequence for expression generator."""
  instrument = midi_data.instruments[inst_num]
  if instrument.is_drum:
    raise ValueError('Cannot synthesize drum')
  note_sequence = note_list_to_sequence(instrument.notes, fs=250,
                                        pitch_offset=pitch_offset,
                                        speed_rate=speed_rate)
  note_sequence['instrument_id'] = instrument_id
  return note_sequence

def generate_audio_from_midi(synth_gen, express_gen, midi_path, instrument, inst_num=0):
    instrument_id = INST_NAME_TO_ID_DICT[instrument]
    midi = pretty_midi.PrettyMIDI(midi_path)
    note_sequence = mono_midi_to_note_sequence(midi,
                                             tf.constant([instrument_id]),
                                             pitch_offset=0,
                                             speed_rate=1)
    expression_generator_outputs = express_gen(note_sequence, out=None,
                                                        training=False)
    conditioning_df = expression_generator_output_to_conditioning_df(
        expression_generator_outputs['output'], note_sequence)
    _, _, conditioning_df, midi_synth_params, f0_changed = modify_params_with_artic_full(midi, conditioning_df, instrument_id, synth_gen, inst=inst_num)
    midi_audio_changed = apply_cresc_desc(midi, midi_synth_params, synth_gen, instrument_id, f0_changed=f0_changed, inst_num=inst_num)
    return midi_audio_changed, conditioning_df, midi_synth_params

def modify_vibrato(df, idx, new_vib):
    df.loc[idx, "vibrato"] = new_vib

def synthesize_fluid(midi_file,
                    sf2_path='/usr/share/sounds/sf2/FluidR3_GM.sf2', SAMPLE_RATE=16000):
  """
  Synthesize a midi file using MIDI-DDSP.
  Args:
      midi_file: The path to the MIDI file.
      sf2_path: The path to a sf2 soundfont file used for FluidSynth.
      inst_num: The MIDI track to synthesize.

  Returns: mix_audio: mix audio
  """

  # Get all the midi program in URMP dataset excluding guitar.
  midi_data = pretty_midi.PrettyMIDI(midi_file)
  midi_audio_all = {}

  # For each part, predict expressions using MIDI-DDSP,
  # or synthesize using FluidSynth.
  for part_number, instrument in enumerate(midi_data.instruments):
    fluidsynth_wav_r3 = instrument.fluidsynth(SAMPLE_RATE, sf2_path=sf2_path)
    fluidsynth_wav_r3 *= 0.25  # * 0.25 for lower volume
    midi_audio_all[part_number] = fluidsynth_wav_r3

    # If there is audio synthesized, mix the audio and return the output.
    midi_audio_mix = np.sum(
      np.stack(ensure_same_length(
        [a.astype(np.float64) for a in midi_audio_all.values()], axis=0),
        axis=-1),
      axis=-1)

    return midi_audio_mix