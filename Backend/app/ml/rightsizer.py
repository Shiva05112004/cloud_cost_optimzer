# Instance type pricing (USD/hour) — simplified AWS on-demand (ap-south-1)
INSTANCE_PRICING = {
    "t3.nano":   0.0052,
    "t3.micro":  0.0104,
    "t3.small":  0.0208,
    "t3.medium": 0.0416,
    "t3.large":  0.0832,
    "t3.xlarge": 0.1664,
    "t3.2xlarge":0.3328,
}

DOWNGRADE_MAP = {
    "t3.2xlarge": "t3.xlarge",
    "t3.xlarge":  "t3.large",
    "t3.large":   "t3.medium",
    "t3.medium":  "t3.small",
    "t3.small":   "t3.micro",
    "t3.micro":   "t3.nano",
}


def suggest_rightsizing(instance_id: str, instance_type: str, avg_cpu: float) -> dict:
    """
    Recommends a smaller instance type if CPU is consistently low.

    Logic:
    - CPU < 10% → idle, suggest stop
    - CPU < 20% → overprovisioned, suggest downgrade
    - CPU >= 20% → healthy, no action

    Returns a recommendation dict with estimated monthly savings.
    """
    current_rate = INSTANCE_PRICING.get(instance_type, 0.0)
    monthly_hours = 720  # 30 days × 24 hours
    current_monthly = round(current_rate * monthly_hours, 2)

    if avg_cpu < 10:
        return {
            "instance_id": instance_id,
            "issue": f"Idle — avg CPU {avg_cpu}% over 7 days",
            "action": "Stop instance",
            "current_cost": current_monthly,
            "recommended_type": None,
            "estimated_savings": current_monthly,
            "confidence": 0.92,
            "risk": "low",
        }

    if avg_cpu < 20 and instance_type in DOWNGRADE_MAP:
        new_type = DOWNGRADE_MAP[instance_type]
        new_rate = INSTANCE_PRICING.get(new_type, current_rate)
        new_monthly = round(new_rate * monthly_hours, 2)
        savings = round(current_monthly - new_monthly, 2)

        return {
            "instance_id": instance_id,
            "issue": f"Over-provisioned — avg CPU {avg_cpu}%",
            "action": f"Downgrade to {new_type}",
            "current_cost": current_monthly,
            "recommended_type": new_type,
            "estimated_savings": savings,
            "confidence": 0.80,
            "risk": "medium",
        }

    return {
        "instance_id": instance_id,
        "issue": "Healthy",
        "action": "No action needed",
        "current_cost": current_monthly,
        "recommended_type": None,
        "estimated_savings": 0.0,
        "confidence": 1.0,
        "risk": "none",
    }