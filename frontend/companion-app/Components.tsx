import RNPickerSelect from "react-native-picker-select";
import {
  View,
  Text,
  TextInput,
  Button,
  TextStyle,
  ViewStyle,
  Pressable,
} from "react-native";
import { OpenSheetMusicDisplay, Cursor } from "opensheetmusicdisplay";
import { MutableRefObject, useEffect, useRef } from "react";

export function Score_Select({
  scores,
  setScore,
  onFileUpload,
}: {
  scores: any[];
  setScore: Function;
  onFileUpload: (file: File) => void;
}) {
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileUpload(file);
    } else {
      console.log("Fail");
    }
  };
  return (
    <View>
      <Text>Select a score:</Text>
      <RNPickerSelect
        key={scores.length} //RNPicker is a new instance depending on the length of score. So, it will rerender if updated
        onValueChange={(value) => setScore(value)}
        items={scores.map((score) => ({
          label: score.piece,
          value: score.filename,
        }))}
        placeholder={{ label: "Select a score", value: null }}
      />
      <Text>Or upload a new score:</Text>
      <input type="file" accept=".musicxml" onChange={handleFileUpload} />
    </View>
  );
}

export function Play_Button({
  my_cursor,
  playing,
  setPlaying,
  button_style,
  text_style,
  cursorPos,
  setCursorPos,
  osdRef,
}: {
  my_cursor: MutableRefObject<Cursor | null>;
  playing: boolean;
  setPlaying: Function;
  button_style: ViewStyle;
  text_style: TextStyle;
  cursorPos: number;
  setCursorPos: Function;
  osdRef: MutableRefObject<OpenSheetMusicDisplay | null>;
}) {
  const timeoutRef = useRef<Number>();

  function find_the_time() {
    if (my_cursor.current && my_cursor.current.NotesUnderCursor().length > 0) {
      const bpm = my_cursor.current?.Iterator.CurrentBpm
        ? my_cursor.current?.Iterator.CurrentBpm
        : 100;
      const note_dur = my_cursor.current
        ?.NotesUnderCursor()
        .map((note) => note.Length)
        .reduce((prev, cur) => (prev < cur ? prev : cur));
      return (60000 / bpm) * note_dur.RealValue;
    } else return 0;
  }

  useEffect(() => {
    if (playing) {
      console.log("Effect is running; cursorPos:", cursorPos);
      if (my_cursor.current) {
        my_cursor.current.next();
        osdRef.current?.render();
      } else console.log("Cursor somehow null.");
      const t = find_the_time();
      if (t) {
        setTimeout(move_function, t);
        console.log("Effect has set find_the_time(): ", t);
      }
    }
  }, [cursorPos]);

  //    If the function below is uncommented - even if it isn't called - the cursor doesn't appear
  const move_function = () => {
    if (my_cursor.current) {
      // console.log("Move function running, cursorPos: ", cursorPos);
      setCursorPos(cursorPos + 1);
    }
  };

  return (
    <Pressable
      style={button_style}
      onPress={() => {
        console.log("The play button's on_press runs.");
        if (my_cursor.current) {
          console.log("And it has a valid ref");
          my_cursor.current.reset();
          my_cursor.current.show();
          console.log("Cursor should show.");
          setPlaying(true);
          setCursorPos(0);
        }
      }}
    >
      <Text style={text_style}>PLAY</Text>
    </Pressable>
  );
}

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
