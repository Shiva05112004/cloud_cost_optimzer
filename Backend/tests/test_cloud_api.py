from unittest.mock import patch, MagicMock
from app.cloud_api.ec2_client import list_ec2_instances
from app.cloud_api.cloudwatch_client import get_avg_cpu


MOCK_EC2_RESPONSE = {
    "Reservations": [{
        "Instances": [{
            "InstanceId": "i-0abc123",
            "InstanceType": "t3.medium",
            "State": {"Name": "running"},
            "LaunchTime": "2024-01-01T00:00:00Z",
        }]
    }]
}


def test_list_ec2_instances():
    with patch("boto3.Session") as mock_session:
        mock_ec2 = MagicMock()
        mock_ec2.describe_instances.return_value = MOCK_EC2_RESPONSE
        mock_session.return_value.client.return_value = mock_ec2

        instances = list_ec2_instances()
        assert len(instances) == 1
        assert instances[0]["instance_id"] == "i-0abc123"


def test_get_avg_cpu_no_data():
    with patch("boto3.Session") as mock_session:
        mock_cw = MagicMock()
        mock_cw.get_metric_statistics.return_value = {"Datapoints": []}
        mock_session.return_value.client.return_value = mock_cw

        result = get_avg_cpu("i-0abc123")
        assert result == 0.0