This file describes how to install Verbify-TTS as a pipx application.
The goal is to make the whole procedure simpler and easier to support for different platforms.

Source: https://ostechnix.com/pipx-install-and-run-python-applications-in-isolated-environments/

1. Install PIPX
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```
2. Check that pipx is installed correctly
```bash
pipx --version
```
3. Check that Verbify-TTS is not installed
```bash
pipx list
```
4. Install Verbify-TTS from the new branch:
```bash
pipx install git+https://github.com/MattePalte/Verbify-TTS.git@dev-pytorch-fastapi
```


## Steps for Contributors
To set up the files required to use Verbify-TTS with PIPX, you need to:
1. Install PIPX
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```
2. Install Poetry
```bash
pipx install poetry
```
3. Clone the repository
```bash
git clone https://github.com/MattePalte/Verbify-TTS.git
```
4. Go to the root directory and initialize the Poetry environment
```bash
cd Verbify-TTS
poetry install
```