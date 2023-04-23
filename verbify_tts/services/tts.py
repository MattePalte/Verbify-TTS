"""
Verbify-TTS with voice generation engine.

This uses the fastspeech2 model from TTSHubInterface.

AUTHOR: Matteo Paltenghi
"""

import fastapi
import platform
import os
import tempfile
import uuid
from threading import Thread
import pygame
import soundfile as sf
import sox
import numpy as np
import uvicorn
import torch

from fairseq.checkpoint_utils import load_model_ensemble_and_task_from_hf_hub
from fairseq.models.text_to_speech.hub_interface import TTSHubInterface

from verbify_tts.utils import read_yaml_file
from verbify_tts.text_preprocessing import replace_acronyms
from verbify_tts.text_preprocessing import replace_idioms


config = read_yaml_file("configuration/config.yaml")

if platform.system() == "Windows":
    LOCAL_IP = "127.0.0.1"
else:
    LOCAL_IP = "0.0.0.0"

app = fastapi.FastAPI(port=config["server_port"])

# MODEL OPTIMIZATION FOR INFERENCE (OPTIONAL)
torch.jit.enable_onednn_fusion(True)
# PREPARE MODELS - REQUIRED
models, cfg, task = load_model_ensemble_and_task_from_hf_hub(
    "facebook/fastspeech2-en-ljspeech",
    arg_overrides={"vocoder": "hifigan", "fp16": False}
)
# MODEL OPTIMIZATION FOR INFERENCE (OPTIONAL)
for model in models:
    model.eval()
for model in models:
    for param in model.parameters():
        param.grad = None
# PREPARE GENERATOR - REQUIRED
model = models[0]
TTSHubInterface.update_cfg_with_data_cfg(cfg, task.data_cfg)
generator = task.build_generator(models[:1], cfg)


def play_audio(
        file_path: str,
        prev_audio_task,
        change_speed_thread):
    """Play the given audio file entirely.

    This task has to wait for the previous audio task to finish.
    And also that its change speed task has finished.
    """
    print("waiting for previous audio task to finish")
    if prev_audio_task is not None:
        prev_audio_task.join()
    print("waiting for change speed task to finish")
    if change_speed_thread is not None:
        change_speed_thread.join()
    print("playing audio")
    pygame.mixer.init()
    obj_sound = pygame.mixer.Sound(file_path)
    channel = obj_sound.play()
    while channel.get_busy():
        pygame.time.wait(333)  # ms
    print("played audio. Done.")


def change_speed(old_file_path: str, new_file_path: str, speed: float):
    """Change the speed without affecting the pitch."""
    print("changing speed")
    tfm = sox.Transformer()
    tfm.tempo(speed)
    tfm.build(old_file_path, new_file_path)
    print("changed speed. Done.")


@app.post("/read")
async def read(text: str, speed: float = config["reading_speed"]):
    """Request to trigger the start of a the speech synthesis.

    Parameters
    ----------
    text : str
        Text to be synthesized.
    speed : float
        Reading speed in words per minute.

    Returns
    -------
    str
        The text to be synthesized.
    """
    # prepare the text
    if "." not in text:
        text += "."
    text = replace_idioms(text)
    sentences = text.split(".")

    all_outputs = []

    audio_thread_tasks = {}
    speed_thread_tasks = {}

    prev_audio_task = None

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        print('created temporary directory', tmp_dir_name)
        with torch.no_grad():
            # remove empty sentences
            sentences = [sentence for sentence in sentences
                        if sentence.strip() != ""]
            for sentence in sentences:
                sentence = replace_acronyms(sentence)
                sentence += " " * 80 + "."  # add padding
                print("sentence: ", sentence)
                print("model entrance...")
                sample = TTSHubInterface.get_model_input(task, sentence)
                wav, rate = TTSHubInterface.get_prediction(
                    task, model, generator, sample)
                print("model exit... Done.")
                # save the file as a temporary file with a unique name
                unique_filename = str(uuid.uuid4())
                file_path = os.path.join(tmp_dir_name, unique_filename + ".wav")
                # write wav to file
                # rate = int(rate * speed)
                sf.write(file_path, wav, rate)

                # initialize the two threads in the dictionary
                audio_thread_tasks[unique_filename] = None
                speed_thread_tasks[unique_filename] = None

                # ALTERNATIVES TO CHANGE SPEED
                # import librosa
                #audio, fs = librosa.load(file_path)
                # audio_different_speed = librosa.effects.time_stretch(
                #     y=audio, rate=speed)
                # import pyrubberband as pyrb
                # audio_different_speed = pyrb.time_stretch(
                #     audio, fs, speed)
                #sf.write(file_path, audio_different_speed, fs)

                # the changing speed tasks can work in parallel
                new_path = file_path.replace(".wav", "_new.wav")
                print("change speed chained...")
                # change_speed_thread = asyncio.create_task(
                #     change_speed(file_path, new_path, speed))
                change_speed_thread = Thread(
                    target=change_speed, args=(file_path, new_path, speed))
                change_speed_thread.start()

                # start the thread
                speed_thread_tasks[unique_filename] = change_speed_thread
                file_path = new_path

                # audio_thread = asyncio.create_task(
                #     play_audio(file_path, prev_audio_task, change_speed_thread))
                audio_thread = Thread(
                    target=play_audio, args=(file_path, prev_audio_task, change_speed_thread))
                audio_thread.start()
                prev_audio_task = audio_thread
                audio_thread_tasks[unique_filename] = audio_thread
                all_outputs.append(file_path)
            # wait for all the audio tasks to finish before returning
            for thread in audio_thread_tasks.values():
                if thread is not None:
                    # await thread
                    thread.join()
    return text


if __name__ == "__main__":
    if platform.system() == "Windows":
        LOCAL_IP = "127.0.0.1"
    else:
        LOCAL_IP = "0.0.0.0"
    uvicorn.run(app, host=LOCAL_IP, port=config["server_port"])
