
const BASE_URL = 'http://127.0.0.1:5000'; // Replace with your API base URL

// Helper function to handle fetch responses
const handleResponse = async (response: Response) => {
  if (response.ok) { //doing below checks because sometimes getting a string sometimes getting a json.
    const contentType = response.headers.get('Content-Type') || '';
    console.log(contentType)
    // If the response is JSON, parse it
    if (contentType.includes('application/json')) {
        return await response.json();
      }
  
      // If it's plain text, return it as a string
      if (contentType.includes('text/plain') || contentType.includes('text/html')) {
        return await response.text();
      }
  
      // Handle other types of content if needed
      throw new Error('Unsupported content type');
  }
  console.log("not ok :(");
  const errorText = await response.text();
  throw new Error(`Error ${response.status}: ${errorText}`);
};

// Start a new session
export const startSession = async (): Promise<{ session_token: string }> => {
  const response = await fetch(`${BASE_URL}/start-session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  return handleResponse(response);
};

// Stop a session
export const stopSession = async (sessionToken: string): Promise<void> => {
  const response = await fetch(`${BASE_URL}/stop-session`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'session-token': sessionToken,
    },
  });
  await handleResponse(response);
};

// Get available MusicXML files
export const getScores = async (): Promise<{ files: string[] }> => {
  const response = await fetch(`${BASE_URL}/scores`, {
    method: 'GET',
  });
  return handleResponse(response);
};

// Utility function to read a Blob as text
const blobToText = (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = () => reject(new Error("Error reading Blob as text"));
      reader.readAsText(blob);
    });
  };

// Get specific MusicXML file
export const getScore = async (filename: string): Promise<String> => {
  const response = await fetch(`${BASE_URL}/score/${filename}`, {
    method: 'GET',
  });
  let store = await response.blob();
  return blobToText(store); // Assuming the file content is returned as a file from send_file()
};

// Synthesize audio for a MusicXML file
export const synthesizeAudio = async (
  sessionToken: string,
  filename: string,
  tempo: number
): Promise<{ audio_data: number[]; sample_rate: number }> => {
  const response = await fetch(`${BASE_URL}/synthesize-audio/${filename}/${tempo}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'session-token': sessionToken,
    },
  });
  return handleResponse(response);
};

// Synchronization API
export const synchronize = async (
  sessionToken: string,
  frames: number[],
  timestamp: number
): Promise<{ playback_rate: number; estimated_position: number }> => {
  const response = await fetch(`${BASE_URL}/synchronization`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'session-token': sessionToken,
    },
    body: JSON.stringify({ frames, timestamp }),
  });
  return handleResponse(response);
};
