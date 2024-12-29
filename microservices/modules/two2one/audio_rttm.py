#config
import config.two2one_config as config

import torch
from microservices.common.gpu_utils import get_device
# Get the best available device
device = get_device()

import os

class AudioRttm:
    def __init__(self, audio_path: str, output_dir: str):
        self.audio_path = audio_path
        self.output_dir = output_dir

    def create_rttm(self) -> None:
        print(config.hf_token)
        if not config.hf_token:
            raise ValueError("HuggingFace token not found. Please set HF_TOKEN in your environment.")

        try:
            from pyannote.audio import Pipeline
            pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",
                                              use_auth_token=config.hf_token)
            print(pipeline)
            if torch.cuda.is_available():
                pipeline = pipeline.to(device)

            diarization = pipeline(self.audio_path, num_speakers=2)
            print(diarization)
            os.makedirs(self.output_dir, exist_ok=True)  # Ensure output directory exists
            with open(f"{self.output_dir}/audio.rttm", "w") as rttm:
                diarization.write_rttm(rttm)

        except Exception as e:
            raise RuntimeError(f"Failed to create RTTM file: {str(e)}")
