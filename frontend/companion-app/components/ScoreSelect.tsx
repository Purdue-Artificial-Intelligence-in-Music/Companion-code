import { StyleSheet, View, Text, TextStyle, Animated } from "react-native";
import RNPickerSelect from "react-native-picker-select";
import React, { useEffect } from "react";

export function Score_Select({
  state,
  dispatch,
  textStyle,
  borderStyle
}: {
  state: { score: string; scores: string[] };
  dispatch: Function;
  textStyle: Animated.AnimatedInterpolation<string | number>;
  borderStyle: Animated.AnimatedInterpolation<string | number>
}) {
  // Fetch scores from the backend
  useEffect(() => {
    const fetchScores = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/scores"); // Replace with your backend endpoint
        console.log("Response is: ", response);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const scores = data.files;
        console.log("Scores are: ", scores);
        dispatch({ type: "new_scores_from_backend", scores });
      } catch (error) {
        console.error("Failed to fetch scores:", error);
      }
    };

    fetchScores();
  }, [dispatch]);

  const handleFileUpload = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const xmlContent = e.target?.result as string;
      const newScore = {
        filename: file.name,
        piece: file.name.replace(".musicxml", ""),
        content: xmlContent,
      };
      dispatch({ type: "new_score_from_upload", score: newScore });
    };
    reader.readAsText(file);
  };

  const noteFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    } else {
      console.log("Fail");
    }
  };

  return (
    <View >
      <Animated.Text style={[{color: textStyle}, styles.text]}>Select a score:</Animated.Text>
      <View style={styles.input}>
        <RNPickerSelect
          key={state.scores.length} //RNPicker is a new instance depending on the length of score. So, it will rerender if updated
          onValueChange={(value) => {
            console.log("The dispatch function is being sent.");
            dispatch({ type: "change_score", score: value });
          }}
          items={state.scores.map((score) => ({
            label: score,
            value: score,
          }))}
          placeholder={{
            label: "Select a score",
            value: "air_on_the_g_string.musicxml",
          }}
        />
      </View>
      <Animated.Text style={[styles.text, {color: textStyle}]}>Or upload a new score:</Animated.Text>
      <Animated.View style={[styles.input, { borderBottomWidth: 2, borderBottomColor: borderStyle, paddingBottom: 24 }]}>
        <input type="file" accept=".musicxml" onChange={noteFileUpload} style={{color: "#000"}}/>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({

    // Main text styles (text labels)
    text : {
      fontSize: 24,
      fontWeight: "bold"
    },
    // Styles added to View component that wraps the inputs (used for spacing purposes)
    input: {
      paddingVertical: 12
    },

    // tempo_text_shape: {
    //     width: "30%",
    //     height: "100%"
    // },
    // tempo_input_shape: {
    //   width: "40%",
    //   height: "100%",
    //   backgroundColor: "white"
    // },
    // flexing_box: {
    //     width: "25%",
    //     height: "100%",
    //     display: "flex",
    //     padding: "2%",
    //     backgroundColor: "lightgray"
    // }
})
