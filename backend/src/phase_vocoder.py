import numpy as np
import librosa
from librosa import core
from librosa.core import convert

def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """Normalize audio data to the range [-1, 1]."""
    return audio / np.max(np.abs(audio))


class PhaseVocoder:
    def __init__(self, path: str,
                 playback_rate: float = 1.0,
                 sample_rate: int = 44100,
                 channels: int = 1,
                 n_fft: int = 8192,
                 win_length: int = 8192,
                 hop_length: int = 2048):
        """
        A streaming phase vocoder that can produce variable-speed audio in real time.

        Parameters
        ----------
        path : str
            Path to the audio file.
        playback_rate : float
            Speed factor (1.0 is original speed, 2.0 is double speed, etc.).
        sample_rate : int
            Sample rate of output audio.
        channels : int
            Number of channels (1 = mono).
        n_fft : int
            FFT size.
        win_length : int
            Window size.
        hop_length : int
            Hop length.
        """
        self.path = path
        self.playback_rate = playback_rate
        self.sample_rate = sample_rate
        self.channels = channels
        self.n_fft = n_fft
        self.win_length = win_length
        self.hop_length = hop_length

        # Load and normalize
        mono = (channels == 1)
        audio, self.sample_rate = librosa.load(path, sr=sample_rate, mono=mono)
        audio = normalize_audio(audio)

        # If mono, shape: (1, samples). If multi-channel, shape: (channels, samples).
        if mono:
            audio = audio.reshape((1, -1))

        # Compute the STFT for each channel individually
        # stft: shape = (channels, freq_bins, time_frames)
        stft_list = []
        for ch in range(self.channels):
            stft_ch = core.stft(audio[ch],
                                n_fft=self.n_fft,
                                hop_length=self.hop_length,
                                win_length=self.win_length,
                                window='hann')
            stft_list.append(stft_ch[np.newaxis, ...])  # shape -> (1, freq_bins, time_frames)
        self.stft = np.concatenate(stft_list, axis=0)  # shape -> (channels, freq_bins, time_frames)

        # Total frames in STFT
        self.num_stft_frames = self.stft.shape[-1]

        # Keep track of current position in STFT (float for fractional indexing)
        self._stft_index = 0.0

        # Expected phase advance in each bin per hop
        self._phi_advance = hop_length * convert.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)

        # Phase accumulator, per channel and frequency bin
        # Initialize to the phase of the first STFT frame
        self._phase_acc = np.angle(self.stft[..., 0])  # shape: (channels, freq_bins)

        # A buffer of time-domain samples that we've synthesized but not yet “consumed”
        # shape: (channels, <some dynamic length>)
        self._output_buffer = np.zeros((self.channels, 0), dtype=np.float32)

        # Keep track of how many time-domain samples we’ve “consumed” in total
        # (for get_time() or any other scheduling)
        self._audio_index = 0

        # This controls how many frames we process in one iSTFT call.
        # Feel free to adjust. A bigger block = more efficient, but more latency.
        self._synthesis_block_size = 6

    def set_playback_rate(self, new_rate: float):
        """Adjust the playback rate on the fly."""
        self.playback_rate = new_rate

    def get_time(self) -> float:
        """Return the timestamp (in seconds) of how much audio we've output so far."""
        return self._audio_index / self.sample_rate

    def _fill_output_buffer(self, num_cols: int = None):
        """
        Synthesize more time-domain audio by processing a chunk of STFT frames
        and appending them to `_output_buffer`.
        
        Parameters
        ----------
        num_cols : int
            Number of “time frames” (hops) in the STFT domain to process.
            Default is `self._synthesis_block_size`.
        """
        if num_cols is None:
            num_cols = self._synthesis_block_size

        # We'll collect the “new” STFT columns in a list
        stft_block = []

        for _ in range(num_cols):
            # If we’re near or past the end, bail out (or pad with zeros if desired).
            if self._stft_index >= self.num_stft_frames - 1:
                break  # We won't generate more STFT data.

            # Integer part
            i0 = int(np.floor(self._stft_index))
            i1 = min(i0 + 1, self.num_stft_frames - 1)  # handle boundary

            # Fractional offset
            alpha = self._stft_index - i0

            # Magnitude interpolation for each channel, freq bin
            mag0 = np.abs(self.stft[..., i0])   # shape: (channels, freq_bins)
            mag1 = np.abs(self.stft[..., i1])
            mag = (1.0 - alpha) * mag0 + alpha * mag1

            # Phase difference
            phase0 = np.angle(self.stft[..., i0])  # (channels, freq_bins)
            phase1 = np.angle(self.stft[..., i1])
            dphase = phase1 - phase0 - self._phi_advance
            # Wrap to -π..π
            dphase = dphase - 2.0 * np.pi * np.round(dphase / (2.0 * np.pi))

            # Accumulate
            self._phase_acc += self._phi_advance + dphase

            # Construct complex STFT column for each channel
            stft_block.append(mag * np.exp(1j * self._phase_acc))

            # Advance fractional index
            self._stft_index += self.playback_rate

        # If no new columns, then we have nothing left to fill (end of audio).
        if not stft_block:
            return

        # Combine the columns along last axis => shape: (channels, freq_bins, number_of_new_cols)
        stft_block = np.stack(stft_block, axis=-1)

        # Now we do an ISTFT on this block. We want them to be contiguous in time
        # so that librosa’s istft does the correct overlap-add.
        #
        # One “trick”: we can't just pass these new columns alone to `istft`,
        # because it won't know the prior overlap. We have two ways to handle that:
        #
        #   A) Keep an ever-growing STFT buffer of all columns so far, then do
        #      `istft` from time=0 to time=end. (Memory-hungry for long audio.)
        #
        #   B) Keep a “sliding window” of STFT frames that always includes the last
        #      frames so that the overlap-add is correct.
        #
        # Below is a simplified approach: we keep track of the "previous columns"
        # in a buffer so that `istft` can do the correct overlap. Then we append
        # the new block and do a partial ISTFT.  

        # 1) If `_prev_stft_buffer` doesn’t exist, create it.
        if not hasattr(self, '_prev_stft_buffer'):
            self._prev_stft_buffer = np.zeros((self.channels,
                                               self.stft.shape[1], 0),
                                              dtype=np.complex64)

        # 2) Concatenate the old leftover + new block
        combined = np.concatenate([self._prev_stft_buffer, stft_block], axis=-1)

        # 3) ISTFT. We can get the time-domain block for the entire “combined” chunk.
        #    Because these frames are consecutive, librosa will do a proper overlap-add.
        #
        #    shape of combined: (channels, freq_bins, total_cols)

        # For multi-channel, we do iSTFT channel by channel:
        time_blocks = []
        for ch in range(self.channels):
            tb = librosa.istft(combined[ch],
                               hop_length=self.hop_length,
                               win_length=self.win_length,
                               window='hann')
            time_blocks.append(tb[np.newaxis, :])  # shape: (1, samples)

        # shape => (channels, samples)
        time_blocks = np.concatenate(time_blocks, axis=0).astype(np.float32)

        # 4) We need to figure out how many STFT frames from `combined` were “new”.
        #    That many frames is “valid” at the end of the iSTFT, but
        #    the earliest frames might have partial overlap with the old buffer.
        #    A simpler approach is: 
        #    - Keep the last (win_length // hop_length) frames in `_prev_stft_buffer`
        #      so the next call can do a correct overlap-add.  
        #    - Then the portion of the time-domain signal that extends beyond that
        #      is the new “valid” samples we can append to `_output_buffer`.

        # Number of frames in combined
        total_cols = combined.shape[-1]
        # We'll keep the last some frames in `_prev_stft_buffer`.
        # Typically, we want enough overlap to cover the window length fully.
        # Let's pick `win_length // hop_length * 2` or something. 
        # But a simpler approach is just keep all columns from the new block
        # so that next iteration we do not break continuity.
        leftover_cols = stft_block.shape[-1]
        # Keep leftover_cols from the end
        keep_start = max(0, total_cols - leftover_cols)
        self._prev_stft_buffer = combined[..., keep_start:]

        # Now we have the time-domain block from the entire `combined`.
        # We want to figure out how many new samples were generated by the last `leftover_cols`.
        # This is tricky to do exactly. A simpler approach is just take the *last*
        # len of the iSTFT that roughly corresponds to the new frames.
        #
        # One way:
        #   total_samples = time_blocks.shape[1]
        #   samples_per_col ~ hop_length  (assuming no time-stretch?)
        # or we can do a “slice from the end” approach:

        # For a rough estimate:
        new_samples = leftover_cols * self.hop_length
        if new_samples > time_blocks.shape[1]:
            # If our estimate is too big, clamp
            new_samples = time_blocks.shape[1]

        # The last `new_samples` from `time_blocks` is newly generated
        new_segment = time_blocks[:, -new_samples:]

        # Append to the output buffer
        self._output_buffer = np.concatenate([self._output_buffer, new_segment], axis=1)

    def get_next_frames(self, num_frames: int) -> np.ndarray:
        """
        Return exactly `num_frames` of audio from the internal ring buffer.
        If we don’t have enough, we generate more via `_fill_output_buffer()`.
        
        Parameters
        ----------
        num_frames : int
            Number of frames (samples) to retrieve in the time domain.

        Returns
        -------
        frames : np.ndarray or None
            Shape (channels, num_frames). None if there is no more audio to synthesize.
        """
        # Keep filling until we have enough in the buffer or we can’t fill more
        while self._output_buffer.shape[1] < num_frames:
            old_len = self._output_buffer.shape[1]
            self._fill_output_buffer()  # fill with the default block size
            new_len = self._output_buffer.shape[1]
            if new_len == old_len:
                # no new samples were produced => end of file
                break

        # Now see if we can supply the requested frames
        available = self._output_buffer.shape[1]
        if available == 0:
            # End of audio
            return None

        # We can at least supply partial
        n_take = min(num_frames, available)
        output = self._output_buffer[:, :n_take]

        # Remove from the ring buffer
        self._output_buffer = self._output_buffer[:, n_take:]

        # Update the global “audio index”
        self._audio_index += n_take * self.playback_rate

        return output


