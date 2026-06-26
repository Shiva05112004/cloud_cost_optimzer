# import random
# from app.cloud_api.ec2_client import list_ec2_instances
# from app.cloud_api.cloudwatch_client import get_avg_cpu
# from app.ml.rightsizer import suggest_rightsizing
# from typing import Optional, List


# def priority_score(savings: float, confidence: float, risk: str) -> float:
#     """
#     Ranks recommendations. Higher = show first.
#     Formula: (savings × confidence) − risk_penalty
#     """
#     risk_penalty = {"low": 0, "medium": 10, "high": 25, "none": 0}
#     return round((savings * confidence) - risk_penalty.get(risk, 0), 2)

# def extract_instance_name(instance_data: dict) -> str:
#     """Parses AWS Boto3 response tags to fetch the actual instance name."""
#     tags = instance_data.get("Tags", []) if instance_data else []
#     for tag in tags:
#         if tag.get("Key") == "Name":
#             return tag.get("Value")
#     return "Unnamed Instance"

# def calculate_true_confidence(avg_cpu: float) -> float:
#     """
#     Calculates a reliable metric score instead of a random number.
#     Lower CPU means we are much more certain the instance is idle waste.
#     """
#     if avg_cpu < 5.0:
#         return 0.95  # 95% confident it's safe to terminate or stop
#     elif avg_cpu < 10.0:
#         return 0.85  # 85% confident
#     elif avg_cpu < 15.0:
#         return 0.70  # 70% confident
#     else:
#         return 0.40 

# def run_optimization(role_arn: Optional[str] = None) -> List[dict]:
#     """
#     Full pipeline:
#     1. Fetch EC2 instances
#     2. Get CPU metrics from CloudWatch
#     3. Run rightsizing ML logic
#     4. Rank by priority score
#     """
#     instances = list_ec2_instances(role_arn)
#     recommendations = []

#     for inst in instances:
#         if inst["state"] != "running":
#             continue

#         avg_cpu = get_avg_cpu(inst["instance_id"], days=7, role_arn=role_arn)
#         rec = suggest_rightsizing(inst["instance_id"], inst["instance_type"], avg_cpu)

#         if rec["action"] != "No action needed":
#             rec["priority_score"] = priority_score(
#                 rec["estimated_savings"],
#                 rec["confidence"],
#                 rec["risk"],
#             )
#             recommendations.append(rec)

#     return sorted(recommendations, key=lambda r: r["priority_score"], reverse=True)


import random  # Maintained for fallback safety, but not used for metrics
from typing import Optional, List
from app.cloud_api.ec2_client import list_ec2_instances
from app.cloud_api.cloudwatch_client import get_avg_cpu
from app.ml.rightsizer import suggest_rightsizing


# ─── CORE MATHEMATICAL UTILITIES ────────────────────────
def priority_score(savings: float, confidence: float, risk: str) -> float:
    """
    Ranks recommendations. Higher scores are prioritized for display.
    Formula: (savings × confidence) − risk_penalty
    """
    risk_penalty = {"low": 0, "medium": 10, "high": 25, "none": 0}
    return round((savings * confidence) - risk_penalty.get(risk, 0), 2)


def extract_instance_name(instance_data: dict) -> str:
    """Parses AWS Boto3 response tags to fetch the actual instance name."""
    tags = instance_data.get("Tags", []) if instance_data else []
    for tag in tags:
        if tag.get("Key") == "Name":
            return tag.get("Value")
    return "Unnamed Instance"


def calculate_true_confidence(avg_cpu: float) -> float:
    """
    Calculates a reliable metric score instead of a random number.
    Lower CPU means higher certainty that the instance is idle waste.
    """
    if avg_cpu < 5.0:
        return 0.95  # 95% confident it's safe to modify/stop
    elif avg_cpu < 10.0:
        return 0.85  # 85% confident
    elif avg_cpu < 15.0:
        return 0.70  # 70% confident
    else:
        return 0.40  # Low confidence, resource is actively performing tasks


# ─── LIVE METRICS PIPELINE ──────────────────────────────
def run_optimization(role_arn: Optional[str] = None) -> List[dict]:
    """
    Full live pipeline:
    1. Fetch real active EC2 instances from AWS
    2. Get actual CPU metrics from CloudWatch
    3. Run rightsizing ML logic
    4. Rank by priority score
    """
    instances = list_ec2_instances(role_arn)
    recommendations = []

    for inst in instances:
        if inst.get("state") != "running":
            continue

        # Fetch actual real-time CPU percentages over the last 7 days
        avg_cpu = get_avg_cpu(inst["instance_id"], days=7, role_arn=role_arn)
        
        # Calculate grounding metrics
        calculated_confidence = calculate_true_confidence(avg_cpu)
        real_name = extract_instance_name(inst)

        # Run optimization analysis
        rec = suggest_rightsizing(inst["instance_id"], inst["instance_type"], avg_cpu)

        if rec["action"] != "No action needed":
            # Override any mock data with real calculated confidence and instance name metadata
            rec["instance_name"] = real_name
            rec["confidence"] = calculated_confidence
            rec["priority_score"] = priority_score(
                rec["estimated_savings"],
                rec["confidence"],
                rec["risk"],
            )
            recommendations.append(rec)

    return sorted(recommendations, key=lambda r: r["priority_score"], reverse=True)


# ─── LOCAL FALLBACK DASHBOARD DATA ──────────────────────
def get_cloud_resources() -> list:
    """
    Generates predictable, structured cloud data with real logic
    to use when a live AWS client session is not active.
    """
    # Raw infrastructure data architecture mirroring Boto3 API outputs
    raw_aws_instances = [
        {
            "InstanceId": "i-09f1a23bc45de678f", 
            "InstanceType": "t3.medium", 
            "AvgCpu": 3.4,  
            "Tags": [{"Key": "Name", "Value": "Production-Web-Server"}]
        },
        {
            "InstanceId": "i-07b6c54da32ef111a", 
            "InstanceType": "m5.large", 
            "AvgCpu": 8.2,  
            "Tags": [{"Key": "Name", "Value": "Staging-Database"}]
        },
        {
            "InstanceId": "i-01a2b3c4d5e6f7g8h", 
            "InstanceType": "t2.micro", 
            "AvgCpu": 45.1, 
            "Tags": []  # Missing explicit name tag metadata
        }
    ]
    
    formatted_instances = []
    
    for inst in raw_aws_instances:
        real_name = extract_instance_name(inst)
        cpu_value = inst["AvgCpu"]
        calculated_confidence = calculate_true_confidence(cpu_value)
        
        instance_dict = {
            "instance_id": inst["InstanceId"],
            "instance_name": real_name,       
            "instance_type": inst["InstanceType"],
            "state": "running",
            "avg_cpu": cpu_value,             
            "confidence_score": calculated_confidence,  
            "region": "ap-south-1",
            "launch_time": "2026-06-26T10:00:00Z"
        }
        formatted_instances.append(instance_dict)
        
    return formatted_instances
