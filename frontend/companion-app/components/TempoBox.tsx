import { StyleSheet, View, Text } from "react-native";
import { TextInput, TextStyle, ViewStyle } from "react-native";

export function TempoBox({
  state,
  dispatch,
  label_text_style,
}: {
  state: { tempo: number };
  dispatch: Function;
  label_text_style: TextStyle;
}) {
  return (
    <View style={styles.flexing_box}>
      <View style={styles.tempo_text_shape}>
        <Text style={label_text_style}>Tempo:</Text>
      </View>
      <TextInput
        onChangeText={(text) =>
          dispatch({ type: "change_tempo", tempo: text as unknown as number })
        }
        value={String(state.tempo)}
        placeholder="Enter tempo"
        inputMode="numeric"
        style={styles.tempo_input_shape}
      />
      <View style={styles.tempo_text_shape}>
        <Text style={label_text_style}>BPM</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
    tempo_text_shape: {
        width: "30%",
        padding: "10%",
        justifyContent: "center"
    },
    tempo_input_shape: {
      width: "40%",
      height: "50%",
      borderRadius: 15,
      backgroundColor: "white"
    },
    flexing_box: {
        width: "37.5%",
        display: "flex",
        flexDirection: "row",
        justifyContent: "center",
        alignContent: "center",
        alignItems: "center"
    }
})
