"""
Common utilities for ML models.
Provides shared functionality for model training, validation, and deployment.
"""

import numpy as np
import pandas as pd
import pickle
import joblib
import logging
from typing import Dict, Any, List, Tuple, Optional, Union
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class ModelUtils:
    """Utility class for common ML operations"""
    
    @staticmethod
    def prepare_time_series_data(df: pd.DataFrame, 
                               target_column: str,
                               sequence_length: int = 60,
                               test_size: float = 0.2) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare time series data for LSTM models.
        
        Args:
            df: DataFrame with time series data
            target_column: Name of target column
            sequence_length: Length of input sequences
            test_size: Proportion of data for testing
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Sort by timestamp
        df = df.sort_index()
        
        # Create sequences
        X, y = [], []
        for i in range(sequence_length, len(df)):
            X.append(df.iloc[i-sequence_length:i].values)
            y.append(df[target_column].iloc[i])
            
        X, y = np.array(X), np.array(y)
        
        # Split data maintaining temporal order
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        return X_train, X_test, y_train, y_test
        
    @staticmethod
    def create_features_targets(df: pd.DataFrame,
                              target_column: str,
                              feature_columns: List[str] = None,
                              horizon: int = 1) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Create features and targets for supervised learning.
        
        Args:
            df: Input DataFrame
            target_column: Target column name
            feature_columns: List of feature columns (None for all except target)
            horizon: Prediction horizon in periods
            
        Returns:
            Tuple of (features_df, targets_series)
        """
        if feature_columns is None:
            feature_columns = [col for col in df.columns if col != target_column]
            
        # Create lagged features
        features_df = df[feature_columns].copy()
        
        # Create future targets
        targets_series = df[target_column].shift(-horizon).dropna()
        
        # Align features and targets
        features_df = features_df.iloc[:-horizon] if horizon > 0 else features_df
        
        return features_df, targets_series
        
    @staticmethod
    def scale_data(X_train: np.ndarray, 
                   X_test: np.ndarray = None,
                   method: str = 'standard') -> Tuple[np.ndarray, np.ndarray, Any]:
        """
        Scale features for ML models.
        
        Args:
            X_train: Training features
            X_test: Test features (optional)
            method: Scaling method ('standard', 'minmax')
            
        Returns:
            Tuple of (X_train_scaled, X_test_scaled, scaler)
        """
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaling method: {method}")
            
        # Reshape if needed for 3D data (LSTM)
        original_shape = X_train.shape
        if len(original_shape) == 3:
            X_train_2d = X_train.reshape(-1, original_shape[-1])
            X_train_scaled = scaler.fit_transform(X_train_2d)
            X_train_scaled = X_train_scaled.reshape(original_shape)
        else:
            X_train_scaled = scaler.fit_transform(X_train)
            
        if X_test is not None:
            if len(X_test.shape) == 3:
                X_test_2d = X_test.reshape(-1, X_test.shape[-1])
                X_test_scaled = scaler.transform(X_test_2d)
                X_test_scaled = X_test_scaled.reshape(X_test.shape)
            else:
                X_test_scaled = scaler.transform(X_test)
        else:
            X_test_scaled = None
            
        return X_train_scaled, X_test_scaled, scaler
        
    @staticmethod
    def evaluate_regression_model(y_true: np.ndarray, 
                                y_pred: np.ndarray) -> Dict[str, float]:
        """
        Evaluate regression model performance.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Dictionary of evaluation metrics
        """
        metrics = {
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100,
            'directional_accuracy': np.mean(np.sign(y_true[1:] - y_true[:-1]) == 
                                          np.sign(y_pred[1:] - y_pred[:-1]))
        }
        
        return metrics
        
    @staticmethod
    def save_model(model: Any, 
                   filepath: str,
                   metadata: Dict[str, Any] = None) -> bool:
        """
        Save ML model with metadata.
        
        Args:
            model: Model to save
            filepath: Path to save model
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            # Determine save method based on model type
            if hasattr(model, 'save'):  # TensorFlow/Keras models
                model.save(filepath)
            else:  # Scikit-learn models
                joblib.dump(model, filepath)
                
            # Save metadata if provided
            if metadata:
                metadata_path = filepath.replace('.pkl', '_metadata.json').replace('.h5', '_metadata.json')
                import json
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2, default=str)
                    
            logger.info(f"Model saved successfully to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
            
    @staticmethod
    def load_model(filepath: str) -> Tuple[Any, Dict[str, Any]]:
        """
        Load ML model with metadata.
        
        Args:
            filepath: Path to model file
            
        Returns:
            Tuple of (model, metadata)
        """
        try:
            # Load model
            if filepath.endswith('.h5'):
                model = tf.keras.models.load_model(filepath)
            else:
                model = joblib.load(filepath)
                
            # Load metadata if exists
            metadata = {}
            metadata_path = filepath.replace('.pkl', '_metadata.json').replace('.h5', '_metadata.json')
            try:
                import json
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            except FileNotFoundError:
                pass
                
            logger.info(f"Model loaded successfully from {filepath}")
            return model, metadata
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
            
    @staticmethod
    def create_time_series_splits(df: pd.DataFrame, 
                                n_splits: int = 5) -> List[Tuple[pd.Index, pd.Index]]:
        """
        Create time series cross-validation splits.
        
        Args:
            df: DataFrame with time series data
            n_splits: Number of splits
            
        Returns:
            List of (train_indices, test_indices) tuples
        """
        tscv = TimeSeriesSplit(n_splits=n_splits)
        splits = []
        
        for train_idx, test_idx in tscv.split(df):
            train_indices = df.index[train_idx]
            test_indices = df.index[test_idx]
            splits.append((train_indices, test_indices))
            
        return splits
        
    @staticmethod
    def calculate_sharpe_ratio(returns: np.ndarray, 
                             risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio for returns.
        
        Args:
            returns: Array of returns
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Sharpe ratio
        """
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        
    @staticmethod
    def calculate_max_drawdown(returns: np.ndarray) -> float:
        """
        Calculate maximum drawdown.
        
        Args:
            returns: Array of returns
            
        Returns:
            Maximum drawdown as percentage
        """
        cumulative_returns = (1 + returns).cumprod()
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        return np.min(drawdown) * 100
        
    @staticmethod
    def prepare_ensemble_features(predictions: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Prepare features for ensemble models from individual predictions.
        
        Args:
            predictions: Dictionary of model_name -> predictions
            
        Returns:
            Feature matrix for ensemble
        """
        feature_matrix = np.column_stack(list(predictions.values()))
        return feature_matrix
