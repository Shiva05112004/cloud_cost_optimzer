from unittest.mock import patch
from app.routes.resources import get_costs


def test_get_costs_missing_role_arn():
    """Test that get_costs raises HTTPException when role_arn is missing."""
    from fastapi import HTTPException
    
    try:
        get_costs(role_arn=None)
        assert False, "Expected HTTPException to be raised"
    except HTTPException as e:
        assert e.status_code == 422
        assert "role_arn query parameter is required" in e.detail


def test_get_costs_with_empty_role_arn():
    """Test that get_costs raises HTTPException when role_arn is empty string."""
    from fastapi import HTTPException
    
    try:
        get_costs(role_arn="")
        assert False, "Expected HTTPException to be raised"
    except HTTPException as e:
        assert e.status_code == 422
        assert "role_arn query parameter is required" in e.detail


def test_get_costs_with_aws_error():
    """Test that get_costs raises HTTPException when AWS API fails."""
    from fastapi import HTTPException
    from botocore.exceptions import NoCredentialsError
    
    with patch("app.routes.resources.get_monthly_cost") as mock_get_monthly_cost:
        mock_get_monthly_cost.side_effect = ValueError("AWS credentials not found. Please configure valid AWS credentials.")
        
        try:
            get_costs(role_arn="arn:aws:iam::123456789012:role/test")
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == 400
            assert "AWS credentials not found" in e.detail
