import { View, Text } from 'react-native';
import { Pressable, TextInput, TextStyle, ViewStyle } from "react-native";
import { MutableRefObject, useEffect,  useRef, useState } from 'react';
import { OpenSheetMusicDisplay, Cursor } from 'opensheetmusicdisplay';
import { Fraction } from 'opensheetmusicdisplay';

export function MeasureSetBox( { cursorRef, osdRef, timestamp, setTimestamp, style } : 
    { cursorRef: MutableRefObject<Cursor | null>, osdRef: MutableRefObject<OpenSheetMusicDisplay | null>,
        timestamp: string, setTimestamp: (text: string) => void, style: ViewStyle }) {
    
    const [resetMeasure, setResetMeasure] = useState<string>("1")
    const [needsReset, setNeedsReset] = useState<Boolean>(false)
    useEffect( () => {
        if (needsReset) {
            console.log(cursorRef.current?.Iterator.CurrentMeasure.ActiveTimeSignature);
            console.log(cursorRef.current?.Iterator.CurrentBpm);
            // Where is the time signature?
            let desired_index = Number(resetMeasure) - 1;
            let ts_secs = 0;
            let ts_meas = new Fraction(); // default value is 0 + 0/1, or 0
            var dt: Fraction;
            cursorRef.current?.resetIterator()
            while (cursorRef.current?.Iterator.CurrentMeasureIndex !== undefined && cursorRef.current?.Iterator.CurrentMeasureIndex < desired_index) {
                cursorRef.current?.Iterator.moveToNextVisibleVoiceEntry(false);
                dt = Fraction.minus(cursorRef.current?.Iterator.CurrentSourceTimestamp, ts_meas);
                ts_secs += dt.RealValue * cursorRef.current?.Iterator.CurrentBpm * cursorRef.current?.Iterator.CurrentMeasure.Duration.Denominator
            }
            cursorRef.current?.update();
            setNeedsReset(false);
        }
    }, [needsReset])

    return(
        <View>
            <Text>Start measure:</Text>
        <TextInput
            onChangeText={setResetMeasure}
            value={resetMeasure}
            placeholder="useless placeholder"
            inputMode="numeric"
        />
        <Pressable onPress={() => { setNeedsReset(true); }}><Text>RESET</Text></Pressable>
        </View>
        
    )
}