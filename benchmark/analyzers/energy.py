import librosa
import numpy as np
from analyzers.utils import load_audio
from benchmark_config import TARGET_SR, FRAME_LENGTH, HOP_LENGTH

def extract_energy_features(file_path):
    y, sr = load_audio(file_path, TARGET_SR)
    rms = librosa.feature.rms(y=y, frame_length=FRAME_LENGTH, hop_length=HOP_LENGTH)[0]
    
    rms_mean = np.mean(rms)
    rms_variance = np.var(rms)
    peak = np.max(np.abs(y))
    
    overall_rms = np.sqrt(np.mean(y**2))
    crest_factor = peak / overall_rms if overall_rms > 0 else 0.0
    
    confidence = 1.0
    if peak < 0.01:
        confidence = 0.2
        print(f"⚠️ [Energy Analyzer] Low confidence ({confidence}): Audio is nearly completely silent (peak: {peak:.4f})")
    
    scalars = {
        "energy_rms_mean": float(rms_mean),
        "energy_rms_variance": float(rms_variance),
        "energy_peak": float(peak),
        "energy_crest_factor": float(crest_factor),
        "energy_confidence": float(confidence)
    }
    arrays = {
        "rms_contour": rms.tolist()
    }
    
    return scalars, arrays
