"""
Demo script to test the Cloud Cost Optimizer API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("Cloud Cost Optimizer API Demo")
print("=" * 80)
print()

# Test 1: Health Check
print("1. Health Check")
print("-" * 40)
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 2: Register User
print("2. Register New User")
print("-" * 40)
try:
    user_data = {
        "email": "demo@example.com",
        "password": "demo123",
        "full_name": "Demo User"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 3: Login
print("3. Login")
print("-" * 40)
try:
    login_data = {
        "username": "demo@example.com",
        "password": "demo123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    print(f"Status: {response.status_code}")
    login_response = response.json()
    print(f"Response: {json.dumps(login_response, indent=2)}")
    
    if "access_token" in login_response:
        token = login_response["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Token obtained: {token[:50]}...")
    else:
        print("No token obtained")
        headers = {}
except Exception as e:
    print(f"Error: {e}")
    headers = {}
print()

# Test 4: Get Cloud Accounts
print("4. Get Cloud Accounts")
print("-" * 40)
try:
    response = requests.get(f"{BASE_URL}/api/accounts", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        accounts = response.json()
        print(f"Found {len(accounts)} accounts")
        for account in accounts[:3]:
            print(f"  - {account['account_name']} ({account['provider']})")
    else:
        print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 5: Get EC2 Instances (with direct credentials, no role_arn)
print("5. Get EC2 Instances (Direct AWS Credentials)")
print("-" * 40)
try:
    response = requests.get(f"{BASE_URL}/api/resources/ec2", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        instances = response.json()
        print(f"Found {len(instances['instances'])} instances")
        for inst in instances['instances'][:3]:
            print(f"  - {inst['instance_id']}: {inst['instance_type']} ({inst['state']})")
    else:
        print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 6: Get Monthly Costs
print("6. Get Monthly Costs")
print("-" * 40)
try:
    response = requests.get(f"{BASE_URL}/api/resources/costs", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        costs = response.json()
        print(f"Total Cost: ${costs['total_usd']}")
        print("Top services:")
        for service, cost in list(costs['by_service'].items())[:3]:
            print(f"  - {service}: ${cost}")
    else:
        print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 7: Phase A ML Info
print("7. Phase A ML Model Info")
print("-" * 40)
try:
    response = requests.get(f"{BASE_URL}/api/phase_a/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
print()

# Test 8: Add Cloud Account
print("8. Add Cloud Account (Direct Credentials)")
print("-" * 40)
try:
    account_data = {
        "account_name": "Demo AWS Account",
        "role_arn": "arn:aws:iam::683872723799:role/testing_purpose"  # Using the existing role
    }
    response = requests.post(f"{BASE_URL}/api/accounts/connect", json=account_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
print()

print("=" * 80)
print("Demo Complete")
print("=" * 80)
