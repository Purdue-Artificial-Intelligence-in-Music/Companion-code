from music21 import *
import pretty_midi as pm
import numpy as np

rn = np.random.default_rng


def get_tempo_markings(score):
    # Returns a bpm curve
    tempo_markings = {}
    for n in score.flatten().recurse():
        if type(n) == tempo.MetronomeMark:
            tempo_markings[n.offset] = n.getQuarterBPM()
    tempo_markings = list(tempo_markings.items())
    if tempo_markings == []:
        return [(0, 120.0)]
    return tempo_markings


def get_beat_cdf(tempo_markings):
    if type(tempo_markings) == dict:
        beat_dens_func = list(tempo_markings.items())
    else:
        beat_dens_func = tempo_markings
    beat_dens_func.sort(key=(lambda x: x[0]))
    beat_cdf = []
    total_integ_time = 0.0
    for i in range(len(beat_dens_func) - 1):
        time_beats = beat_dens_func[i + 1][0] - beat_dens_func[i][0]
        tempo = beat_dens_func[i][1]
        beat_cdf.append((beat_dens_func[i][0], total_integ_time, tempo))
        total_integ_time += (time_beats / tempo) * 60.0
    i = len(beat_dens_func) - 1
    beat_cdf.append((beat_dens_func[i][0], total_integ_time, beat_dens_func[i][1]))
    return beat_cdf


def get_time(beat_num, beat_cdf):
    # Returns a time in seconds based on a tempo curve
    # General structure:
    # 1. Find the greatest key in tempo_curve/beat_cdf which is less than beat_num, call it k
    # 2. Calculate the time as follows: elapsed_time = beat_cdf[k] + (beat_num - k) / tempo_curve[k] * 60
    # 3. Return this time
    i = 0
    while True:
        if i == 0 and beat_cdf[0][0] == beat_num:
            break
        elif i == len(beat_cdf) - 1:
            break
        elif beat_cdf[i][0] < beat_num < beat_cdf[i + 1][0]:
            break
        i += 1
    return beat_cdf[i][1] + (beat_num - beat_cdf[i][0]) / beat_cdf[i][2] * 60.0


def convert_times_list(markings, beat_cdf):
    new_list = []
    for x in markings:
        new_list.append((get_time(x[0], beat_cdf), *x[1:]))
    return new_list


def convert_times_spanner(markings, beat_cdf):
    new_list = []
    for x in markings:
        new_list.append((get_time(x[0], beat_cdf), get_time(x[1], beat_cdf), *x[2:]))
    return new_list


def get_dynamics_list(part):
    dynamics_dict = {}
    for n in part.flatten().recurse():
        if type(n) == dynamics.Dynamic:
            dynamics_dict[n.offset] = n.volumeScalar
    dynamics_dict = list(dynamics_dict.items())
    dynamics_dict.sort(key=(lambda x: x[0]))
    return dynamics_dict


def get_cresc_desc(part):
    span_dyn_list = []
    for n in part.flatten().recurse():
        if type(n) == dynamics.Crescendo:
            print(n)
            if len(n) > 2:
                raise Exception("Cresc has too many objects")
            elif len(n) == 1:
                span_dyn_list.append((n[0].offset, n[0].offset + n[0].duration.quarterLength, "cresc"))
            else:
                span_dyn_list.append((n[0].offset, n[1].offset, "cresc"))
        if type(n) == dynamics.Diminuendo:
            if len(n) > 2:
                raise Exception("Dim has too many objects")
            elif len(n) == 1:
                span_dyn_list.append((n[0].offset, n[0].offset + n[0].duration.quarterLength, "dim"))
            else:
                span_dyn_list.append((n[0].offset, n[1].offset, "dim"))
    span_dyn_list.sort(key=(lambda x: x[0]))
    return span_dyn_list


