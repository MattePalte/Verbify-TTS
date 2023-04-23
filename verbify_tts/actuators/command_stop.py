"""Request to trigger the stop of the speech synthesis.

AUTHOR: Matteo Paltenghi
"""
import os
import requests
import platform

from verbify_tts.utils import read_yaml_file
from verbify_tts.utils import get_root_directory

config = read_yaml_file(os.path.join(
    get_root_directory(), "configuration/config.yaml"))

if platform.system() == "Windows":
    LOCAL_IP = "127.0.0.1"
else:
    LOCAL_IP = "0.0.0.0"


def command_stop():
    """Request to trigger the stop of the speech synthesis."""
    r = requests.post(f'http://{LOCAL_IP}/:{config["server_port"]}/stop')


if __name__ == "__main__":
    command_stop()
