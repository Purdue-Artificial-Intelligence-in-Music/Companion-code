import React, { useEffect } from 'react';
import {
  Platform,
  StyleSheet,
  View,
  Text,
  Animated,
  TouchableOpacity,
} from 'react-native';
import RNPickerSelect from 'react-native-picker-select';
import Icon from 'react-native-vector-icons/FontAwesome';

// Conditionally require native modules
let DocumentPicker: any;
let FileSystem: any;
if (Platform.OS !== 'web') {
  DocumentPicker = require('expo-document-picker');
  FileSystem = require('expo-file-system');
}


export function Score_Select({
  state,
  dispatch,
  textStyle,
  borderStyle,
}: {
  state: { score: string; scores: string[] };
  dispatch: Function;
  textStyle: Animated.AnimatedInterpolation<string | number>;
  borderStyle: Animated.AnimatedInterpolation<string | number>;
}) {

  // Array of score names used to render score display options 
  const musicxmlFiles: string[] = [
    'air_on_the_g_string.musicxml',
    'twelve_duets.musicxml',
  ];

  useEffect(() => {
    dispatch({ type: 'new_scores_from_backend', scores: musicxmlFiles }); // pass in defined array of musicxml files
  }, [dispatch]);

  // Handlers
  const handleWebUpload = (e: React.ChangeEvent<HTMLInputElement>) => {

    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onload = (ev) => {
      const xmlContent = ev.target?.result as string;
      const name = file.name; // extract the file name 
      if (!state.scores.includes(name)) { // only add new score if the new uploaded score's name isn't already stored within scores
        const newScore = {
          filename: file.name,
          piece: file.name.replace(".musicxml", ""),
          content: xmlContent,
        };
        dispatch({ type: "new_score_from_upload", score: newScore }); 
      }
    };
    reader.onerror = (e) => {
      console.error("Error reading file:", e);
    };
    reader.readAsText(file); // invokes reader.onload()
  };

  const handleNativeUpload = async () => {
    try {
      const res = await DocumentPicker.getDocumentAsync({
        type: ['application/*', 'text/*'],
        copyToCacheDirectory: true,
      });
      if (res.type === 'success') {
        const xmlContent = await FileSystem.readAsStringAsync(res.uri);
        if (!state.scores.includes(res.name)) {
          dispatch({
            type: 'new_score_from_upload',
            score: { filename: res.name, piece: res.name.replace('.musicxml', ''), content: xmlContent },
          });
        }
      }
    } catch (err) {
      console.error('File pick error:', err);
    }
  };

  // When selection changes
  const onSelect = (value: string) => {
    if (value) dispatch({ type: 'change_score', score: value });
  };

  return (
    <View>
      <Animated.Text style={[styles.text, { color: textStyle }]}>Select a score:</Animated.Text>
      <View style={styles.inputContainer}>
        {Platform.OS === 'web' ? (
          <select
            value={state.score || ''}
            onChange={(e) => onSelect(e.target.value)}
            style={styles.webSelect as any}
          >
            <option value="" disabled>
              select a score...
            </option>
            {state.scores.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        ) : (
          <RNPickerSelect
            useNativeAndroidPickerStyle={false}
            placeholder={{ label: 'Select a score...', value: null }}
            value={state.score}
            onValueChange={onSelect}
            items={state.scores.map((s) => ({ label: s, value: s }))}
            style={{
              inputIOS: styles.pickerInput,
              inputAndroid: styles.pickerInput,
              iconContainer: styles.iconContainer,
            }}
            Icon={() => <Icon name="chevron-down" size={20} color="#000" />}
          />
        )}
      </View>

      <Animated.Text style={[styles.text, { color: textStyle }]}>Or upload a new score:</Animated.Text>
      <View style={[styles.inputContainer, { borderBottomWidth: 2, borderBottomColor: borderStyle, paddingBottom: 24 }]}
      >
        {Platform.OS === 'web' ? (
          <input
            type="file"
            accept=".musicxml"
            onChange={handleWebUpload}
            style={{ color: '#000' }}
          />
        ) : (
          <TouchableOpacity style={styles.button} onPress={handleNativeUpload}>
            <Text style={styles.buttonText}>Upload a file</Text>
          </TouchableOpacity>
        )}
      </View>
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
    marginBottom: 8,
  },
  inputContainer: {
    marginBottom: 16,
  },
  webSelect: {
    width: '100%',
    padding: 8,
    fontSize: 16,
    borderColor: '#ccc',
    borderWidth: 1,
    borderRadius: 4,
    backgroundColor: '#fff',
  },
  pickerInput: {
    color: '#000',
    fontSize: 16,
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 4,
    backgroundColor: '#fff',
  },
  iconContainer: {
    top: 16,
    right: 12,
  },
  button: {
    padding: 12,
    backgroundColor: '#2C3E50',
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: "bold"
  },
});
