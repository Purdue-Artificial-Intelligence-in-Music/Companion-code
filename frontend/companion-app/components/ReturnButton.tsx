import { StyleSheet, View, Text, TextStyle, ViewStyle, Pressable } from "react-native";

export function Return_Button({
    state,
    dispatch,
    button_format,
    text_style,
  }: {
    state: { inPlayMode: boolean };
    dispatch: Function;
    button_format: ViewStyle;
    text_style: TextStyle;
  }) {
    return (
        <View style={styles.flexing_box}>
            <Pressable
                style={{...styles.button_shape, ...button_format, ...{display: state.inPlayMode ? "flex": "none"}}}
                onPress={() => { dispatch({ type: "swap_mode" }); }}
            >
                <Text style={text_style}>{"↩️"}</Text>
            </Pressable>
        </View>
    );
  }

const styles = StyleSheet.create({
    button_shape: {
        width: "50%",
        height: "50%"
    },
    flexing_box: {
        width: "12.5%",
        height: "100%",
        justifyContent: "center",
        alignContent: "center",
        alignItems: "center"
    }
})