def get_artic(part):
    artic_list = []
    for n in part.flatten().recurse():
        if type(n) == spanner.Slur:
            if len(n) != 2:
                raise Exception("Slur has too many objects")
            artic_list.append((n[0].offset, "slur", 1))
            artic_list.append((n[1].offset, "slur", -1))
        if type(n) == note.Note:
            for art in n.articulations:
                artic_list.append((n.offset, art.name, 1))
                artic_list.append((float(n.offset + n.duration.quarterLength), art.name, -1))
    artic_list.sort(key=(lambda x: x[0]))
    return artic_list


def randomize_note_times(midi, mean_shift, stdev_shift, mean_dur, stdev_dur):
    for inst in midi.instruments:
        # Shift note times
        for note in inst.notes:
            shift = rn().normal(loc=mean_shift, scale=(stdev_shift * stdev_shift))
            dur_var = rn().gamma(shape=mean_dur / (stdev_dur * stdev_dur), scale=stdev_dur * stdev_dur)
            dur = note.end - note.start
            start = note.start - shift
            end = start + max(0, (dur * dur_var))
            note.start = start
            note.end = end
        # Make sure note times are normalized
        inst.notes.sort(key=(lambda x: x.start))

        # Option 1: Shift all notes by position of first note
        # min_time = inst.notes[0].start
        # for note in inst.notes:
        #     note.start -= min_time
        #     note.end -= min_time

        # Option 2: Set first note only to start at 0
        inst.notes[0].start = 0


def add_screwups(midi, lambda_occur, stdev_pitch_delta):
    for inst in midi.instruments:
        # Make sure note times are normalized
        inst.notes.sort(key=(lambda x: x.start))

        occurrences = rn().poisson(lam=lambda_occur * inst.notes[len(inst.notes) - 1].end)
        for iter in range(occurrences):
            if len(inst.notes) == 0:
                break
            idx = int(rn().uniform(low=0, high=len(inst.notes)))
            screwup_len = int(rn().poisson(lam=0.01) + 1)
            end_screwup_idx = min(len(inst.notes), idx + screwup_len - 1)
            screwup_type = int(rn().uniform(low=0, high=2))
            # Didn't play notes
            if screwup_type == 0:
                del inst.notes[idx: end_screwup_idx]
            # Messed up pitches
            elif screwup_type == 1:
                pitch_delta = int(rn().normal(loc=0, scale=stdev_pitch_delta))
                for note in inst.notes[idx: end_screwup_idx]:
                    note.pitch = note.pitch + pitch_delta
                    if note.pitch < 0:
                        note.pitch = 0
                    if note.pitch > 127:
                        note.pitch = 127


def add_pitch_bends(midi, lambda_occur, mean_delta, stdev_delta, step_size):
    for inst in midi.instruments:
        inst.pitch_bends = []
        # Flatten note times list
        single_notes = []
        last_time = 0.0
        for note in inst.notes:
            if note.start > last_time:
                single_notes.append(note)
                last_time = note.end

        fixed_bend_points = []
        # Add fixed point pitch bends
        for note in single_notes:
            # Do 1 pitch bend at start of each note
            bend = int(rn().normal(mean_delta, stdev_delta * stdev_delta))
            if bend > 8191:
                bend = 8191
            elif bend < -8192:
                bend = -8192
            fixed_bend_points.append(pm.PitchBend(bend, note.start))
            # Add more randomly
            occurrences = rn().poisson(lam=lambda_occur * (note.end - note.start))
            for i in range(occurrences):
                time = rn().uniform(low=note.start, high=note.end)
                bend = int(rn().normal(mean_delta, stdev_delta * stdev_delta))
                fixed_bend_points.append(pm.PitchBend(bend, time))

        # Sort by time from least to greatest
        fixed_bend_points.sort(key=(lambda x: x.time))

        # Linear interpolation
        inst.pitch_bends = fixed_bend_points.copy()
        for i in range(len(fixed_bend_points) - 1):
            l_pb = fixed_bend_points[i]
            r_pb = fixed_bend_points[i + 1]
            n_points_to_add = int(np.floor((r_pb.time - l_pb.time) / step_size))
            for j in range(1, n_points_to_add + 1):
                time = l_pb.time + j * step_size
                bend = int(l_pb.pitch + ((r_pb.pitch - l_pb.pitch) * (j / (n_points_to_add + 1))))
                if bend > 8191:
                    bend = 8191
                elif bend < -8192:
                    bend = -8192
                inst.pitch_bends.append(pm.PitchBend(bend, time))


