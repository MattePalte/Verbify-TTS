"""Request to trigger the start of a the speech synthesis.

AUTHOR: Matteo Paltenghi
"""

import os
import requests
from tkinter import Tk
import pyautogui as pya
import time

from utils import read_yaml_file
from utils import get_root_directory

pya.hotkey("ctrl", "c")
root = Tk()
root.withdraw()
text_from_clipboard = root.clipboard_get()
text_to_pronounce = text_from_clipboard
time.sleep(100/1000)  # milliseconds

# MANUAL SERVER - FOR DEBUG
# sample_text = 'First words. Second words. many more words for you.'
# text_to_pronounce = sample_text

def simple_reprocessing(text):
    """Patch together the words which are split between two lines."""
    text = text.replace("-\n", "")
    return text

config = read_yaml_file(os.path.join(
    get_root_directory(), "configuration/config.yaml"))

# Prepare the request to send to the Verbify-TTS local server.
payload = {
    'text': simple_reprocessing(text_to_pronounce),
    'speed': config["reading_speed"]}


r = requests.post(f'http://0.0.0.0:{config["server_port"]}/api', json=payload)
print(r.text)
