import librosa
import numpy as np
from analyzers.utils import load_audio
from benchmark_config import TARGET_SR

def extract_spectral_features(file_path):
    y, sr = load_audio(file_path, TARGET_SR)
    
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    
    mean_centroid = np.mean(centroid)
    mean_rolloff = np.mean(rolloff)
    mean_bandwidth = np.mean(bandwidth)
    mean_contrast = np.mean(contrast)
    
    confidence = 1.0
    if mean_centroid < 100.0:
        confidence = 0.4
        print(f"⚠️ [Spectral Analyzer] Low confidence ({confidence}): Spectral centroid abnormally low.")
    
    scalars = {
        "spectral_centroid_mean": float(mean_centroid),
        "spectral_rolloff_mean": float(mean_rolloff),
        "spectral_bandwidth_mean": float(mean_bandwidth),
        "spectral_contrast_mean": float(mean_contrast),
        "spectral_confidence": float(confidence)
    }
    arrays = {
        "centroid_contour": centroid.tolist()
    }
    
    return scalars, arrays
