from typing import Optional


def priority_score(savings: float, confidence: float, risk: str) -> float:
    """
    Ranks recommendations. Higher = show first.
    Formula: (savings x confidence) - risk_penalty
    """
    risk_penalty = {"low": 0, "medium": 10, "high": 25, "none": 0}
    return round((savings * confidence) - risk_penalty.get(risk, 0), 2)
