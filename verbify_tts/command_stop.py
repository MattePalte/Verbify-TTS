"""Request to trigger the stop of the speech synthesis.

AUTHOR: Matteo Paltenghi
"""
import os
import requests
from verbify_tts.utils import (
    read_yaml_file,
    get_root_directory,
    get_host_address,
)


def stop_tts():
    """Stop the TTS server."""
    config = read_yaml_file(os.path.join(
        get_root_directory(), "configuration/config.yaml"))
    host = get_host_address()
    return requests.post(f'http://{host}:{config["server_port"]}/stop')


def main():
    """Stop the TTS server."""
    response = stop_tts()
    print(f"Stop request sent. Response status: {response.status_code}")


if __name__ == "__main__":
    main()