def normalize_velocity(midi, vel):
    for inst in midi.instruments:
        for note in inst.notes:
            note.velocity = vel


def randomize_velocity(midi, stdev_vel):
    for inst in midi.instruments:
        for note in inst.notes:
            delta = rn().normal(0, stdev_vel * stdev_vel)
            note.velocity += delta
            if note.velocity > 127:
                note.velocity = 127
            if note.velocity < 1:
                note.velocity = 1

def find_closest_marking(markings, time, key=(lambda x : x.start)):
    if len(markings) < 1:
        return None
    closest = markings[0]
    min_t = abs(key(marking) - time)
    for marking in markings:
        dt = abs(key(marking) - time)
        if dt < min_t:
            closest = marking
            min_t = dt
    return closest



def get_closest_prev_time(markings, i_time, idx):
    if len(markings) == 0:
        return None
    for j in range(len(markings)):
        if abs(markings[j][i_time] - idx) < 1e-4:
            return markings[j]
        elif markings[j][i_time] > idx:
            if j == 0:
                return markings[j]
            return markings[j - 1]
    return None


def get_closest_next_time(markings, i_time, idx):
    if len(markings) == 0:
        return None
    for j in range(len(markings)):
        if abs(markings[j][i_time] - idx) < 1e-4:
            return markings[j]
        elif markings[j][i_time] > idx:
            return markings[j]
    return markings[len(markings) - 1]


def update_dynamics(score_part, midi_part, beat_cdf, bad_dir_delta=0.15):
    dyn_markings = get_dynamics_list(score_part)
    dyn_markings = convert_times_list(dyn_markings, beat_cdf)

    cr_dr = get_cresc_desc(score_part)
    cr_dr = convert_times_spanner(cr_dr, beat_cdf)
    interp_pairs = []
    bad_dir_delta = 0.15
    for x in cr_dr:
        interp_pairs.append((x[0], x[1]))
        start_dyn_obj = get_closest_prev_time(dyn_markings, 0, x[0])
        start_dyn = start_dyn_obj[1]
        end_dyn_obj = get_closest_next_time(dyn_markings, 0, x[1])
        if x[2] == "cresc" and end_dyn_obj[1] < start_dyn:
            end_dyn = min(start_dyn + bad_dir_delta, 1)
            dyn_markings.append((x[1], end_dyn))
        elif x[2] == "dim" and end_dyn_obj[1] > start_dyn:
            end_dyn = max(start_dyn - bad_dir_delta, 0)
            dyn_markings.append((x[1], end_dyn))
        elif end_dyn_obj[0] > x[1]:
            end_dyn = start_dyn + (end_dyn_obj[1] - start_dyn) * (x[1] - x[0]) / (end_dyn_obj[0] - x[0])
            dyn_markings.append((x[1], end_dyn))
    dyn_markings.sort(key=(lambda x: x[0]))
    event_delta = 0.05
    for pair in interp_pairs:
        num_points = (pair[1] - pair[0]) / event_delta
        start_val = get_closest_prev_time(dyn_markings, 0, pair[0])[1]
        end_val = get_closest_next_time(dyn_markings, 0, pair[1])[1]
        for j in range(1, int(num_points)):
            dyn_markings.append((pair[0] + (pair[1] - pair[0]) * j / num_points,
                                 start_val + (end_val - start_val) * j / num_points))
    midi_part.control_changes.clear()

    # 4.5. Convert to velocity values
    vel_vals = []
    for val in dyn_markings:
        vel_vals.append((val[0], min(max(int(val[1] * 128), 0), 127)))

    # 5a. Store the velocity curve on the MIDI "Breath" CC (2)
    for event in vel_vals:
        midi_part.control_changes.append(pm.ControlChange(2, event[1], event[0]))

    # 5b. For each note, look at the velocity curve and find the closest point - copy over the velocity
    for note in midi_part.notes:
        dyn = get_closest_prev_time(vel_vals, 0, note.start)
        if dyn is None:
            dyn = get_closest_next_time(vel_vals, 0, note.start)
        if dyn is not None:
            note.velocity = dyn[1]


