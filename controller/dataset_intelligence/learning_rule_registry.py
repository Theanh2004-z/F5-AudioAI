"""
learning_rule_registry.py
Absolute thresholds and fixed histogram bins.
"""

HISTOGRAM_BINS = [
    "0.0_0.1", "0.1_0.2", "0.2_0.3", "0.3_0.4", "0.4_0.5",
    "0.5_0.6", "0.6_0.7", "0.7_0.8", "0.8_0.9", "0.9_1.0"
]

def get_bin(value):
    if value < 0.0: return "<0.0"
    if value >= 1.0: return ">=1.0"
    idx = int(value * 10)
    if idx == 10: idx = 9
    return HISTOGRAM_BINS[idx]

def get_evidence_strength(support_count):
    if support_count < 5:
        return "VERY_LOW"
    elif support_count < 20:
        return "LOW"
    elif support_count < 50:
        return "MEDIUM"
    elif support_count < 100:
        return "HIGH"
    else:
        return "VERY_HIGH"
