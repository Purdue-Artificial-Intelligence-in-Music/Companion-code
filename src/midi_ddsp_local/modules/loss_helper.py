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

"""Loss helper for handling and logging the losses."""

import tensorflow as tf


class LossHelper:
  """Loss helper for handling and logging the losses."""
  def __init__(self):
    self.metrics = None

  def init_metrics(self):
    self.metrics = {f'mean_{l}': tf.keras.metrics.Mean(name=f'mean_{l}') for l
                    in self.loss_list}

  def reset_metrics(self):
    for m in self.metrics.values():
      m.reset_states()

  def update_metrics(self, loss_dict):
    for loss_name, value in loss_dict.items():
      self.metrics[f'mean_{loss_name}'](value)

  def compute_loss(self, inputs, outputs, **kwargs):
    return self.loss_group(inputs, outputs, **kwargs)

  def get_loss_log(self):
    log = ''
    for loss_name in self.loss_list:
      loss_result = self.metrics[f'mean_{loss_name}'].result()
      log = log + f'| {loss_name} {loss_result:5.4f} '
    return log

  def write_mean_summary(self, writer, group_name, step):
    with writer.as_default():
      for loss_name in self.loss_list:
        loss_result = self.metrics[f'mean_{loss_name}'].result().numpy()
        tf.summary.scalar(f'{group_name}/{loss_name}', loss_result, step)

  @staticmethod
  def write_summary(loss_dict, writer, group_name, step):
    with writer.as_default():
      for loss_name, value in loss_dict.items():
        tf.summary.scalar(f'{group_name}/{loss_name}', value.numpy(), step)
