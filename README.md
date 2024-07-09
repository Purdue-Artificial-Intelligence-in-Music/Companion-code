# Companion
Companion is an app that not only plays along with a human player during a chamber music piece, but actively responds to their playing habits and voice commands like a real human would. 

## System requirements
- Windows 10/11 or Linux (macOS may work but is untested and unsupported)
- An Nvidia GPU with >=4GB VRAM (RTX 3050 mobile and above tested + working)
- 16GB of system RAM (probably)
- 10GB of space for installation of libraries
- A microphone
- Headphones (to avoid feedback with the microphone)
- Apple M-series chips as well as Intel/AMD GPUs may work if you manually tell PyTorch to use MPS shaders, Intel Performance Extensions or AMD ROCm, respectively. This configuration is not supported, however.

## Getting Started
1. Clone the repository.
2. In a python 3.8 environment, run the command ```python setup.py```
4. Run ``src/main.py`` to start Companion.
