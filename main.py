#imports
import os

## import audio rttm to create audio.rttm
from microservices.modules.two2one.audio_rttm import AudioRttm
from microservices.modules.two2one.separate_speakers import RttmToTwo2One
# generate a audio at notebooklm

class AutoCreator:
    def __init__(self):
        pass

    def create_two2one_audio(self, audio_path: str, output_dir: str):
        audio_rttm = AudioRttm(audio_path, output_dir)
        audio_rttm.create_rttm()
    
    def create_two2one_audio_from_input(self, rttm_file: str, input_audio: str, output_dir: str):
        audio_rttm = RttmToTwo2One(rttm_file, input_audio, output_dir)
        audio_rttm.create_two2one_audio()


if __name__ == "__main__":
    auto_creator = AutoCreator()
    step = input("Enter the step: ")
    match step:
        case "1":
            two2one_output_dir = os.path.join(os.path.dirname(__file__), "output_pool/two2one/")

            # creating audio rttm
            two2one_audio_path = os.path.join(os.path.dirname(__file__), "input_pool/two2one/audio.wav")
            auto_creator.create_two2one_audio(two2one_audio_path, two2one_output_dir)
        case "2":
            rttm_file = os.path.join(os.path.dirname(__file__), "output_pool/two2one/audio.rttm")
            input_audio = os.path.join(os.path.dirname(__file__), "input_pool/two2one/audio.wav")
            output_dir = os.path.join(os.path.dirname(__file__), "output_pool/two2one/")
            auto_creator.create_two2one_audio_from_input(rttm_file, input_audio, output_dir)

