import { View, Text } from 'react-native';
import { Pressable, TextInput, TextStyle, ViewStyle } from "react-native";
import { MutableRefObject, useEffect,  useRef, useState } from 'react';
import { OpenSheetMusicDisplay, Cursor } from 'opensheetmusicdisplay';
import { Fraction } from 'opensheetmusicdisplay';

export function MeasureSetBox( { state, dispatch, wrapper_style, button_style, text_input_style, button_text_style, label_text_style, BPM, TSD } : 
    { state: {resetMeasure: number}, dispatch: Function, wrapper_style: ViewStyle,
        button_style: ViewStyle, text_input_style: ViewStyle, button_text_style: TextStyle, label_text_style: TextStyle,
        BPM: number, TSD: number // Beats per minute and time signature denominator, respectively
    }) {
    
    // const [needsReset, setNeedsReset] = useState<boolean>(false); // indicates whether a reset to start measure is occurring
    // const [resetMeasure, setResetMeasure] = useState<string>("1")
    
    // useEffect( () => {
    //     if (needsReset) {
    //         let desired_index = Number(resetMeasure) - 1;
    //         // // If we are using the active BPM and time signature in the given score, uncomment: 
    //         // let ts_meas = new Fraction(); // default is 0 + 0/1 = 0
    //         // let ts_secs = 0;
    //         // var dt;
    //         cursorRef.current?.resetIterator()
    //         while (cursorRef.current?.Iterator.CurrentMeasureIndex !== undefined && cursorRef.current?.Iterator.CurrentMeasureIndex < desired_index) {
    //             cursorRef.current?.Iterator.moveToNextVisibleVoiceEntry(false);
    //             // // If we are using the active BPM and time signature in the given score, uncomment: 
    //             // dt = Fraction.minus(cursorRef.current?.Iterator.CurrentSourceTimestamp, ts_meas);
    //             // // dt is a fraction indicating how much - in whole notes - the iterator moved
    //             // ts_secs += 60 * dt.RealValue * cursorRef.current?.Iterator.CurrentMeasure.ActiveTimeSignature.Denominator / cursorRef.current?.Iterator.CurrentBpm
    //             // ts_meas = Fraction.plus(ts_meas, dt);
    //         }
    //         if (cursorRef.current?.Iterator.CurrentSourceTimestamp.RealValue !== undefined) {
    //             // // If we are using the active BPM and time signature in the given score, REcomment: 
    //             setTimestamp(60 * cursorRef.current?.Iterator.CurrentSourceTimestamp.RealValue * TSD / BPM)
    //             // // If we are using the active BPM and time signature in the given score, uncomment: 
    //             // setTimestamp(ts_secs);
    //         }
    //         // either way, the calculation is:
    //         // 60 secs/min * dt wholes * time signature denominator (beats/whole) / BPM (beats/minute) yields seconds
    //         setNeedsReset(false);
    //         cursorRef.current?.update();
    //     }
    // }, [needsReset])

    return(
        <View style={wrapper_style}>
            <Text style={label_text_style}>Start measure:</Text>
        <TextInput
            onChangeText={(text) => dispatch( { type:'change_reset', measure:Number(text) })}
            value={String(state.resetMeasure)}
            placeholder="Enter measure number"
            inputMode="numeric"
            style={text_input_style}
        />
        <Pressable style={button_style} onPress={() => { dispatch( { type:'reset' } ); }}>
            <Text style={button_text_style}>RESET</Text>
        </Pressable>
        </View>
        
    )
}