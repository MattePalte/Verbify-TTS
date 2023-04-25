"""This modules handles the usage of the microphone.

There are methods to record audio and speech to text.
"""

import os
import time
import tempfile

import sounddevice as sd
import soundfile as sf
import uuid
from threading import Thread

import pygame

from verbify_tts.actions.shortcut import shortcut_copy
from verbify_tts.actions.shortcut import shortcut_paste
from verbify_tts.actions.shortcut import shortcut_switch_window


RECORDING_IN_PROGRESS = False


def beep():
    """Play the mp3 file with the beep sound."""
    path = os.path.join("verbify_tts/resources/success.mp3")
    # Starting the mixer
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()


def record_audio(folder_path: str, duration: int = 5) -> str:
    """Record audio from the microphone.

    Args:
        folder_path: Path to the folder where the audio file will be saved.
        duration: Duration of the recording in seconds.

    Returns:
        Path to the audio file.

    Note that the file will be a WAV file.
    """

    fs = 44100  # Sample rate
    seconds = duration  # Duration of recording

    print(f"Recording audio... ({duration} seconds)")
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()  # Wait until recording is finished
    file_path = os.path.join(folder_path, str(uuid.uuid4()) + ".wav")
    sf.write(file_path, myrecording, fs)  # Save as WAV file
    return file_path


def play_audio(audio_file_path: str) -> None:
    """Play an audio file.

    Args:
        audio_file_path: Path to the audio file.
    """
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(300)


def transcribe(filepath: str, endpoint_ip: str = "localhost", endpoint_port: int = 9000) -> str:
    """Transcribe the audio file via the Whisper API.

    Equivalent to:
    curl -X 'POST' \
        'http://localhost:9000/asr?method=openai-whisper&task=transcribe&encode=true&output=json' \
        -H 'accept: application/json' \
        -H 'Content-Type: multipart/form-data' \
        -F 'audio_file=@test_transcribe.wav;type=audio/wav'

    Response:
    {
        "text": " I am here with you.",
        "segments": [{
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 2.0,
            "text": " I am here with you.",
            "tokens": [50364, 286, 669, 510, 365, 291, 13, 50464],
            "temperature": 0.0,
            "avg_logprob": -0.5349887212117513,
            "compression_ratio": 0.7037037037037037,
            "no_speech_prob": 0.06548802554607391}],
        "language": "en"
    }

    """
    import requests
    import json

    url = f"http://{endpoint_ip}:{endpoint_port}/asr"
    params = {
        "method": "openai-whisper",
        "task": "transcribe",
        "encode": "true",
        "output": "json"
    }
    files = {
        "audio_file": open(filepath, "rb")
    }
    response = requests.post(url, params=params, files=files)
    return json.loads(response.text)["text"]


def listen_and_execute():
    """Listen to the user and execute the command.

    Note that this starts a new thread.

    Returns:
        The command to execute.
    """
    global RECORDING_IN_PROGRESS
    if RECORDING_IN_PROGRESS:
        return

    def _listen_and_execute():
        global RECORDING_IN_PROGRESS
        RECORDING_IN_PROGRESS = True
        try:
            with tempfile.TemporaryDirectory() as tmpdirname:
                print('created temporary directory', tmpdirname)
                # Test the record_audio method
                file_path = record_audio(tmpdirname, 3)
                print(file_path)
                beep()
                command = transcribe(file_path)
                command = command.lower()
                beep()
                print("Command: ", command)
                if "window" in command:
                    n_times = 1
                    if "two" in command or "to" in command or "too" in command or "2" in command:
                        n_times = 2
                    elif "three" in command or "3" in command or "free" in command:
                        n_times = 3
                    elif "four" in command or "for" in command or "4" in command:
                        n_times = 4
                    shortcut_switch_window(n_times)
                elif "copy" in command:
                    shortcut_copy()
                elif "paste" in command:
                    shortcut_paste()

        except Exception as e:
            print("Audio recording failed. (not failing deliberately)")
            print(e)
        finally:
            RECORDING_IN_PROGRESS = False

    t = Thread(target=_listen_and_execute)
    t.start()



if __name__ == '__main__':
    # # Test the audio module
    # with tempfile.TemporaryDirectory() as tmpdirname:
    #     print('created temporary directory', tmpdirname)
    #     # Test the record_audio method
    #     file_path = record_audio(tmpdirname, 3)
    #     print(file_path)

    #     # Test the play_audio method
    #     play_audio(file_path)

    # # Test the transcribe method
    # file_path = os.path.join("verbify_tts/resources/test_transcribe.wav")

    # res = transcribe(file_path)
    # print(res)
    pass