# if __name__ == '__main__':
#     import os
#     # Replace this with your own code or integrator
#     # Example usage:

#     reference = os.path.join('data', 'audio', 'air_on_the_g_string',
#                              'synthesized', 'solo.wav')

#     phase_vocoder = PhaseVocoder(path=reference,
#                                  sample_rate=44100,
#                                  channels=1,
#                                  playback_rate=1,
#                                  n_fft=8192,
#                                  win_length=8192,
#                                  hop_length=2048)

#     # Here’s a mock example: we want 1024 frames repeatedly, akin to a PyAudio callback
#     frames_per_buffer = 1024
#     all_output = []

#     while True:
#         frames = phase_vocoder.get_next_frames(frames_per_buffer)
#         if frames is None:
#             # Done
#             break
#         # frames.shape -> (1, 1024) in this example
#         all_output.append(frames)

#     # Combine into a single array
#     output_array = np.concatenate(all_output, axis=1)

#     # Save for testing
#     import soundfile as sf
#     sf.write('phase_vocoder_output.wav',
#              output_array.T,  # Librosa writes (samples, channels), so transpose
#              samplerate=44100)

if __name__ == '__main__':
    import os
    from audio_buffer import AudioBuffer

    reference = os.path.join('data', 'audio', 'air_on_the_g_string',
                             'synthesized', 'solo.wav')

    phase_vocoder = PhaseVocoder(path=reference,
                                 sample_rate=44100,
                                 channels=1,
                                 playback_rate=2,
                                 n_fft=8192,
                                 win_length=8192,
                                 hop_length=2048)

    buffer = AudioBuffer(sample_rate=44100, channels=1)
    frames_per_buffer = 1024

    while True:
        phase_vocoder.set_playback_rate(2)
        frames = phase_vocoder.get_next_frames(frames_per_buffer)
        if frames is None:
            break
        print(phase_vocoder.get_time())
        buffer.write(frames)

    buffer.save('phase_vocoder_output.wav')
