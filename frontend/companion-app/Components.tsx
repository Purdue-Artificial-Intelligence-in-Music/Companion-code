import { Pressable } from "react-native";
import RNPickerSelect from "react-native-picker-select";
import { View, Text, TextInput, Button } from 'react-native';
import { OpenSheetMusicDisplay, Cursor } from 'opensheetmusicdisplay';
import { MutableRefObject, useState } from 'react';




export function Score_Select( {score, scoreOptions, setScore}:
    { score: string, scoreOptions: Array<{ filename: string, piece: string}>, setScore: Function }
) {
    const my_options = scoreOptions.map( (score) => { return { label: score["piece"], value: score["filename"]}})
    return <div>
        <Text>Choose a piece:</Text>
        <RNPickerSelect value={score} items={my_options} onValueChange={(value) => setScore(value)}/>
    </div>
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
            my_cursor.current.Iterator.CurrentVoiceEntries[0].Notes[0].NoteheadColor = "#22ee55";
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