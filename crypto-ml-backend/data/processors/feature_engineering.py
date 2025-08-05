"""
Advanced feature engineering for cryptocurrency machine learning.
Creates technical indicators, sentiment features, and market signals.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import talib
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """
    Comprehensive feature engineering for cryptocurrency ML models.
    Creates technical indicators, sentiment features, and advanced market signals.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.scalers = {}
        self.feature_columns = []
        
        # Technical indicator parameters
        self.ta_params = {
            'sma_periods': [5, 10, 20, 50, 200],
            'ema_periods': [12, 26, 50],
            'rsi_period': 14,
            'macd_params': {'fast': 12, 'slow': 26, 'signal': 9},
            'bb_period': 20,
            'bb_std': 2,
            'stoch_params': {'k_period': 14, 'd_period': 3},
            'atr_period': 14,
            'cci_period': 20,
            'williams_period': 14
        }
        
    def create_technical_features(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """
        Create comprehensive technical analysis features.
        
        Args:
            price_data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with technical features added
        """
        logger.info("Creating technical analysis features")
        
        df = price_data.copy()
        
        # Ensure required columns exist
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
                
        try:
            # Price-based indicators
            df = self._add_moving_averages(df)
            df = self._add_momentum_indicators(df)
            df = self._add_volatility_indicators(df)
            df = self._add_volume_indicators(df)
            df = self._add_price_patterns(df)
            
            # Advanced features
            df = self._add_market_structure_features(df)
            df = self._add_statistical_features(df)
            
            logger.info(f"Created {len(df.columns) - len(price_data.columns)} technical features")
            
        except Exception as e:
            logger.error(f"Error creating technical features: {e}")
            raise
            
        return df
        
    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add various moving average indicators"""
        close = df['close'].values
        
        # Simple Moving Averages
        for period in self.ta_params['sma_periods']:
            df[f'sma_{period}'] = talib.SMA(close, timeperiod=period)
            df[f'price_vs_sma_{period}'] = df['close'] / df[f'sma_{period}'] - 1
            
        # Exponential Moving Averages
        for period in self.ta_params['ema_periods']:
            df[f'ema_{period}'] = talib.EMA(close, timeperiod=period)
            df[f'price_vs_ema_{period}'] = df['close'] / df[f'ema_{period}'] - 1
            
        # DEMA and TEMA
        df['dema_21'] = talib.DEMA(close, timeperiod=21)
        df['tema_21'] = talib.TEMA(close, timeperiod=21)
        
        # Moving Average Convergence
        df['sma_5_20_ratio'] = df['sma_5'] / df['sma_20']
        df['ema_12_26_ratio'] = df['ema_12'] / df['ema_26']
        
        return df
        
    def _add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum-based indicators"""
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        # RSI
        df['rsi'] = talib.RSI(close, timeperiod=self.ta_params['rsi_period'])
        df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
        df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
        
        # MACD
        macd_params = self.ta_params['macd_params']
        df['macd'], df['macd_signal'], df['macd_histogram'] = talib.MACD(
            close, 
            fastperiod=macd_params['fast'],
            slowperiod=macd_params['slow'],
            signalperiod=macd_params['signal']
        )
        df['macd_bullish'] = (df['macd'] > df['macd_signal']).astype(int)
        
        # Stochastic Oscillator
        stoch_params = self.ta_params['stoch_params']
        df['stoch_k'], df['stoch_d'] = talib.STOCH(
            high, low, close,
            fastk_period=stoch_params['k_period'],
            slowk_period=stoch_params['d_period'],
            slowd_period=stoch_params['d_period']
        )
        
        # Williams %R
        df['williams_r'] = talib.WILLR(high, low, close, timeperiod=self.ta_params['williams_period'])
        
        # CCI (Commodity Channel Index)
        df['cci'] = talib.CCI(high, low, close, timeperiod=self.ta_params['cci_period'])
        
        # ROC (Rate of Change)
        for period in [1, 5, 10, 20]:
            df[f'roc_{period}'] = talib.ROC(close, timeperiod=period)
            
        # Momentum
        df['momentum_10'] = talib.MOM(close, timeperiod=10)
        
        return df
        
    def _add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility-based indicators"""
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        # Bollinger Bands
        bb_period = self.ta_params['bb_period']
        bb_std = self.ta_params['bb_std']
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(
            close, timeperiod=bb_period, nbdevup=bb_std, nbdevdn=bb_std
        )
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (close - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Average True Range
        df['atr'] = talib.ATR(high, low, close, timeperiod=self.ta_params['atr_period'])
        df['atr_ratio'] = df['atr'] / close
        
        # True Range
        df['true_range'] = talib.TRANGE(high, low, close)
        
        # Standard Deviation
        df['price_std_20'] = close.rolling(window=20).std()
        df['price_std_ratio'] = df['price_std_20'] / close
        
        return df
        
    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based indicators"""
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        volume = df['volume'].values
        
        # Volume Moving Averages
        df['volume_sma_20'] = talib.SMA(volume, timeperiod=20)
        df['volume_ratio'] = volume / df['volume_sma_20']
        
        # On-Balance Volume
        df['obv'] = talib.OBV(close, volume)
        df['obv_sma_20'] = talib.SMA(df['obv'].values, timeperiod=20)
        df['obv_ratio'] = df['obv'] / df['obv_sma_20']
        
        # Accumulation/Distribution Line
        df['ad'] = talib.AD(high, low, close, volume)
        
        # Chaikin Money Flow
        df['cmf'] = self._calculate_cmf(df, period=20)
        
        # Volume Price Trend
        df['vpt'] = self._calculate_vpt(df)
        
        # Volume-Weighted Average Price (approximation)
        df['vwap'] = self._calculate_vwap(df, period=20)
        df['price_vs_vwap'] = close / df['vwap'] - 1
        
        return df
        
    def _add_price_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add price pattern recognition features"""
        open_prices = df['open'].values
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        # Candlestick patterns (selection of most important ones)
        df['doji'] = talib.CDLDOJI(open_prices, high, low, close)
        df['hammer'] = talib.CDLHAMMER(open_prices, high, low, close)
        df['shooting_star'] = talib.CDLSHOOTINGSTAR(open_prices, high, low, close)
        df['engulfing_bullish'] = talib.CDLENGULFING(open_prices, high, low, close)
        df['morning_star'] = talib.CDLMORNINGSTAR(open_prices, high, low, close)
        df['evening_star'] = talib.CDLEVENINGSTAR(open_prices, high, low, close)
        
        # Price gaps
        df['gap_up'] = ((df['open'] > df['high'].shift(1)) & (df['open'] > df['close'].shift(1))).astype(int)
        df['gap_down'] = ((df['open'] < df['low'].shift(1)) & (df['open'] < df['close'].shift(1))).astype(int)
        
        # Support and Resistance levels (simplified)
        df['is_local_high'] = self._identify_local_extremes(df['high'], window=5, extreme_type='high')
        df['is_local_low'] = self._identify_local_extremes(df['low'], window=5, extreme_type='low')
        
        return df
        
    def _add_market_structure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market structure and regime features"""
        close = df['close'].values
        
        # Trend strength
        df['trend_strength'] = self._calculate_trend_strength(df)
        
        # Market regime indicators
        df['volatility_regime'] = self._identify_volatility_regime(df)
        df['trend_regime'] = self._identify_trend_regime(df)
        
        # Price fractals
        df['fractal_high'] = self._identify_fractals(df['high'], fractal_type='high')
        df['fractal_low'] = self._identify_fractals(df['low'], fractal_type='low')
        
        # Higher highs and lower lows
        df['higher_high'] = self._identify_higher_highs(df['high'])
        df['lower_low'] = self._identify_lower_lows(df['low'])
        
        return df
        
    def _add_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add statistical features"""
        close = df['close'].values
        
        # Rolling statistics
        for window in [5, 10, 20, 50]:
            df[f'price_mean_{window}'] = df['close'].rolling(window=window).mean()
            df[f'price_std_{window}'] = df['close'].rolling(window=window).std()
            df[f'price_skew_{window}'] = df['close'].rolling(window=window).skew()
            df[f'price_kurt_{window}'] = df['close'].rolling(window=window).kurt()
            
        # Z-scores
        df['price_zscore_20'] = (df['close'] - df['price_mean_20']) / df['price_std_20']
        
        # Percentile ranks
        df['price_percentile_20'] = df['close'].rolling(window=20).rank(pct=True)
        df['volume_percentile_20'] = df['volume'].rolling(window=20).rank(pct=True)
        
        return df
        
    def create_sentiment_features(self, sentiment_data: List[Dict]) -> pd.DataFrame:
        """
        Create features from news and social media sentiment data.
        
        Args:
            sentiment_data: List of sentiment dictionaries with timestamp, score, source
            
        Returns:
            DataFrame with sentiment features
        """
        logger.info("Creating sentiment features")
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(sentiment_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Resample to hourly data
            hourly_sentiment = df.groupby('source').resample('1H').agg({
                'sentiment_score': ['mean', 'std', 'count'],
                'relevance_score': 'mean'
            }).fillna(0)
            
            # Flatten column names
            hourly_sentiment.columns = ['_'.join(col).strip() for col in hourly_sentiment.columns.values]
            
            # Create aggregate features across all sources
            sentiment_features = pd.DataFrame()
            sentiment_features['sentiment_mean'] = hourly_sentiment.groupby(level=1)['sentiment_score_mean'].mean()
            sentiment_features['sentiment_std'] = hourly_sentiment.groupby(level=1)['sentiment_score_std'].mean()
            sentiment_features['sentiment_volume'] = hourly_sentiment.groupby(level=1)['sentiment_score_count'].sum()
            sentiment_features['relevance_mean'] = hourly_sentiment.groupby(level=1)['relevance_score_mean'].mean()
            
            # Rolling sentiment features
            for window in [6, 12, 24]:  # 6, 12, 24 hours
                sentiment_features[f'sentiment_sma_{window}'] = sentiment_features['sentiment_mean'].rolling(window=window).mean()
                sentiment_features[f'sentiment_momentum_{window}'] = sentiment_features['sentiment_mean'].rolling(window=window).apply(
                    lambda x: (x[-1] - x[0]) / window if len(x) == window else 0
                )
                
            # Sentiment regime indicators
            sentiment_features['sentiment_bullish'] = (sentiment_features['sentiment_mean'] > 0.1).astype(int)
            sentiment_features['sentiment_bearish'] = (sentiment_features['sentiment_mean'] < -0.1).astype(int)
            sentiment_features['sentiment_neutral'] = (
                (sentiment_features['sentiment_mean'] >= -0.1) & 
                (sentiment_features['sentiment_mean'] <= 0.1)
            ).astype(int)
            
            logger.info(f"Created {len(sentiment_features.columns)} sentiment features")
            
        except Exception as e:
            logger.error(f"Error creating sentiment features: {e}")
            raise
            
        return sentiment_features
        
    # Helper methods for complex calculations
    def _calculate_cmf(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Chaikin Money Flow"""
        mfv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low']) * df['volume']
        return mfv.rolling(window=period).sum() / df['volume'].rolling(window=period).sum()
        
    def _calculate_vpt(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Volume Price Trend"""
        price_change = df['close'].pct_change()
        return (price_change * df['volume']).cumsum()
        
    def _calculate_vwap(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Volume Weighted Average Price"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        return (typical_price * df['volume']).rolling(window=period).sum() / df['volume'].rolling(window=period).sum()
        
    def _identify_local_extremes(self, series: pd.Series, window: int = 5, extreme_type: str = 'high') -> pd.Series:
        """Identify local highs or lows"""
        if extreme_type == 'high':
            return series.rolling(window=window*2+1, center=True).max() == series
        else:
            return series.rolling(window=window*2+1, center=True).min() == series
            
    def _calculate_trend_strength(self, df: pd.DataFrame) -> pd.Series:
        """Calculate trend strength using multiple moving averages"""
        sma_5 = df['sma_5']
        sma_20 = df['sma_20']
        sma_50 = df['sma_50']
        
        # Count aligned moving averages
        uptrend_strength = (sma_5 > sma_20).astype(int) + (sma_20 > sma_50).astype(int)
        downtrend_strength = (sma_5 < sma_20).astype(int) + (sma_20 < sma_50).astype(int)
        
        return uptrend_strength - downtrend_strength
        
    def _identify_volatility_regime(self, df: pd.DataFrame) -> pd.Series:
        """Identify volatility regime (low, medium, high)"""
        atr_percentile = df['atr'].rolling(window=100).rank(pct=True)
        
        volatility_regime = pd.Series(index=df.index, dtype=int)
        volatility_regime[atr_percentile < 0.33] = 0  # Low volatility
        volatility_regime[(atr_percentile >= 0.33) & (atr_percentile < 0.67)] = 1  # Medium volatility
        volatility_regime[atr_percentile >= 0.67] = 2  # High volatility
        
        return volatility_regime
        
    def _identify_trend_regime(self, df: pd.DataFrame) -> pd.Series:
        """Identify trend regime using price vs moving averages"""
        price_above_sma_20 = df['close'] > df['sma_20']
        price_above_sma_50 = df['close'] > df['sma_50']
        
        trend_regime = pd.Series(index=df.index, dtype=int)
        trend_regime[price_above_sma_20 & price_above_sma_50] = 1    # Uptrend
        trend_regime[~price_above_sma_20 & ~price_above_sma_50] = -1  # Downtrend
        trend_regime[price_above_sma_20 != price_above_sma_50] = 0    # Sideways
        
        return trend_regime
        
    def _identify_fractals(self, series: pd.Series, fractal_type: str = 'high') -> pd.Series:
        """Identify fractal highs or lows (5-period pattern)"""
        fractals = pd.Series(False, index=series.index)
        
        for i in range(2, len(series) - 2):
            if fractal_type == 'high':
                if (series.iloc[i] > series.iloc[i-2] and 
                    series.iloc[i] > series.iloc[i-1] and 
                    series.iloc[i] > series.iloc[i+1] and 
                    series.iloc[i] > series.iloc[i+2]):
                    fractals.iloc[i] = True
            else:  # low
                if (series.iloc[i] < series.iloc[i-2] and 
                    series.iloc[i] < series.iloc[i-1] and 
                    series.iloc[i] < series.iloc[i+1] and 
                    series.iloc[i] < series.iloc[i+2]):
                    fractals.iloc[i] = True
                    
        return fractals.astype(int)
        
    def _identify_higher_highs(self, series: pd.Series, window: int = 20) -> pd.Series:
        """Identify higher highs pattern"""
        rolling_max = series.rolling(window=window).max()
        return (series > rolling_max.shift(1)).astype(int)
        
    def _identify_lower_lows(self, series: pd.Series, window: int = 20) -> pd.Series:
        """Identify lower lows pattern"""
        rolling_min = series.rolling(window=window).min()
        return (series < rolling_min.shift(1)).astype(int)
        
    def create_onchain_features(self, onchain_data: List[Dict]) -> pd.DataFrame:
        """
        Create features from on-chain blockchain data.
        
        Args:
            onchain_data: List of on-chain metrics dictionaries
            
        Returns:
            DataFrame with on-chain features
        """
        logger.info("Creating on-chain features")
        
        try:
            df = pd.DataFrame(onchain_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Create derived features
            df['active_addresses_growth'] = df['active_addresses'].pct_change()
            df['tx_volume_growth'] = df['transaction_volume'].pct_change()
            df['new_addresses_ratio'] = df['new_addresses'] / df['active_addresses']
            
            # Rolling averages
            for window in [7, 14, 30]:
                df[f'active_addresses_sma_{window}'] = df['active_addresses'].rolling(window=window).mean()
                df[f'tx_volume_sma_{window}'] = df['transaction_volume'].rolling(window=window).mean()
                
            # Network health indicators
            df['network_growth'] = (df['active_addresses'] > df['active_addresses_sma_7']).astype(int)
            df['tx_momentum'] = (df['transaction_volume'] > df['tx_volume_sma_7']).astype(int)
            
            logger.info(f"Created {len(df.columns)} on-chain features")
            
        except Exception as e:
            logger.error(f"Error creating on-chain features: {e}")
            raise
            
        return df
        
    def combine_all_features(self, 
                           price_features: pd.DataFrame,
                           sentiment_features: pd.DataFrame,
                           onchain_features: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Combine all feature sets into a single DataFrame with proper alignment.
        
        Args:
            price_features: Technical analysis features
            sentiment_features: Sentiment analysis features  
            onchain_features: On-chain features (optional)
            
        Returns:
            Combined features DataFrame
        """
        logger.info("Combining all feature sets")
        
        try:
            # Start with price features as base
            combined_df = price_features.copy()
            
            # Add sentiment features with forward fill for missing values
            if not sentiment_features.empty:
                sentiment_resampled = sentiment_features.reindex(combined_df.index, method='ffill')
                combined_df = pd.concat([combined_df, sentiment_resampled], axis=1)
                
            # Add on-chain features if available
            if onchain_features is not None and not onchain_features.empty:
                onchain_resampled = onchain_features.reindex(combined_df.index, method='ffill')
                combined_df = pd.concat([combined_df, onchain_resampled], axis=1)
                
            # Fill any remaining NaN values
            combined_df.fillna(method='ffill', inplace=True)
            combined_df.fillna(0, inplace=True)
            
            # Remove infinite values
            combined_df.replace([np.inf, -np.inf], np.nan, inplace=True)
            combined_df.fillna(0, inplace=True)
            
            self.feature_columns = combined_df.columns.tolist()
            
            logger.info(f"Combined dataset shape: {combined_df.shape}")
            
        except Exception as e:
            logger.error(f"Error combining features: {e}")
            raise
            
        return combined_df
        
    def prepare_features_for_ml(self, 
                              df: pd.DataFrame, 
                              target_column: str = 'target',
                              feature_selection: bool = True,
                              scaling: str = 'standard') -> Dict[str, Any]:
        """
        Prepare features for machine learning with scaling and selection.
        
        Args:
            df: Combined features DataFrame
            target_column: Name of target column
            feature_selection: Whether to perform feature selection
            scaling: Type of scaling ('standard', 'minmax', 'none')
            
        Returns:
            Dictionary with processed features and metadata
        """
        logger.info("Preparing features for machine learning")
        
        try:
            # Separate features and target
            if target_column in df.columns:
                y = df[target_column].values
                X = df.drop(columns=[target_column])
            else:
                y = None
                X = df.copy()
                
            # Remove constant features
            constant_features = X.columns[X.std() == 0].tolist()
            if constant_features:
                logger.info(f"Removing {len(constant_features)} constant features")
                X = X.drop(columns=constant_features)
                
            # Feature scaling
            if scaling == 'standard':
                scaler = StandardScaler()
                X_scaled = pd.DataFrame(
                    scaler.fit_transform(X),
                    columns=X.columns,
                    index=X.index
                )
                self.scalers['features'] = scaler
            elif scaling == 'minmax':
                scaler = MinMaxScaler()
                X_scaled = pd.DataFrame(
                    scaler.fit_transform(X),
                    columns=X.columns,
                    index=X.index
                )
                self.scalers['features'] = scaler
            else:
                X_scaled = X.copy()
                
            # Feature selection (optional)
            selected_features = X.columns.tolist()
            if feature_selection and y is not None:
                selected_features = self._select_important_features(X_scaled, y)
                X_scaled = X_scaled[selected_features]
                
            result = {
                'features': X_scaled,
                'target': y,
                'feature_names': selected_features,
                'scaler': self.scalers.get('features'),
                'removed_features': constant_features,
                'original_shape': df.shape,
                'final_shape': X_scaled.shape
            }
            
            logger.info(f"Final feature set: {X_scaled.shape[1]} features, {X_scaled.shape[0]} samples")
            
        except Exception as e:
            logger.error(f"Error preparing features for ML: {e}")
            raise
            
        return result
        
    def _select_important_features(self, X: pd.DataFrame, y: np.ndarray, top_k: int = 50) -> List[str]:
        """Select most important features using multiple methods"""
        from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
        from sklearn.ensemble import RandomForestRegressor
        
        try:
            # Method 1: Statistical selection
            selector_stat = SelectKBest(score_func=f_regression, k=min(top_k, X.shape[1]))
            selector_stat.fit(X, y)
            stat_features = X.columns[selector_stat.get_support()].tolist()
            
            # Method 2: Mutual information
            selector_mi = SelectKBest(score_func=mutual_info_regression, k=min(top_k, X.shape[1]))  
            selector_mi.fit(X, y)
            mi_features = X.columns[selector_mi.get_support()].tolist()
            
            # Method 3: Random Forest importance
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(X, y)
            feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': rf.feature_importances_
            }).sort_values('importance', ascending=False)
            rf_features = feature_importance.head(top_k)['feature'].tolist()
            
            # Combine and rank features
            all_selected = set(stat_features + mi_features + rf_features)
            
            # Score each feature by how many methods selected it
            feature_scores = {}
            for feature in all_selected:
                score = 0
                if feature in stat_features:
                    score += 1
                if feature in mi_features:
                    score += 1
                if feature in rf_features:
                    score += 1
                feature_scores[feature] = score
                
            # Select top features based on combined score
            selected_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)
            final_features = [feature for feature, score in selected_features[:top_k]]
            
            logger.info(f"Selected {len(final_features)} important features")
            
            return final_features
            
        except Exception as e:
            logger.warning(f"Error in feature selection, using all features: {e}")
            return X.columns.tolist()
