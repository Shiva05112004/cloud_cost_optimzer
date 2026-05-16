import boto3
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
        sts = boto3.client("sts", region_name=settings.aws_default_region)
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
        session = boto3.Session(region_name=settings.aws_default_region)
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