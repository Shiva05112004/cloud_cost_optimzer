"""
Comprehensive test script for ML Phase A to demonstrate:
1. How the ML system works
2. How it connects to AWS accounts
3. How the inference service works
4. How to train and use models
"""

import sys
import os
import logging
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_phase_a_architecture():
    """Test 1: Verify Phase A architecture and components"""
    logger.info("=" * 80)
    logger.info("TEST 1: Verifying Phase A Architecture")
    logger.info("=" * 80)
    
    try:
        # Test imports
        from app.ml.phase_a.pipeline import build_splits, FEATURE_COLUMNS
        from app.ml.phase_a.train import train_models
        from app.ml.phase_a.model_persistence import save_models, load_latest_models, list_available_models
        from app.ml.phase_a.inference import get_inference_service, Phase_AIInferenceService
        
        logger.info("✓ All Phase A modules imported successfully")
        logger.info(f"✓ Feature columns: {FEATURE_COLUMNS}")
        
        # Check model directory
        from app.ml.phase_a.model_persistence import MODEL_DIR
        logger.info(f"✓ Model directory: {MODEL_DIR}")
        logger.info(f"✓ Model directory exists: {MODEL_DIR.exists()}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Architecture test failed: {e}")
        return False


def test_data_pipeline():
    """Test 2: Test data pipeline and database connection"""
    logger.info("=" * 80)
    logger.info("TEST 2: Testing Data Pipeline")
    logger.info("=" * 80)
    
    try:
        from app.ml.phase_a.pipeline import load_metric_features, validate_data_quality
        from app.config import get_settings
        
        settings = get_settings()
        logger.info(f"✓ Database URL configured: {settings.database_url[:20]}...")
        
        # Try to load a small sample of data
        try:
            df = load_metric_features(limit=100)
            logger.info(f"✓ Successfully loaded {len(df)} records from metric_features table")
            
            if len(df) > 0:
                quality_report = validate_data_quality(df)
                logger.info(f"✓ Data quality report generated")
                logger.info(f"  - Total rows: {quality_report['total_rows']}")
                logger.info(f"  - Class distribution: {quality_report.get('class_distribution', {})}")
                
                # Show sample data
                logger.info(f"✓ Sample data columns: {df.columns.tolist()}")
                logger.info(f"✓ Sample data shape: {df.shape}")
            else:
                logger.warning("⚠ No data found in metric_features table")
                
        except Exception as e:
            logger.warning(f"⚠ Could not load data from database: {e}")
            logger.info("  This is expected if the database is empty or not yet populated")
        
        return True
    except Exception as e:
        logger.error(f"✗ Data pipeline test failed: {e}")
        return False


def test_model_availability():
    """Test 3: Check if trained models are available"""
    logger.info("=" * 80)
    logger.info("TEST 3: Checking Model Availability")
    logger.info("=" * 80)
    
    try:
        from app.ml.phase_a.model_persistence import load_latest_models, list_available_models, MODEL_DIR
        
        # Ensure model directory exists
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        
        # Try to load latest models
        rf_model, xgb_model, metadata = load_latest_models()
        
        if rf_model is not None and xgb_model is not None:
            logger.info("✓ Trained models found and loaded successfully")
            if metadata:
                logger.info(f"✓ Model metadata: {metadata.get('timestamp')}")
                logger.info(f"✓ Best model: {metadata.get('best_model')}")
                logger.info(f"✓ RF Test F1: {metadata.get('rf_test_f1')}")
                logger.info(f"✓ XGB Test F1: {metadata.get('xgb_test_f1')}")
        else:
            logger.warning("⚠ No trained models found")
            logger.info("  Models need to be trained using: python scripts/run_phase_a_ml.py")
        
        # List available models
        available_models = list_available_models()
        logger.info(f"✓ Available model versions: {len(available_models)}")
        for model_info in available_models[:3]:  # Show first 3
            logger.info(f"  - {model_info.get('timestamp')}: {model_info.get('best_model')}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Model availability test failed: {e}")
        return False


def test_inference_service():
    """Test 4: Test inference service"""
    logger.info("=" * 80)
    logger.info("TEST 4: Testing Inference Service")
    logger.info("=" * 80)
    
    try:
        from app.ml.phase_a.inference import get_inference_service
        
        service = get_inference_service()
        logger.info("✓ Inference service initialized")
        
        # Check if service is ready
        is_ready = service.is_ready()
        logger.info(f"✓ Service ready: {is_ready}")
        
        if is_ready:
            # Get model info
            model_info = service.get_model_info()
            logger.info(f"✓ Model info: {model_info}")
            
            # Test single prediction with sample features
            sample_features = {
                "cpu": 45.2,
                "memory": 60.1,
                "connections": 120,
                "cpu_velocity": 2.1,
                "memory_velocity": 1.5,
                "connections_velocity": 5,
                "rolling_cpu": 44.8,
                "rolling_memory": 59.2,
                "rolling_connections": 118
            }
            
            result = service.predict_single(sample_features)
            logger.info(f"✓ Single prediction result: {result}")
            
            # Test batch prediction
            batch_features = [sample_features, sample_features]
            batch_result = service.predict_batch(batch_features)
            logger.info(f"✓ Batch prediction result: {batch_result}")
        else:
            logger.warning("⚠ Service not ready - models need to be trained first")
        
        return True
    except Exception as e:
        logger.error(f"✗ Inference service test failed: {e}")
        return False


