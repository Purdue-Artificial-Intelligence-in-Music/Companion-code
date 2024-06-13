# Companion
Companion is an app that not only plays along with a human player during a chamber music piece, but actively responds to their playing habits and voice commands like a real human would. 

## System requirements
- Windows 10/11 or Linux (macOS may work but is untested and unsupported)
- An Nvidia GPU (RTX 3050 mobile or better preferred)
- 16GB of system RAM (probably)
- 10GB of space for installation of libraries
- A microphone
- Headphones (to avoid feedback with the microphone)
- Apple M-series chips as well as Intel/AMD GPUs may work if you manually tell PyTorch to use MPS shaders, Intel Performance Extensions or AMD ROCm, respectively. This configuration is not supported, however.

## Getting Started
1. Clone the repository.
2. Make sure conda is installed. 
3. Run the following commands in-order to create a conda environment for the project (the ipywidgets line is NOT a typo):
```
conda create -n companion_env
conda activate companion_env
conda install python==3.8
pip install librosa
pip install Cython
pip install madmom
conda install nvidia/label/cuda-11.8.0::cuda-toolkit
conda install ipython ipykernel
pip install midi-ddsp
pip install ipywidgets===7.0.1
pip install ipython_genutils
pip install numpy==1.23.0
pip install -q git+https://github.com/lukewys/qgrid.git
pip install pyaudio simple-pid speechrecognition nltk pyttsx3
pip install transformers
```
4. Run ``src/main.py`` (using your conda environment) to start Companion.
