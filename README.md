# Audio Time-Stretching with Beat Detection

This branch of the main project implements audio time-stretching using beat detection. It allows you to stretch the time of an audio file while preserving the tempo, based on beat detection analysis.

## Authors
Temirlan Karataev
Tanin Padungkirtsakul

## Modifications
All edits made by this branch are highlighted in red.
![image](https://github.com/Purdue-Artificial-Intelligence-in-Music/Companion-code/assets/77745845/4174026c-9e36-4670-8f97-90b442352924)


## Features

- Time-stretch audio files while maintaining the original tempo.
- Automatic beat detection to accurately determine the tempo of the audio.
- Multi-threaded implementation for efficient processing.

## Requirements

- Python 3.x
- numpy
- pytsmod
- soundfile
- scipy
- pydub

## Installation

1. Clone the repository:
2. Install the required dependencies:

## Usage

1. Place your audio file in the appropriate directory.

2. Modify the `filepath` and `output_file` variables in the `main.py` script to specify the input and output file paths.

3. Adjust the `pairs` variable in the `main.py` script to match the desired time and tempo values for time-stretching.


## Contributing
Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.
