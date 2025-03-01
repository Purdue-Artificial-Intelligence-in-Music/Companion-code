import { StyleSheet, View, Text } from "react-native";
import { Pressable, TextInput, TextStyle, ViewStyle } from "react-native";

export function MeasureSetBox({
  state,
  dispatch,
  button_style,
  button_text_style
}: {
  state: { resetMeasure: number };
  dispatch: Function;
  button_style: ViewStyle;
  button_text_style: TextStyle;
}) {
  return (
    <View style={styles.flexing_box}>
      <TextInput
        onChangeText={(text) =>
          dispatch({ type: "change_reset", measure: text as unknown as number })
        }
        value={String(state.resetMeasure)}
        placeholder="Enter measure number"
        inputMode="numeric"
        style={styles.measure_input_shape}
      />
      <Pressable
        style={{...button_style, ...styles.measure_button_shape}}
        onPress={() => {
          dispatch({ type: "reset" });
        }}
      >
        <Text style={button_text_style}>RESET</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
    measure_button_shape: {
        // width: "40%",
        // marginRight: "10%",
        // height: "50%"
    },
    measure_input_shape: {
      flex: 1,
      // width: "40%",
      // marginRight: "10%",
      // height: "50%",
      borderRadius: 15,
      backgroundColor: "white",
      padding: 6
    },
    flexing_box: {
      marginVertical: 12
        // width: "37.5%",
        // display: "flex",
        // flexDirection: "row",
        // justifyContent: "center",
        // alignContent: "center",
        // alignItems: "center"
    }
})
