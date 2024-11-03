import { View, Text, TextStyle, ViewStyle, Pressable  } from 'react-native';
import { OpenSheetMusicDisplay, Cursor } from 'opensheetmusicdisplay';
import { MutableRefObject, useEffect,  useRef } from 'react';

export function Start_Stop_Button( { state, dispatch, 
    button_style, text_style
     } : 
    { state: { playing: boolean }, dispatch: Function,
        button_style: ViewStyle, text_style: TextStyle
     } ) {
    
    // const timeoutRef = useRef<Number>();

    // function find_the_time() {
    //     if (my_cursor.current && my_cursor.current.NotesUnderCursor().length > 0 ) {
    //         const bpm = my_cursor.current?.Iterator.CurrentBpm ? my_cursor.current?.Iterator.CurrentBpm : 100
    //         const note_dur = my_cursor.current?.NotesUnderCursor().map( note => note.Length ).reduce( (prev, cur) => (prev < cur ? prev : cur));
    //         return 60000 / bpm * note_dur.RealValue
    //     } else return 0;
    // }

    return <Pressable style={ button_style } onPress={ () => {
        console.log("The play button's on_press runs.");
        dispatch({type: "start/stop"})
    }}>
        <Text style={ text_style }>{state.playing ? "STOP":"PLAY"}</Text>
    </Pressable>
}