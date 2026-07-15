import librosa
import numpy as np
from analyzers.utils import load_audio
from benchmark_config import TARGET_SR, PYIN_MIN_F0, PYIN_MAX_F0, FRAME_LENGTH, HOP_LENGTH

def extract_pitch_features(file_path):
    y, sr = load_audio(file_path, TARGET_SR)
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y, fmin=PYIN_MIN_F0, fmax=PYIN_MAX_F0, sr=sr,
        frame_length=FRAME_LENGTH, hop_length=HOP_LENGTH
    )
    
    f0_valid = f0[voiced_flag]
    f0_mean = np.mean(f0_valid) if len(f0_valid) > 0 else 0.0
    f0_variance = np.var(f0_valid) if len(f0_valid) > 0 else 0.0
    voiced_ratio = np.sum(voiced_flag) / len(f0) if len(f0) > 0 else 0.0
    
    f0_contour = np.copy(f0)
    f0_contour[~voiced_flag] = 0.0
    
    # Confidence heuristic: if very low voiced ratio or NaN f0, confidence drops
    confidence = 1.0
    if voiced_ratio < 0.1:
        confidence = 0.5
        print(f"⚠️ [Pitch Analyzer] Low confidence ({confidence}): Very low voiced ratio ({voiced_ratio:.2f})")
    
    scalars = {
        "pitch_f0_mean": float(f0_mean),
        "pitch_f0_variance": float(f0_variance),
        "pitch_voiced_ratio": float(voiced_ratio),
        "pitch_confidence": float(confidence)
    }
    arrays = {
        "f0_contour": f0_contour.tolist()
    }
    
    return scalars, arrays
