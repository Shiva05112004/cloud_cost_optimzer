from app.cloud_api.ec2_client import list_ec2_instances
from app.cloud_api.cloudwatch_client import get_avg_cpu
from app.ml.rightsizer import suggest_rightsizing
from typing import Optional, List


def priority_score(savings: float, confidence: float, risk: str) -> float:
    """
    Ranks recommendations. Higher = show first.
    Formula: (savings × confidence) − risk_penalty
    """
    risk_penalty = {"low": 0, "medium": 10, "high": 25, "none": 0}
    return round((savings * confidence) - risk_penalty.get(risk, 0), 2)


def run_optimization(role_arn: Optional[str] = None) -> List[dict]:
    """
    Full pipeline:
    1. Fetch EC2 instances
    2. Get CPU metrics from CloudWatch
    3. Run rightsizing ML logic
    4. Rank by priority score
    """
    instances = list_ec2_instances(role_arn)
    recommendations = []

    for inst in instances:
        if inst["state"] != "running":
            continue

        avg_cpu = get_avg_cpu(inst["instance_id"], days=7, role_arn=role_arn)
        rec = suggest_rightsizing(inst["instance_id"], inst["instance_type"], avg_cpu)

        if rec["action"] != "No action needed":
            rec["priority_score"] = priority_score(
                rec["estimated_savings"],
                rec["confidence"],
                rec["risk"],
            )
            recommendations.append(rec)

    return sorted(recommendations, key=lambda r: r["priority_score"], reverse=True)