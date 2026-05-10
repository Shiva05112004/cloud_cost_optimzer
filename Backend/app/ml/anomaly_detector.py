import numpy as np
from typing import List


def z_score_anomaly(costs: List[float], threshold: float = 2.0) -> dict:
    """
    Detects if the latest cost value is an anomaly using Z-score.

    Args:
        costs: list of daily/monthly cost values (most recent last)
        threshold: z-score cutoff (2.0 = ~95% confidence)

    Returns:
        dict with is_anomaly flag, z_score, and message
    """
    if len(costs) < 3:
        return {"is_anomaly": False, "z_score": 0.0, "message": "Not enough data"}

    history = np.array(costs[:-1])
    current = costs[-1]

    mu = float(np.mean(history))
    sigma = float(np.std(history))

    if sigma == 0:
        return {"is_anomaly": False, "z_score": 0.0, "message": "No variance in history"}

    z = (current - mu) / sigma

    return {
        "is_anomaly": abs(z) > threshold,
        "z_score": round(z, 3),
        "current": current,
        "mean": round(mu, 2),
        "message": f"Cost spike detected (z={z:.2f})" if abs(z) > threshold else "Normal",
    }