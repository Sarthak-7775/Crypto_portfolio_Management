"""
LSTM model for cryptocurrency price prediction.
Specialized for time series forecasting with advanced features.
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, Any, Tuple, Optional
import logging

from .base_predictor import BasePredictor

logger = logging.getLogger(__name__)

class LSTMPredictor(BasePredictor):
    """
    LSTM-based cryptocurrency price predictor.
    Optimized for capturing temporal dependencies in price data.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # LSTM-specific parameters
        self.sequence_length = config.get('sequence_length', 60)
        self.lstm_units = config.get('lstm_units', [50, 50])
        self.dropout_rate = config.get('dropout_rate', 0.2)
        self.learning_rate = config.get('learning_rate', 0.001)
        self.batch_size = config.get('batch_size', 32)
        self.epochs = config.get('epochs', 100)
        self.patience = config.get('patience', 10)
        
        # Model components
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
    def build_model(self) -> None:
        """Build LSTM model architecture"""
        
        model = Sequential()
        
        # First LSTM layer
        model.add(LSTM(
            units=self.lstm_units[0],
            return_sequences=len(self.lstm_units) > 1,
            input_shape=(self.sequence_length, len(self.feature_columns) or 1)
        ))
        model.add(Dropout(self.dropout_rate))
        model.add(BatchNormalization())
        
        # Additional LSTM layers
        for i, units in enumerate(self.lstm_units[1:], 1):
            return_sequences = i < len(self.lstm_units) - 1
            model.add(LSTM(units=units, return_sequences=return_sequences))
            model.add(Dropout(self.dropout_rate))
            model.add(BatchNormalization())
        
        # Dense layers
        model.add(Dense(25, activation='relu'))
        model.add(Dropout(self.dropout_rate))
        model.add(Dense(1))  # Single output for price prediction
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        
        self.model = model
        logger.info(f"LSTM model built with {model.count_params()} parameters")
        
    def prepare_data(self, 
                    df: pd.DataFrame,
                    sequence_length: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare sequential data for LSTM training.
        
        Args:
            df: Input DataFrame with time series data
            sequence_length: Length of input sequences
            
        Returns:
            Tuple of (X_sequences, y_values)
        """
        if sequence_length is None:
            sequence_length = self.sequence_length
            
        # Sort by timestamp
        df = df.sort_index()
        
        # Select features
        if self.feature_columns:
            feature_data = df[self.feature_columns].values
        else:
            feature_data = df.drop(columns=[self.target_column]).values
            self.feature_columns = [col for col in df.columns if col != self.target_column]
        
        target_data = df[self.target_column].values
        
        # Scale the data
        feature_data_scaled = self.scaler.fit_transform(feature_data)
        
        # Create sequences
        X, y = [], []
        for i in range(sequence_length, len(feature_data_scaled)):
            X.append(feature_data_scaled[i-sequence_length:i])
            y.append(target_data[i])
            
        return np.array(X), np.array(y)
        
    def train(self, 
             X_train: np.ndarray, 
             y_train: np.ndarray,
             X_val: np.ndarray = None,
             y_val: np.ndarray = None) -> Dict[str, Any]:
        """
        Train the LSTM model.
        
        Args:
            X_train: Training sequences
            y_train: Training targets
            X_val: Validation sequences
            y_val: Validation targets
            
        Returns:
            Training history
        """
        if self.model is None:
            self.build_model()
            
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=self.patience,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss' if X_val is not None else 'loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            )
        ]
        
        # Validation data
        validation_data = (X_val, y_val) if X_val is not None else None
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            batch_size=self.batch_size,
            epochs=self.epochs,
            validation_data=validation_data,
            callbacks=callbacks,
            verbose=1,
            shuffle=False  # Important for time series
        )
        
        self.is_trained = True
        
        # Return training metrics
        training_metrics = {
            'final_loss': history.history['loss'][-1],
            'final_mae': history.history['mae'][-1],
            'epochs_trained': len(history.history['loss']),
            'history': history.history
        }
        
        if validation_data is not None:
            training_metrics.update({
                'final_val_loss': history.history['val_loss'][-1],
                'final_val_mae': history.history['val_mae'][-1]
            })
        
        logger.info(f"LSTM training completed. Final loss: {training_metrics['final_loss']:.6f}")
        
        return training_metrics
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions using trained LSTM model.
        
        Args:
            X: Input sequences
            
        Returns:
            Predictions array
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
            
        predictions = self.model.predict(X, verbose=0)
        return predictions.flatten()
        
    def predict_sequence(self, 
                        initial_sequence: np.ndarray,
                        num_predictions: int) -> np.ndarray:
        """
        Predict a sequence of future values.
        
        Args:
            initial_sequence: Starting sequence
            num_predictions: Number of future predictions
            
        Returns:
            Array of predictions
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
            
        predictions = []
        current_sequence = initial_sequence.copy()
        
        for _ in range(num_predictions):
            # Predict next value
            pred = self.model.predict(current_sequence[np.newaxis, :], verbose=0)[0, 0]
            predictions.append(pred)
            
            # Update sequence: remove first element, add prediction
            current_sequence = np.roll(current_sequence, -1, axis=0)
            current_sequence[-1, 0] = pred  # Add prediction to first feature
            
        return np.array(predictions)
        
    def get_attention_weights(self, X: np.ndarray) -> np.ndarray:
        """
        Get attention weights if model supports it.
        This is a placeholder for advanced LSTM variants.
        """
        # This would require a custom LSTM with attention mechanism
        # For now, return None
        return None
        
    def plot_training_history(self, history: Dict[str, Any]) -> None:
        """Plot training history"""
        try:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
            
            # Loss plot
            ax1.plot(history['loss'], label='Training Loss')
            if 'val_loss' in history:
                ax1.plot(history['val_loss'], label='Validation Loss')
            ax1.set_title('Model Loss')
            ax1.set_xlabel('Epoch')
            ax1.set_ylabel('Loss')
            ax1.legend()
            
            # MAE plot
            ax2.plot(history['mae'], label='Training MAE')
            if 'val_mae' in history:
                ax2.plot(history['val_mae'], label='Validation MAE')
            ax2.set_title('Model MAE')
            ax2.set_xlabel('Epoch')
            ax2.set_ylabel('MAE')
            ax2.legend()
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            logger.warning("Matplotlib not available for plotting")
