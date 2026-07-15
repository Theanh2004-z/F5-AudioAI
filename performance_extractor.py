import librosa
import numpy as np
import warnings
import sys

warnings.filterwarnings('ignore')

class PerformanceObject:
    """
    GIAI ĐOẠN 3: Xây Performance Representation
    Object chung dùng để lưu trữ toàn bộ diễn xuất của một đoạn audio.
    """
    def __init__(self, f0, rms, tempo, pause_ratio, duration):
        self.f0 = f0                # Đường cong cao độ (Pitch contour)
        self.rms = rms              # Đường cong cường độ (Energy envelope)
        self.tempo = tempo          # Tốc độ đọc (BPM)
        self.pause_ratio = pause_ratio # Tỷ lệ thời gian im lặng
        self.duration = duration    # Tổng độ dài (giây)

def extract_performance(audio_path, sr=24000):
    """Bóc tách Performance từ file audio"""
    y, sr = librosa.load(audio_path, sr=sr)
    
    # 1. Cường độ (Energy - RMS)
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=256)[0]
    
    # 2. Cao độ (Pitch - F0)
    # Dùng thuật toán YIN, nhanh và đủ tốt để tính độ tương quan
    f0 = librosa.yin(y, fmin=50, fmax=500, sr=sr, frame_length=1024, hop_length=256)
    # Loại bỏ nhiễu NaN ở các đoạn câm
    f0[np.isnan(f0)] = 0
    
    # 3. Tốc độ nói (Tempo)
    tempo_array, _ = librosa.beat.beat_track(y=y, sr=sr)
    # Fix compatibility for different librosa versions
    tempo = float(tempo_array[0]) if isinstance(tempo_array, (np.ndarray, list)) else float(tempo_array)
    
    # 4. Ngắt nghỉ (Pause)
    # Lọc ra các đoạn có tiếng (lớn hơn ngưỡng noise 30dB)
    non_mute_intervals = librosa.effects.split(y, top_db=30)
    non_mute_duration = np.sum([intv[1] - intv[0] for intv in non_mute_intervals]) / sr
    total_duration = len(y) / sr
    pause_ratio = (total_duration - non_mute_duration) / total_duration if total_duration > 0 else 0
    
    return PerformanceObject(f0, rms, tempo, pause_ratio, total_duration)

def calculate_correlation(ref_seq, gen_seq):
    """
    Tính độ tương quan (Correlation) giữa 2 mảng (Pitch hoặc Energy).
    Dùng DTW (Dynamic Time Warping) để đồng bộ thời gian vì audio Việt có thể dài/ngắn hơn audio Trung.
    """
    if len(ref_seq) < 2 or len(gen_seq) < 2:
        return 0.0
        
    # Đồng bộ thời gian bằng DTW
    D, wp = librosa.sequence.dtw(ref_seq, gen_seq, metric='euclidean')
    
    ref_aligned = ref_seq[wp[:, 0]]
    gen_aligned = gen_seq[wp[:, 1]]
    
    # Tính Pearson Correlation Coefficient (-1 đến 1)
    if np.std(ref_aligned) == 0 or np.std(gen_aligned) == 0:
        return 0.0
    
    correlation = np.corrcoef(ref_aligned, gen_aligned)[0, 1]
    
    # Quy đổi ra % (Chỉ lấy phần tương quan dương)
    score = max(0, correlation) * 100 
    return score

def benchmark_f5(ref_path, gen_path):
    """
    GIAI ĐOẠN 1 & 4: Benchmark đo lường tự động
    """
    print(f"[Extractor] Đang bóc tách Audio Gốc: {ref_path}")
    ref_perf = extract_performance(ref_path)
    
    print(f"[Extractor] Đang bóc tách Audio F5 sinh ra: {gen_path}")
    gen_perf = extract_performance(gen_path)
    
    # Chấm điểm Pitch & Energy bằng DTW + Pearson
    pitch_score = calculate_correlation(ref_perf.f0, gen_perf.f0)
    energy_score = calculate_correlation(ref_perf.rms, gen_perf.rms)
    
    # Chấm điểm Tempo (Tốc độ càng giống nhau điểm càng cao)
    tempo_score = min(ref_perf.tempo, gen_perf.tempo) / max(ref_perf.tempo, gen_perf.tempo) * 100 if max(ref_perf.tempo, gen_perf.tempo) > 0 else 0
    
    # Chấm điểm Pause (Chênh lệch % ngắt nghỉ)
    pause_diff = abs(ref_perf.pause_ratio - gen_perf.pause_ratio)
    pause_score = max(0, (1.0 - pause_diff)) * 100
    
    print("\n" + "="*50)
    print(" 📊 KẾT QUẢ BENCHMARK F5-TTS (GIAI ĐOẠN 1)")
    print("="*50)
    print(f"  🎵 Pitch (Cao độ)  : {pitch_score:5.2f}% (Khả năng lên xuống giọng)")
    print(f"  🔊 Energy(Cường độ): {energy_score:5.2f}% (Khả năng gào/thì thầm)")
    print(f"  ⏱️ Tempo (Nhịp độ) : {tempo_score:5.2f}% ({ref_perf.tempo:.0f} vs {gen_perf.tempo:.0f} BPM)")
    print(f"  ⏸️ Pause (Ngắt nghỉ): {pause_score:5.2f}% ({ref_perf.pause_ratio*100:.0f}% vs {gen_perf.pause_ratio*100:.0f}%)")
    print("="*50)
    
    return {
        "pitch": pitch_score,
        "energy": energy_score,
        "tempo": tempo_score,
        "pause": pause_score
    }

if __name__ == '__main__':
    if len(sys.argv) == 3:
        benchmark_f5(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python performance_extractor.py <file_mau_trung.wav> <file_f5_viet.wav>")
        print("Bạn có thể import hàm benchmark_f5(ref, gen) vào Colab để tự động đo lường hàng loạt.")
