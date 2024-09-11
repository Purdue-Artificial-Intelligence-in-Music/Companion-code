from subprocess import run
import os
import requests


run(['pip', 'install', '-r', 'requirements.txt'])

url = 'https://keymusician01.s3.amazonaws.com/FluidR3_GM.zip'
response = requests.get(url)

if response.status_code == 200:
    if not os.path.exists('soundfonts'):
        os.mkdir('soundfonts')
    path = os.path.join('soundfonts', 'soundfontsFluidR3_GM.zip')
    with open(path, 'wb') as file:
        file.write(response.content)
    print("Download completed.")
else:
    print(f"Failed to download file. Status code: {response.status_code}")
