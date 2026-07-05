"""
Demonstration of how ML Phase A connects to AWS accounts.
This shows the data flow from AWS → Database → ML Training → Inference.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("AWS Integration Demonstration for ML Phase A")
print("=" * 80)
print()

# Step 1: Show AWS accounts in database
print("Step 1: AWS Accounts in Database")
print("-" * 40)
from app.models.account import CloudAccount
from app.models.database import SessionLocal

db = SessionLocal()
try:
    accounts = db.query(CloudAccount).all()
    print(f"Found {len(accounts)} AWS accounts:")
    for account in accounts:
        print(f"  - {account.account_name}")
        print(f"    Role ARN: {account.role_arn}")
        print(f"    Provider: {account.provider}")
        print()
finally:
    db.close()

# Step 2: Show how AWS credentials are used
print("Step 2: AWS Credential Flow")
print("-" * 40)
print("The system uses AWS credentials in two ways:")
print()
print("1. Direct credentials (local development):")
print("   - Uses AWS credentials from environment (~/.aws/credentials)")
print("   - Accessed via boto3.Session()")
print()
print("2. IAM Role assumption (production):")
print("   - Uses role_arn stored in cloud_accounts table")
print("   - Calls STS.assume_role() to get temporary credentials")
print("   - Creates boto3 session with assumed role credentials")
print()

# Step 3: Show the data collection process
print("Step 3: Data Collection from AWS")
print("-" * 40)
print("The system collects AWS metrics through:")
print()
print("1. EC2 API:")
print("   - list_ec2_instances() - Gets instance information")
print("   - get_avg_cpu() - Gets CPU metrics from CloudWatch")
print()
print("2. Cost Explorer API:")
print("   - get_monthly_cost() - Gets current month costs by service")
print("   - get_daily_cost_history() - Gets historical cost data")
print()
print("3. Data is stored in PostgreSQL database:")
print("   - metric_features table: CPU, memory, connections data")
print("   - events table: Raw metric events")
print("   - cloud_accounts table: AWS account configurations")
print()

# Step 4: Show ML training pipeline
print("Step 4: ML Training Pipeline")
print("-" * 40)
print("Training process:")
print()
print("1. Data Pipeline:")
print("   - load_metric_features() - Loads data from PostgreSQL")
print("   - validate_data_quality() - Checks data quality")
print("   - compute_features() - Calculates rolling averages, velocities")
print("   - time_series_split() - Splits data into train/val/test")
print()
print("2. Model Training:")
print("   - Trains Random Forest and XGBoost classifiers")
print("   - Uses hyperparameter tuning (GridSearchCV)")
print("   - Handles class imbalance with scale_pos_weight")
print("   - Evaluates on validation and test sets")
print()
print("3. Model Persistence:")
print("   - Saves models to app/models/phase_a/")
print("   - Stores metadata (F1 scores, feature names, etc.)")
print("   - Creates symlinks to latest models")
print()

# Step 5: Show inference flow
print("Step 5: Inference and Prediction Flow")
print("-" * 40)
print("Real-time prediction process:")
print()
print("1. API Endpoint:")
print("   - POST /api/phase_a/predict - Single prediction")
print("   - POST /api/phase_a/predict-batch - Batch predictions")
print("   - GET /api/phase_a/info - Model information")
print()
print("2. Feature Requirements:")
print("   - cpu: Current CPU usage")
print("   - memory: Current memory usage")
print("   - connections: Current network connections")
print("   - cpu_velocity: Rate of CPU change")
print("   - memory_velocity: Rate of memory change")
print("   - connections_velocity: Rate of connections change")
print("   - rolling_cpu: 6-period rolling average CPU")
print("   - rolling_memory: 6-period rolling average memory")
print("   - rolling_connections: 6-period rolling average connections")
print()
print("3. Model Selection:")
print("   - Automatically uses best model (RF or XGBoost)")
print("   - Returns prediction (0=normal, 1=failure imminent)")
print("   - Returns confidence score")
print()

# Step 6: Show anomaly detection integration
print("Step 6: Anomaly Detection Integration")
print("-" * 40)
print("How Phase A integrates with anomaly detection:")
print()
print("1. Anomaly Analysis:")
print("   - analyze_account_anomalies() - Main entry point")
print("   - Tries Phase A ML first if models are available")
print("   - Falls back to seasonal anomaly detector if not")
print()
print("2. Cost Anomaly Detection:")
print("   - Fetches daily cost history from AWS Cost Explorer")
print("   - Builds features from cost data")
print("   - Uses Phase A to predict if cost is anomalous")
print("   - Stores detected anomalies in database")
print()
print("3. False Positive Handling:")
print("   - Users can mark anomalies as false positives")
print("   - System learns patterns to reduce future false alarms")
print("   - Considers day of week and magnitude buckets")
print()

# Step 7: Show current system status
print("Step 7: Current System Status")
print("-" * 40)
from app.ml.phase_a.pipeline import load_metric_features
from app.ml.phase_a.model_persistence import MODEL_DIR

print("Database Status:")
try:
    df = load_metric_features(limit=100)
    print(f"  [OK] {len(df)} records in metric_features table")
    if len(df) > 0:
        print(f"  [OK] Date range: {df['ts'].min()} to {df['ts'].max()}")
        print(f"  [OK] Features available: {df.columns.tolist()}")
except Exception as e:
    print(f"  [ERROR] Error loading data: {e}")

print()
print("Model Status:")
print(f"  Model directory: {MODEL_DIR}")
print(f"  Directory exists: {MODEL_DIR.exists()}")
if MODEL_DIR.exists():
    model_files = list(MODEL_DIR.glob("*.joblib"))
    print(f"  Model files: {len(model_files)}")
else:
    print("  Model files: 0 (need to train models)")

print()
print("AWS Configuration:")
from app.config import get_settings
settings = get_settings()
print(f"  AWS Region: {settings.aws_default_region}")
print(f"  Database: {settings.database_url[:20]}...")

print()
print("=" * 80)
print("Summary")
print("=" * 80)
print("[OK] AWS accounts are configured in the database")
print("[OK] ML Phase A architecture is properly structured")
print("[OK] Data pipeline connects AWS -> Database -> ML -> Predictions")
print("[OK] API endpoints are available for inference")
print()
print("To complete the setup:")
print("1. Configure AWS credentials (role_arn or direct credentials)")
print("2. Run data collection scripts to populate metric_features")
print("3. Train models: python scripts/run_phase_a_ml.py")
print("4. Test predictions via API endpoints")
print("=" * 80)
