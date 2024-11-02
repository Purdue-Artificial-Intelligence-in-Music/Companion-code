import { useEffect, useRef } from 'react';
import './App.css';
import * as music21 from 'music21j';
import AudioRecorder from './components/AudioRecorder';

function App() {
  // Create a ref to attach the musical score to a specific div
  const musicRef = useRef(null);

  useEffect(() => {
    const notes = [new music21.note.Note("F#"), new music21.note.Note("A#")]
    const stream = new music21.stream.Stream();
    stream.append(notes);

    if (musicRef.current) {
      stream.appendNewDOM(musicRef.current);
    }
  }, []); 

  return (
    <>
      <AudioRecorder />
      <div ref={musicRef}></div> {}   
    </>
  );
}

export default App;
