from app.ml.anomaly_detector import z_score_anomaly
from app.ml.cost_forecaster import linear_forecast
from app.ml.rightsizer import suggest_rightsizing


def test_anomaly_detected():
    costs = [100, 102, 99, 101, 98, 300]   # last value is a spike
    result = z_score_anomaly(costs)
    assert result["is_anomaly"] is True


def test_no_anomaly():
    costs = [100, 102, 99, 101, 98, 100]
    result = z_score_anomaly(costs)
    assert result["is_anomaly"] is False


def test_forecast_trend():
    costs = [100, 120, 140, 160]
    result = linear_forecast(costs, periods_ahead=2)
    assert result["trend"] == "increasing"
    assert len(result["forecast"]) == 2


def test_rightsizer_idle():
    rec = suggest_rightsizing("i-test", "t3.large", avg_cpu=4.5)
    assert rec["action"] == "Stop instance"
    assert rec["estimated_savings"] > 0


def test_rightsizer_healthy():
    rec = suggest_rightsizing("i-test", "t3.large", avg_cpu=55.0)
    assert rec["action"] == "No action needed"