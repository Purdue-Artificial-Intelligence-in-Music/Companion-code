# Author: Mojtaba Heydari <mheydari@ur.rochester.edu>


# This is the script handler of the BeatNet. First, it extracts the input embeddings of the current frame or the whole song, depending on the working mode. 
# Then by feeding them into the selected pre-trained model, it calculates the beat/downbeat activation probabilities.
# Finally, it infers beats and downbeats of the current frame/song based on one of the four performance modes and selected inference method.

import os
import torch
import numpy as np
from BeatNet_local.particle_filtering_cascade import particle_filter_cascade
from BeatNet_local.log_spect import LOG_SPECT
from BeatNet_local.model import BDA
import time
import threading
from AudioBuffer import *
from BeatTracker import *

class BeatNet_thread(BeatTracker):

    '''
    The main BeatNet handler class including different trained models, different modes for extracting the activation and causal and non-causal inferences

        Parameters
        ----------
        Inputs: 
            model: An scalar in the range [1,3] to select which pre-trained CRNN models to utilize. 
            mode: An string to determine the working mode. Fixed in 'stream' mode, which uses the system microphone to capture sound 
                  and does the process in real-time. Due to training the model on standard mastered songs, it is highly recommended to 
                  make sure the microphone sound is as loud as possible. Less reverbrations leads to the better results.  
            inference model: A string to choose the inference approach. Fixed to 'PF', standing for Particle Filtering for causal inferences.
            plot: A list of strings to plot. 
                'activations': Plots the neural network activations for beats and downbeats of each time frame. 
                'beat_particles': Plots beat/tempo tracking state space and current particle states at each time frame.
                'downbeat_particles': Plots the downbeat/meter tracking state space and current particle states at each time frame.
                Note that to speedup plotting the figures, rather than new plots per frame, the previous plots get updated. However, to secure realtime results, it is recommended to not plot or have as less number of plots as possible at the time.   
            threading: To decide whether accomplish the inference at the main thread or another thread. 
            device: type of dvice. cpu or cuda:i

        Outputs:
            A vector including beat times and downbeat identifier columns, respectively with the following shape: numpy_array(num_beats, 2).
    '''
    
    
    def __init__(self, model, BUFFER: AudioBuffer, plot=[], device='cpu'):
        super().__init__()
        self.model = model
        self.mode = 'stream'
        self.inference_model = 'PF'
        self.BUFFER = BUFFER
        self.plot = plot
        self.device = device
        self.thread = False
        self.daemon = True
        if plot and self.thread:
            raise RuntimeError('Plotting cannot be accomplished in the threading mode')
        self.sample_rate = self.BUFFER.RATE
        self.log_spec_sample_rate = 22050
        self.log_spec_hop_length = int(20 * 0.001 * self.log_spec_sample_rate)
        self.log_spec_win_length = int(64 * 0.001 * self.log_spec_sample_rate)
        self.proc = LOG_SPECT(sample_rate=self.log_spec_sample_rate, win_length=self.log_spec_win_length,
                             hop_size=self.log_spec_hop_length, n_bands=[24], mode = self.mode)
        
        self.estimator = particle_filter_cascade(beats_per_bar=[], fps=50, plot=self.plot, mode=self.mode) # instantiating a Particle Filter decoder - Is Chosen for online inference
        self.pred = np.zeros([1,2])
        self.frames_processed = 0  # number of frames processed by BeatNet

        script_dir = os.path.dirname(__file__)
        #assiging a BeatNet CRNN instance to extract joint beat and downbeat activations
        self.model = BDA(272, 150, 2, self.device)   #Beat Downbeat Activation detector
        #loading the pre-trained BeatNet CRNN weigths
        if model == 1:  # GTZAN out trained model
            self.model.load_state_dict(torch.load(os.path.join(script_dir, 'models/model_1_weights.pt')), strict=False)
        elif model == 2:  # Ballroom out trained model
            self.model.load_state_dict(torch.load(os.path.join(script_dir, 'models/model_2_weights.pt')), strict=False)
        elif model == 3:  # Rock_corpus out trained model
            self.model.load_state_dict(torch.load(os.path.join(script_dir, 'models/model_3_weights.pt')), strict=False)
        else:
            raise RuntimeError(f'Failed to open the trained model: {model}')
        self.model.eval()

        self.stream_window = np.zeros(self.log_spec_win_length + 2 * self.log_spec_hop_length, dtype=np.float32)                                          

        self.stop_request = False

        self.loops_sleeping = 0
        self.loops_running = 0

    def get_downbeats(self) -> int:
        return self.estimator.downbeats
    
    def get_total_beats(self) -> int:
        return self.estimator.beats
    
    def get_current_beats(self):
        return self.estimator.path[1:]

    def run(self):  
        if self.inference_model != "PF":
                raise RuntimeError('The inference model should be set to "PF" for the streaming mode!')
        self.counter = 0

        while self.BUFFER.stream is None or self.BUFFER.buffer_index < self.log_spec_hop_length + 1:
            time.sleep(0.2)

        while self.BUFFER.stream.is_active() and not self.stop_request:
            self.activation_extractor_stream()  # Using BeatNet causal Neural network streaming mode to extract activations
            if self.thread:
                x = threading.Thread(target=self.estimator.process, args=(self.pred), daemon=True)   # Processing the inference in another thread 
                x.start()
                x.join()
            else:
                self.estimator.process(self.pred)
            self.counter += 1
            
    def activation_extractor_stream(self):
        # TODO: 
        ''' Streaming window
        Given the training input window's origin set to center, this streaming data formation causes 0.084 (s) delay compared to the trained model that needs to be fixed. 
        '''
        with torch.no_grad():
            # if there are not enough new frames for BeatNet to process, wait
            if self.frames_processed + self.log_spec_hop_length > self.BUFFER.mic_frame_count:
                self.loops_sleeping += 1
                time.sleep(self.BUFFER.FRAMES_PER_BUFFER / self.BUFFER.RATE * 5)
                return
            
            self.loops_running += 1

            # get the start and end indices for the next chunk of audio data
            start = self.frames_processed % self.BUFFER.buffer_length
            end = (start + self.log_spec_hop_length) % self.BUFFER.buffer_length

            # get the next chunk from audio buffer
            audio = self.BUFFER.get_frames(start, end)

            if self.BUFFER.CHANNELS > 1: 
                audio = np.mean(audio, axis=0)
            
            # increment the number of frames processed
            self.frames_processed += self.log_spec_hop_length

            # cast the audio to 32-bit floats
            audio = audio.astype(dtype=np.float32, casting='safe')

            # remove the oldest audio to make room for the new audio
            self.stream_window = np.append(self.stream_window[self.log_spec_hop_length:], audio)
        
            # If BeatNet has been running for less than 5 cycles, return zeros
            if self.counter < 5:
                self.pred = np.zeros([1,2])
            # Else make a prediction
            else:
                feats = self.proc.process_audio(self.stream_window).T[-1]
                feats = torch.from_numpy(feats)
                feats = feats.unsqueeze(0).unsqueeze(0).to(self.device)
                pred = self.model(feats)[0]
                pred = self.model.final_pred(pred)
                pred = pred.cpu().detach().numpy()
                self.pred = np.transpose(pred[:2, :])
