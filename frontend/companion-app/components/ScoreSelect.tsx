import { StyleSheet, View, Text, Animated, Platform, TouchableOpacity } from "react-native";
import RNPickerSelect from "react-native-picker-select";
import React, { useEffect } from "react";
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import Icon from "react-native-vector-icons/FontAwesome";

export function Score_Select({
  state,
  dispatch,
  textStyle,
  borderStyle, 
  button_format,
  button_text_style
}: {
  state: { score: string; scores: string[] };
  dispatch: Function;
  textStyle: Animated.AnimatedInterpolation<string | number>;
  borderStyle: Animated.AnimatedInterpolation<string | number>
  button_format: object[];
  button_text_style: Animated.AnimatedInterpolation<string | number>;
}) {
  // Fetch scores from the backend
  // useEffect(() => {
  //   const fetchScores = async () => {
  //     try {
  //       const response = await fetch("http://127.0.0.1:5000/scores"); // Replace with your backend endpoint
  //       console.log("Response is: ", response);
  //       if (!response.ok) {
  //         throw new Error(`HTTP error! status: ${response.status}`);
  //       }
  //       const data = await response.json();
  //       const scores = data.files;
  //       console.log("Scores are: ", scores);
  //       dispatch({ type: "new_scores_from_backend", scores });
  //     } catch (error) {
  //       console.error("Failed to fetch scores:", error);
  //     }
  //   };

  //   fetchScores();
  // }, [dispatch]);

  // Array of score names used to render score display options 
  const musicxmlFiles: string[] = [
    'air_on_the_g_string.musicxml',
    'twelve_duets.musicxml',
  ];
  
  useEffect(() => {
    dispatch({ type: "new_scores_from_backend", scores: musicxmlFiles }); // pass in defined array of musicxml files
  }, [dispatch]);

  // Web file upload handler
  const noteFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        const xmlContent = ev.target?.result as string;
        const fileName = file.name; // extract the file name 
        if (!state.scores.includes(fileName)) { // only add new score if the new uploaded score's name isn't already stored within scores
          const newScore = {
            filename: fileName,
            piece: fileName.replace(".musicxml", ""),
            content: xmlContent,
          };
          dispatch({ type: "new_score_from_upload", score: newScore });
        }
      };
      reader.onerror = (e) => {
        console.error("Error reading file:", e);
      };      
      reader.readAsText(file);
    } else {
      console.log("No file selected");
    }
  };

  // mobile file upload handler
  const nativeNoteFileUpload = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: '*/*', // Alllow any file
        copyToCacheDirectory: true, // Save to cache for performance
      });
  
      if (result.canceled || !result.assets || result.assets.length === 0) { // Error handling  
        console.log("No file selected or canceled");
        return;
      }
      // Extract the file URI and name from the result
      const { uri, name: fileName } = result.assets[0];
      console.log("lets goooo!", fileName);
      
      // Error handling if file is not type .musicxml 
      if (!fileName.toLowerCase().endsWith('.musicxml')) {
        alert('Please select a .musicxml file');
        return;
      }
      // Only read from URI if file name is not already in the available scores
      if (!state.scores.includes(fileName)) {
        const xmlContent = await FileSystem.readAsStringAsync(uri, {
          encoding: FileSystem.EncodingType.UTF8,
        });
        
        // Setup payload  (object containing: filename, piecename (filtered out .musicxml), and the loaded xml content)
        const newScore = {
          filename: fileName,
          piece: fileName.replace(/\.musicxml$/, ''),
          content: xmlContent,
        };

        dispatch({ type: 'new_score_from_upload', score: newScore });
      }
      // Catch any errors (e.g. getting file using DocumentPicker or reading using FileSystem)
    } catch (err) {
      console.error('Error picking document:', err);
      alert('Something went wrong. Check console.');
    }
  };
  

  return (
    <View>
      <Animated.Text style={[{color: textStyle}, styles.text]}>Select a score:</Animated.Text>
      <View style={styles.input}>
        <RNPickerSelect
          key={state.scores.length} //RNPicker is a new instance depending on the length of score. So, it will rerender if updated
          onValueChange={(value) => {
            console.log("The dispatch function is being sent.");
            console.log("val: ", value)
            dispatch({ type: "change_score", score: value });
          }}
          items={state.scores.map((score) => ({
            label: score,
            value: score,
          }))}
          placeholder={{
            label: "Select a score",
            value: "",
          }}
          // Drop down arrow for mobile to select score
          Icon={Platform.OS !== 'web' ? () => <Icon name="chevron-down" size={16} color="#000" /> : undefined}
        />
      </View>

      <Animated.Text style={{ color: textStyle, marginTop: 12}}>Or upload a new score:</Animated.Text>
      <Animated.View style={[styles.input, { borderBottomWidth: 2, borderBottomColor: borderStyle, paddingBottom: 24 }]}>      

        {/* If on browser render upload field for web*/}
        {Platform.OS === 'web' ? 
        (
          <input type="file" accept=".musicxml" onChange={noteFileUpload} style={{ color: '#000' }} />
        ) : 
        (
          // Else render upload field for mobile
          <Animated.View 
            style={
              [...button_format]
            }
            >
              <TouchableOpacity onPress={nativeNoteFileUpload} >
                <Animated.Text style={{color: button_text_style, fontWeight: "bold"}}>Upload File</Animated.Text>
              </TouchableOpacity>
          </Animated.View>
        )}
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({

  // Main text styles (text labels)
  text : {
    fontSize: 24,
    fontWeight: "bold",
    // Text shadow properties
    textShadowColor: 'rgba(0, 0, 0, 0.3)', // Shadow color with transparency
    textShadowOffset: { width: 1, height: 1 }, // Slight offset
    textShadowRadius: 4,
  },
  // Styles added to View component that wraps the inputs (used for spacing purposes)
  input: {
    paddingVertical: 12
  },
})