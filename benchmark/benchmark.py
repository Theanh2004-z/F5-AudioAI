import argparse
import os
import json
import time
from datetime import datetime
import librosa
import numpy as np

from analyzers.pitch import extract_pitch_features
from analyzers.energy import extract_energy_features
from analyzers.rhythm import extract_rhythm_features
from analyzers.spectral import extract_spectral_features
from analyzers.voice_quality import extract_voice_quality_features
from difference_engine import calculate_difference
from feature_vector import build_feature_vector
from visualization.plotter import generate_dashboard
from controller_interface import export_controller_input
from benchmark_config import TARGET_SR, ANALYSIS_VERSION, FEATURE_VECTOR_VERSION

def extract_all(file_path):
    s_pitch, a_pitch = extract_pitch_features(file_path)
    s_energy, a_energy = extract_energy_features(file_path)
    s_rhythm, a_rhythm = extract_rhythm_features(file_path)
    s_spectral, a_spectral = extract_spectral_features(file_path)
    s_vq, a_vq = extract_voice_quality_features(file_path)
    
    scalars = {**s_pitch, **s_energy, **s_rhythm, **s_spectral, **s_vq}
    arrays = {**a_pitch, **a_energy, **a_rhythm, **a_spectral, **a_vq}
    return scalars, arrays

def get_metadata(file_path):
    y, sr = librosa.load(file_path, sr=TARGET_SR)
    return {
        "sample_rate": sr,
        "duration": len(y) / sr,
        "frame_count": len(y),
        "hop_length": 256
    }

def run_benchmark(ref_path, gen_path):
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("reports", timestamp_str)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n--- Output Directory: {output_dir} ---")
    
    # 1. Load & Extract
    print("Extracting Reference Features...")
    ref_scalars, ref_arrays = extract_all(ref_path)
    ref_metadata = get_metadata(ref_path)
    
    print("Extracting Generated Features...")
    gen_scalars, gen_arrays = extract_all(gen_path)
    gen_metadata = get_metadata(gen_path)
    
    # 2. Difference
    print("Calculating Feature Differences...")
    differences = calculate_difference(ref_scalars, gen_scalars)
    
    # 3. Vectorize
    print("Vectorizing Features...")
    ref_vector = build_feature_vector(ref_scalars)
    gen_vector = build_feature_vector(gen_scalars)
    vector_path = os.path.join(output_dir, "feature_vector.npy")
    np.save(vector_path, {"ref_vector": ref_vector, "gen_vector": gen_vector})
    
    # 4. Visualize
    print("Generating Dashboard...")
    png_path = os.path.join(output_dir, "dashboard.png")
    generate_dashboard(ref_arrays, gen_arrays, ref_scalars, gen_scalars, png_path)
    
    # 5. Export Report
    print("Exporting JSON Report...")
    metadata_block = {
        "analysis_version": ANALYSIS_VERSION,
        "feature_vector_version": FEATURE_VECTOR_VERSION,
        "timestamp": timestamp_str,
        "reference": ref_metadata,
        "generated": gen_metadata
    }
    
    report = {
        "metadata": metadata_block,
        "reference": ref_scalars,
        "generated": gen_scalars,
        "difference": differences
    }
    
    report_path = os.path.join(output_dir, "report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    # 6. Export Controller Input
    print("Exporting Controller Interface...")
    controller_path = export_controller_input(vector_path, differences, metadata_block, output_dir)
        
    print("\n✅ PIPELINE COMPLETED")
    print(f"Report: {report_path}")
    print(f"Vector: {vector_path}")
    print(f"Controller: {controller_path}")
    print(f"Visual: {png_path}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="F5-TTS Feature Extraction Framework")
    parser.add_argument("--ref", type=str, required=True, help="Path to reference audio")
    parser.add_argument("--gen", type=str, required=True, help="Path to generated audio")
    
    args = parser.parse_args()
    run_benchmark(args.ref, args.gen)
