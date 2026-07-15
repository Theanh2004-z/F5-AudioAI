import numpy as np

def calculate_pearson_similarity(seq1, seq2):
    """
    Calculate Pearson Correlation between 2 sequences.
    Returns value in range [0, 1].
    Linearly interpolates to match length if necessary.
    """
    seq1 = np.array(seq1)
    seq2 = np.array(seq2)
    
    # Linearly interpolate to match length (as requested by previous architecture design to enable Pearson without DTW)
    if len(seq1) != len(seq2):
        x_old = np.linspace(0, 1, len(seq2))
        x_new = np.linspace(0, 1, len(seq1))
        seq2 = np.interp(x_new, x_old, seq2)
        
    if np.std(seq1) == 0 or np.std(seq2) == 0:
        return 0.0
        
    corr = np.corrcoef(seq1, seq2)[0, 1]
    
    # Clip negative values
    return float(max(0.0, corr))
