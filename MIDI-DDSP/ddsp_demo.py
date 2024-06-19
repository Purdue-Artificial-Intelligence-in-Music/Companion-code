# !!! Run download model weights in the package directory if they don't already exist
import pretty_midi
from subprocess import run

# # Define the path or paths of the model weights or relevant files you expect after downloading
# expected_file_path = './midi_ddsp_model_weights_urmp_9_10'  # Adjust this to your file's expected location

# # Save the current working directory
# original_dir = os.getcwd()

# # Get the path to the midi_ddsp package
# package_path = os.path.dirname(midi_ddsp.__file__)
# print(f"Package directory: {package_path}")

# Change to the package directory
# os.chdir(package_path)

# Check if the model weights or relevant files already exist
# if not os.path.exists(expected_file_path):
#     print("Downloading model weights...")
#     # Execute the script to download model weights
#     run(['python', 'download_model_weights.py'])
# else:
#     print("Model weights already exist. No need to download.")

# Return to the original directory
# os.chdir(original_dir)
# print(f"Returned to original directory: {os.getcwd()}")

#@title #Install Dependencies, Import Code and Setup Models

#@markdown Run this cell to install dependencies, import codes, 
#@markdown setup utility functions and load MIDI-DDSP model weights.
#@markdown Running this cell could take a while.
# %pip install -q git+https://github.com/lukewys/qgrid.git

# # !pip install -q git+https://github.com/magenta/midi-ddsp
import os

# !!! Run these once
# if not os.path.exists('./midi-ddsp') or not os.path.exists('./FluidR3_GM.zip'):
#     # Your commands
#     run(['git', 'clone', '-q', 'https://github.com/magenta/midi-ddsp.git'])
#     run(['wget', '-q', 'https://keymusician01.s3.amazonaws.com/FluidR3_GM.zip'])
#     run(['unzip', '-q', 'FluidR3_GM.zip'])
# else:
#     print('The required resources are already present.')

# Ignore a bunch of deprecation warnings
# import sys
# sys.path.append('./midi-ddsp')
import warnings
warnings.filterwarnings("ignore")

# import os
import matplotlib.pyplot as plt
from midi_ddsp import load_pretrained_model
from midi_ddsp.utils.training_utils import set_seed
from ddsp_funcs import *

set_seed(1234)
sample_rate = 16000

synthesis_generator, expression_generator = load_pretrained_model()

print('Done!')

midi_path = "exes.mid"
midi = pretty_midi.PrettyMIDI(midi_path)
inst = "violin"

print('Generating audio from MIDI')
midi_audio_changed, conditioning_df, midi_synth_params = generate_audio_from_midi(synthesis_generator, expression_generator, midi_path, inst, inst_num=0)
plt.figure(figsize=(15,5))
plot_spec(midi_audio_changed[0].numpy(), sr=16000, title='Add pitch bend')
plt.show()
