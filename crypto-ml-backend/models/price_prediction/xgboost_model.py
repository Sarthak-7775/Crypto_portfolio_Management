"""
XGBoost model for cryptocurrency price prediction.
Uses feature-based approach with technical indicators and sentiment data.
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from typing import Dict, Any, Tuple, Optional, List
import logging

from .base_predictor import BasePredictor

logger = logging.getLogger(__name__)

class XGBoostPredictor(BasePredictor):
    """
    XGBoost-based cryptocurrency price predictor.
    Optimized for feature-based prediction with technical indicators.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # XGBoost-specific parameters
        self.n_estimators = config.get('n_estimators', 1000)
        self.max_depth = config.get('max_depth', 6)
        self.learning_rate = config.get('learning_rate', 0.1)
        self.subsample = config.get('subsample', 0.8)
        self.colsample_bytree = config.get('colsample_bytree', 0.8)
        self.reg_alpha = config.get('reg_alpha', 0.1)
        self.reg_lambda = config.get('reg_lambda', 0.1)
        self.random_state = config.get('random_state', 42)
        
        # Feature engineering parameters
        self.use_feature_selection = config.get('use_feature_selection', True)
        self.max_features = config.get('max_features', 50)
        
        # Model components
        self.scaler = StandardScaler()
        self.feature_selector = None
        self.feature_importance_scores = None
        
    def build_model(self) -> None:
        """Build XGBoost model"""
        
        self.model = xgb.XGBRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            subsample=self.subsample,
            colsample_bytree=self.colsample_bytree,
            reg_alpha=self.reg_alpha,
            reg_lambda=self.reg_lambda,
            random_state=self.random_state,
            n_jobs=-1,
            verbosity=0
        )
        
        logger.info("XGBoost model initialized")
        
    def prepare_data(self, 
                    df: pd.DataFrame,
                    sequence_length: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare feature-based data for XGBoost.
        
        Args:
            df: Input DataFrame
            sequence_length: Not used for XGBoost (compatibility)
            
        Returns:
            Tuple of (features, targets)
        """
        # Sort by timestamp
        df = df.sort_index()
        
        # Select features
        if self.feature_columns:
            feature_data = df[self.feature_columns].values
        else:
            feature_data = df.drop(columns=[self.target_column]).values
            self.feature_columns = [col for col in df.columns if col != self.target_column]
        
        target_data = df[self.target_column].values
        
        # Handle missing values
        feature_data = pd.DataFrame(feature_data, columns=self.feature_columns)
        feature_data = feature_data.fillna(method='ffill').fillna(0)
        feature_data = feature_data.values
        
        return feature_data, target_data
        
    def feature_selection(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Select most important features using XGBoost feature importance.
        
        Args:
            X: Feature matrix
            y: Target values
            
        Returns:
            Selected feature indices
        """
        # Train a preliminary model for feature selection
        temp_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=self.random_state,
            n_jobs=-1,
            verbosity=0
        )
        
        temp_model.fit(X, y)
        feature_importance = temp_model.feature_importances_
        
        # Select top features
        important_features = np.argsort(feature_importance)[-self.max_features:]
        
        self.feature_importance_scores = {
            self.feature_columns[i]: feature_importance[i] 
            for i in range(len(self.feature_columns))
        }
        
        logger.info(f"Selected {len(important_features)} most important features")
        
        return important_features
        
    def train(self, 
             X_train: np.ndarray, 
             y_train: np.ndarray,
             X_val: np.ndarray = None,
             y_val: np.ndarray = None) -> Dict[str, Any]:
        """
        Train the XGBoost model.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            
        Returns:
            Training metrics
        """
        if self.model is None:
            self.build_model()
            
        # Feature selection
        if self.use_feature_selection and X_train.shape[1] > self.max_features:
            selected_features = self.feature_selection(X_train, y_train)
            X_train = X_train[:, selected_features]
            if X_val is not None:
                X_val = X_val[:, selected_features]
            
            # Update feature columns
            self.feature_columns = [self.feature_columns[i] for i in selected_features]
            self.feature_selector = selected_features
            
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val) if X_val is not None else None
        
        # Prepare validation set for early stopping
        eval_set = [(X_train_scaled, y_train)]
        if X_val_scaled is not None:
            eval_set.append((X_val_scaled, y_val))
            
        # Train model
        self.model.fit(
            X_train_scaled, y_train,
            eval_set=eval_set,
            eval_metric='rmse',
            early_stopping_rounds=50,
            verbose=False
        )
        
        self.is_trained = True
        
        # Calculate training metrics
        train_pred = self.model.predict(X_train_scaled)
        train_rmse = np.sqrt(np.mean((y_train - train_pred) ** 2))
        train_mae = np.mean(np.abs(y_train - train_pred))
        
        training_metrics = {
            'train_rmse': train_rmse,
            'train_mae': train_mae,
            'n_estimators_used': self.model.best_iteration + 1,
            'feature_importance': self.get_feature_importance()
        }
        
        if X_val_scaled is not None:
            val_pred = self.model.predict(X_val_scaled)
            val_rmse = np.sqrt(np.mean((y_val - val_pred) ** 2))
            val_mae = np.mean(np.abs(y_val - val_pred))
            
            training_metrics.update({
                'val_rmse': val_rmse,
                'val_mae': val_mae
            })
            
        logger.info(f"XGBoost training completed. Train RMSE: {train_rmse:.6f}")
        
        return training_metrics
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using trained XGBoost model.
        
        Args:
            X: Input features
            
        Returns:
            Predictions array
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
            
        # Apply feature selection if used
        if self.feature_selector is not None:
            X = X[:, self.feature_selector]
            
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        predictions = self.model.predict(X_scaled)
        return predictions
        
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary of feature names and importance scores
        """
        if not self.is_trained:
            return {}
            
        importance_scores = self.model.feature_importances_
        feature_importance = {
            feature: score 
            for feature, score in zip(self.feature_columns, importance_scores)
        }
        
        # Sort by importance
        return dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        
    def hyperparameter_tuning(self, 
                            X_train: np.ndarray,
                            y_train: np.ndarray,
                            param_grid: Dict[str, List] = None) -> Dict[str, Any]:
        """
        Perform hyperparameter tuning using time series cross-validation.
        
        Args:
            X_train: Training features
            y_train: Training targets
            param_grid: Parameter grid for search
            
        Returns:
            Best parameters and CV results
        """
        if param_grid is None:
            param_grid = {
                'n_estimators': [500, 1000],
                'max_depth': [4, 6, 8],
                'learning_rate': [0.05, 0.1, 0.15],
                'subsample': [0.8, 0.9],
                'colsample_bytree': [0.8, 0.9]
            }
            
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=3)
        
        # Grid search
        grid_search = GridSearchCV(
            estimator=xgb.XGBRegressor(random_state=self.random_state),
            param_grid=param_grid,
            cv=tscv,
            scoring='neg_mean_squared_error',
            n_jobs=-1,
            verbose=1
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Perform search
        grid_search.fit(X_train_scaled, y_train)
        
        # Update model with best parameters
        self.model = grid_search.best_estimator_
        
        results = {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'cv_results': grid_search.cv_results_
        }
        
        logger.info(f"Hyperparameter tuning completed. Best score: {results['best_score']:.6f}")
        
        return results
        
    def plot_feature_importance(self, top_n: int = 20) -> None:
        """
        Plot feature importance.
        
        Args:
            top_n: Number of top features to plot
        """
        if not self.is_trained:
            logger.warning("Model must be trained to plot feature importance")
            return
            
        try:
            import matplotlib.pyplot as plt
            
            feature_importance = self.get_feature_importance()
            
            # Get top N features
            top_features = dict(list(feature_importance.items())[:top_n])
            
            plt.figure(figsize=(10, 8))
            plt.barh(range(len(top_features)), list(top_features.values()))
            plt.yticks(range(len(top_features)), list(top_features.keys()))
            plt.xlabel('Feature Importance')
            plt.title(f'Top {top_n} Feature Importance - XGBoost')
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            logger.warning("Matplotlib not available for plotting")
            
    def predict_with_uncertainty(self, X: np.ndarray, n_estimators: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions with uncertainty estimates using quantile regression.
        
        Args:
            X: Input features
            n_estimators: Number of estimators for uncertainty estimation
            
        Returns:
            Tuple of (predictions, uncertainties)
        """
        # This is a simplified approach - proper uncertainty would require
        # ensemble methods or Bayesian approaches
        predictions = self.predict(X)
        
        # Estimate uncertainty based on feature importance and prediction variance
        # This is a placeholder implementation
        uncertainties = np.std(predictions) * np.ones_like(predictions)
        
        return predictions, uncertainties
