"""Inference service for Phase A ML predictions."""
import logging
from typing import Dict, Optional

import pandas as pd
import numpy as np

from app.ml.phase_a.model_persistence import load_latest_models

logger = logging.getLogger(__name__)


class Phase_AIInferenceService:
    """Service for making predictions with Phase A models."""
    
    def __init__(self):
        """Initialize with latest trained models."""
        self.rf_model = None
        self.xgb_model = None
        self.metadata = None
        self.feature_names = None
        self._load_models()
    
    def _load_models(self):
        """Load the latest trained models."""
        self.rf_model, self.xgb_model, self.metadata = load_latest_models()
        
        if self.metadata:
            self.feature_names = self.metadata.get('feature_names', [])
            logger.info(f"Loaded Phase A models from {self.metadata.get('timestamp')}")
            logger.info(f"Best model: {self.metadata.get('best_model')}")
        else:
            logger.warning("No Phase A models found - predictions will fail")
    
    def is_ready(self) -> bool:
        """Check if models are loaded and ready."""
        return self.rf_model is not None and self.xgb_model is not None
    
    def predict_single(self, features: Dict) -> Dict:
        """
        Make a prediction for a single instance.
        
        Args:
            features: Dict with feature values (e.g., {'cpu': 45.2, 'memory': 60.1, ...})
        
        Returns:
            {
                'prediction': 0/1,
                'probability': float,
                'confidence': float,
                'model': 'xgboost'|'random_forest',
                'feature_names_missing': list,
            }
        """
        if not self.is_ready():
            return {'error': 'Models not loaded'}
        
        # Validate features
        missing_features = [f for f in self.feature_names if f not in features]
        if missing_features:
            logger.warning(f"Missing features: {missing_features}")
            return {'error': f'Missing required features: {missing_features}'}
        
        # Create feature vector in correct order
        X = pd.DataFrame([[features[f] for f in self.feature_names]], columns=self.feature_names)
        
        try:
            # Use the best model (as determined during training)
            best_model_name = self.metadata.get('best_model', 'xgboost')
            best_model = self.xgb_model if best_model_name == 'xgboost' else self.rf_model
            
            prediction = best_model.predict(X)[0]
            probability = best_model.predict_proba(X)[0, int(prediction)]
            
            return {
                'prediction': int(prediction),
                'probability': float(probability),
                'confidence': float(probability),
                'model': best_model_name,
                'status': 'success',
            }
        except Exception as e:
            logger.error(f"Prediction failed: {e}", exc_info=True)
            return {'error': str(e)}
    
    def predict_batch(self, features_list: list) -> Dict:
        """
        Make predictions for multiple instances.
        
        Args:
            features_list: List of dicts with feature values
        
        Returns:
            {
                'predictions': [0/1, ...],
                'probabilities': [float, ...],
                'confidences': [float, ...],
                'model': 'xgboost'|'random_forest',
                'count': int,
            }
        """
        if not self.is_ready():
            return {'error': 'Models not loaded'}
        
        if not features_list:
            return {'error': 'Empty features list'}
        
        try:
            # Create feature dataframe
            X = pd.DataFrame(features_list, columns=self.feature_names)
            X = X[self.feature_names]  # Ensure correct column order
            
            best_model_name = self.metadata.get('best_model', 'xgboost')
            best_model = self.xgb_model if best_model_name == 'xgboost' else self.rf_model
            
            predictions = best_model.predict(X)
            probabilities = best_model.predict_proba(X)[:, 1]  # Probability of failure (class 1)
            
            return {
                'predictions': predictions.tolist(),
                'probabilities': probabilities.tolist(),
                'confidences': probabilities.tolist(),
                'model': best_model_name,
                'count': len(predictions),
                'status': 'success',
            }
        except Exception as e:
            logger.error(f"Batch prediction failed: {e}", exc_info=True)
            return {'error': str(e)}
    
    def get_model_info(self) -> Dict:
        """Get metadata about the loaded models."""
        if not self.is_ready():
            return {'error': 'Models not loaded'}
        
        return {
            'timestamp': self.metadata.get('timestamp'),
            'best_model': self.metadata.get('best_model'),
            'rf_test_f1': self.metadata.get('rf_test_f1'),
            'xgb_test_f1': self.metadata.get('xgb_test_f1'),
            'class_imbalance_ratio': self.metadata.get('class_imbalance_ratio'),
            'feature_names': self.feature_names,
            'num_features': len(self.feature_names),
            'status': 'ready',
        }


# Global inference service instance
_inference_service: Optional[Phase_AIInferenceService] = None


def get_inference_service() -> Phase_AIInferenceService:
    """Get the global Phase A inference service instance."""
    global _inference_service
    if _inference_service is None:
        _inference_service = Phase_AIInferenceService()
    return _inference_service


def reload_models():
    """Reload models (useful after training new models)."""
    global _inference_service
    _inference_service = Phase_AIInferenceService()
    logger.info("Reloaded Phase A models")
