"""
Standalone script — run manually or via cron/scheduler.
Fetches EC2 + CPU data and prints a report.

Usage:
    python scripts/collect_metrics.py --role-arn arn:aws:iam::123:role/MyRole
"""
import argparse
from app.cloud_api.ec2_client import list_ec2_instances
from app.cloud_api.cloudwatch_client import get_avg_cpu


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--role-arn", default=None)
    args = parser.parse_args()

    print("Fetching EC2 instances...")
    instances = list_ec2_instances(args.role_arn)

    for inst in instances:
        if inst["state"] != "running":
            continue
        cpu = get_avg_cpu(inst["instance_id"], role_arn=args.role_arn)
        flag = " *** IDLE ***" if cpu < 10 else ""
        print(f"  {inst['instance_id']} | {inst['instance_type']} | CPU: {cpu}%{flag}")


if __name__ == "__main__":
    main()