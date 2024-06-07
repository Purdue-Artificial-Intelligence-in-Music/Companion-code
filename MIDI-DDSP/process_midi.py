import midi_ddsp_local
import pretty_midi
import os
import librosa
import matplotlib.pyplot as plt
import numpy as np
import tensorflow.compat.v2 as tf
import pandas as pd
import qgrid
import music21
from IPython.display import Javascript
import IPython.display as ipd
from midi_ddsp_local import load_pretrained_model
from midi_ddsp_local.utils.training_utils import set_seed, get_hp
import soundfile as sf

from ddsp_funcs import *

import sys
sys.path.append('./midi-ddsp')
import warnings
warnings.filterwarnings("ignore")


def process_midi(in_str):
    set_seed(1234)
    sample_rate = 16000
    synthesis_generator, expression_generator = load_pretrained_model()
    audio, _, _ = generate_audio_from_midi(synth_gen=synthesis_generator, express_gen=expression_generator, midi_path=in_str+".midi", instrument="violin", inst_num=0)
    sf.write(in_str+'.wav', audio, sample_rate, subtype='PCM_24')



