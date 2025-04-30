import { Midi, Track } from "@tonejs/midi";
import * as Tone from "tone";
import { parseStringPromise } from "xml2js";
import scoresData from "../musicxml/scores";

interface ProcessedNote {
  frequency: number; // MIDI note number
  duration: number; // Duration in seconds
  offset: number; // Onset time in seconds
}

class MidiPerformance {
  private filePath: string;
  private currentTempo: number;
  private instrumentIndex: number;
  private notes: ProcessedNote[] = []; // Array to store processed notes
  private scorePosition: number = 0; // Current position in beats
  private nextNoteIndex: number = 0;
  private isPlaying: boolean = false;
  private synth: Tone.PolySynth;
  private isMusicXML: boolean = false;
  private midiData: Midi | null = null;


  constructor(filePath: string, tempo: number = 120, instrumentIndex: number = 0) {
    this.filePath = filePath;
    this.currentTempo = tempo;
    this.instrumentIndex = instrumentIndex;
    

    // Initialize the Tone.js synthesizer
    this.synth = new Tone.PolySynth(Tone.Synth).toDestination();

    // Load the MIDI file
    this.isMusicXML = filePath.endsWith(".musicxml");
    this.loadFile();
  }

  private async loadFile() {
    try {
      // const response = await fetch(this.filePath);
      // const fileContent = await response.text();
      const fileContent = scoresData[this.filePath];

      if (this.isMusicXML) {
        console.log("Parsing MusicXML file...");
        await this.parseMusicXML(fileContent); // Parse MusicXML file
      } else {
        console.log("Parsing MIDI file...");
        await this.parseMidiFile(fileContent); // Parse MIDI file
      }
    } catch (error) {
      console.error("Failed to load file:", error);
    }
  }

  // Parse MIDI File
  private async parseMidiFile(fileContent: string) {
    const arrayBuffer = new TextEncoder().encode(fileContent).buffer;
    this.midiData = new Midi(arrayBuffer as ArrayBuffer);
    console.log("MIDI file parsed:", this.midiData);
  }

  // Parse MusicXML File
  private async parseMusicXML(fileContent: string) {
    try {
      const parsedXML = await parseStringPromise(fileContent); // Parse XML into a JS object
      console.log("MusicXML parsed:", parsedXML);

      // Extract note data
      const notes = this.extractNotesFromMusicXML(parsedXML);
      this.notes = notes;
      console.log("Extracted notes:", notes);
    } catch (error) {
      console.error("Failed to parse MusicXML file:", error);
    }
  }

  // Extract notes from parsed MusicXML
  // private extractNotesFromMusicXML(parsedXML: any): any[] {
  //   const notes: any[] = [];
  //   const parts = parsedXML["score-partwise"]["part"];

  //   parts.forEach((part: any) => {
  //     const measures = part["measure"];
  //     measures.forEach((measure: any) => {
  //       const measureNotes = measure["note"];
  //       measureNotes.forEach((note: any) => {
  //         if (note["pitch"]) {
  //           const pitch = note["pitch"][0];
  //           const step = pitch["step"][0];
  //           const octave = pitch["octave"][0];
  //           const duration = note["duration"][0];

  //           notes.push({
  //             step,
  //             octave: parseInt(octave, 10),
  //             duration: parseFloat(duration),
  //           });
  //         }
  //       });
  //     });
  //   });

  //   return notes;
  // }

  private extractNotesFromMusicXML(parsedXML: any): ProcessedNote[] {
    const notes: ProcessedNote[] = [];
  
    const parts = parsedXML["score-partwise"]["part"];
    parts.forEach((part: any) => {
      let currentOffset = 0; // Initialize offset for each part
      const measures = part["measure"];
      const divisions = parseFloat(measures[0]["attributes"][0]["divisions"][0]); // Get divisions for the measure
      measures.forEach((measure: any) => {
        const measureNotes = measure["note"];
        measureNotes.forEach((note: any) => {
          if (note["pitch"]) {
            const pitch = note["pitch"][0];
            const step = pitch["step"][0];
            const octave = pitch["octave"][0];
            const duration = parseFloat(note["duration"][0]) / divisions;
  
            notes.push({
              frequency: Tone.Frequency(`${step}${octave}`).toMidi(),
              duration: duration,
              offset: currentOffset,
            });
  
            currentOffset += duration; // Update offset based on duration
          }
        });
      });
    });

    notes.sort((a, b) => a.offset - b.offset); // Sort notes by offset
  
    return notes;
  }
  

  public setTempo(tempo: number): void {
    this.currentTempo = tempo;
  }

  public updateScorePosition(position: number): void {
    this.scorePosition = position;
    // this.nextNoteIndex = 0;
  }

  public async start(): Promise<void> {
    if (this.isPlaying) {
      console.warn("Performance is already running.");
      return;
    }

    this.isPlaying = true;
    await Tone.start();
    console.log("Audio context started.");

    const performanceLoop = async () => {
      console.log("Performance loop started.");
      console.log(`${this.notes.length} notes to play.`);
      console.log(`Current tempo: ${this.currentTempo} BPM`);
      console.log(`Current score position: ${this.scorePosition} beats`);
      console.log(`Next note index: ${this.nextNoteIndex}`);
      console.log(`Is playing: ${this.isPlaying}`);
      while (this.isPlaying && this.nextNoteIndex < this.notes.length) {
        console.log("nextNoteIndex:", this.nextNoteIndex);
        console.log("notes length:", this.notes.length);
        const currentNote = this.notes[this.nextNoteIndex];
        const secondsPerBeat = 60 / this.currentTempo;

        if (this.scorePosition >= currentNote.offset) {
          console.log(
            `Playing note at offset ${currentNote.offset}: frequency ${currentNote.frequency}, duration ${currentNote.duration}`
          );
          this.synth.triggerAttackRelease(
            Tone.Frequency(currentNote.frequency, "midi").toFrequency(),
            currentNote.duration
          );
          this.nextNoteIndex += 1;
        }

        await new Promise((resolve) => setTimeout(resolve, 10));
      }

      console.log("Performance loop ended.");
    };

    performanceLoop();
  }

  public stop(): void {
    this.isPlaying = false;
  }
}

export default MidiPerformance;
// Function to connect and update the tempo
export function changeTempo(midiPerformance: MidiPerformance, newTempo: number): void {
  if (newTempo <= 0) {
    console.error("Tempo must be greater than 0.");
    return;
  }

  // Update the tempo using the setTempo method
  midiPerformance.setTempo(newTempo);
  console.log(`Tempo updated to ${newTempo} BPM.`);
}

// Function to connect and update the score position
export function changeScorePosition(midiPerformance: MidiPerformance, newPosition: number): void {
  if (newPosition < 0) {
    console.error("Score position cannot be negative.");
    return;
  }

  // Update the score position using the updateScorePosition method
  midiPerformance.updateScorePosition(newPosition);
  console.log(`Score position updated to ${newPosition} beats.`);
}

export async function togglePerformance(midiPerformance: MidiPerformance): Promise<void> {
  // Check if the performance is currently playing
  if (midiPerformance['isPlaying']) {
    // If playing, stop the performance
    midiPerformance.stop();
    console.log("Performance stopped.");
  } else {
    // If not playing, start the performance
    await midiPerformance.start();
    console.log("Performance started.");
  }
}