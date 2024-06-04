from BeatNet_local.BeatNet_files import *

estimator = BeatNet_for_files(1, mode='online', inference_model='PF', plot=[], thread=False)

Output = estimator.process("new_src\hunt.wav")

print(Output)