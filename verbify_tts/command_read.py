"""Request to trigger the start of a the speech synthesis.

AUTHOR: Matteo Paltenghi
"""

import os
import re
import requests
from tkinter import Tk
import pyautogui as pya
import time

from verbify_tts.utils import read_yaml_file
from verbify_tts.utils import get_root_directory
from verbify_tts.utils import get_host_address


def get_text_from_clipboard():
    """Get text from clipboard by simulating Ctrl+C and retrieving clipboard content."""
    with pya.hold('ctrl'):
        pya.press(['c'])
    root = Tk()
    text_from_clipboard = root.clipboard_get()
    time.sleep(100/1000)  # milliseconds
    root.withdraw()
    return text_from_clipboard


# MANUAL SERVER - FOR DEBUG
# sample_text = 'First words. Second words. many more words for you.'
# text_to_pronounce = sample_text

def simple_reprocessing(text):
    """Patch together the words which are split between two lines."""
    text = text.replace("-\n", "")
    # remove numbers and commas between square brackets
    text = re.sub(r'\[[0-9, ]+\]', '', text)
    return text


def main():
    """Main function to get text from clipboard and send it to the TTS server."""
    # Get text to pronounce from clipboard
    text_to_pronounce = get_text_from_clipboard()
    config = read_yaml_file(os.path.join(
        get_root_directory(), "configuration/config.yaml"))

    # Prepare the request to send to the Verbify-TTS local server.
    payload = {
        'text': simple_reprocessing(text_to_pronounce),
        'speed': config["reading_speed"]}
    host = get_host_address()
    r = requests.post(
        f'http://{host}:{config["server_port"]}/api', json=payload)
    print(r.text)


if __name__ == "__main__":
    main()
