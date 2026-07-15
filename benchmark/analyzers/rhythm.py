import librosa
import numpy as np
from analyzers.utils import load_audio
from benchmark_config import TARGET_SR, TOP_DB_SILENCE

def extract_rhythm_features(file_path):
    y, sr = load_audio(file_path, TARGET_SR)
    
    intervals = librosa.effects.split(y, top_db=TOP_DB_SILENCE)
    
    total_duration = len(y) / sr
    speech_duration = np.sum([intv[1] - intv[0] for intv in intervals]) / sr
    silence_duration = total_duration - speech_duration
    
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo_val, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    speech_rate = float(tempo_val[0]) if isinstance(tempo_val, np.ndarray) else float(tempo_val)
    
    pause_positions = []
    pause_durations = []
    
    for i in range(len(intervals) - 1):
        end_current = intervals[i][1]
        start_next = intervals[i+1][0]
        p_dur = (start_next - end_current) / sr
        p_pos = end_current / sr
        pause_durations.append(float(p_dur))
        pause_positions.append(float(p_pos))
        
    pause_count = len(pause_durations)
    mean_pause_duration = float(np.mean(pause_durations)) if pause_count > 0 else 0.0
    
    mask = np.zeros(len(y))
    for start, end in intervals:
        mask[start:end] = 1.0
        
    step = max(1, len(mask) // 1000)
    timeline = mask[::step].tolist()
    
    confidence = 1.0
    if speech_rate == 0.0 or speech_duration < 0.5:
        confidence = 0.3
        print(f"⚠️ [Rhythm Analyzer] Low confidence ({confidence}): Unable to reliably detect speech rhythm.")
        
    scalars = {
        "rhythm_speech_duration": float(speech_duration),
        "rhythm_silence_duration": float(silence_duration),
        "rhythm_speech_rate": float(speech_rate),
        "rhythm_pause_count": float(pause_count),
        "rhythm_mean_pause_duration": float(mean_pause_duration),
        "rhythm_confidence": float(confidence)
    }
    arrays = {
        "pause_positions": pause_positions,
        "pause_durations": pause_durations,
        "timeline_mask": timeline
    }
    
    return scalars, arrays
