import { StyleSheet, View, Text } from "react-native";
import { TextInput, TextStyle, ViewStyle } from "react-native";

export function TempoBox({
  state,
  dispatch,
  label_text_style,
  textStyle
}: {
  state: { tempo: number };
  dispatch: Function;
  label_text_style: TextStyle;
  textStyle: object;
}) {
  return (
    <View style={styles.container}>
      <Text style={textStyle}>Tempo (BPM):</Text>
      <TextInput
        onChangeText={(text) =>
          dispatch({ type: "change_tempo", tempo: text as unknown as number })
        }
        value={String(state.tempo)}
        placeholder="Enter tempo"
        inputMode="numeric"
        style={styles.input}
      />
    </View>
  );
}

const styles = StyleSheet.create({

    // Container for display both text and input on same line 
    container: {
      flexDirection: "row",
      alignItems: "center",
    },
    // Text label styles
    label: {
      fontSize: 16,
      fontWeight: "bold",
      color: "#2C3E50", // Dark gray for readability
      marginHorizontal: 5,
    },
    // Input for label styles
    input: {
      flex: 1,
      backgroundColor: "#FFFFFF",
      borderWidth: 1,
      borderColor: "#BDC3C7",
      borderRadius: 6,
      paddingHorizontal: 10,
      paddingVertical: 5,
      fontSize: 16,
      color: "#2C3E50",
      textAlign: "center",
    },
   
})
