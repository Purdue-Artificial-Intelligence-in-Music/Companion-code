import RNPickerSelect from "react-native-picker-select";
import {
  View,
  Text,
} from "react-native";

export function Score_Select({
  scores,
  setScore,
  onFileUpload,
}: {
  scores: any[];
  setScore: Function;
  onFileUpload: (file: File) => void;
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
        onValueChange={(value) => setScore(value)}
        items={scores.map((score) => ({
          label: score.piece,
          value: score.filename,
        }))}
        placeholder={{ label: "Select a score", value: null }}
      />
      <Text>Or upload a new score:</Text>
      <input type="file" accept=".musicxml" onChange={handleFileUpload} />
    </View>
  );
}