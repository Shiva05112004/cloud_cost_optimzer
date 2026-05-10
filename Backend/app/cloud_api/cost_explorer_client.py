import boto3
from datetime import datetime, timedelta
from typing import Optional
from app.cloud_api.ec2_client import get_boto3_session


def get_monthly_cost(role_arn: Optional[str] = None) -> dict:
    """
    Returns total AWS cost for the current month broken down by service.
    Uses the Cost Explorer API (us-east-1 only — AWS requirement).
    """
    session = get_boto3_session(role_arn)
    ce = session.client("ce", region_name="us-east-1")

    today = datetime.utcnow().date()
    first_of_month = today.replace(day=1)

    response = ce.get_cost_and_usage(
        TimePeriod={
            "Start": str(first_of_month),
            "End": str(today),
        },
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    results = {}
    for group in response.get("ResultsByTime", [{}])[0].get("Groups", []):
        service = group["Keys"][0]
        amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
        results[service] = round(amount, 4)

    return results