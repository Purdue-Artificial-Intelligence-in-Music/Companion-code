from subprocess import run

with open('requirements.txt') as f:
    packages = f.readlines()
    packages = [name.strip() for name in packages]

for package in packages:
    run(['pip', 'install', package])

run(['pip', 'install', 'torch', 'torchvision', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cu121'])

run(['midi_ddsp_download_model_weights'])
