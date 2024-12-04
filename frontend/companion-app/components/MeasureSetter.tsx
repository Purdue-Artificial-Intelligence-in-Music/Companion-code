import { View, Text } from "react-native";
import { Pressable, TextInput, TextStyle, ViewStyle } from "react-native";

export function MeasureSetBox({
  state,
  dispatch,
  wrapper_style,
  button_style,
  text_input_style,
  button_text_style,
  label_text_style,
}: {
  state: { resetMeasure: number };
  dispatch: Function;
  wrapper_style: ViewStyle;
  button_style: ViewStyle;
  text_input_style: ViewStyle;
  button_text_style: TextStyle;
  label_text_style: TextStyle;
}) {
  return (
    <View style={wrapper_style}>
      <Text style={label_text_style}>Start measure:</Text>
      <TextInput
        onChangeText={(text) =>
          dispatch({ type: "change_reset", measure: text as unknown as number })
        }
        value={String(state.resetMeasure)}
        placeholder="Enter measure number"
        inputMode="numeric"
        style={text_input_style}
      />
      <Pressable
        style={button_style}
        onPress={() => {
          dispatch({ type: "reset" });
        }}
      >
        <Text style={button_text_style}>RESET</Text>
      </Pressable>
    </View>
  );
}
