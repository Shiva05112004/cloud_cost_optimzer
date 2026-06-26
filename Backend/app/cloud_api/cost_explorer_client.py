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
    sts = session.client("sts")
    print(sts.get_caller_identity())
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
    print("Raw Cost Explorer response:")
    print(response)
    
    results = {}
    for group in response.get("ResultsByTime", [{}])[0].get("Groups", []):
        service = group["Keys"][0]
        amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
        results[service] = round(amount, 4)

    return results


# def get_cost_trend(role_arn: Optional[str] = None) -> list[dict]:
#     """Return a simple 6-month cost trend series for the dashboard."""
#     costs = get_monthly_cost(role_arn)
#     total = round(sum(costs.values()), 2)
#     trend = []

#     for month_index in range(6):
#         month_date = datetime.utcnow().replace(day=1) - timedelta(days=30 * month_index)
#         trend.append({
#             "month": month_date.strftime("%b"),
#             "cost": round(total / max(1, len(costs)), 2),
#         })
from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_cost_trend(role_arn=None):
    session = get_boto3_session(role_arn)
    ce = session.client("ce", region_name="us-east-1")

    end = datetime.utcnow().date().replace(day=1) + relativedelta(months=1)
    start = end - relativedelta(months=6)

    response = ce.get_cost_and_usage(
        TimePeriod={
            "Start": str(start),
            "End": str(end),
        },
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"]
    )

    trend = []

    for item in response["ResultsByTime"]:
        trend.append({
            "month": datetime.strptime(
                item["TimePeriod"]["Start"],
                "%Y-%m-%d"
            ).strftime("%b"),
            "cost": float(
                item["Total"]["UnblendedCost"]["Amount"]
            ),
        })

    return trend

    #return trend








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