"""TTS Model based on FastSpeech2."""

import os
import uuid
import soundfile as sf

import torch
from fairseq.checkpoint_utils import load_model_ensemble_and_task_from_hf_hub
from fairseq.models.text_to_speech.hub_interface import TTSHubInterface

from verbify_tts.services.base_model import TTSBaseModel


class FastSpeechModel(TTSBaseModel):
    """FastSpeech2 TTS Model."""

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
            model_name='FastSpeech2',
            model_path_huggingface='facebook/fastspeech2-en-ljspeech',
            default_output_dir=default_output_dir)

    def initialize(self):
        # MODEL OPTIMIZATION FOR INFERENCE (OPTIONAL)
        torch.jit.enable_onednn_fusion(True)
        # PREPARE MODELS - REQUIRED
        models, cfg, task = load_model_ensemble_and_task_from_hf_hub(
            "facebook/fastspeech2-en-ljspeech",
            arg_overrides={"vocoder": "hifigan", "fp16": False}
        )
        self._task = task
        # MODEL OPTIMIZATION FOR INFERENCE (OPTIONAL)
        for model in models:
            model.eval()
        for model in models:
            for param in model.parameters():
                param.grad = None
        # PREPARE GENERATOR - REQUIRED
        model = models[0]
        self._model = model
        TTSHubInterface.update_cfg_with_data_cfg(cfg, task.data_cfg)
        self._generator = task.build_generator(models[:1], cfg)

    def support_speed(self) -> bool:
        return False

    def generate_audio_file(
            self, text: str, speed: float, output_dir: str = None) -> str:
        if output_dir is None:
            output_dir = self.default_output_dir
        super().generate_audio_file(text, speed, output_dir)
        sample = TTSHubInterface.get_model_input(self._task, text)
        wav, rate = TTSHubInterface.get_prediction(
            task=self._task,
            model=self._model,
            generator=self._generator,
            sample=sample)
        unique_filename = str(uuid.uuid4())
        file_path = os.path.join(output_dir, unique_filename + ".wav")
        sf.write(file_path, wav, rate)
        return file_path
