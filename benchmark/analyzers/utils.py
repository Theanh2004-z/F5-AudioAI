import librosa
import numpy as np

def load_audio(file_path, target_sr=24000):
    """Load audio and resample to target_sr."""
    y, sr = librosa.load(file_path, sr=target_sr)
    # Convert to mono if stereo
    if len(y.shape) > 1:
        y = librosa.to_mono(y)
    return y, sr
