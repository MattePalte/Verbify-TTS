"""Request to trigger the start of a the speech synthesis.

AUTHOR: Matteo Paltenghi
"""

import os
import requests
from tkinter import Tk
import pyautogui as pya
import time
import platform

from verbify_tts.utils import read_yaml_file
from verbify_tts.utils import get_root_directory

config = read_yaml_file(os.path.join(
    get_root_directory(), "configuration/config.yaml"))

if platform.system() == "Windows":
    LOCAL_IP = "127.0.0.1"
else:
    LOCAL_IP = "0.0.0.0"


def get_text_from_selection():
    """Get the text from the selection with CTRL+C and the clipboard."""
    with pya.hold('ctrl'):
        pya.press(['c'])
    root = Tk()
    text_from_clipboard = root.clipboard_get()
    time.sleep(100/1000)  # milliseconds
    root.withdraw()
    return text_from_clipboard


def simple_reprocessing(text):
    """Patch together the words which are split between two lines."""
    text = text.replace("-\n", "")
    return text


def command_speak_selection():
    # Prepare the request to send to the Verbify-TTS local server.
    text_to_pronounce = get_text_from_selection()
    payload = {
        'text': simple_reprocessing(text_to_pronounce),
        'speed': config["reading_speed"]}
    r = requests.post(f'http://{LOCAL_IP}:{config["server_port"]}/api', json=payload)
    print(r.text)


if __name__ == "__main__":
    command_speak_selection()
