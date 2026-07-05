import boto3
from datetime import datetime, timedelta
from typing import Optional
from app.config import get_settings

settings = get_settings()


def get_boto3_session(role_arn: Optional[str] = None):
    """
    Returns a boto3 session.
    - If role_arn is provided: assumes that IAM role (production flow)
    - Otherwise: uses env credentials (local dev only)
    """
    if role_arn:
        sts = boto3.client(
            "sts",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_default_region,
        )
        assumed = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName="cloud-optimizer-session",
        )
        creds = assumed["Credentials"]
        session = boto3.Session(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
            region_name=settings.aws_default_region,
        )
    else:
        session = boto3.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_default_region,
        )
    return session


def list_ec2_instances(role_arn: Optional[str] = None) -> list:
    """
    Fetches all EC2 instances from the user's AWS account.
    Returns a flat list of instance dicts.
    """
    session = get_boto3_session(role_arn)
    ec2 = session.client("ec2")

    response = ec2.describe_instances()
    instances = []

    for reservation in response.get("Reservations", []):
        for inst in reservation.get("Instances", []):
            instances.append({
                "instance_id": inst["InstanceId"],
                "instance_type": inst["InstanceType"],
                "state": inst["State"]["Name"],
                "launch_time": str(inst.get("LaunchTime", "")),
                "region": settings.aws_default_region,
            })

    return instances


def get_avg_cpu(instance_id: str, days: int = 7, role_arn: Optional[str] = None) -> float:
    """
    Returns the average CPU utilization for an EC2 instance over the past `days` days.
    """
    session = get_boto3_session(role_arn)
    cloudwatch = session.client("cloudwatch")

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=["Average"],
        Unit="Percent",
    )

    datapoints = response.get("Datapoints", [])
    if not datapoints:
        return 0.0

    avg_cpu = sum(point["Average"] for point in datapoints) / len(datapoints)
    return round(avg_cpu, 2)
