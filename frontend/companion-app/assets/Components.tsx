import { Pressable, TextInput } from "react-native";
import RNPickerSelect from "react-native-picker-select";
import { View, Text } from 'react-native';
import { OpenSheetMusicDisplay, Cursor, Fraction } from 'opensheetmusicdisplay';
import { MutableRefObject, useEffect, useState, useRef } from 'react';

export function Score_Select( {score, scoreOptions, setScore}:
    { score: string, scoreOptions: Array<{ filename: string, piece: string}>, setScore: Function }
) {
    const my_options = scoreOptions.map( (score) => { return { label: score["piece"], value: score["filename"]}})
    return <div>
        {/* <Text>Choose a piece:</Text> */}
        <RNPickerSelect value={score} items={my_options} onValueChange={(value) => setScore(value)}/>
    </div>
}

export function Play_Button( { my_cursor, playing, setPlaying, 
    cursorPos, setCursorPos, osdRef
     } : 
    { my_cursor: MutableRefObject<Cursor | null>, playing: boolean, setPlaying: Function,
       cursorPos: number, setCursorPos: Function,
       osdRef: MutableRefObject<OpenSheetMusicDisplay | null>
     } ) {
    
    // const [cursorPos, setCursorPos] = useState<number>(-1);
    const timeoutRef = useRef<Number>();

    function find_the_time() {
        if (my_cursor.current && my_cursor.current.NotesUnderCursor().length > 0 ) {
            const bpm = my_cursor.current?.Iterator.CurrentBpm ? my_cursor.current?.Iterator.CurrentBpm : 100
            const note_dur = my_cursor.current?.NotesUnderCursor().map( note => note.Length ).reduce( (prev, cur) => (prev < cur ? prev : cur));
            return 60000 / bpm * note_dur.RealValue
        } else return 0;
    }

    useEffect(() => {
        if (playing) {
            console.log("Effect is running; cursorPos:", cursorPos);
            if (my_cursor.current) {
                my_cursor.current.next();
                osdRef.current?.render();
            } else console.log("Cursor somehow null.");
            const t = find_the_time();
            if (t) {
                setTimeout(move_function, t);
                console.log("Effect has set find_the_time(): ", t);
            }
        }
    }, [cursorPos]);
    
    //    If the function below is uncommented - even if it isn't called - the cursor doesn't appear
    const move_function = () => {
        if (my_cursor.current) {
            // console.log("Move function running, cursorPos: ", cursorPos);
            setCursorPos(cursorPos + 1);
        }
    }

    return <Pressable onPress={ () => {
        console.log("The play button's on_press runs.");
        if (my_cursor.current) {
            console.log("And it has a valid ref");
            my_cursor.current.reset();
            my_cursor.current.show();
            // osdRef.current?.render();
            console.log("Cursor should show.");
            setPlaying(true);
            // const bpm = my_cursor.current?.Iterator.CurrentBpm ? my_cursor.current?.Iterator.CurrentBpm : 100
            // const note_dur = my_cursor.current?.NotesUnderCursor().map( note => note.Length ).reduce( (prev, cur) => (prev < cur ? prev : cur));
            // const time = 60000 / bpm * note_dur.RealValue
            setCursorPos(0);
        }
    }}><Text>PLAY</Text></Pressable>
}

export function Next_Button( { my_cursor } : 
    { my_cursor: MutableRefObject<Cursor | null> } ) {
    return <Pressable onPress={ () => {
        console.log("The NEXT button's on_press runs.");
        if (my_cursor.current) {
            console.log("And it has a valid ref");
            my_cursor.current.next();
        }
    }}><Text>NEXT</Text></Pressable>
}

export function Stop_Button( { setPlaying } : 
    { setPlaying: Function } ) {
    return <Pressable onPress={ () => {
        setPlaying(false);
    }}><Text>STOP</Text></Pressable>
}

export function RenderSomethingButton( { osdRef } : { osdRef: MutableRefObject<OpenSheetMusicDisplay | null>}) {
    return(<Pressable onPress={ () => {
        osdRef.current?.setOptions( { autoResize: true });
        console.log("The RENDER SOMETHING button was pressed");
    }}>
        <Text>RENDER SOMETHING!!!</Text>
    </Pressable>)
}

export function TimeStampBox( { timestamp, setTimestamp } : 
    { timestamp: string, setTimestamp: (text: string) => void }) {
    return(
        <TextInput
        onChangeText={setTimestamp}
        value={timestamp}
        placeholder="useless placeholder"
        inputMode="numeric"
      />
    )
}

export function UpdateCursorBox( { timestamp, cursorRef, osdRef, cursorPos, setCursorPos } : 
    { timestamp: string, cursorRef: MutableRefObject<Cursor | null>,
        osdRef: MutableRefObject<OpenSheetMusicDisplay | null>,
        cursorPos: number, setCursorPos: Function
     }) {
    return(<Pressable onPress={ () => {
        if (cursorRef.current?.hidden) cursorRef.current?.show();
        var ts = Number(timestamp);
        var ct = cursorRef.current?.Iterator.CurrentSourceTimestamp.RealValue;
        var nct;
        var cpos = cursorPos;
        console.log("Number of cursors: ", osdRef?.current?.cursors.length)
        console.log("ts: ", ts, "\tct: ", ct);
        if (ct !== undefined) {
            while (ct < ts && !(cursorRef.current?.Iterator.EndReached)) {
                // cursorRef.current?.Iterator.moveToNext()
                cursorRef.current?.next();
                cpos += 1;
                nct = cursorRef.current?.Iterator.CurrentSourceTimestamp.RealValue
                if (nct !== undefined) ct = nct;
                console.log("ts: ", ts, "\tct: ", ct);
            }
            if (!(cursorRef.current?.Iterator.EndReached)) {
                // cursorRef.current?.Iterator.moveToPrevious()
                cursorRef.current?.previous();
                setCursorPos(cpos - 1);
            }
        }
        osdRef.current?.render();
    }}><Text>Update cursor to timestamp</Text></Pressable>)
}