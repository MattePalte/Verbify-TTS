"""TTS Model based on MMS Facebook Model"""

import os
import uuid
import soundfile as sf

import torch
from transformers import VitsModel, AutoTokenizer

from verbify_tts.services.base_model import TTSBaseModel


class MultiLingualSpeech(TTSBaseModel):
    """MultiLingualSpeech TTS Model."""

    def __init__(
            self,
            default_output_dir: str):
        """Initialize the model.

        Parameters
        ----------
        output_dir : str
            Path to the output directory.
        """
        super().__init__(
            model_name='MMS-Facebook',
            model_path_huggingface='facebook/mms-tts-eng',
            default_output_dir=default_output_dir)

    def initialize(self):
        # MODEL OPTIMIZATION FOR INFERENCE (OPTIONAL)
        torch.jit.enable_onednn_fusion(True)
        model = VitsModel.from_pretrained("facebook/mms-tts-eng")
        tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-eng")
        model.eval()

        self._model = model
        self._tokenizer = tokenizer

    def support_speed(self) -> bool:
        return False

    def generate_audio_file(
            self, text: str, speed: float, output_dir: str = None) -> str:
        if output_dir is None:
            output_dir = self.default_output_dir
        super().generate_audio_file(text, speed, output_dir)
        inputs = self._tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            output = self._model(**inputs).waveform
        unique_filename = str(uuid.uuid4())
        file_path = os.path.join(output_dir, unique_filename + ".wav")
        waveform = output.float().numpy()
        # transpose the output
        waveform = waveform.T
        sample_rate = self._model.config.sampling_rate
        print("size of output: ", waveform.shape)
        print("rate: ", sample_rate)
        sf.write(
            file=file_path,
            data=waveform,
            samplerate=sample_rate)
        return file_path
