"""
Fairness audit: checks if any demographic group is systematically ranked lower.

Uses category as a proxy for demographic grouping (in production, use actual
demographic data). Computes selection rate parity and flags disparities.
"""
from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional

import numpy as np
from fairlearn.metrics import (
    MetricFrame,
    selection_rate,
    demographic_parity_difference,
    demographic_parity_ratio,
)

logger = logging.getLogger(__name__)


def run_fairness_audit(
    candidates: List[Dict[str, Any]],
    scores: List[float],
    group_key: str = "category",
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """
    Audit match scores for fairness across demographic groups.

    Args:
        candidates: list of candidate dicts (must contain group_key)
        scores: list of match scores (0-1) corresponding to candidates
        group_key: which field to use for group comparison
        threshold: score above which a candidate is "selected"

    Returns:
        Audit report with metrics and flagged disparities.
    """
    if not candidates or not scores:
        return {"error": "No data to audit", "is_fair": True}

    groups = np.array([c.get(group_key, "UNKNOWN") for c in candidates])
    scores_arr = np.array(scores)
    selected = (scores_arr >= threshold).astype(int)

    # Need at least 2 groups to compare
    unique_groups = np.unique(groups)
    if len(unique_groups) < 2:
        return {
            "is_fair": True,
            "message": "Only one group present, fairness comparison not applicable",
            "groups": unique_groups.tolist(),
        }

    # Compute per-group selection rates
    metric_frame = MetricFrame(
        metrics=selection_rate,
        y_true=selected,  # using selected as both true and pred for selection rate
        y_pred=selected,
        sensitive_features=groups,
    )

    group_rates = metric_frame.by_group.to_dict()
    overall_rate = float(metric_frame.overall)

    # Compute disparity metrics
    dp_difference = float(demographic_parity_difference(
        y_true=selected, y_pred=selected, sensitive_features=groups
    ))
    dp_ratio = float(demographic_parity_ratio(
        y_true=selected, y_pred=selected, sensitive_features=groups
    ))

    # Flag if disparity is concerning (4/5ths rule: ratio < 0.8 is adverse impact)
    is_fair = dp_ratio >= 0.8

    # Identify disadvantaged groups
    flagged_groups = []
    for group, rate in group_rates.items():
        if rate < overall_rate * 0.8:
            flagged_groups.append({
                "group": group,
                "selection_rate": round(rate, 4),
                "overall_rate": round(overall_rate, 4),
                "ratio_to_overall": round(rate / overall_rate if overall_rate > 0 else 0, 4),
            })

    return {
        "is_fair": is_fair,
        "threshold": threshold,
        "overall_selection_rate": round(overall_rate, 4),
        "group_selection_rates": {k: round(v, 4) for k, v in group_rates.items()},
        "demographic_parity_difference": round(dp_difference, 4),
        "demographic_parity_ratio": round(dp_ratio, 4),
        "four_fifths_rule_passed": dp_ratio >= 0.8,
        "flagged_groups": flagged_groups,
        "recommendation": (
            "No significant disparities detected."
            if is_fair
            else f"Potential adverse impact detected. Groups flagged: {[g['group'] for g in flagged_groups]}. "
                 "Review scoring criteria and consider re-calibration."
        ),
    }
