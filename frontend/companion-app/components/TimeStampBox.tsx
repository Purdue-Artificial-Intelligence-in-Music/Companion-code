import {
  View,
  Text,
  TextInput,
  ViewStyle,
} from "react-native";

export function TimeStampBox({
    timestamp,
    setTimestamp,
    style,
  }: {
    timestamp: number;
    setTimestamp: (val: number) => void;
    style: ViewStyle;
  }) {
    return (
      <View style={style}>
        <Text>Go to time in seconds live:</Text>
        <TextInput
          onChangeText={(mytext) => {
            setTimestamp(Number(mytext));
          }}
          value={String(timestamp)}
          placeholder="0"
          inputMode="numeric"
        />
      </View>
    );
  }