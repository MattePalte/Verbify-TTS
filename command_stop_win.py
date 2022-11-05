"""Request to trigger the stop of the speech synthesis.

AUTHOR: Matteo Paltenghi
"""
import os
import requests
from utils import read_yaml_file
from utils import get_root_directory

config = read_yaml_file(os.path.join(
    get_root_directory(), "configuration/config.yaml"))
r = requests.post(f'http://127.0.0.1:{config["server_port"]}/stop')
