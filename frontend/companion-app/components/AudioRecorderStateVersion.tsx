import { useState, useRef, useEffect, Ref } from "react";
import { synchronize } from "./Utils";

const mimeType = "audio/webm";

const AudioRecorder = ({
  state,
  dispatch,
  updateWaveFormData
}: {
  state: { playing: boolean, inPlayMode: boolean };
  dispatch: Function;
  updateWaveFormData: Function
}) => {
  const [permission, setPermission] = useState(false);
  const mediaRecorder = useRef<MediaRecorder>(
    new MediaRecorder(new MediaStream()),
  );
  const [stream, setStream] = useState<MediaStream>(new MediaStream());
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
  const [audio, setAudio] = useState<string>("");
  const [, setAnalyserData] = useState<any>();

  const audioContextRef = useRef<any>(null);
  const analyserRef = useRef<any>(null);
  const dataArrayRef = useRef<any>(null);
  const startTimeRef = useRef<any>(null);

  // Starts recorder instances
  const startRecording = async () => {
    startTimeRef.current = Date.now();
    //create new Media recorder instance using the stream
    const media = new MediaRecorder(stream, { mimeType: mimeType });
    //set the MediaRecorder instance to the mediaRecorder ref
    mediaRecorder.current = media;
    //invokes the start method to start the recording process
    mediaRecorder.current.start();
    let localAudioChunks: Blob[] = [];
    mediaRecorder.current.ondataavailable = (event) => {
      if (typeof event.data === "undefined") return;
      if (event.data.size === 0) return;
      localAudioChunks.push(event.data);
    };
    setAudioChunks(localAudioChunks);

    audioContextRef.current = new window.AudioContext();
    const source = audioContextRef.current.createMediaStreamSource(stream);
    analyserRef.current = audioContextRef.current.createAnalyser();
    analyserRef.current.fftSize = 2048;
    source.connect(analyserRef.current);

    const bufferLength = analyserRef.current.frequencyBinCount;
    dataArrayRef.current = new Uint8Array(bufferLength);
  };

    // Analyze frequency data continuously
    const getFrequencyData = () => {
        if (state.playing && dataArrayRef.current) {
          analyserRef.current?.getByteTimeDomainData(dataArrayRef.current);
          const waveForm = Array.from(dataArrayRef.current);
          updateWaveFormData(waveForm);
          requestAnimationFrame(getFrequencyData);
        }
    };
  
    getFrequencyData();

  //stops the recording instance
  const stopRecording = () => {
    mediaRecorder.current.stop();
    audioContextRef.current?.close();
  };

  // Function to get permission to use browser microphone
  const getMicrophonePermission = async () => {
    if ("MediaRecorder" in window) {
      try {
        const streamData = await navigator.mediaDevices.getUserMedia({
          audio: true,
          video: false,
        });
        setPermission(true);
        setStream(streamData);
      } catch (err) {
        alert((err as Error).message);
      }
    } else {
      alert("The MediaRecorder API is not supported in your browser.");
    }
  };

  // Get microphone permission on first time entering play state
  useEffect(() => {
    if (!permission) getMicrophonePermission();
  }, [state.inPlayMode]);

  // Start and stop recording when player is or isn't playing
  useEffect(() => {
    if (state.playing) startRecording();
    else stopRecording();
  }, [state.playing]);

  return (
    <div
      style={{ display: "flex", flexDirection: "column", alignItems: "center" }}
    >
      <h1>Audio Recorder</h1>
      {audio ? (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <audio src={audio} controls></audio>
          <a download href={audio}>
            Download Recording
          </a>
        </div>
      ) : null}
    </div>
  );
};
export default AudioRecorder;
