import librosa
import soundfile as sf
import numpy as np
from pydub import AudioSegment
import os

class RttmToTwo2One:
    def __init__(self, rttm_file: str, input_audio: str, output_dir: str):
        self.rttm_file = rttm_file
        self.input_audio = input_audio
        self.output_dir = output_dir

    def read_rttm(self):
        speaker_segments = {'SPEAKER_00': [], 'SPEAKER_01': []}
        with open(self.rttm_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 8:
                    start_time = float(parts[3])
                    duration = float(parts[4])
                    speaker = parts[7]
                    speaker_segments[speaker].append((start_time, duration))
        return speaker_segments

    def create_speaker_audio(self, speaker_segments, output_file: str, sr: int = 44100):
        # Load the audio file
        audio, sample_rate = librosa.load(self.input_audio, sr=sr)
        
        # Create silent audio of the same length
        output_audio = np.zeros_like(audio)
        
        # Fill in the segments for this speaker
        for start_time, duration in speaker_segments:
            start_sample = int(start_time * sample_rate)
            end_sample = int((start_time + duration) * sample_rate)
            if end_sample <= len(audio):
                output_audio[start_sample:end_sample] = audio[start_sample:end_sample]
        
        # Save the output
        sf.write(output_file, output_audio, sample_rate)

    def create_two2one_audio(self):
        speaker_segments = self.read_rttm()
        
        # Create separate files for each speaker
        for speaker, segments in speaker_segments.items():
            output_file = os.path.join(self.output_dir, f"{speaker}.wav")
            self.create_speaker_audio(segments, output_file)