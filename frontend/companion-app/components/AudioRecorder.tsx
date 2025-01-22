import { useState, useRef } from "react";

const mimeType = "audio/webm";

const AudioRecorder = ({
  state,
  dispatch,
}: {
  state: { playing: boolean }; // state.playing should likely take the role of recordingStatus;
  // it is changed by the big play/stop buttons
  dispatch: Function;
}) => {
  const [permission, setPermission] = useState(false);
  const mediaRecorder = useRef<MediaRecorder>(
    new MediaRecorder(new MediaStream()),
  );
  const [recordingStatus, setRecordingStatus] = useState("inactive");
  const [stream, setStream] = useState<MediaStream>(new MediaStream());
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
  const [audio, setAudio] = useState<string>("");
  const [, setAnalyserData] = useState<any>();
  const recordingStatusRef = useRef("inactive");

  const audioContextRef = useRef<any>(null);
  const analyserRef = useRef<any>(null);
  const dataArrayRef = useRef<any>(null);
  const startTimeRef = useRef<any>(null);

  const startRecording = async () => {
    setRecordingStatus("recording");
    recordingStatusRef.current = "recording";
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

    // Analyze frequency data continuously
    const getFrequencyData = () => {
      if (recordingStatusRef.current === "recording") {
        analyserRef.current.getByteTimeDomainData(dataArrayRef.current);
        const timestamp = Date.now() - startTimeRef.current;
        const waveForm = Array.from(dataArrayRef.current);
        sendWaveformData({ timestamp, waveForm });
        setAnalyserData([...dataArrayRef.current]);
        requestAnimationFrame(getFrequencyData);
      }
    };

    getFrequencyData();
  };

  const sendWaveformData = async (data: any) => {
    try {
      const options = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      };
      console.log(JSON.stringify(data));
      await fetch("http://127.0.0.1:5000/sendWaveform", options);
    } catch (error) {
      console.error("Error occurred: ", error);
    }
  };

  const stopRecording = () => {
    setRecordingStatus("inactive");
    recordingStatusRef.current = "inactive";
    //stops the recording instance
    mediaRecorder.current.stop();
    mediaRecorder.current.onstop = () => {
      //creates a blob file from the audiochunks data
      const audioBlob = new Blob(audioChunks, { type: mimeType });
      //creates a playable URL from the blob file.
      const audioUrl = URL.createObjectURL(audioBlob);
      setAudio(audioUrl);
      setAudioChunks([]);
      audioContextRef.current.close();
    };
  };
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

  return (
    <div
      style={{ display: "flex", flexDirection: "column", alignItems: "center" }}
    >
      <h1>Audio Recorder</h1>
      {!permission ? (
        <button onClick={getMicrophonePermission} type="button">
          Get Microphone
        </button>
      ) : null}
      {permission && recordingStatus === "inactive" ? (
        <button onClick={startRecording} type="button">
          Start Recording
        </button>
      ) : null}
      {recordingStatus === "recording" ? (
        <button onClick={stopRecording} type="button">
          Stop Recording
        </button>
      ) : null}
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
