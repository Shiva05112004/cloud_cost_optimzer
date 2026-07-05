from unittest.mock import patch, MagicMock
from app.cloud_api.ec2_client import list_ec2_instances
from app.cloud_api.cloudwatch_client import get_avg_cpu
from app.cloud_api.cost_explorer_client import get_monthly_cost
from botocore.exceptions import NoCredentialsError, ClientError


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


def test_get_monthly_cost_no_credentials():
    """Test that get_monthly_cost raises ValueError when AWS credentials are missing."""
    with patch("app.cloud_api.cost_explorer_client.get_boto3_session") as mock_get_session:
        mock_session = MagicMock()
        mock_ce = MagicMock()
        mock_ce.get_cost_and_usage.side_effect = NoCredentialsError()
        mock_session.client.return_value = mock_ce
        mock_get_session.return_value = mock_session

        try:
            get_monthly_cost("arn:aws:iam::123456789012:role/test-role")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "AWS credentials not found" in str(e)


def test_get_monthly_cost_client_error():
    """Test that get_monthly_cost raises ValueError when AWS API returns an error."""
    with patch("app.cloud_api.cost_explorer_client.get_boto3_session") as mock_get_session:
        mock_session = MagicMock()
        mock_ce = MagicMock()
        error_response = {"Error": {"Message": "Access Denied"}}
        mock_ce.get_cost_and_usage.side_effect = ClientError(error_response, "GetCostAndUsage")
        mock_session.client.return_value = mock_ce
        mock_get_session.return_value = mock_session

        try:
            get_monthly_cost("arn:aws:iam::123456789012:role/test-role")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "AWS API error" in str(e)
            assert "Access Denied" in str(e)