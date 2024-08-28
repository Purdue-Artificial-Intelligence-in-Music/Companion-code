#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 19:20:29 2017

@author: jbraga
"""

import librosa as lr
import numpy as np
import scipy.io.wavfile as wav
import csv


def list_of_fragments(dataset_file):

    fragments=[]   
    cr = csv.reader(open(dataset_file))
    for row in cr:	
    	fragments.append(row[0]) 
    
    return fragments

    
def score(filename):
    
    notes = []
    onset = []
    articulation = []
    articulation_onset = []
    grace_notes = []
    grace_onset = []
    grace_diff = []
    tempo = []
    tempo_onset = []

    with open(filename) as csvfile:
        notes_reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
#        onset.append('0.0')
#        notes.append('0')
        for row in notes_reader:
            if row[1] == 'tempo':
                tempo.append(float(row[2])/4)
                tempo_onset.append(row[0])
            if row[1] =='script':
                articulation_onset.append(row[0])
                articulation.append(row[2])
#            if row[1] =='breathe':
#                instants.append(row[0])
#                events.append('breathe')
                    
            if row[1] == 'note' or row[1] == 'rest':
                if row[0].find('-')>0:
                    aux1, aux2 = row[0].split('-')
                    grace_onset.append(aux1)
                    grace_diff.append(aux2)
                    grace_notes.append(row[2])
                    
                elif row[2].find('/')>0:
                    onset.append(row[0]) 
                    notes.append('0')
                else:
                    onset.append(row[0]) 
                    if row[1] == 'rest':
                        notes.append('0')
                    else:
                        notes.append(row[2])

    tempo=np.array(tempo,dtype='float32')
    tempo_onset=np.array(tempo_onset,dtype='float32')                
    
    onset=np.array(onset,dtype='float32')
    notes=np.array(notes,dtype='float32') 
#    hole_note=4*60/tempo[1]
#    onset=onset*hole_note
    hole_note=1
    for i in range(0,len(tempo)):
        hole_note=(4*60/float(tempo[i]))/hole_note
        onset[onset>=tempo_onset[i]]=onset[onset>=tempo_onset[i]]*hole_note
    
    if len(articulation)==0:
        articulation=None
        articulation_onset=None
    else:
        articulation_onset=np.array(articulation_onset,dtype='float32')
#        articulation_onset=articulation_onset*hole_note
        hole_note=1
        for i in range(0,len(tempo)):
            hole_note=(4*60/float(tempo[i]))/hole_note
            articulation_onset[articulation_onset>=tempo_onset[i]]=articulation_onset[articulation_onset>=tempo_onset[i]]*hole_note
    
    if len(grace_notes)==0:
        grace_onset=None
        grace_diff=None
        grace_notes=None
    else:
        grace_onset=np.array(grace_onset,dtype='float32')
        grace_diff=np.array(grace_diff,dtype='float32')
        grace_notes=np.array(grace_notes,dtype='float32')
#        grace_onset=grace_onset*hole_note
        hole_note=1
        for i in range(0,len(tempo)):
            hole_note=(4*60/float(tempo[i]))/hole_note
            grace_onset[grace_onset>=tempo_onset[i]]=grace_onset[grace_onset>=tempo_onset[i]]*hole_note 
            grace_diff[grace_onset>=tempo_onset[i]]=grace_diff[grace_onset>=tempo_onset[i]]*hole_note

    if articulation is not None:
        for i in range(0,len(articulation)):
            if articulation[i] == 'fermata':
                tempo_aux = tempo[tempo_onset<=articulation_onset[i]][0]
#                print tempo_aux
                onset[onset>articulation_onset[i]] = onset[onset>articulation_onset[i]] + 60*float(4)/tempo_aux #one bar of fermata
                grace_onset[grace_onset>articulation_onset[i]] = grace_onset[grace_onset>articulation_onset[i]] + 60*float(4)/tempo_aux
                
    if grace_notes is not None:
#        print len(onset)
#        for i in range(len(grace_notes)-1, -1, -1):
        for i in range(0,len(grace_notes)):
            notes=np.insert(notes, np.where(onset==grace_onset[i])[0][0], grace_notes[i])
            onset=np.insert(onset, np.where(onset==grace_onset[i])[0][0], grace_onset[i]-grace_diff[i]/8)

    duration = onset[1:] - onset[:-1]   
    return onset[:-1], notes[:-1], duration 
    

def ground_truth(gt_file):
        
    cr = csv.reader(open(gt_file))
    onset=[]
    note=[]
    duration=[]
    for row in cr:
        onset.append(row[0]) 
        note.append(row[1])
        duration.append(row[2])
    
    onset = np.array(onset, 'float')
    note = np.array(note, 'float')
    duration = np.array(duration, 'float')
    
    return onset, note, duration

def synth_truth(synth_file):
        
    cr = csv.reader(open(synth_file))
    onset=[]
    note=[]
    duration=[]
    for row in cr:
        onset.append(row[1]) 
        note.append(row[4])
        duration.append(row[2])
    
    onset = np.array(onset, 'float')
    note = np.array(note, 'float')
    note = lr.hz_to_midi(note)
    duration = np.array(duration, 'float')
    
    return onset, note, duration
    
    
def to_array(onset, notes, duration, fs=44100, hop=128):
    
    t_f = onset[-1]+duration[-1]

    t_note_formatted = np.linspace(0, t_f, int(t_f*fs/float(hop)))
    notes_formatted = np.zeros([len(t_note_formatted),], 'float')
    index = np.zeros([len(onset),])
    
    j=0     
    for i in range(0,len(onset)):
        nuevo = True
        while (nuevo and t_note_formatted[j]<onset[i]):
            j=j+1
        while (j<len(t_note_formatted) and t_note_formatted[j]>=onset[i] and t_note_formatted[j]<(onset[i]+duration[i])):
            notes_formatted[j]=notes[i]
            j=j+1
            nuevo=False
        index[i] = j
            
    return notes_formatted, t_note_formatted, index
    
          
def audio(audio_file):
    
    fs, audio = wav.read(audio_file)
    audio = audio.astype('float')
    t = np.arange(len(audio)) * float(1)/fs

    return audio, t, fs  
    
    
if __name__=="__main__":

    train, test = list_of_fragments('sequenza')    


#    fragment = fragments[3]#.replace('/performances/','/wist_synth/gt/') 
#
#    print fragment
#    
#    audio_file = fragment + '.wav'
#    gt_file = fragment + '.gt'
#    score_file = fragment[0:fragment.rfind('_')].replace('/performances/','/score/') + '.notes'
#
#    audio, t, fs = audio(audio_file)
#    
#    gt_onset, gt_note, gt_duration = ground_truth(gt_file)       
#    gt_note=lr.hz_to_midi(gt_note)
#    gt_note[np.isinf(gt_note)]=0    
#    score_onset, score_note, score_duration = score(score_file)
#      
#    gt_array, gt_t, gt_index = to_array(gt_onset, gt_note, gt_duration)
#    score_array, score_t, score_index = to_array(score_onset, score_note, score_duration)
#
###    import melosynth as ms
###    ms.melosynth_pitch(gt_array, outputfile, fs, nHarmonics, square, useneg):
#        
##%% PLOTTING
#    
#    fig = plt.figure(figsize=(18,6))                                                               
#    ax = fig.add_subplot(3,1,(1,2))                                                      
#    
#    yticks_major = [ 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88, 89, 91, 93, 95, 96 ]
#    yticks_minor = [ 61, 63, 66, 68, 70, 73, 75, 78, 80, 82, 85, 87, 90, 92, 94 ]
#    yticks_labels = ['59-B3', '60-C4', '62-D4', '64-E4', '65-F4', '67-G4', '69-A4', '71-B4', '72-C5', '74-D5', '76-E5', '77-F5', '79-G5', '81-A5', '83-B5', '84-C6', '86-D6', '88-E6', '89-F6', '91-G6', '93-A6', '95-B6', '96-C7']                         
#                                             
#    ax.set_yticks(yticks_major)                                                   
#    ax.set_yticks(yticks_minor, minor=True)
#    
#    ax.set_yticklabels(yticks_labels, size='small')                                
#    
#    plt.ylim(58, 96) #flute register in midi   
#    plt.xlim([t[0], t[-1]])
#    ax.grid(b=True, which='major', color='black', axis='y', linestyle='-', alpha=0.3)
#    ax.grid(b=True, which='minor', color='black', axis='y', linestyle='-', alpha=1)    
#    
#    plt.plot(gt_t,gt_array,'k')
#    plt.plot(score_t,score_array,'b')
#    plt.fill_between(gt_t, gt_array-0.5, gt_array+0.5, facecolor='yellow', label='gt', alpha=0.6)
#    plt.fill_between(score_t, score_array-0.5, score_array+0.5, facecolor='cyan', label='score', alpha=0.6)
#    
#    plt.title("Melody")
#    plt.ylabel("Pitch")
#    
#    plt.subplot(3,1,3)
#    plt.plot(t, audio, color='black', alpha=0.5)
#    plt.grid()
#    plt.axis('tight')
#    plt.ylabel("Amplitude")
#    plt.xlabel("Time (s)")    
#    plt.xlim([t[0], t[-1]])
#    plt.show()
