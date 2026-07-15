import os
import sys
import numpy as np
import librosa
import soundfile as sf

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from benchmark import extract_all
from difference_engine import calculate_difference

def create_test_files(y, sr, output_dir):
    """Generate all transformed files for stress testing"""
    os.makedirs(output_dir, exist_ok=True)
    files = {}
    
    # 1. Identity
    out = os.path.join(output_dir, "identity.wav")
    sf.write(out, y, sr)
    files["identity"] = out
    
    # 2. Volume (+6dB)
    out = os.path.join(output_dir, "volume.wav")
    sf.write(out, y * 2.0, sr)
    files["volume"] = out
    
    # 3. Tempo Stretch (1.2x)
    out = os.path.join(output_dir, "tempo.wav")
    sf.write(out, librosa.effects.time_stretch(y, rate=1.2), sr)
    files["tempo"] = out
    
    # 4. Pitch Shift (+4 semitones)
    out = os.path.join(output_dir, "pitch.wav")
    sf.write(out, librosa.effects.pitch_shift(y, sr=sr, n_steps=4), sr)
    files["pitch"] = out
    
    # 5. Noise (SNR 20dB)
    out = os.path.join(output_dir, "noise.wav")
    rms = np.sqrt(np.mean(y**2))
    noise = np.random.normal(0, rms * 0.1, len(y))
    sf.write(out, y + noise, sr)
    files["noise"] = out
    
    # 6. Compression (Hard clipping)
    out = os.path.join(output_dir, "compression.wav")
    y_comp = np.clip(y, -0.5, 0.5)
    if np.max(np.abs(y_comp)) > 0:
        y_comp = y_comp / np.max(np.abs(y_comp)) * np.max(np.abs(y))
    sf.write(out, y_comp, sr)
    files["compression"] = out
    
    return files

def check_pass_fail(test_name, diff):
    """
    Automatic PASS/FAIL logic based on raw numerical differences.
    """
    if test_name == "identity":
        # All differences must be essentially zero
        return all(abs(v) < 1e-4 for v in diff.values())
        
    elif test_name == "volume":
        # RMS should increase significantly, Pitch shouldn't change
        return diff["energy_rms_mean_difference"] > 0 and abs(diff["pitch_f0_mean_difference"]) < 1.0
        
    elif test_name == "tempo":
        # Speech rate should increase, Pitch shouldn't change
        return diff["rhythm_speech_rate_difference"] > 0.0 and abs(diff["pitch_f0_mean_difference"]) < 1.0
        
    elif test_name == "pitch":
        # F0 mean should increase, Speech rate shouldn't change much
        return diff["pitch_f0_mean_difference"] > 10.0 and abs(diff["rhythm_speech_rate_difference"]) < 0.5
        
    elif test_name == "noise":
        # ZCR should increase due to white noise
        return diff["vq_zero_crossing_rate_difference"] > 0
        
    elif test_name == "compression":
        # Crest factor should decrease because peaks are clipped
        return diff["energy_crest_factor_difference"] < 0
        
    return False

def run_validation_suite(ref_file):
    print(f"=== STARTING AUTOMATIC VALIDATION SUITE on {ref_file} ===")
    y, sr = librosa.load(ref_file, sr=24000)
    
    test_dir = "validation_temp"
    files = create_test_files(y, sr, test_dir)
    
    # Extract reference base
    ref_scalars, _ = extract_all(files["identity"])
    
    for test_name, file_path in files.items():
        gen_scalars, _ = extract_all(file_path)
        diff = calculate_difference(ref_scalars, gen_scalars)
        
        passed = check_pass_fail(test_name, diff)
        
        status = "PASS" if passed else "FAIL"
        print(f"Test [{test_name.upper():<12}] : {status}")

    print("=== VALIDATION COMPLETED ===")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", type=str, required=True, help="Path to reference audio")
    args = parser.parse_args()
    
    run_validation_suite(args.ref)
