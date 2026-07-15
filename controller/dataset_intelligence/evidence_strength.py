"""
evidence_strength.py
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from learning_rule_registry import get_evidence_strength

def lookup_evidence_strength(support_count):
    return get_evidence_strength(support_count)
