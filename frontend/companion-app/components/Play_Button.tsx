import {
  Text,
  TextStyle,
  ViewStyle,
  Pressable,
} from "react-native";
import { OpenSheetMusicDisplay, Cursor } from "opensheetmusicdisplay";
import { MutableRefObject, useEffect, useRef } from "react";

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