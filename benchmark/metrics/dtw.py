import librosa
import numpy as np

def calculate_dtw_similarity(seq1, seq2):
    """
    Tính khoảng cách DTW và quy đổi về điểm số tương quan [0, 1].
    """
    # Chuyển thành dạng ma trận (1, N) cho librosa
    seq1 = np.array(seq1).reshape(1, -1)
    seq2 = np.array(seq2).reshape(1, -1)
    
    # Tính DTW
    D, wp = librosa.sequence.dtw(seq1, seq2)
    
    # D[-1, -1] là tổng khoảng cách tích lũy (accumulated distance)
    distance = D[-1, -1]
    path_len = len(wp)
    
    if path_len == 0:
        return 0.0
        
    norm_distance = distance / path_len
    
    # Hàm mũ suy giảm để đổi khoảng cách thành điểm số.
    # norm_distance càng nhỏ -> Điểm càng gần 1. 
    # Số chia 2.0 có thể tinh chỉnh sau này để giãn cách điểm số.
    similarity = np.exp(-norm_distance / 2.0)
    
    return float(similarity)
