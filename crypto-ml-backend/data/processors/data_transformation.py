"""
Advanced data transformations for cryptocurrency ML pipeline.
Handles scaling, encoding, resampling, target creation, and feature transformations.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, OneHotEncoder, LabelEncoder
from sklearn.decomposition import PCA
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class DataTransformer:
    """
    Comprehensive data transformation pipeline for cryptocurrency ML.
    Handles preprocessing, feature creation, and data preparation.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.scalers = {}
        self.encoders = {}
        self.transformers = {}
        
        # Transformation parameters
        self.scaling_methods = ['standard', 'minmax', 'robust', 'none']
        self.target_methods = ['returns', 'price_change', 'direction', 'volatility']
        
    def create_price_targets(self, 
                           df: pd.DataFrame, 
                           price_column: str = 'close',
                           target_type: str = 'returns',
                           horizon: int = 1) -> pd.DataFrame:
        """
        Create target variables for price prediction.
        
        Args:
            df: DataFrame with price data
            price_column: Column containing price data
            target_type: Type of target ('returns', 'price_change', 'direction', 'volatility')
            horizon: Number of periods ahead to predict
            
        Returns:
            DataFrame with target columns added
        """
        logger.info(f"Creating {target_type} targets with horizon {horizon}")
        
        try:
            df = df.copy()
            
            if target_type == 'returns':
                # Percentage returns
                df[f'target_returns_{horizon}'] = df[price_column].pct_change(horizon).shift(-horizon) * 100
                
            elif target_type == 'price_change':
                # Absolute price change
                df[f'target_price_change_{horizon}'] = (
                    df[price_column].shift(-horizon) - df[price_column]
                )
                
            elif target_type == 'direction':
                # Binary direction (1 for up, 0 for down)
                future_returns = df[price_column].pct_change(horizon).shift(-horizon)
                df[f'target_direction_{horizon}'] = (future_returns > 0).astype(int)
                
            elif target_type == 'volatility':
                # Rolling volatility of returns
                returns = df[price_column].pct_change()
                df[f'target_volatility_{horizon}'] = (
                    returns.rolling(window=horizon).std().shift(-horizon) * 100
                )
                
            else:
                raise ValueError(f"Unknown target type: {target_type}")
                
            logger.info(f"Created target with {df[f'target_{target_type}_{horizon}'].notna().sum()} valid values")
            
        except Exception as e:
            logger.error(f"Error creating price targets: {e}")
            raise
            
        return df
        
    def create_classification_targets(self, 
                                    df: pd.DataFrame,
                                    price_column: str = 'close',
                                    thresholds: List[float] = [-2, 2],
                                    horizon: int = 1) -> pd.DataFrame:
        """
        Create multi-class classification targets based on return thresholds.
        
        Args:
            df: DataFrame with price data
            price_column: Column containing price data
            thresholds: List of threshold percentages for classification
            horizon: Number of periods ahead to predict
            
        Returns:
            DataFrame with classification target
        """
        logger.info(f"Creating classification targets with thresholds {thresholds}")
        
        try:
            df = df.copy()
            
            # Calculate future returns
            future_returns = df[price_column].pct_change(horizon).shift(-horizon) * 100
            
            # Create class labels based on thresholds
            target_class = pd.Series(1, index=df.index)  # Default: neutral (1)
            
            # Strong down (0)
            target_class[future_returns <= thresholds[0]] = 0
            
            # Strong up (2)
            target_class[future_returns >= thresholds[1]] = 2
            
            df[f'target_class_{horizon}'] = target_class
            
            # Also create probability-like targets
            df[f'target_prob_down_{horizon}'] = (future_returns <= thresholds[0]).astype(float)
            df[f'target_prob_up_{horizon}'] = (future_returns >= thresholds[1]).astype(float)
            df[f'target_prob_neutral_{horizon}'] = (
                (future_returns > thresholds[0]) & (future_returns < thresholds[1])
            ).astype(float)
            
            # Log class distribution
            class_counts = target_class.value_counts().sort_index()
            logger.info(f"Class distribution: {class_counts.to_dict()}")
            
        except Exception as e:
            logger.error(f"Error creating classification targets: {e}")
            raise
            
        return df
        
    def scale_features(self, 
                      df: pd.DataFrame,
                      columns: List[str],
                      method: str = 'standard',
                      fit: bool = True) -> pd.DataFrame:
        """
        Scale numerical features using various methods.
        
        Args:
            df: DataFrame to scale
            columns: Columns to scale
            method: Scaling method ('standard', 'minmax', 'robust', 'none')
            fit: Whether to fit the scaler or use existing one
            
        Returns:
            DataFrame with scaled features
        """
        logger.info(f"Scaling {len(columns)} features using {method} method")
        
        try:
            df = df.copy()
            
            if method == 'none':
                return df
                
            # Initialize scaler
            if method not in self.scalers or fit:
                if method == 'standard':
                    self.scalers[method] = StandardScaler()
                elif method == 'minmax':
                    self.scalers[method] = MinMaxScaler()
                elif method == 'robust':
                    self.scalers[method] = RobustScaler()
                else:
                    raise ValueError(f"Unknown scaling method: {method}")
                    
            scaler = self.scalers[method]
            
            # Scale features
            if fit:
                scaled_values = scaler.fit_transform(df[columns])
            else:
                scaled_values = scaler.transform(df[columns])
                
            # Replace original columns with scaled values
            df[columns] = scaled_values
            
            logger.info(f"Successfully scaled {len(columns)} features")
            
        except Exception as e:
            logger.error(f"Error scaling features: {e}")
            raise
            
        return df
        
    def create_lagged_features(self, 
                             df: pd.DataFrame,
                             columns: List[str],
                             lags: Union[int, List[int]] = [1, 2, 3, 5, 10]) -> pd.DataFrame:
        """
        Create lagged versions of features for time series modeling.
        
        Args:
            df: DataFrame with time series data
            columns: Columns to create lags for
            lags: Number of lags or list of specific lag periods
            
        Returns:
            DataFrame with lagged features added
        """
        logger.info(f"Creating lagged features for {len(columns)} columns")
        
        try:
            df = df.copy()
            
            # Convert single lag to list
            if isinstance(lags, int):
                lags = list(range(1, lags + 1))
                
            # Create lagged features
            for col in columns:
                for lag in lags:
                    df[f'{col}_lag_{lag}'] = df[col].shift(lag)
                    
            logger.info(f"Created {len(columns) * len(lags)} lagged features")
            
        except Exception as e:
            logger.error(f"Error creating lagged features: {e}")
            raise
            
        return df
        
    def create_rolling_features(self, 
                              df: pd.DataFrame,
                              columns: List[str],
                              windows: List[int] = [5, 10, 20, 50],
                              operations: List[str] = ['mean', 'std', 'min', 'max']) -> pd.DataFrame:
        """
        Create rolling window statistical features.
        
        Args:
            df: DataFrame with time series data
            columns: Columns to create rolling features for
            windows: Window sizes for rolling calculations
            operations: Statistical operations to apply
            
        Returns:
            DataFrame with rolling features added
        """
        logger.info(f"Creating rolling features for {len(columns)} columns")
        
        try:
            df = df.copy()
            
            for col in columns:
                for window in windows:
                    for op in operations:
                        feature_name = f'{col}_rolling_{window}_{op}'
                        
                        if op == 'mean':
                            df[feature_name] = df[col].rolling(window=window).mean()
                        elif op == 'std':
                            df[feature_name] = df[col].rolling(window=window).std()
                        elif op == 'min':
                            df[feature_name] = df[col].rolling(window=window).min()
                        elif op == 'max':
                            df[feature_name] = df[col].rolling(window=window).max()
                        elif op == 'sum':
                            df[feature_name] = df[col].rolling(window=window).sum()
                        elif op == 'median':
                            df[feature_name] = df[col].rolling(window=window).median()
                        elif op == 'skew':
                            df[feature_name] = df[col].rolling(window=window).skew()
                        elif op == 'kurt':
                            df[feature_name] = df[col].rolling(window=window).kurt()
                            
            logger.info(f"Created {len(columns) * len(windows) * len(operations)} rolling features")
            
        except Exception as e:
            logger.error(f"Error creating rolling features: {e}")
            raise
            
        return df
        
    def create_time_features(self, df: pd.DataFrame, timestamp_column: str = None) -> pd.DataFrame:
        """
        Create time-based features from datetime index or column.
        
        Args:
            df: DataFrame with datetime index or column
            timestamp_column: Name of timestamp column (if not using index)
            
        Returns:
            DataFrame with time features added
        """
        logger.info("Creating time-based features")
        
        try:
            df = df.copy()
            
            # Determine timestamp source
            if timestamp_column and timestamp_column in df.columns:
                timestamps = pd.to_datetime(df[timestamp_column])
            elif isinstance(df.index, pd.DatetimeIndex):
                timestamps = df.index
            else:
                logger.warning("No valid timestamp found, skipping time features")
                return df
                
            # Create time features
            df['hour'] = timestamps.hour
            df['day_of_week'] = timestamps.dayofweek
            df['day_of_month'] = timestamps.day
            df['month'] = timestamps.month
            df['quarter'] = timestamps.quarter
            df['year'] = timestamps.year
            
            # Cyclical encoding for periodic features
            df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
            
            df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
            df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
            
            df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
            df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
            
            # Weekend indicator
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
            
            # Market hours (assuming crypto trades 24/7, but can be customized)
            df['is_market_hours'] = 1  # Crypto markets are always open
            
            logger.info("Created comprehensive time-based features")
            
        except Exception as e:
            logger.error(f"Error creating time features: {e}")
            raise
            
        return df
        
    def encode_categorical_features(self, 
                                  df: pd.DataFrame,
                                  columns: List[str],
                                  method: str = 'onehot') -> pd.DataFrame:
        """
        Encode categorical features using various methods.
        
        Args:
            df: DataFrame with categorical features
            columns: Categorical columns to encode
            method: Encoding method ('onehot', 'label', 'target')
            
        Returns:
            DataFrame with encoded features
        """
        logger.info(f"Encoding {len(columns)} categorical features using {method}")
        
        try:
            df = df.copy()
            
            for col in columns:
                if col not in df.columns:
                    continue
                    
                if method == 'onehot':
                    # One-hot encoding
                    if col not in self.encoders:
                        self.encoders[col] = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
                        
                    encoder = self.encoders[col]
                    encoded = encoder.fit_transform(df[[col]])
                    
                    # Create new column names
                    feature_names = [f'{col}_{cat}' for cat in encoder.categories_[0]]
                    encoded_df = pd.DataFrame(encoded, columns=feature_names, index=df.index)
                    
                    # Add to original dataframe and remove original
                    df = pd.concat([df.drop(columns=[col]), encoded_df], axis=1)
                    
                elif method == 'label':
                    # Label encoding
                    if col not in self.encoders:
                        self.encoders[col] = LabelEncoder()
                        
                    encoder = self.encoders[col]
                    df[f'{col}_encoded'] = encoder.fit_transform(df[col].astype(str))
                    
                else:
                    raise ValueError(f"Unknown encoding method: {method}")
                    
            logger.info(f"Successfully encoded categorical features")
            
        except Exception as e:
            logger.error(f"Error encoding categorical features: {e}")
            raise
            
        return df
        
    def resample_time_series(self, 
                           df: pd.DataFrame,
                           freq: str = '1H',
                           agg_methods: Dict[str, str] = None) -> pd.DataFrame:
        """
        Resample time series data to different frequencies.
        
        Args:
            df: DataFrame with datetime index
            freq: Target frequency ('1H', '1D', '4H', etc.)
            agg_methods: Dictionary mapping columns to aggregation methods
            
        Returns:
            Resampled DataFrame
        """
        logger.info(f"Resampling time series to {freq} frequency")
        
        try:
            if not isinstance(df.index, pd.DatetimeIndex):
                logger.error("DataFrame must have DatetimeIndex for resampling")
                return df
                
            # Default aggregation methods
            if agg_methods is None:
                agg_methods = {
                    'open': 'first',
                    'high': 'max', 
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }
                
            # Apply resampling with different aggregation methods per column
            resampled_data = {}
            
            for col in df.columns:
                if col in agg_methods:
                    method = agg_methods[col]
                else:
                    method = 'mean'  # Default method
                    
                if method == 'ohlc' and col in ['close', 'price']:
                    # Special OHLC handling for price columns
                    ohlc = df[col].resample(freq).ohlc()
                    resampled_data[f'{col}_open'] = ohlc['open']
                    resampled_data[f'{col}_high'] = ohlc['high']
                    resampled_data[f'{col}_low'] = ohlc['low']
                    resampled_data[f'{col}_close'] = ohlc['close']
                else:
                    resampled_data[col] = getattr(df[col].resample(freq), method)()
                    
            resampled_df = pd.DataFrame(resampled_data)
            
            logger.info(f"Resampled from {len(df)} to {len(resampled_df)} rows")
            
        except Exception as e:
            logger.error(f"Error resampling time series: {e}")
            raise
            
        return resampled_df
        
    def apply_log_transform(self, 
                          df: pd.DataFrame,
                          columns: List[str],
                          method: str = 'log1p') -> pd.DataFrame:
        """
        Apply logarithmic transformations to reduce skewness.
        
        Args:
            df: DataFrame to transform
            columns: Columns to apply log transform
            method: Log method ('log1p', 'log', 'log10')
            
        Returns:
            DataFrame with log-transformed features
        """
        logger.info(f"Applying {method} transform to {len(columns)} columns")
        
        try:
            df = df.copy()
            
            for col in columns:
                if col not in df.columns:
                    continue
                    
                # Ensure positive values for log transform
                min_val = df[col].min()
                if min_val <= 0:
                    logger.warning(f"Column {col} has non-positive values, adding offset")
                    df[col] = df[col] - min_val + 1
                    
                if method == 'log1p':
                    df[f'{col}_log1p'] = np.log1p(df[col])
                elif method == 'log':
                    df[f'{col}_log'] = np.log(df[col])
                elif method == 'log10':
                    df[f'{col}_log10'] = np.log10(df[col])
                else:
                    raise ValueError(f"Unknown log method: {method}")
                    
            logger.info("Successfully applied log transformations")
            
        except Exception as e:
            logger.error(f"Error applying log transform: {e}")
            raise
            
        return df
        
    def create_interaction_features(self, 
                                  df: pd.DataFrame,
                                  feature_pairs: List[Tuple[str, str]],
                                  operations: List[str] = ['multiply', 'divide', 'add', 'subtract']) -> pd.DataFrame:
        """
        Create interaction features between pairs of columns.
        
        Args:
            df: DataFrame with features
            feature_pairs: List of (col1, col2) tuples to create interactions
            operations: List of operations to apply
            
        Returns:
            DataFrame with interaction features added
        """
        logger.info(f"Creating interaction features for {len(feature_pairs)} pairs")
        
        try:
            df = df.copy()
            
            for col1, col2 in feature_pairs:
                if col1 not in df.columns or col2 not in df.columns:
                    continue
                    
                for op in operations:
                    if op == 'multiply':
                        df[f'{col1}_x_{col2}'] = df[col1] * df[col2]
                    elif op == 'divide':
                        df[f'{col1}_div_{col2}'] = df[col1] / (df[col2] + 1e-8)  # Avoid division by zero
                    elif op == 'add':
                        df[f'{col1}_plus_{col2}'] = df[col1] + df[col2]
                    elif op == 'subtract':
                        df[f'{col1}_minus_{col2}'] = df[col1] - df[col2]
                        
            logger.info(f"Created {len(feature_pairs) * len(operations)} interaction features")
            
        except Exception as e:
            logger.error(f"Error creating interaction features: {e}")
            raise
            
        return df
        
    def apply_pca_transformation(self, 
                               df: pd.DataFrame,
                               columns: List[str],
                               n_components: Union[int, float] = 0.95,
                               prefix: str = 'pca') -> pd.DataFrame:
        """
        Apply PCA dimensionality reduction to features.
        
        Args:
            df: DataFrame with features
            columns: Columns to apply PCA to
            n_components: Number of components or variance ratio to retain
            prefix: Prefix for PCA component column names
            
        Returns:
            DataFrame with PCA components added
        """
        logger.info(f"Applying PCA to {len(columns)} features")
        
        try:
            df = df.copy()
            
            # Initialize PCA
            pca = PCA(n_components=n_components, random_state=42)
            
            # Fit and transform
            pca_features = pca.fit_transform(df[columns])
            
            # Create component column names
            n_comp = pca_features.shape[1]
            component_names = [f'{prefix}_component_{i+1}' for i in range(n_comp)]
            
            # Add PCA components to dataframe
            pca_df = pd.DataFrame(pca_features, columns=component_names, index=df.index)
            df = pd.concat([df, pca_df], axis=1)
            
            # Store PCA transformer
            self.transformers['pca'] = pca
            
            logger.info(f"Created {n_comp} PCA components explaining {pca.explained_variance_ratio_.sum():.3f} variance")
            
        except Exception as e:
            logger.error(f"Error applying PCA transformation: {e}")
            raise
            
        return df
        
    def handle_missing_values(self, 
                            df: pd.DataFrame,
                            strategy: str = 'forward_fill',
                            columns: List[str] = None) -> pd.DataFrame:
        """
        Handle missing values using various strategies.
        
        Args:
            df: DataFrame with missing values
            strategy: Strategy to handle missing values
            columns: Specific columns to handle (None for all)
            
        Returns:
            DataFrame with missing values handled
        """
        logger.info(f"Handling missing values using {strategy} strategy")
        
        try:
            df = df.copy()
            
            if columns is None:
                columns = df.columns.tolist()
                
            missing_before = df[columns].isnull().sum().sum()
            
            if strategy == 'forward_fill':
                df[columns] = df[columns].fillna(method='ffill')
            elif strategy == 'backward_fill':
                df[columns] = df[columns].fillna(method='bfill')
            elif strategy == 'mean':
                df[columns] = df[columns].fillna(df[columns].mean())
            elif strategy == 'median':
                df[columns] = df[columns].fillna(df[columns].median())
            elif strategy == 'zero':
                df[columns] = df[columns].fillna(0)
            elif strategy == 'drop':
                df = df.dropna(subset=columns)
            else:
                raise ValueError(f"Unknown missing value strategy: {strategy}")
                
            missing_after = df[columns].isnull().sum().sum()
            
            logger.info(f"Handled {missing_before - missing_after} missing values")
            
        except Exception as e:
            logger.error(f"Error handling missing values: {e}")
            raise
            
        return df
        
    def create_sequence_data(self, 
                           df: pd.DataFrame,
                           sequence_length: int = 60,
                           target_column: str = 'target',
                           feature_columns: List[str] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM/RNN models.
        
        Args:
            df: DataFrame with time series data
            sequence_length: Length of input sequences
            target_column: Column containing targets
            feature_columns: Columns to use as features
            
        Returns:
            Tuple of (X_sequences, y_sequences) as numpy arrays
        """
        logger.info(f"Creating sequences with length {sequence_length}")
        
        try:
            if feature_columns is None:
                feature_columns = [col for col in df.columns if col != target_column]
                
            # Extract features and targets
            X_data = df[feature_columns].values
            y_data = df[target_column].values if target_column in df.columns else None
            
            # Create sequences
            X_sequences = []
            y_sequences = []
            
            for i in range(sequence_length, len(X_data)):
                X_sequences.append(X_data[i-sequence_length:i])
                if y_data is not None:
                    y_sequences.append(y_data[i])
                    
            X_sequences = np.array(X_sequences)
            y_sequences = np.array(y_sequences) if y_sequences else None
            
            logger.info(f"Created {len(X_sequences)} sequences with shape {X_sequences.shape}")
            
            return X_sequences, y_sequences
            
        except Exception as e:
            logger.error(f"Error creating sequences: {e}")
            raise
            
    def inverse_transform_predictions(self, 
                                    predictions: np.ndarray,
                                    scaler_name: str = 'standard',
                                    target_column: str = 'target') -> np.ndarray:
        """
        Inverse transform scaled predictions back to original scale.
        
        Args:
            predictions: Scaled predictions
            scaler_name: Name of scaler used
            target_column: Target column name
            
        Returns:
            Predictions in original scale
        """
        try:
            if scaler_name in self.scalers:
                scaler = self.scalers[scaler_name]
                # This is a simplified version - in practice you'd need to handle
                # the specific target column scaling properly
                return scaler.inverse_transform(predictions.reshape(-1, 1)).flatten()
            else:
                logger.warning(f"Scaler {scaler_name} not found, returning original predictions")
                return predictions
                
        except Exception as e:
            logger.error(f"Error inverse transforming predictions: {e}")
            return predictions
            
    def get_transformation_summary(self) -> Dict[str, Any]:
        """Get summary of all applied transformations"""
        return {
            'scalers': list(self.scalers.keys()),
            'encoders': list(self.encoders.keys()),
            'transformers': list(self.transformers.keys()),
            'available_methods': {
                'scaling': self.scaling_methods,
                'targets': self.target_methods
            }
        }
