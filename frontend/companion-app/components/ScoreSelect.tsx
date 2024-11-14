import { View, Text } from "react-native";
import RNPickerSelect from "react-native-picker-select";
import { Fraction } from "opensheetmusicdisplay";

export function Score_Select({
    scores,
    setScore,
    onFileUpload,
    state,
    dispatch
  }: {
    scores: any[],
    setScore: Function,
    onFileUpload: (file: File) => void,
    state : { score: string, scores: Array<{filename: string}>},
    dispatch: Function
  }) {
    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        onFileUpload(file);
      } else {
        console.log("Fail");
      }
    };
    return (
      <View>
        <Text>Select a score:</Text>
        <RNPickerSelect
          key={scores.length} //RNPicker is a new instance depending on the length of score. So, it will rerender if updated
          onValueChange={(value) => { 
            // setScore(value); 
            console.log("The dispatch function is being sent.");
            dispatch({ type:'change_score', score:value}) 
        } }
          items={scores.map((score) => ({
            label: score.piece,
            value: score.filename,
          }))}
          placeholder={{ label: "Select a score", value: "air_on_the_g_string.musicxml" }}
        />
        <Text>Or upload a new score:</Text>
        <input type="file" accept=".musicxml" onChange={handleFileUpload} />
        <Text>Now viewing: {state.score}</Text>
      </View>
    );
  }