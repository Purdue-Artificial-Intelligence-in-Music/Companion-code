from subprocess import run

with open('requirements.txt') as f:
    packages = f.readlines()
    packages = [name.strip() for name in packages]

for package in packages:
    run(['pip', 'install', package])