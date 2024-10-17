import { Pressable } from "react-native";
import RNPickerSelect from "react-native-picker-select";
import { View, Text, TextInput } from 'react-native';
import { OpenSheetMusicDisplay, Cursor } from 'opensheetmusicdisplay';
import { MutableRefObject, useState } from 'react';

// export function Score_Select( {score, scoreOptions, setScore}:
//     { score: string, scoreOptions: Array<{ filename: string, piece: string}>, setScore: Function }
// ) {
//     const my_options = scoreOptions.map( (score) => { return { label: score["piece"], value: score["filename"]}})
//     return <div>
//         <Text>Choose a piece:</Text>
//         <RNPickerSelect value={score} items={my_options} onValueChange={(value) => setScore(value)}/>
//     </div>
// }

export function Score_Select({ scores, setScore, onFileUpload }: { scores: any[], setScore: Function, onFileUpload: (file: File) => void }) {
    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
          onFileUpload(file);
        }
        else {
            console.log("Fail")
        }
      
    
    }
    return (
      <View>
        <Text>Select a score:</Text>
        <RNPickerSelect
          key = {scores.length} //RNPicker is a new instance depending on the length of score. So, it will rerender if updated
          onValueChange={(value) => setScore(value)}
          items={scores.map((score) => ({
            label: score.piece,
            value: score.filename,
          }))}
          placeholder={{ label: "Select a score", value: null }}
        />
        <Text>Or upload a new score:</Text>
        <input
          type="file"
          accept=".musicxml"
          onChange={handleFileUpload}
        />
      </View>
    );
  }
export function Play_Button( { my_cursor, playing, setPlaying } : 
    { my_cursor: MutableRefObject<Cursor | null>, playing: boolean, setPlaying: Function } ) {
    
        // If the function below is uncommented - even if it isn't called - the cursor doesn't appear
    // const move_function = () => {
    //     if (my_cursor.current) {
    //         my_cursor.current?.next()
    //         const bpm = my_cursor.current?.Iterator.CurrentBpm ? my_cursor.current?.Iterator.CurrentBpm : 100
    //         const note_dur = my_cursor.current?.NotesUnderCursor().map( note => note.Length ).reduce( (prev, cur) => (prev < cur ? prev : cur));
    //         const time = 60000 / bpm * note_dur.RealValue
    //         console.log("Moving time: ", time)
    //         setTimeout(move_function, time)
    //     }
    // }

    return <Pressable onPress={ () => {
        console.log("The play button's on_press runs.");
        if (my_cursor.current) {
            console.log("And it has a valid ref");
            my_cursor.current.reset();
            my_cursor.current.show();
            setPlaying(true);
            // const bpm = my_cursor.current?.Iterator.CurrentBpm ? my_cursor.current?.Iterator.CurrentBpm : 100
            // const note_dur = my_cursor.current?.NotesUnderCursor().map( note => note.Length ).reduce( (prev, cur) => (prev < cur ? prev : cur));
            // const time = 60000 / bpm * note_dur.RealValue
            // setTimeout(move_function, time)
        }
    }}><Text>PLAY</Text></Pressable>
}

export function Next_Button( { my_cursor } : 
    { my_cursor: MutableRefObject<Cursor | null> } ) {
    return <Pressable onPress={ () => {
        console.log("The NEXT button's on_press runs.");
        if (my_cursor.current) {
            console.log("And it has a valid ref");
            my_cursor.current.Iterator.CurrentVoiceEntries[0].Notes[0].NoteheadColor = "red";
            my_cursor.current.next();
        }
    }}><Text>NEXT</Text></Pressable>
}

export function RenderSomethingButton( { osdRef } : { osdRef: MutableRefObject<OpenSheetMusicDisplay | null>}) {
    return(<Pressable onPress={ () => {
        osdRef.current?.setOptions( { autoResize: true });
        console.log("The RENDER SOMETHING button was pressed");
    }}>
        <Text>RENDER SOMETHING!!!</Text>
    </Pressable>)
}