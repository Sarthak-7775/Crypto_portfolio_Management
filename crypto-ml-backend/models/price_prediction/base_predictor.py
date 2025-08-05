"""
Abstract base class for price prediction models.
Defines common interface for all predictors.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)

class BasePredictor(ABC):
    """Abstract base class for cryptocurrency price predictors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.scaler = None
        self.is_trained = False
        self.feature_columns = []
        self.target_column = config.get('target_column', 'close')
        
    @abstractmethod
    def build_model(self) -> None:
        """Build the ML model architecture"""
        pass
        
    @abstractmethod
    def train(self, 
             X_train: np.ndarray, 
             y_train: np.ndarray,
             X_val: np.ndarray = None,
             y_val: np.ndarray = None) -> Dict[str, Any]:
        """
        Train the model.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            
        Returns:
            Training history/metrics
        """
        pass
        
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Input features
            
        Returns:
            Predictions array
        """
        pass
        
    def prepare_data(self, 
                    df: pd.DataFrame,
                    sequence_length: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for training/prediction.
        
        Args:
            df: Input DataFrame
            sequence_length: Length of sequences (for RNN models)
            
        Returns:
            Tuple of (features, targets)
        """
        # Default implementation for non-sequential models
        if self.feature_columns:
            X = df[self.feature_columns].values
        else:
            X = df.drop(columns=[self.target_column]).values
            
        y = df[self.target_column].values
        
        return X, y
        
    def save_model(self, filepath: str) -> bool:
        """Save trained model"""
        try:
            from ..utils.model_utils import ModelUtils
            
            metadata = {
                'model_type': self.__class__.__name__,
                'config': self.config,
                'feature_columns': self.feature_columns,
                'target_column': self.target_column,
                'is_trained': self.is_trained
            }
            
            return ModelUtils.save_model(self.model, filepath, metadata)
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
            
    def load_model(self, filepath: str) -> bool:
        """Load trained model"""
        try:
            from ..utils.model_utils import ModelUtils
            
            self.model, metadata = ModelUtils.load_model(filepath)
            
            # Restore metadata
            if metadata:
                self.config = metadata.get('config', self.config)
                self.feature_columns = metadata.get('feature_columns', [])
                self.target_column = metadata.get('target_column', 'close')
                self.is_trained = metadata.get('is_trained', False)
                
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
            
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance"""
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")
            
        predictions = self.predict(X_test)
        
        from ..utils.evaluation_metrics import ModelEvaluator
        return ModelEvaluator.evaluate_price_prediction(y_test, predictions)
        
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance (if supported by model)"""
        return None
        
    def predict_next_price(self, 
                          recent_data: pd.DataFrame,
                          horizon: int = 1) -> np.ndarray:
        """
        Predict next price(s) given recent data.
        
        Args:
            recent_data: Recent market data
            horizon: Number of future periods to predict
            
        Returns:
            Array of predicted prices
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
            
        # Prepare input data
        X, _ = self.prepare_data(recent_data)
        
        predictions = []
        current_input = X[-1:] if len(X.shape) > 1 else X[-1].reshape(1, -1)
        
        for _ in range(horizon):
            pred = self.predict(current_input)
            predictions.append(pred[0])
            
            # Update input for next prediction (simple approach)
            if len(X.shape) > 2:  # Sequential data
                current_input = np.roll(current_input, -1, axis=1)
                current_input[0, -1, :] = pred[0]  # Add prediction as new input
                
        return np.array(predictions)
