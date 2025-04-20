// ScoreDisplay.tsx
import React, { useRef, useEffect, useState } from 'react';
import {
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
  NativeSyntheticEvent,
  NativeScrollEvent,
} from 'react-native';
import { WebView, WebViewMessageEvent } from 'react-native-webview';
import { Cursor, OpenSheetMusicDisplay } from 'opensheetmusicdisplay';
import Icon from 'react-native-vector-icons/FontAwesome';
import scoresData from '../musicxml/scores'; // Local mapping of score filenames to XML content


// Conditionally require native modules for mobile
let DocumentPicker: any, FileSystem: any;
if (Platform.OS !== 'web') {
  DocumentPicker = require('expo-document-picker');
  FileSystem = require('expo-file-system');
}

export default function ScoreDisplay({
  state,
  dispatch,
}: {
  state: any;
  dispatch: any;
}) {
  // Shared state for both platforms (speed / steps)
  const [steps, setSteps] = useState('1');
  const [speed, setSpeed] = useState('500');

  // Refs for web version
  const osmContainerRef = useRef<HTMLDivElement | null>(null); // Reference for the SVG container
  // Create refs to the cursor and to the OSDiv
  const cursorRef = useRef<Cursor | null>(null); 
  const osdRef = useRef<OpenSheetMusicDisplay | null>(null);

  const scrollViewRef = useRef<ScrollView>(null); // reference to scroll view component
  const scrollPositionRef = useRef(0); // ref to keep track of current y position of scroll view (used ref instead of state to prevent rerender when scroll)

  // Refs/state for native version
  const webviewRef = useRef<WebView>(null);
  const [webviewHtml, setWebviewHtml] = useState('');

  // Function that is used to move cursor x amount of steps, updating the cursor y milleconds
  const moveCursorAhead = () => {
    const s = parseInt(steps, 10) || 1; // parse 
    const sp = parseInt(speed, 10) || 500;

    // web logic
    if (Platform.OS === 'web') {
      // return if error in cursor or osd 
      if (!cursorRef.current || !osdRef.current) return;

      // Make sure Y position is always 0 when starting the cursor 
      scrollPositionRef.current = 0;

      const stepFn = (i: number) => {
        if (i >= s) return;
        cursorRef.current!.next();
        osdRef.current!.render();
        scrollUp(scrollPositionRef.current);
        setTimeout(() => stepFn(i + 1), sp);
      };

      stepFn(0);

    } else {
      // Safely call the _moveCursor function inside the WebView (native) to animate the OSMD cursor
      // s = number of steps to move, sp = speed in ms between steps
      // The `true;` at the end ensures the injected JS returns something non-falsy to avoid WebView warnings
      webviewRef.current?.injectJavaScript(
        `window._moveCursor(${s}, ${sp}); true;`
      );
    }
  };

  // WEB: initialize OSMD
  useEffect(() => {

    // ignore this use effect if on mobile
    if (Platform.OS !== 'web') return;

    // Remove any previously-loaded music
    if (osmContainerRef.current) {
      while (osmContainerRef.current.firstChild) {
        osmContainerRef.current.removeChild(
          osmContainerRef.current.firstChild
        );
      }
    }
    if (!state.score) return;

    const xml = scoresData[state.score];
    if (!xml) return;

    const osm = new OpenSheetMusicDisplay(
      osmContainerRef.current as HTMLElement,
      { autoResize: true, followCursor: true }
    );
    osdRef.current = osm;

    osm
      .load(xml)
      .then(() => {
        osm.render();
        cursorRef.current = osm.cursor;
        cursorRef.current.show();
        cursorRef.current.CursorOptions = {
          ...cursorRef.current.CursorOptions,
          follow: true,
        };
        dispatch({
          type: 'update_piece_info',
          time_signature:
            cursorRef.current.Iterator.CurrentMeasure.ActiveTimeSignature,
          tempo: 100,
        });
        // expose for stepping
        (window as any)._moveCursor = (steps: number, speed: number) => {
          let i = 0;
          const fn = () => {
            if (i >= steps) return;
            cursorRef.current!.next();
            osm.render();
            i++;
            setTimeout(fn, speed);
          };
          fn();
        };
      })
      .catch((err) => console.error('Error loading OSMD:', err));
  }, [state.score]);

  // === NATIVE: prepare HTML for WebView ===
  useEffect(() => {
    if (Platform.OS === 'web') return;
    if (!state.score) return;

    const xml = scoresData[state.score];
    if (!xml) return;
    const escaped = JSON.stringify(xml);

    const html = `<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<script src="https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.7.6/build/opensheetmusicdisplay.min.js"></script>
<style>html,body{margin:0;padding:0;height:100%}#osmd{width:100%;height:100%;}</style>
</head><body>
  <div id="osmd"></div>
  <script>
    let osmd;
    document.addEventListener('DOMContentLoaded', async () => {
      osmd = new opensheetmusicdisplay.OpenSheetMusicDisplay('osmd',{autoResize:true,followCursor:true});
      await osmd.load(${escaped});
      osmd.render();
      osmd.cursor.show();
      const ts = osmd.cursor.Iterator.CurrentMeasure.ActiveTimeSignature;
      const tempo = osmd.sheet.SourceMeasures[0].tempoInBPM || 100;
      window.ReactNativeWebView.postMessage(JSON.stringify({type:'LOADED',timeSignature:ts,tempo}));
      window._moveCursor = (steps,speed) => {
        let i=0;
        const fn=()=>{ if(i>=steps) return; osmd.cursor.next(); osmd.render(); i++; setTimeout(fn,speed); };
        fn();
      };
    });

    window.addEventListener('message', ev => {
      try {
        const m = JSON.parse(ev.data);
        if (m.type === 'NEXT') { osmd.cursor.next(); osmd.render(); }
        if (m.type === 'RESET') { osmd.cursor.reset(); osmd.render(); }
      } catch {}
    });
  </script>
</body></html>`;

    setWebviewHtml(html);
  }, [state.score]);


  // Function used for scrolling vertically through the OSM Container based on passed in value
  const scrollUp = (y: number) => {
    scrollViewRef.current?.scrollTo({ y, animated: false });
  };
  
  // Function used to listen to scroll on OSM container and saves current Y position
  const handleScroll = (e: NativeSyntheticEvent<NativeScrollEvent>) => {
    scrollPositionRef.current = e.nativeEvent.contentOffset.y;
  };

  // Handle messages from WebView (native)
  const onWebViewMessage = (e: WebViewMessageEvent) => {
    try {
      const msg = JSON.parse(e.nativeEvent.data);
      if (msg.type === 'LOADED') {
        dispatch({
          type: 'update_piece_info',
          time_signature: msg.timeSignature,
          tempo: msg.tempo,
        });
      }
    } catch {}
  };

  return (
    <>
      {/* Inputs + Start button (shared) */}
      <TextInput
        value={steps}
        onChangeText={setSteps}
        placeholder="Type Number Of Steps"
        keyboardType="numeric"
      />
      <TextInput
        value={speed}
        onChangeText={setSpeed}
        placeholder="Type Cursor Update Speed (ms)"
        keyboardType="numeric"
      />
      <TouchableOpacity style={styles.startBtn} onPress={moveCursorAhead}>
        <Text style={styles.startBtnText}>Start</Text>
      </TouchableOpacity>

      {Platform.OS === 'web' ? (
        // ====== YOUR ORIGINAL WEB LAYOUT ======
        <ScrollView
          indicatorStyle="white"
          contentContainerStyle={{ flexGrow: 1 }}
          showsVerticalScrollIndicator
          ref={scrollViewRef}
          onScroll={handleScroll}
          scrollEventThrottle={16}
          style={styles.scrollContainer}
        >
          <div ref={osmContainerRef as any} style={styles.osmContainer} />
          <Text style={styles.text}>
            <Icon name="music" size={20} color="#2C3E50" /> Reference to the
            SVG container for sheet music <Icon name="music" size={20} color="#2C3E50" />
          </Text>
        </ScrollView>
      ) : webviewHtml ? (
        // ====== NATIVE: mirror via WebView ======
        <View style={styles.webviewWrapper}>
          <WebView
            ref={webviewRef}
            originWhitelist={['*']}
            source={{ html: webviewHtml }}
            onMessage={onWebViewMessage}
            javaScriptEnabled
            style={[styles.osmContainer, {flex: 1}]}
          />
        </View>
      ) : null}
    </>
  );
}

const styles = StyleSheet.create({
  scrollContainer: {
    width: '100%',
    height: '100%',
    borderWidth: 1,
    borderColor: 'black',
  },
  osmContainer: {
    width: '100%',
    borderWidth: 1,
    borderColor: 'black',
    overflow: 'hidden',
    // no height here, so on web it expands to fit full score
  },
  text: {
    fontSize: 20,
    textAlign: 'center',
    color: '#2C3E50',
    marginTop: 8,
  },
  input: {
    borderColor: '#ccc',
    borderWidth: 1,
    padding: 8,
    marginVertical: 4,
  },
  startBtn: {
    backgroundColor: '#007AFF',
    borderRadius: 4,
    alignItems: 'center',
    marginVertical: 6,
  },
  startBtnText: { color: '#fff' },
  webviewWrapper: { flex: 1 },
});