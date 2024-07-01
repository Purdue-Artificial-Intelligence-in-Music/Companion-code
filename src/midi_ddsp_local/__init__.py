#  Copyright 2022 The MIDI-DDSP Authors.
#  #
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  #
#      http://www.apache.org/licenses/LICENSE-2.0
#  #
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Base module for the MIDI-DDSP library."""

from midi_ddsp_local import data_handling
from midi_ddsp_local import utils
from midi_ddsp_local import modules
from midi_ddsp_local import hparams_synthesis_generator
from midi_ddsp_local.midi_ddsp_synthesize import synthesize_midi, \
  load_pretrained_model
