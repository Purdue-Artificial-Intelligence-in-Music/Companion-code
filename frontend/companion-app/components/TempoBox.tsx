import { View, Text } from "react-native";
import { TextInput, TextStyle, ViewStyle } from "react-native";

export function TempoBox({
  state,
  dispatch,
  wrapper_style,
  text_input_style,
  label_text_style,
}: {
  state: { tempo: number };
  dispatch: Function;
  wrapper_style: ViewStyle;
  text_input_style: ViewStyle;
  label_text_style: TextStyle;
}) {
  return (
    <View style={wrapper_style}>
      <Text style={label_text_style}>Tempo (BPM):</Text>
      <TextInput
        onChangeText={(text) =>
          dispatch({ type: "change_tempo", tempo: text as unknown as number })
        }
        value={String(state.tempo)}
        placeholder="Enter tempo"
        inputMode="numeric"
        style={text_input_style}
      />
    </View>
  );
}
