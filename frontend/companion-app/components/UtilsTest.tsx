import React, { useState } from "react";
import {
  startSession,
  stopSession,
  getScores,
  getScore,
  synthesizeAudio,
  synchronize,
} from "./Utils"; // Importing functions from Utils.tsx

const UtilsTest = () => {
  // State for storing inputs and API responses
  const [sessionToken, setSessionToken] = useState<string>("");
  const [scoreFilename, setScoreFilename] = useState<string>("");
  const [tempo, setTempo] = useState<number>(120);
  const [frames, setFrames] = useState<number[]>([]);
  const [timestamp, setTimestamp] = useState<number>(0);
  const [response, setResponse] = useState<any>(null);
  const [scoreList, setScoreList] = useState<string[]>([]);

  // Handlers for API calls
  const handleStartSession = async () => {
    try {
      const data = await startSession();
      setSessionToken(data.session_token); // Store session token
      setResponse(data);
    } catch (error) {
      setResponse({ error: error });
    }
  };

  const handleStopSession = async () => {
    if (!sessionToken) {
      setResponse({ error: "Session token is required" });
      return;
    }

    try {
      console.log("Trying with: ", sessionToken);
      await stopSession(sessionToken);
      setResponse({ message: "Session stopped successfully" });
    } catch (error) {
      if (error instanceof Error) setResponse({ error: error.message });
      else setResponse({ error: "Error" });
    }
  };

  const handleGetScores = async () => {
    try {
      const data = await getScores();
      setScoreList(data.files);
      setResponse(data);
    } catch (error) {
      if (error instanceof Error) setResponse({ error: error.message });
      else setResponse({ error: "Error" });
    }
  };

  const handleGetScore = async () => {
    if (!scoreFilename) {
      setResponse({ error: "Please provide a score filename" });
      return;
    }

    try {
      const data = await getScore(scoreFilename);
      console.log("made it!", data);
      setResponse({ score: data });
    } catch (error) {
      if (error instanceof Error) setResponse({ error: error.message });
      else setResponse({ error: "Error" });
    }
  };

  const handleSynthesizeAudio = async () => {
    if (!sessionToken || !scoreFilename || !tempo) {
      setResponse({
        error: "Session token, score filename, and tempo are required",
      });
      return;
    }

    try {
      const data = await synthesizeAudio(sessionToken, scoreFilename, tempo);
      setResponse(data);
    } catch (error) {
      if (error instanceof Error) setResponse({ error: error.message });
      else setResponse({ error: "Error" });
    }
  };

  const handleSynchronization = async () => {
    if (!sessionToken || !frames || frames.length === 0 || !timestamp) {
      setResponse({
        error: "Session token, frames, and timestamp are required",
      });
      return;
    }

    try {
      const data = await synchronize(sessionToken, frames, timestamp);
      setResponse(data);
    } catch (error) {
      if (error instanceof Error) setResponse({ error: error.message });
      else setResponse({ error: "Error" });
    }
  };

  return (
    <div>
      <h1>API Test Component</h1>

      {/* Start Session Button */}
      <div>
        <button onClick={handleStartSession}>Start Session</button>
        {sessionToken && <p>Session Token: {sessionToken}</p>}
      </div>

      {/* Stop Session Button */}
      <div>
        <button onClick={handleStopSession}>Stop Session</button>
      </div>

      {/* Get Scores Button */}
      <div>
        <button onClick={handleGetScores}>Get Available Scores</button>
        {scoreList.length > 0 && (
          <ul>
            {scoreList.map((score, index) => (
              <li key={index}>{score}</li>
            ))}
          </ul>
        )}
      </div>

      {/* Get Specific Score Button */}
      <div>
        <label>Score Filename:</label>
        <input
          type="text"
          value={scoreFilename}
          onChange={(e) => setScoreFilename(e.target.value)}
        />
        <button onClick={handleGetScore}>Get Score</button>
        {response?.score && <pre>{response.score}</pre>}
      </div>

      {/* Synthesize Audio Button */}
      <div>
        <label>Tempo (BPM):</label>
        <input
          type="number"
          value={tempo}
          onChange={(e) => setTempo(Number(e.target.value))}
        />
        <button onClick={handleSynthesizeAudio}>Synthesize Audio</button>
        {response?.audio_data && (
          <pre>{JSON.stringify(response.audio_data)}</pre>
        )}
      </div>

      {/* Synchronization Button */}
      <div>
        <label>Frames (comma-separated):</label>
        <input
          type="text"
          value={frames.join(",")}
          onChange={(e) =>
            setFrames(
              e.target.value.split(",").map((num) => parseInt(num.trim(), 10)),
            )
          }
        />
        <label>Timestamp:</label>
        <input
          type="number"
          value={timestamp}
          onChange={(e) => setTimestamp(Number(e.target.value))}
        />
        <button onClick={handleSynchronization}>Synchronize Audio</button>
        {response?.playback_rate && (
          <p>
            Playback Rate: {response.playback_rate} | Estimated Position:{" "}
            {response.estimated_position}
          </p>
        )}
      </div>

      {/* Display API response */}
      <div>
        <h2>Response:</h2>
        <pre>{JSON.stringify(response, null, 2)}</pre>
      </div>
    </div>
  );
};

export default UtilsTest;
