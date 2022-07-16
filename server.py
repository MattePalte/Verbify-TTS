"""
Verbify-TTS with voice generation engine.

AUTHOR: Matteo Paltenghi
"""

import gc
import glob
import multiprocessing
import os
import pathlib
from random import randint

# server
from flask import Flask, request, jsonify
from flask_cors import CORS
# idioms handling
import pandas as pd
# audio
import pygame
import soundfile as sf
# voice engine
import tensorflow as tf
from tensorflow_tts.inference import TFAutoModel
from tensorflow_tts.inference import AutoProcessor

from utils import read_yaml_file


TEMPORARY_AUDIO_FOLDER = "tmp_audio_tts_deep_learning"
THIS_SCRIPT_FOLDER = pathlib.Path(__file__).parent.resolve()

# 1. initialize model once and for all and reload weights
# initialize fastspeech2 model.
fastspeech2 = TFAutoModel.from_pretrained(
    "tensorspeech/tts-fastspeech2-ljspeech-en")
# initialize mb_melgan model
mb_melgan = TFAutoModel.from_pretrained(
    "tensorspeech/tts-mb_melgan-ljspeech-en")
# inference
processor = AutoProcessor.from_pretrained(
    "tensorspeech/tts-fastspeech2-ljspeech-en")


def replace_acronyms(text):
    """Replace acronyms TPL with their hyphened version T-P-L."""
    # get all upper case words
    words = text.split()
    mapping_dict = dict()
    for i, word in enumerate(words):
        if len(word) > 2 and word.isupper():
            replacement_word = '-'.join(word.lower())
            mapping_dict[word] = replacement_word
    # replace all words in the mapping dict
    for key, value in mapping_dict.items():
        text = text.replace(key, value)
    return text


def replace_idioms(text):
    """Replace idioms such as "e.g." with "for example"."""
    df = pd.read_csv(
        os.path.join(THIS_SCRIPT_FOLDER, "configuration/idioms.csv"),
        header=0, delimiter=",")
    for i, row in df.iterrows():
        text = text.replace(str(row["idiom"]), str(row["replacement"]))
    return text


def read_out_loud(filepath: str):
    """Play the given audio file entirely."""
    pygame.mixer.init()
    obj_sound = pygame.mixer.Sound(filepath)
    channel = obj_sound.play()
    while channel.get_busy():
        pygame.time.wait(333)  # ms


def get_model_api():
    """Returns lambda function for api"""

    def model_api(input_data):
        """Generation of the voice based on the input text.

        Note that the text will first pass the idioms substitution, then the
        acronyms substitution, then the text will be passed to the model.
        """

        global play_process
        global interrupt
        global TEMPORARY_AUDIO_FOLDER
        global THIS_SCRIPT_FOLDER

        interrupt = False

        print("input_data: ", input_data)
        speed = float(input_data.get('speed', 1))
        speed_ratio = float(1 / speed)
        # fastspeech inference

        raw_input = input_data["text"]
        raw_input = replace_idioms(raw_input)
        sentences = raw_input.split(".")

        all_outputs = []

        for sentence in sentences:
            sentence = replace_acronyms(sentence)
            input_ids = processor.text_to_sequence(sentence)
            mel_before, mel_after, duration_outputs, _, _ = fastspeech2.inference(
                input_ids=tf.expand_dims(
                    tf.convert_to_tensor(input_ids, dtype=tf.int32), 0),
                speaker_ids=tf.convert_to_tensor([0], dtype=tf.int32),
                speed_ratios=tf.convert_to_tensor(
                    [speed_ratio], dtype=tf.float32),
                f0_ratios=tf.convert_to_tensor([1.0], dtype=tf.float32),
                energy_ratios=tf.convert_to_tensor([1.0], dtype=tf.float32),
            )

            # melgan inference
            try:
                audio_before = mb_melgan.inference(mel_before)[0, :, 0]
                audio_after = mb_melgan.inference(mel_after)[0, :, 0]
            except Exception as e:
                print("Exception: ", e)
                break

            # random filename
            random_id = str(randint(0, 10000000000))
            out_filename = f"{random_id}.wav"
            path_original_audio = os.path.join(
                THIS_SCRIPT_FOLDER, TEMPORARY_AUDIO_FOLDER, out_filename)
            # save to file
            sf.write(path_original_audio, audio_before, 22050, "PCM_16")
            sf.write(path_original_audio, audio_after, 22050, "PCM_16")

            out_path = path_original_audio

            play_process = multiprocessing.Process(
                target=read_out_loud, args=(out_path,))
            play_process.start()
            play_process.join()
            if interrupt:
                return ""
            all_outputs.append(out_path)

        gc.collect()
        return all_outputs

    return model_api


app = Flask(__name__)
CORS(app)  # needed for cross-domain requests, allow everything by default
model_api = get_model_api()


# default route
@app.route('/')
def index():
    return "Index API"


# HTTP Errors handlers
@app.errorhandler(404)
def url_error(e):
    return """
    Wrong URL!
    <pre>{}</pre>""".format(e), 404


@app.errorhandler(500)
def server_error(e):
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


# API route
@app.route('/api', methods=['POST'])
def api():
    """Endpoint to receive request to read out loud.

    The request should be a JSON object with the following fields:
    - text: the text to read out loud
    - speed: the speed of the text reading
    """
    input_data = request.json
    all_outputs = model_api(input_data)
    response = jsonify({"text": all_outputs})
    return response


@app.route('/stop', methods=['POST'])
def stop():
    """Endpoint to receive request to stop reading."""
    global play_process
    global interrupt
    interrupt = True
    play_process.terminate()
    return ""


if __name__ == '__main__':
    # clean folder with temporary files
    tmp_folder_path = os.path.join(THIS_SCRIPT_FOLDER, TEMPORARY_AUDIO_FOLDER)
    try:
        if os.path.isdir(tmp_folder_path):
            files = glob.glob(f'{tmp_folder_path}/*.wav')
            for f in files:
                os.remove(f)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (tmp_folder_path, e))
    # to inspect the log of the server use the following command:
    # journalctl -xefu verify-tts.service
    config = read_yaml_file(
        os.path.join(THIS_SCRIPT_FOLDER,"configuration/config.yaml"))
    app.run(host='0.0.0.0', debug=False, port=config["server_port"])