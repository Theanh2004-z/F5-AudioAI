import librosa
import numpy as np
from analyzers.utils import load_audio
from benchmark_config import TARGET_SR

def extract_voice_quality_features(file_path):
    y, sr = load_audio(file_path, TARGET_SR)
    
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    mean_zcr = np.mean(zcr)
    
    flatness = librosa.feature.spectral_flatness(y=y)[0]
    mean_flatness = np.mean(flatness)
    
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    energy_h = np.sum(y_harmonic**2)
    energy_t = np.sum(y**2)
    harmonic_ratio = energy_h / energy_t if energy_t > 0 else 0.0
    
    confidence = 1.0
    if mean_zcr > 0.5:
        confidence = 0.5
        print(f"⚠️ [Voice Quality Analyzer] Low confidence ({confidence}): Exceptionally high zero-crossing rate implies mostly noise.")
    
    scalars = {
        "vq_zero_crossing_rate": float(mean_zcr),
        "vq_spectral_flatness": float(mean_flatness),
        "vq_harmonic_ratio": float(harmonic_ratio),
        "vq_confidence": float(confidence)
    }
    arrays = {}
    
    return scalars, arrays
