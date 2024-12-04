import {
  Text,
  TextStyle,
  ViewStyle,
  Pressable,
} from "react-native";

export function Stop_Button({
    setPlaying,
    button_style,
    text_style,
  }: {
    setPlaying: Function;
    button_style: ViewStyle;
    text_style: TextStyle;
  }) {
    return (
      <Pressable
        style={button_style}
        onPress={() => {
          setPlaying(false);
        }}
      >
        <Text style={text_style}>STOP</Text>
      </Pressable>
    );
  }