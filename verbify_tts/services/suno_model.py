"""TTS Model based on Suno's Bark Model"""

import os
import uuid
import soundfile as sf

import torch
import scipy
from transformers import AutoProcessor, AutoModel


from verbify_tts.services.base_model import TTSBaseModel


class SunoBarkModel(TTSBaseModel):
    """SunoBark TTS Model."""

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
            model_name='SunoBark',
            model_path_huggingface='suno/bark-small',
            default_output_dir=default_output_dir)

    def initialize(self):
        # MODEL OPTIMIZATION FOR INFERENCE (OPTIONAL)
        torch.jit.enable_onednn_fusion(True)
        self._processor = AutoProcessor.from_pretrained("suno/bark-small")
        self._model = AutoModel.from_pretrained(
            "suno/bark-small", torch_dtype=torch.float32)
        self._model.to_bettertransformer()

    def support_speed(self) -> bool:
        return False

    def generate_audio_file(
            self, text: str, speed: float, output_dir: str = None) -> str:
        if output_dir is None:
            output_dir = self.default_output_dir
        super().generate_audio_file(text, speed, output_dir)
        inputs = self._processor(text=[text], return_tensors="pt")
        with torch.no_grad():
            speech_values = self._model.generate(**inputs, do_sample=True)
        sampling_rate = 24_000
        unique_filename = str(uuid.uuid4())
        file_path = os.path.join(output_dir, unique_filename + ".wav")
        scipy.io.wavfile.write(
            file_path,
            rate=sampling_rate,
            data=speech_values.cpu().numpy().squeeze())
        return file_path
