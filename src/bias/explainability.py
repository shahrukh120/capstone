"""
Explainability module: provides SHAP-based explanations for match scores.

Uses feature importance to explain why a candidate scored high/low for a role.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Any

import numpy as np

logger = logging.getLogger(__name__)


def explain_match_score(
    candidate: Dict[str, Any],
    job: Dict[str, Any],
    match_score: float,
) -> Dict[str, Any]:
    """
    Generate a feature-level explanation for a candidate's match score.

    Uses heuristic feature decomposition (since the underlying model is an
    embedding similarity, we approximate feature importance by measuring
    overlap between candidate attributes and job requirements).
    """
    explanations = []

    # 1. Skills overlap
    candidate_skills = set(s.lower() for s in candidate.get("skills", []))
    job_requirements = set()
    for req in job.get("requirements", []):
        job_requirements.update(w.lower() for w in req.split() if len(w) > 3)
    job_desc_words = set(w.lower() for w in job.get("description", "").split() if len(w) > 3)

    skill_overlap = candidate_skills & (job_requirements | job_desc_words)
    skill_score = len(skill_overlap) / max(len(candidate_skills), 1)
    explanations.append({
        "feature": "skills_match",
        "importance": round(skill_score * 0.4, 4),  # 40% weight
        "detail": f"Matched {len(skill_overlap)} skills: {', '.join(list(skill_overlap)[:10])}",
        "direction": "positive" if skill_overlap else "neutral",
    })

    # 2. Experience match
    candidate_years = candidate.get("total_years_experience") or 0
    required_years = job.get("min_experience_years", 0)
    if required_years > 0:
        exp_ratio = min(candidate_years / required_years, 2.0) / 2.0
    else:
        exp_ratio = 0.5
    explanations.append({
        "feature": "experience_match",
        "importance": round(exp_ratio * 0.3, 4),  # 30% weight
        "detail": f"Candidate has {candidate_years} years, job requires {required_years}+ years",
        "direction": "positive" if candidate_years >= required_years else "negative",
    })

    # 3. Education match
    edu_keywords = {"bachelor", "master", "phd", "mba", "degree", "bs", "ms", "ba", "ma"}
    candidate_edu = " ".join(
        e.get("degree", "").lower() for e in candidate.get("education", [])
    )
    has_degree = any(kw in candidate_edu for kw in edu_keywords)
    edu_score = 0.8 if has_degree else 0.2
    explanations.append({
        "feature": "education_match",
        "importance": round(edu_score * 0.15, 4),  # 15% weight
        "detail": f"{'Has relevant degree' if has_degree else 'No degree detected'}",
        "direction": "positive" if has_degree else "neutral",
    })

    # 4. Category relevance
    category = candidate.get("category", "").lower()
    job_title = job.get("title", "").lower()
    job_dept = job.get("department", "").lower()
    category_match = (
        category in job_title
        or category in job_dept
        or job_dept in category
    )
    cat_score = 0.9 if category_match else 0.3
    explanations.append({
        "feature": "category_relevance",
        "importance": round(cat_score * 0.15, 4),  # 15% weight
        "detail": f"Candidate category '{candidate.get('category')}' {'matches' if category_match else 'does not match'} job department",
        "direction": "positive" if category_match else "negative",
    })

    # Compute approximate explained score
    total_importance = sum(e["importance"] for e in explanations)

    return {
        "match_score": match_score,
        "explained_score": round(total_importance, 4),
        "explanations": sorted(explanations, key=lambda x: x["importance"], reverse=True),
        "top_positive_factors": [
            e["detail"] for e in explanations if e["direction"] == "positive"
        ],
        "top_negative_factors": [
            e["detail"] for e in explanations if e["direction"] == "negative"
        ],
    }
