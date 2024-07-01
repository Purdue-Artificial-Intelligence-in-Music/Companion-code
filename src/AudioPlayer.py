from threading import Thread
import librosa
import pyaudio
import time
import numpy as np


class AudioPlayer(Thread):
    def __init__(self, path, sample_rate=22050, channels=1, frames_per_buffer=1024, playback_rate=1.0):
        super(AudioPlayer, self).__init__()

        # AUDIO
        self.path = path
        self.sample_rate = sample_rate
        self.channels = channels

        # Check for mono audio
        mono = channels == 1

        # Load the audio
        self.audio, self.sample_rate = librosa.load(path, sr=sample_rate, mono=mono)

        # Reshape mono audio. Multi-channel audio should already be in the correct shape
        if mono:
            self.audio = self.audio.reshape((1, -1))

        self.audio_len = self.audio.shape[-1]

        # PYAUDIO
        self.p = pyaudio.PyAudio()

        # Open an output stream
        self.stream = None
        
        self.index = 0
        self.frames_per_buffer = frames_per_buffer
        self.playback_rate = playback_rate
        self.paused = False
        self.daemon=True

    def fade_in(self, audio, num_frames):
        """Fades in an audio segment.

        Parameters
        ----------
        audio : np.ndarray
            Audio to fade in.
        num_frames : int
            Number of frames to fade in.

        Returns
        -------
        None
        """
        num_frames = min(audio.shape[1], num_frames)
        fade_curve = np.log(np.linspace(1, np.e, num_frames))

        for channel in audio[:, :num_frames]:
            channel *= fade_curve

    def fade_out(self, audio, num_frames):
        """Fades out an audio segment.

        Parameters
        ----------
        audio : np.ndarray
            Audio to fade in.
        num_frames : int
            Number of frames to fade in.

        Returns
        -------
        None
        """
        num_frames = min(audio.shape[1], num_frames)
        start = audio.shape[1] - num_frames
        fade_curve = np.log(np.linspace(np.e, 1, num_frames))

        for channel in audio[:, start:]:
            channel *= fade_curve

    def callback(self, in_data, frame_count, time_info, status):
        # If len(data) is less than requested frame_count, PyAudio automatically
        # assumes the stream is finished, and the stream stops.
        
        if self.paused:
            return np.zeros((self.channels, frame_count)), pyaudio.paContinue
        
        start = max(0, self.index)
        end = min(self.index + 5 * self.playback_rate * frame_count, self.audio_len)

        # Increment the wav_index based on the playback rate
        self.index += self.playback_rate * frame_count

        # Time stretch the audio based on the playback rate
        stretched_audio = librosa.effects.time_stretch(y=self.audio[:, int(start):int(end)], rate=self.playback_rate)  # get audio
        
        # Reshaped the stretched audio (necessary if there is only one channel)
        stretched_audio = stretched_audio.reshape((self.channels, -1))

        # Get exactly enough frames to fill the PyAudio buffer
        audio_segment = stretched_audio[:, :frame_count]

        # Fade in and out of each wav_slice to eliminate popping noise
        fade_size = 128
        self.fade_in(audio_segment, num_frames=fade_size)
        self.fade_out(audio_segment, num_frames=fade_size)
        
        # no more audio to read
        if audio_segment.shape[-1] < frame_count:
            return audio_segment, pyaudio.paComplete
        
        return audio_segment, pyaudio.paContinue
    
    def run(self):

        # Open an output stream
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                  channels=self.channels,
                                  rate=self.sample_rate,
                                  input=False,
                                  output=True,
                                  stream_callback=self.callback,
                                  frames_per_buffer=self.frames_per_buffer)
        
    def is_active(self):
        if self.stream is None:
            return False
        return self.stream.is_active()
    
    def pause(self):
        """Pause but do not kill the thread."""
        self.paused = True

    def unpause(self):
        """Unpause the thread."""
        self.paused = False

    def stop(self):
        self.stream.close()
        self.p.terminate()

if __name__ == '__main__':
    player = AudioPlayer(path='audio_files/buns_viola.wav')
    player.start()
    
    while not player.is_active():
        time.sleep(0.01)

    try:
        while player.is_active():
            time.sleep(0.1)
    except KeyboardInterrupt:
        player.stop()
        player.join()