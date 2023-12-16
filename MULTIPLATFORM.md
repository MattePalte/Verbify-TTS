## Multi-platform Installer

The goal of this guide is to provide a simple way to install Verbify-TTS on different platforms.

### Requirements

1. Python 3.8 or higher
2. PIPX which is a Python package to install and run Python applications in isolated environments. You can get it via:
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

### Installation
To install Verbify-TTS, run the following command:
```bash
pipx install git+https://github.com/MattePalte/Verbify-TTS.git@dev-pytorch-fastapi
```

This will give you access to several entry points:
1. `verbify_server` which is a FastAPI server that exposes the TTS functionality via a REST API.
2. `verbify_read_selected` which is a CLI tool to read the selected text.
3. `verbify_stop_tts` which is a CLI tool to stop reading the text from the TTS process.



### Troubleshooting
If you have problems you can clone the project in the current directory, then use the following command
```bash
# clone
git clone https://github.com/MattePalte/Verbify-TTS.git@dev-pytorch-fastapi
# downgrade the packaging package to 21.3
pip install packaging==21.3
# upgrade pip
pip install --upgrade pip
# install
pipx install .
```


