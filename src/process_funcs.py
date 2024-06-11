def process_func(self, input_array, wav_data):
    if wav_data is not None:
        output = wav_data[self.wav_index, self.wav_index+self.FRAMES_PER_BUFFER]
        self.wav_index += self.FRAMES_PER_BUFFER
    else:
        output = input_array
    return output