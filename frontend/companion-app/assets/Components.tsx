import { Button } from "react-native";
import RNPickerSelect from "react-native-picker-select";
import { View, Text } from 'react-native';

export function Score_Select( {score, scoreOptions, setScore}:
    { score: string, scoreOptions: Array<{ filename: string, piece: string}>, setScore: Function }
) {
    const my_options = scoreOptions.map( (score) => { return { label: score["piece"], value: score["filename"]}})
    return <div>
        <Text>Choose a piece:</Text>
        <RNPickerSelect value={score} items={my_options} onValueChange={(value) => setScore(value)}/>
    </div>
}