def update_artics(score_part, midi_part, beat_cdf):
    artic_list = get_artic(score_part)
    artic_list = convert_times_list(artic_list, beat_cdf)
    track_ar = {}
    for ar in artic_list:
        if not ar[1] in track_ar.keys():
            track_ar[ar[1]] = 0
        track_ar[ar[1]] += ar[2]
        cc_num = 0
        if ar[1] == "staccato":
                cc_num = 20
        elif ar[1] == "tenuto":
            cc_num = 21
        elif ar[1] == "strong accent":
            cc_num = 22
        elif ar[1] == "accent":
            cc_num = 23
        elif ar[1] == "slur":
                cc_num = 24
        if track_ar[ar[1]] > 0:
            midi_part.control_changes.append(pm.ControlChange(cc_num, 127, ar[0]))
        else:
            midi_part.control_changes.append(pm.ControlChange(cc_num, 0, ar[0]))


def process_score(in_str):
    score = converter.parse("".join([in_str, '.musicxml']))
    _ = score.write('midi', "".join([in_str, '.midi']))
    midi = pm.PrettyMIDI("".join([in_str, '.midi']))
    
    tempo_markings = get_tempo_markings(score)
    beat_cdf = get_beat_cdf(tempo_markings)

    for i in range(len(score.parts)):
        score_part = score.parts[i]
        midi_part = midi.instruments[i]

        # Dynamics
        update_dynamics(score_part, midi_part, beat_cdf)
        update_artics(score_part, midi_part, beat_cdf)
        
    #randomize_note_times(midi=midi, mean_shift=0, stdev_shift=0.04, mean_dur=1, stdev_dur=0.02)
    add_pitch_bends(midi=midi, lambda_occur=2, mean_delta=0, stdev_delta=np.sqrt(500), step_size=0.01)
    #add_screwups(midi=midi, lambda_occur=0.03, stdev_pitch_delta=1)
    print("".join([in_str, '_modified.midi']))
    midi.write("".join([in_str, '_modified.midi']))
    
    pass

def remove_notes(midi, time, delta):
    for inst in midi.instruments:
        for note in inst.notes:
            if abs(note.start - time) < delta or abs(note.end - time) < delta:
                inst.notes.remove(note)

def add_extra_notes(midi, time, lambda_occur, stdev_pitch_delta, stdev_dur):
    for inst in midi.instruments:
        notes = inst.notes
        if len(notes) < 1:
            continue
        notes.sort(key=(lambda x : x.start))
        closest_idx = 0
        min_t = abs(notes[closest_idx].start - time)
        for i in range(len(notes)):
            dt = abs(notes[i].start - time)
            if dt < min_t:
                closest_idx = i
                min_t = dt
        time_before = 0.0 if closest_idx == 0 else notes[closest_idx - 1].end
        time_after = time if closest_idx == len(notes) - 1 else notes[closest_idx + 1].start
        note = notes[closest_idx]
        notes.remove(note)
        occurrences = rn().poisson(lam=lambda_occur * inst.notes[len(inst.notes) - 1].end)
        for iter in range(occurrences):
            dur = abs(min(rn().normal(loc=0, scale=stdev_dur)))
            time = rn().uniform(low=time_before, high=time_after-dur)
            pitch_delta = int(np.round(rn().normal(loc=0, scale=stdev_pitch_delta)))
            inst.notes.append(pm.Note(velocity=note.velocity, pitch=note.pitch+pitch_delta, start = time, end=time+dur))