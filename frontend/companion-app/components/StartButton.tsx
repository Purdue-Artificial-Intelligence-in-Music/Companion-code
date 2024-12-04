import { Text, TextStyle, ViewStyle, Pressable } from "react-native";

export function Start_Stop_Button({
  state,
  dispatch,
  button_style,
  text_style,
}: {
  state: { playing: boolean };
  dispatch: Function;
  button_style: ViewStyle;
  text_style: TextStyle;
}) {
  return (
    <Pressable
      style={button_style}
      onPress={() => {
        console.log("The play button's on_press runs.");
        dispatch({ type: "start/stop" });
      }}
    >
      <Text style={text_style}>{state.playing ? "STOP" : "PLAY"}</Text>
    </Pressable>
  );
}
