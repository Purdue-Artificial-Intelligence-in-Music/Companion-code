import { StyleSheet, View, Text, TextStyle, ViewStyle, Pressable, Animated } from "react-native";
import Icon from "react-native-vector-icons/FontAwesome"; // Font Awesome import for icons

export function Return_Button({
    state,
    dispatch,
    button_format,
    text_style,
  }: {
    state: { inPlayMode: boolean };
    dispatch: Function;
    button_format: object[];
    text_style: Animated.AnimatedInterpolation<string | number>;
  }) {
    return (
        <Animated.View style={state.inPlayMode? [...button_format]: {}}>
            <Pressable
                style={[{...styles.button_shape, ...{display: state.inPlayMode ? "flex": "none"}}]}
                onPress={() => { dispatch({ type: "swap_mode" }); }}
            >
                {/* Font Awesome Return Arrow Icon */}
                <Animated.Text style={[{color: text_style, textAlign: "center"}]}>
                    <Icon name="arrow-left" size={14} /> 
                </Animated.Text>
            </Pressable>
        </Animated.View>
    );
  }
const styles = StyleSheet.create({
    button_shape: {
        // width: "50%",
        // height: "50%"
    },
    flexing_box: {
        // width: "12.5%",
        // height: "100%",
        // justifyContent: "center",
        // alignContent: "center",
        // alignItems: "center"
    },
})