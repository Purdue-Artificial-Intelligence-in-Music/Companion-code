import numpy as np

class Compressor:
    def compress_clip(self, data, num_samples, threshold, ratio, attack, release):
        """
        Compress clip.
        Parameters:
            self: self parameter for when this function is called from inside AudioThreadWithBuffer
            data: file data (numpy array)
            num_samples: parameter for number of samples to take from the buffer
            threshold: parameter beyond which to compress.
            attack: parameter how quickly the compression starts, right away to delayed
            release: parameter how quickly the compression fades, right away to delayed
            ratio: how much compression
        Returns: Audio for AudioThreadWithBuffer with compressed content.
        """

        data = data.astype(np.int32, casting='safe')
        if not data:
            return []
        # Take the last num_samples of data.
        sample_data = data[-num_samples:]
        amplitude = np.sqrt(np.mean(sample_data ** 2))
        diff = amplitude - threshold
        scaling_factor = (threshold + diff/ratio) / amplitude
        return [d * scaling_factor for d in data]