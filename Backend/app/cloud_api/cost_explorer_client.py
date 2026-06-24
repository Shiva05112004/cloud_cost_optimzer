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


<<<<<<< HEAD






# def get_monthly_cost(role_arn: Optional[str] = None) -> dict:
#     """
#     Returns total AWS cost for the current month broken down by service.
#     Uses the Cost Explorer API (us-east-1 only — AWS requirement).
#     """
#     session = get_boto3_session(role_arn)
#     ce = session.client("ce", region_name="us-east-1")

#     today = datetime.utcnow().date()
#     first_of_month = today.replace(day=1)

#     response = ce.get_cost_and_usage(
#         TimePeriod={
#             "Start": str(first_of_month),
#             "End": str(today),
#         },
#         Granularity="MONTHLY",
#         Metrics=["UnblendedCost"],
#         GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
#     )

#     print(f"DEBUG: Cost Explorer response: {response}")  # ← Add this
    
#     results = {}
#     for group in response.get("ResultsByTime", [{}])[0].get("Groups", []):
#         service = group["Keys"][0]
#         amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
#         results[service] = round(amount, 4)

#     print(f"DEBUG: Parsed costs: {results}")  # ← Add this
#     return results
=======
def get_daily_cost_history(role_arn: Optional[str] = None, days: int = 30) -> dict:
    """Return a mapping of date (YYYY-MM-DD) -> total cost for the last `days` days.

    Uses Cost Explorer with DAILY granularity.
    """
    session = get_boto3_session(role_arn)
    ce = session.client("ce", region_name="us-east-1")

    today = datetime.utcnow().date()
    start = today - timedelta(days=days - 1)

    response = ce.get_cost_and_usage(
        TimePeriod={"Start": str(start), "End": str(today)},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
    )

    results = {}
    for row in response.get("ResultsByTime", []):
        day = row.get("TimePeriod", {}).get("Start")
        amount = 0.0
        for grp in row.get("Groups", []) or []:
            # if grouped by service, sum groups; otherwise look at Total
            try:
                amount += float(grp["Metrics"]["UnblendedCost"]["Amount"])  # type: ignore
            except Exception:
                pass

        if amount == 0.0:
            # fallback to Total if present
            try:
                amount = float(row.get("Total", {}).get("UnblendedCost", {}).get("Amount", 0.0))
            except Exception:
                amount = 0.0

        results[day] = round(amount, 4)

    return results
>>>>>>> 922b580a6d45d3a25797d6e2a9dd655eacbf6e28
