"""
evidence_collector.py
Reads and consolidates evidence from three input sources:
  - observation_report.json
  - confidence_report.json
  - normalized_feature_difference.json

For each registered feature, produces a single "evidence packet" containing
all available observational data.

Responsibility: COLLECTION ONLY.
No graph lookup. No hypothesis. No recommendation. No optimization.
"""

import math


def collect_evidence(observation_report, confidence_report, normalized_diff_report):
    """
    Consolidates observation data for every feature present across all inputs.

    Args:
        observation_report   : dict — loaded from observation_report.json
        confidence_report    : dict — loaded from confidence_report.json
        normalized_diff_report: dict — loaded from normalized_feature_difference.json

    Returns:
        evidence_map : dict[feature_name -> evidence_packet]
        warnings     : list[str]
    """
    warnings    = []
    evidence_map = {}

    # Unpack nested structures
    classifications  = observation_report.get("classifications", {})
    validation_issues = observation_report.get("validation_issues", [])
    conf_data        = confidence_report.get("confidence_report", {})
    norm_diffs       = normalized_diff_report.get("normalized_feature_difference", {})

    # Build a fast lookup for validation issues by feature
    issue_lookup = {}
    for issue in validation_issues:
        fname = issue.get("feature")
        if fname:
            issue_lookup.setdefault(fname, []).append(issue)

    # Collect all feature names across all sources
    all_features = set(classifications) | set(conf_data) | set(norm_diffs)

    for feature in sorted(all_features):

        # Quality classification (ref and gen)
        qual = classifications.get(feature, {})
        ref_quality = qual.get("ref", "MISSING")
        gen_quality = qual.get("gen", "MISSING")

        # Confidence scores
        conf = conf_data.get(feature, {})
        ref_conf = conf.get("ref_confidence", 0.0)
        gen_conf = conf.get("gen_confidence", 0.0)

        # Normalized difference
        norm = norm_diffs.get(feature, {})
        normalized_difference = norm.get("normalized_difference", None)
        raw_difference        = norm.get("raw_difference", None)
        norm_status           = norm.get("status", "UNREGISTERED")

        # Observation strength: |normalized_diff| x min(ref_conf, gen_conf)
        # This quantifies "how notable is this observation AND how much do we trust it"
        if normalized_difference is not None and not math.isnan(normalized_difference):
            observation_strength = round(abs(normalized_difference) * min(ref_conf, gen_conf), 6)
        else:
            observation_strength = 0.0
            warnings.append(
                f"[{feature}] normalized_difference is None or NaN — observation_strength set to 0."
            )

        # Collect any validation issues
        issues = issue_lookup.get(feature, [])

        evidence_map[feature] = {
            "feature":               feature,
            "ref_quality":           ref_quality,
            "gen_quality":           gen_quality,
            "ref_confidence":        ref_conf,
            "gen_confidence":        gen_conf,
            "normalized_difference": normalized_difference,
            "raw_difference":        raw_difference,
            "normalization_status":  norm_status,
            "observation_strength":  observation_strength,
            "validation_issues":     issues
        }

    return evidence_map, warnings
