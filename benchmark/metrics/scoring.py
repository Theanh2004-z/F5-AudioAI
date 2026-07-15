def calculate_overall_score(pitch_score, energy_score, tempo_score, pause_score):
    """
    Calculate the overall score based on the Architect's specification:
    Pitch: 30%, Energy: 30%, Tempo: 20%, Pause: 20%
    """
    return (pitch_score * 0.30) + (energy_score * 0.30) + (tempo_score * 0.20) + (pause_score * 0.20)
