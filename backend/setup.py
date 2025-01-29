from subprocess import run
import os
import requests
import zipfile


run(['pip', 'install', '-r', 'requirements.txt'])

url = 'https://keymusician01.s3.amazonaws.com/FluidR3_GM.zip'
response = requests.get(url)


if response.status_code == 200:
    if not os.path.exists('soundfonts'):
        os.mkdir('soundfonts')
    zip_path = os.path.join('soundfonts', 'FluidR3_GM.zip')

    with open(zip_path, 'wb') as file:
        file.write(response.content)
    print("Download completed.")

    print("Extracting files...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall('soundfonts')
    print("Extraction completed.")
    os.remove(zip_path)
else:
    print(f"Failed to download file. Status code: {response.status_code}")


fluidsynth_url = 'https://github.com/FluidSynth/fluidsynth/releases/download/v2.4.2/fluidsynth-2.4.2-win10-x64.zip'
fluidsynth_response = requests.get(fluidsynth_url)

if fluidsynth_response.status_code == 200:
    if not os.path.exists('fluidsynth'):
        os.mkdir('fluidsynth')
    zip_path = os.path.join('fluidsynth', 'fluidsynth.zip')

    with open(zip_path, 'wb') as file:
        file.write(fluidsynth_response.content)
    print("Download completed.")

    # print("Extracting files...")
    # with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    #     zip_ref.extractall('fluidsynth')
    # print("Extraction completed.")
    # os.remove(zip_path)
else:
    print(f"Failed to download file. Status code: {response.status_code}")