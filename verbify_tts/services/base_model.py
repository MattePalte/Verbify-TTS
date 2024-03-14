"""Base class for TTS model prediction.

The class has to be initialized and to produce a .wav file as output.
"""


class TTSBaseModel(object):
    """Base class for TTS model prediction."""

    def __init__(
            self,
            model_name: str,
            model_path_huggingface: str,
            default_output_dir: str):
        """Initialize the model.

        Parameters
        ----------
        model_name : str
            Name of the model.
        model_path_huggingface : str
            Path to the model in Hugging Face format.
        default_output_dir : str
            Path to the output directory.
        """
        self.model_name = model_name
        self.model_path_huggingface = model_path_huggingface
        self.default_output_dir = default_output_dir

    def initialize(self):
        """Initialize the model."""
        pass

    def support_speed(self) -> bool:
        """Check if the model supports speed parameter.

        Returns
        -------
        bool
            True if the model supports speed parameter, False otherwise.
        """
        pass

    def generate_audio_file(
            self,
            text: str,
            speed: float,
            output_dir: str) -> str:
        """Generate the audio file in .wav format.

        Parameters
        ----------
        text : str
            Text to be synthesized.
        speed : float
            This is a relative speed up to the normal speed.
            This parameters might not be directly supported by all models.
        output_dir : str
            Path to the output directory. If None, the default output
            directory is used.

        Returns
        -------
        str
            Full path to the .wav file.
        """
        print(f"Generating audio file...")
        print(f"Model: {self.model_name}")
        print(f"Text: {text}")
        print(f"Speed: {speed}")
        print(f"Output dir: {output_dir}")