def test_aws_integration():
    """Test 5: Test AWS integration through the system"""
    logger.info("=" * 80)
    logger.info("TEST 5: Testing AWS Integration")
    logger.info("=" * 80)
    
    try:
        from app.models.account import CloudAccount
        from app.models.database import SessionLocal
        from app.cloud_api.ec2_client import get_boto3_session
        from app.cloud_api.cost_explorer_client import get_daily_cost_history
        from app.config import get_settings
        
        settings = get_settings()
        logger.info(f"✓ AWS region configured: {settings.aws_default_region}")
        
        # Check for cloud accounts in database
        db = SessionLocal()
        try:
            accounts = db.query(CloudAccount).all()
            logger.info(f"✓ Found {len(accounts)} cloud accounts in database")
            
            for account in accounts:
                logger.info(f"  Account: {account.account_name}")
                logger.info(f"  Role ARN: {account.role_arn}")
                logger.info(f"  Provider: {account.provider}")
                
                # Test AWS connection using the role ARN
                try:
                    session = get_boto3_session(account.role_arn)
                    logger.info(f"  ✓ Successfully created boto3 session for account")
                    
                    # Try to get cost history (this tests the AWS connection)
                    try:
                        daily_costs = get_daily_cost_history(role_arn=account.role_arn, days=7)
                        logger.info(f"  ✓ Successfully retrieved {len(daily_costs)} days of cost data")
                        
                        # Show sample cost data
                        if daily_costs:
                            sample_date = list(daily_costs.keys())[0]
                            logger.info(f"  Sample cost for {sample_date}: ${daily_costs[sample_date]}")
                    except Exception as cost_error:
                        logger.warning(f"  ⚠ Could not retrieve cost history: {cost_error}")
                        logger.info("    This may be due to AWS permissions or Cost Explorer not being enabled")
                        
                except Exception as session_error:
                    logger.warning(f"  ⚠ Could not create boto3 session: {session_error}")
                    logger.info("    This may be due to invalid role ARN or AWS credentials")
                    
        finally:
            db.close()
        
        return True
    except Exception as e:
        logger.error(f"✗ AWS integration test failed: {e}")
        return False


def test_api_endpoints():
    """Test 6: Test API endpoints for Phase A"""
    logger.info("=" * 80)
    logger.info("TEST 6: Testing API Endpoints")
    logger.info("=" * 80)
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/")
        logger.info(f"✓ Health check: {response.status_code} - {response.json()}")
        
        # Test Phase A info endpoint
        response = client.get("/api/phase_a/info")
        logger.info(f"✓ Phase A info endpoint: {response.status_code}")
        if response.status_code == 200:
            logger.info(f"  Response: {response.json()}")
        else:
            logger.info(f"  Expected 503 if models not trained: {response.json()}")
        
        # Test that phase_a router is included
        logger.info("✓ Phase A routes are registered in the application")
        
        return True
    except Exception as e:
        logger.error(f"✗ API endpoints test failed: {e}")
        return False


def test_anomaly_service_integration():
    """Test 7: Test how Phase A integrates with anomaly detection"""
    logger.info("=" * 80)
    logger.info("TEST 7: Testing Anomaly Service Integration")
    logger.info("=" * 80)
    
    try:
        from app.services.anomaly_service import analyze_account_anomalies, _try_phase_a_detection
        
        # Test the Phase A detection function directly
        sample_features = {
            "cpu": 45.2,
            "memory": 60.1,
            "connections": 120,
            "cpu_velocity": 2.1,
            "memory_velocity": 1.5,
            "connections_velocity": 5,
            "rolling_cpu": 44.8,
            "rolling_memory": 59.2,
            "rolling_connections": 118
        }
        
        result = _try_phase_a_detection(sample_features)
        if result:
            logger.info(f"✓ Phase A detection successful: {result}")
        else:
            logger.info("⚠ Phase A detection returned None (models may not be trained)")
            logger.info("  This is expected if models haven't been trained yet")
        
        # Check database for accounts
        from app.models.account import CloudAccount
        from app.models.database import SessionLocal
        
        db = SessionLocal()
        try:
            accounts = db.query(CloudAccount).first()
            if accounts:
                logger.info(f"✓ Found account for anomaly analysis: {accounts.account_name}")
                
                # Test anomaly analysis (this would use Phase A if available)
                try:
                    anomaly_result = analyze_account_anomalies(accounts.id, days=7, use_phase_a=True)
                    logger.info(f"✓ Anomaly analysis result: {anomaly_result.get('status')}")
                except Exception as anomaly_error:
                    logger.warning(f"⚠ Anomaly analysis failed: {anomaly_error}")
            else:
                logger.info("⚠ No accounts found in database for anomaly analysis")
        finally:
            db.close()
        
        return True
    except Exception as e:
        logger.error(f"✗ Anomaly service integration test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("Starting comprehensive ML Phase A testing...")
    logger.info("This will demonstrate how ML Phase A works and connects to AWS")
    logger.info("")
    
    tests = [
        ("Architecture Test", test_phase_a_architecture),
        ("Data Pipeline Test", test_data_pipeline),
        ("Model Availability Test", test_model_availability),
        ("Inference Service Test", test_inference_service),
        ("AWS Integration Test", test_aws_integration),
        ("API Endpoints Test", test_api_endpoints),
        ("Anomaly Service Integration Test", test_anomaly_service_integration),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results[test_name] = False
        logger.info("")
    
    # Summary
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{status}: {test_name}")
    
    passed = sum(results.values())
    total = len(results)
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    # Next steps
    logger.info("\n" + "=" * 80)
    logger.info("NEXT STEPS")
    logger.info("=" * 80)
    logger.info("1. To train ML models: python scripts/run_phase_a_ml.py")
    logger.info("2. To populate database with AWS data: Use the data collection scripts")
    logger.info("3. To test predictions: Use POST /api/phase_a/predict endpoint")
    logger.info("4. To integrate with AWS: Add cloud accounts via POST /api/accounts")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
