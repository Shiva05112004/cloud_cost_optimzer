from app.ml.rightsizer import suggest_rightsizing
from app.ml.cost_forecast import linear_forecast
from app.ml.anomaly_detection import z_score_anomaly


def generate_recommendations(instances, cost_trend):

    recommendations = []

    total_savings = 0

    # ------------------------
    # Rightsizing
    # ------------------------

    for inst in instances:

        rec = suggest_rightsizing(
            inst["instance_id"],
            inst["instance_type"],
            inst["avg_cpu"]
        )

        if rec["estimated_savings"] > 0:
            recommendations.append(rec)
            total_savings += rec["estimated_savings"]

    # ------------------------
    # Forecast
    # ------------------------

    costs = [x["cost"] for x in cost_trend]

    forecast = linear_forecast(costs, 1)

    anomaly = z_score_anomaly(costs)

    return {

        "recommendations": recommendations,

        "forecast": forecast,

        "anomaly": anomaly,

        "total_potential_savings": round(total_savings,2)

    }