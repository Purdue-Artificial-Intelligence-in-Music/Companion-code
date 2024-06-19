from music21 import *
import pandas as pd
import numpy as np
import music21
import math
import os

class AudioAnalysis:

    '''
    This class takes a pandas DataFrame representing the correct and incorrect notes respectively played by a solo instrument
    and converts it into a music21 score that highlights any mistakes in intonation, ignoring issues in time.
    '''

    CENT_TOLERANCE = 15 # changed for demo
    BEAT_TOLERANCE = 0.2
    
    def __init__(self, input_df: pd.DataFrame, score: str):
        self.input_df = input_df
        script_dir = os.path.dirname(__file__)  # Get the directory of the current script
        score_path = os.path.join(script_dir, score)
        self.score = converter.parse(score_path)
        self.correct_df = None
    
    def generate_dataframe_from_score(self) -> None:

        """
        Given a score that has been converted to a music21.stream.Score object, this method extracts information from the
        score about the notes in the score and displays it as a pandas DataFrame.
        """

        beats = self.score.getTimeSignatures(recurse=True)[0].numerator
        measures = int(math.ceil(self.score.highestTime / beats)) + 1

        tempo_changes = {}
        for i in range(1, measures, 1):
            measure = self.score.parts[0].measure(i)
            for j in range(0, len(measure)):
                if isinstance(measure[j], music21.tempo.MetronomeMark):
                    tempo_changes[measure.number] = measure[j].getQuarterBPM()
        if not tempo_changes:
            tempo_changes[1] = 120

        durations = []

        for i in range(1, measures, 1):
            measure = self.score.parts[0].measure(i).flatten().notesAndRests
            lengths = []
            for j in range(0, len(measure)):
                s = measure[j].duration.quarterLength
                lengths.append(float(s))
            durations.append(lengths)

        measure_notes = []
        measure_notes_frequency = []

        for i in range(1, measures, 1):
            measure = self.score.parts[0].measure(i).flatten().notesAndRests
            notes = []
            notes_frequency = []
            for j in range(0, len(measure)):
                if (measure[j].isChord):
                    chord = measure[j].notes
                    notes.append(str(chord[-1].pitch.name + str(chord[-1].pitch.octave)))
                    notes_frequency.append(chord[-1].pitch.frequency)
                    continue
                elif (measure[j].isRest):
                    s = 'rest'
                    f = 0.0
                else:
                    f = measure[j].pitch.frequency
                    s = str(measure[j].pitch.name)
                    s += str(measure[j].pitch.octave)
                notes.append(s)
                notes_frequency.append(f)
            measure_notes.append(notes)
            measure_notes_frequency.append(notes_frequency)

        bpm = tempo_changes[1]
        quarter_note_duration = (1 / bpm) * 60
        note_duration = []
        for measure in durations:
            note_duration.append([note_length * quarter_note_duration for note_length in measure])
        new_durations = np.concatenate(durations)
        new_measure_notes = np.concatenate(measure_notes)
        new_measure_notes_frequency = np.concatenate(measure_notes_frequency)
        new_note_duration = np.concatenate(note_duration)

        start_times = []
        start_times.append(0)
        curr_time = 0

        for i in range(0, len(new_note_duration) - 1):
            curr_time += new_note_duration[i]
            start_times.append(curr_time)
        assert(len(new_measure_notes) == len(new_measure_notes_frequency))

        note_type = [duration.Duration(quarterLength=quarter_note_length).type for quarter_note_length in new_durations]
        df = pd.DataFrame({'Note Type': note_type, 'Duration': new_note_duration, 
                   'Note Name': new_measure_notes, 'Note Frequency': new_measure_notes_frequency, 
                   'Start Time': start_times})
        
        self.correct_df = df

    def compare_dataframe_by_time(self) -> pd.DataFrame:
        
        """
        Compares the two dataframes representing correct notes and notes played by the user and appends information
        comparing differences to a new dataframe so notes with wrong intonation can be easily identified.
        """

        self.generate_dataframe_from_score()
        # print(self.input_df)
        # print(self.correct_df)
        # return

        correct_notes = list(self.correct_df['Note Name'])
        input_notes = list(self.input_df['Note Name'])
        input_cents = list(self.input_df['Cents'])
        input_durations = list(self.input_df['Duration'])
        expected_durations = list(self.correct_df['Duration'])
        note_statuses = [] # ANTHONY: changed format. A list of lists. Each list is of note characteristics for each note played. Contains what note it correlates to in score and info on how well it was played
        audio_df_iterator = 0

        # Prevent comparison of notes from going out of bounds.
        num_notes = len(list(self.correct_df['Note Name'])) # Number of notes in the score
        # For each note in the score, find all of the notes played (could be none) in the time frame that the user should have been playing that score note
        # Notes are added to attempted_notes as rows of a df
        for score_note_idx in range(num_notes):
            note_start = self.correct_df['Start Time'][score_note_idx]
            note_end = note_start + self.correct_df['Duration'][score_note_idx]
            attempted_notes = []
            while (audio_df_iterator < num_notes and self.input_df['Start Time'][audio_df_iterator] < note_end):
                attempted_notes.append(self.input_df.iloc[audio_df_iterator])
                audio_df_iterator += 1
            
            # Now compare each note played the correct note at that time
            correct_note = self.correct_df.iloc[score_note_idx]
            for played_note in attempted_notes:
                note_status = [score_note_idx]
                played_cents = int(played_note['Cents'])
                played_length = float(played_note['Duration'])
                score_length = float(correct_note['Duration'])
                played_start = float(played_note['Start Time'])
                score_start = float(correct_note['Start Time'])
                
                note_status_dict = {}

                note_status_dict['Index'] = score_note_idx

                # Extra notes played
                if len(attempted_notes) > 1:
                    note_status_dict['Extra'] = True
                else:
                    note_status_dict['Extra'] = False

                # Check frequency
                if correct_note['Note Name'] == played_note['Note Name']:
                    if correct_note['Note Name'] == 'rest':
                        note_status_dict['Intonation'] = "Rest"
                        note_status.append("Rest")
                    elif abs(played_cents) > AudioAnalysis.CENT_TOLERANCE and played_cents < 0:
                        note_status_dict['Intonation'] = "Flat"
                        note_status.append("Flat")
                    elif abs(played_cents) > AudioAnalysis.CENT_TOLERANCE and played_cents > 0:
                        note_status_dict['Intonation'] = 'Sharp'
                        note_status.append("Sharp")

                    else:
                        note_status_dict['Intonation'] = 'Correct'
                        # note_status.append("Correct")
                        # pass statements here for now in case we want to explicitly say each thing done correctly
                else:
                    note_status_dict['Intonation'] = "Wrong"
                    note_status.append("Wrong Note")
                
                note_status_dict['Played Note'] = played_note['Note Name']
                note_status_dict['Expected Note'] = correct_note['Note Name']

                # Check length (short/long)
                if abs(played_length - score_length) > AudioAnalysis.BEAT_TOLERANCE and played_length > score_length: # What does beat tolerance mean? It's measured in seconds not beats here
                    note_status_dict['Duration'] = "Long"
                    note_status.append("Long")
                elif abs(played_length - score_length) > AudioAnalysis.BEAT_TOLERANCE and played_length < score_length:
                    note_status.append("Short")
                    note_status_dict['Duration'] = "Short"
                else:
                    note_status_dict['Duration'] = "Correct"
                    # note_status.append("Correct")
                    

                # Check start (early/late)
                if abs(played_start - score_start) > AudioAnalysis.BEAT_TOLERANCE and played_start > score_start: # Should we have a different tolerance for early/late starts?
                    note_status_dict['Start Time'] = "Late"
                    note_status.append("Late")
                elif abs(played_start - score_start) > AudioAnalysis.BEAT_TOLERANCE and played_start < score_start:
                    note_status_dict['Start Time'] = "Early"
                    note_status.append("Early")
                else:
                    note_status_dict['Start Time'] = "Correct"
                    # note_status.append("Correct")              
                note_statuses.append(note_status_dict)
        
        
        series_list = []
        for note_status in note_statuses:
            temp_series = pd.Series(note_status)
            series_list.append(temp_series)
        played_notes_df = pd.DataFrame(series_list)
        

        # If less input notes than notes in score detected, extend input lists so that they match the length of 
        # correct notes

        '''
        My plan for comparing notes and creating the score output:
        For each note played in the score:
            - Look at the note status list(s) for attempted note(s) that correspond to that note
            - print every attempted note in the output score with its type based on how long it was and when it started (ideally, if the user plays like four notes insted of one,
                the output will be a set of 16th notes in the order they were played)
            - For each note printed (each note attempted), add colors and other notes (we will have to decide how to denote these other notes) based on what its status list looks like.
                A correctly played note will have nothing in the list.
                This should be super easy: basically just for each status list:
                if "Sharp" in status_list -> make orange
                if "Flat" in status_list -> make blue
                if "Wrong" in status_list -> make red
                etc.
        '''

        # padding = len(correct_notes) - len(input_notes) if len(correct_notes) > len(input_notes) else 0
        # for i in range(padding):
        #     input_notes.append(math.nan)
        #     note_status.append(False)
        #     input_durations.append(math.nan)
        #     beat_status.append(math.nan)
        # new_df.insert(3, "Played Notes", input_notes)
        # new_df.insert(4, "Note Status", note_status)
        # new_df.insert(5, "Input Duration", input_durations)
        # new_df.insert(6, "Beat Status", beat_status)
        # return new_df
        print(played_notes_df)
        return played_notes_df

    def compare_dataframe(self) -> pd.DataFrame:
        """
        Compares the two dataframes representing correct notes and notes played by the user and appends information
        comparing differences to a new dataframe so notes with wrong intonation can be easily identified.
        """
        self.generate_dataframe_from_score()
        correct_notes = list(self.correct_df['Note Name'])
        input_notes = list(self.input_df['Note Name'])
        input_cents = list(self.input_df['Cents'])
        input_durations = list(self.input_df['Duration'])
        expected_durations = list(self.correct_df['Duration'])
        note_status = []
        beat_status = []

        # Prevent comparison of notes from going out of bounds.
        num_notes = len(correct_notes) if len(correct_notes) < len(input_notes) else len(input_notes)
        for i in range(num_notes):
            if correct_notes[i] == input_notes[i]:
                if abs(int(input_cents[i])) > AudioAnalysis.CENT_TOLERANCE and int(input_cents[i]) < 0:
                    note_status.append("Flat")
                elif abs(int(input_cents[i])) > AudioAnalysis.CENT_TOLERANCE and int(input_cents[i]) > 0:
                    note_status.append("Sharp")
                else:
                    note_status.append("Correct")
            else:
                note_status.append("Wrong")

            if abs(input_durations[i] - expected_durations[i]) > AudioAnalysis.BEAT_TOLERANCE and input_durations[i] > expected_durations[i]:
                beat_status.append("Long")
            elif abs(input_durations[i] - expected_durations[i]) > AudioAnalysis.BEAT_TOLERANCE and input_durations[i] < expected_durations[i]:
                beat_status.append("Short")
            else:
                beat_status.append("Correct")

        new_df = self.correct_df

        # If less input notes than notes in score detected, extend input lists so that they match the length of 
        # correct notes
        padding = len(correct_notes) - len(input_notes) if len(correct_notes) > len(input_notes) else 0
        for i in range(padding):
            input_notes.append(math.nan)
            note_status.append(False)
            input_durations.append(math.nan)
            beat_status.append(math.nan)
        new_df.insert(3, "Played Notes", input_notes)
        new_df.insert(4, "Note Status", note_status)
        new_df.insert(5, "Input Duration", input_durations)
        new_df.insert(6, "Beat Status", beat_status)
        return new_df
    
    def generate_overlay_score(self):
        """
        Takes information from a DataFrame that shows differences between expected and played notes and generates
        a new score from it. Notes with incorrect intonation are displayed together, and the wrong note is colored in red. 
        """
        df = self.compare_dataframe_by_time()
        new_score = stream.Stream()
        played_notes = list(df['Played Note'])
        intonation = list(df['Intonation'])
        expected_notes = list(df['Expected Note'])
        # correct_notes = df['Note Name']
        # note_status = df["Note Status"]
        # input_notes = df['Played Notes']
        # note_type = df['Note Type']
        # beat_status = df["Beat Status"]
        time_signature = self.score.getTimeSignatures()[0].ratioString
        new_score.append(meter.TimeSignature(time_signature))
        for i in range(len(played_notes)):
            note_type = self.correct_df.iloc[i]['Note Type']
            match intonation[i]:
                case "Rest":
                    rest = music21.note.Rest()
                    rest.duration.type = note_type
                    new_score.append(rest)
                case "Flat":
                    new_note = music21.note.Note(str(played_notes[i]))
                    new_note.duration.type = str(note_type)
                    new_note.style.color = 'blue'
                    new_score.append(new_note)
                case "Sharp":
                    new_note = music21.note.Note(str(played_notes[i]))
                    new_note.duration.type = str(note_type)
                    new_note.style.color = 'orange'
                    new_score.append(new_note)
                case "Correct":
                    new_note = music21.note.Note(str(played_notes[i]))
                    new_note.duration.type = str(note_type)
                    new_score.append(new_note)
                case "Wrong":
                    correct_note = music21.note.Note(str(expected_notes[i]))
                    incorrect_note = music21.note.Note(str(played_notes[i]))
                    correct_note.duration.type = str(note_type)
                    incorrect_note.duration.type = str(note_type)
                    incorrect_note.style.color = 'red'
                    combined_chord = music21.chord.Chord([correct_note, incorrect_note])
                    new_score.append(combined_chord)
            # match 
        # for i in range(len(note_status)):
        #     if input_notes[i] == 'nan':
        #         continue
        #     if (correct_notes[i] == 'rest'):
        #         rest = music21.note.Rest()
        #         rest.duration.type = note_type[i]
        #         new_score.append(rest)
        #         continue
        #     if (note_type[i] == 'zero'):
        #         continue
        #     if note_status[i] == "Correct":
        #         new_note = music21.note.Note(str(correct_notes[i]))
        #         new_note.duration.type = str(note_type[i])
        #         new_score.append(new_note)
        #     elif note_status[i] == "Wrong":
        #         correct_note = music21.note.Note(str(correct_notes[i]))
        #         incorrect_note = music21.note.Note(str(input_notes[i]))
        #         correct_note.duration.type = str(note_type[i])
        #         incorrect_note.duration.type = str(note_type[i])
        #         incorrect_note.style.color = 'red'
        #         combined_chord = music21.chord.Chord([correct_note, incorrect_note])
        #         new_score.append(combined_chord)
        #     elif note_status[i] == "Flat":
        #         incorrect_note = music21.note.Note(str(input_notes[i]))
        #         incorrect_note.duration.type = str(note_type[i])
        #         incorrect_note.style.color = 'blue'
        #         new_score.append(incorrect_note)
        #     elif note_status[i] == "Sharp":
        #         incorrect_note = music21.note.Note(str(input_notes[i]))
        #         incorrect_note.duration.type = str(note_type[i])
        #         incorrect_note.style.color = 'orange'
        #         new_score.append(incorrect_note)
        #     print(beat_status[i])
        new_score.show('musicxml')
        new_score.write('mxl', 'josh_demo.mxl') # changed for demo
        
        
if __name__ == '__main__':
    df = pd.read_csv('scale.csv')
    a = AudioAnalysis(df, 'cscale.xml')
    print(a.compare_dataframe_by_time())