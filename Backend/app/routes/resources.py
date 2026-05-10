from fastapi import APIRouter, Query
from typing import Optional
from app.cloud_api.ec2_client import list_ec2_instances
from app.cloud_api.cloudwatch_client import get_avg_cpu
from app.cloud_api.cost_explorer_client import get_monthly_cost

router = APIRouter()


@router.get("/ec2")
def get_ec2(role_arn: Optional[str] = Query(None)):
    instances = list_ec2_instances(role_arn)
    for inst in instances:
        inst["avg_cpu"] = get_avg_cpu(inst["instance_id"], role_arn=role_arn)
    return {"instances": instances}


@router.get("/costs")
def get_costs(role_arn: Optional[str] = Query(None)):
    costs = get_monthly_cost(role_arn)
    total = round(sum(costs.values()), 2)
    return {"total_usd": total, "by_service": costs}