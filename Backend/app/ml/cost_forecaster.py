import numpy as np
from typing import List


def linear_forecast(costs: List[float], periods_ahead: int = 1) -> dict:
    """
    Forecasts future cost using simple linear regression.

    Args:
        costs: historical cost values ordered by time
        periods_ahead: how many future periods to forecast

    Returns:
        dict with slope, intercept, and predicted values
    """
    if len(costs) < 2:
        return {"error": "Need at least 2 data points"}

    x = np.arange(len(costs), dtype=float)
    y = np.array(costs, dtype=float)

    # Least squares: y = mx + b
    m, b = np.polyfit(x, y, 1)

    predictions = []
    for i in range(1, periods_ahead + 1):
        future_x = len(costs) - 1 + i
        predicted = m * future_x + b
        predictions.append(round(max(predicted, 0), 2))

    return {
        "slope": round(float(m), 4),
        "intercept": round(float(b), 4),
        "forecast": predictions,
        "trend": "increasing" if m > 0 else "decreasing",
    }