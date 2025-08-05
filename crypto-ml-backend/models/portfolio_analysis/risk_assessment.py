"""
Risk assessment models for cryptocurrency portfolios.
Uses machine learning to predict portfolio risk and volatility.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

from typing import Dict, List, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class RiskAssessment:
    """
    ML-based risk assessment for cryptocurrency portfolios.
    Predicts VaR, volatility, and other risk metrics.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Model parameters
        self.lookback_period = config.get('lookback_period', 252)  # 1 year
        self.confidence_levels = config.get('confidence_levels', [0.95, 0.99])
        self.volatility_model = config.get('volatility_model', 'garch')
        
        # ML models for risk prediction
        self.var_model = None
        self.volatility_model_ml = None
        self.correlation_model = None
        
        # Scalers
        self.scaler = StandardScaler()
        
        # Risk metrics cache
        self.risk_metrics_cache = {}
        
    def calculate_portfolio_returns(self, 
                                  prices: pd.DataFrame,
                                  weights: np.ndarray) -> pd.Series:
        """
        Calculate portfolio returns given asset prices and weights.
        
        Args:
            prices: DataFrame of asset prices
            weights: Portfolio weights
            
        Returns:
            Series of portfolio returns
        """
        # Calculate individual asset returns
        returns = prices.pct_change().dropna()
        
        # Calculate portfolio returns
        portfolio_returns = (returns * weights).sum(axis=1)
        
        return portfolio_returns
        
    def calculate_var(self, 
                     returns: pd.Series,
                     confidence_level: float = 0.95,
                     method: str = 'historical') -> float:
        """
        Calculate Value at Risk (VaR).
        
        Args:
            returns: Series of returns
            confidence_level: Confidence level (0.95 = 95%)
            method: VaR calculation method
            
        Returns:
            VaR value
        """
        if method == 'historical':
            # Historical VaR
            var = np.percentile(returns, (1 - confidence_level) * 100)
            
        elif method == 'parametric':
            # Parametric VaR (assuming normal distribution)
            mean_return = returns.mean()
            std_return = returns.std()
            var = mean_return - stats.norm.ppf(confidence_level) * std_return
            
        elif method == 'cornish_fisher':
            # Cornish-Fisher expansion (accounts for skewness and kurtosis)
            mean_return = returns.mean()
            std_return = returns.std()
            skewness = returns.skew()
            kurtosis = returns.kurtosis()
            
            # Z-score adjustment
            z = stats.norm.ppf(confidence_level)
            z_cf = (z + 
                   (z**2 - 1) * skewness / 6 +
                   (z**3 - 3*z) * kurtosis / 24 -
                   (2*z**3 - 5*z) * skewness**2 / 36)
            
            var = mean_return - z_cf * std_return
            
        else:
            raise ValueError(f"Unknown VaR method: {method}")
            
        return var
        
    def calculate_cvar(self, 
                      returns: pd.Series,
                      confidence_level: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR/Expected Shortfall).
        
        Args:
            returns: Series of returns
            confidence_level: Confidence level
            
        Returns:
            CVaR value
        """
        var = self.calculate_var(returns, confidence_level, 'historical')
        
        # CVaR is the mean of returns below VaR
        tail_returns = returns[returns <= var]
        
        if len(tail_returns) > 0:
            cvar = tail_returns.mean()
        else:
            cvar = var
            
        return cvar
        
    def calculate_maximum_drawdown(self, returns: pd.Series) -> Dict[str, float]:
        """
        Calculate maximum drawdown and related metrics.
        
        Args:
            returns: Series of returns
            
        Returns:
            Dictionary of drawdown metrics
        """
        # Calculate cumulative returns
        cumulative_returns = (1 + returns).cumprod()
        
        # Calculate running maximum
        running_max = cumulative_returns.expanding().max()
        
        # Calculate drawdown
        drawdown = (cumulative_returns - running_max) / running_max
        
        # Maximum drawdown
        max_drawdown = drawdown.min()
        
        # Duration of maximum drawdown
        max_dd_end = drawdown.idxmin()
        max_dd_start = cumulative_returns.loc[:max_dd_end].idxmax()
        max_dd_duration = (max_dd_end - max_dd_start).days
        
        # Recovery time (if recovered)
        recovery_threshold = cumulative_returns.loc[max_dd_start]
        post_dd_data = cumulative_returns.loc[max_dd_end:]
        recovery_dates = post_dd_data[post_dd_data >= recovery_threshold]
        
        if len(recovery_dates) > 0:
            recovery_time = (recovery_dates.index[0] - max_dd_end).days
        else:
            recovery_time = None  # Not yet recovered
            
        return {
            'max_drawdown': max_drawdown,
            'max_drawdown_start': max_dd_start,
            'max_drawdown_end': max_dd_end,
            'max_drawdown_duration': max_dd_duration,
            'recovery_time': recovery_time,
            'current_drawdown': drawdown.iloc[-1]
        }
        
    def estimate_garch_volatility(self, returns: pd.Series) -> np.ndarray:
        """
        Estimate volatility using GARCH model.
        
        Args:
            returns: Series of returns
            
        Returns:
            Array of conditional volatilities
        """
        try:
            from arch import arch_model
            
            # Fit GARCH(1,1) model
            model = arch_model(returns * 100, vol='Garch', p=1, q=1)
            result = model.fit(disp='off')
            
            # Extract conditional volatilities
            volatilities = result.conditional_volatility / 100
            
            return volatilities.values
            
        except ImportError:
            logger.warning("ARCH package not available, using rolling volatility")
            # Fallback to rolling volatility
            return returns.rolling(window=20).std().values
            
    def build_risk_prediction_models(self, 
                                   features: pd.DataFrame,
                                   targets: Dict[str, pd.Series]) -> Dict[str, Any]:
        """
        Build ML models to predict risk metrics.
        
        Args:
            features: Feature matrix (technical indicators, market data, etc.)
            targets: Dictionary of target variables (volatility, VaR, etc.)
            
        Returns:
            Dictionary of trained models and performance metrics
        """
        models = {}
        performance = {}
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        for target_name, target_values in targets.items():
            logger.info(f"Training model for {target_name}")
            
            # Align features and targets
            aligned_features, aligned_targets = self._align_data(features_scaled, target_values)
            
            if len(aligned_targets) < 50:  # Minimum data requirement
                logger.warning(f"Insufficient data for {target_name} model")
                continue
                
            # Try different models
            model_candidates = {
                'random_forest': RandomForestRegressor(
                    n_estimators=100, 
                    max_depth=10, 
                    random_state=42
                ),
                'gradient_boosting': GradientBoostingRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )
            }
            
            best_model = None
            best_score = -np.inf
            
            for model_name, model in model_candidates.items():
                try:
                    # Cross-validation
                    cv_scores = cross_val_score(
                        model, aligned_features, aligned_targets,
                        cv=5, scoring='neg_mean_squared_error'
                    )
                    
                    mean_score = cv_scores.mean()
                    
                    if mean_score > best_score:
                        best_score = mean_score
                        best_model = model
                        
                except Exception as e:
                    logger.warning(f"Error training {model_name} for {target_name}: {e}")
                    continue
                    
            if best_model is not None:
                # Train best model on full data
                best_model.fit(aligned_features, aligned_targets)
                
                models[target_name] = best_model
                performance[target_name] = {
                    'cv_score': best_score,
                    'cv_std': cv_scores.std(),
                    'model_type': type(best_model).__name__
                }
                
                logger.info(f"Best model for {target_name}: {type(best_model).__name__} (CV score: {best_score:.4f})")
                
        # Store models
        self.var_model = models.get('var')
        self.volatility_model_ml = models.get('volatility')
        
        return {
            'models': models,
            'performance': performance,
            'scaler': self.scaler
        }
        
    def predict_portfolio_risk(self, 
                             portfolio_returns: pd.Series,
                             features: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Comprehensive risk assessment for a portfolio.
        
        Args:
            portfolio_returns: Series of portfolio returns
            features: Optional features for ML prediction
            
        Returns:
            Dictionary of risk metrics
        """
        risk_metrics = {}
        
        # Basic statistical metrics
        risk_metrics.update({
            'returns_mean': portfolio_returns.mean(),
            'returns_std': portfolio_returns.std(),
            'annualized_volatility': portfolio_returns.std() * np.sqrt(252),
            'skewness': portfolio_returns.skew(),
            'kurtosis': portfolio_returns.kurtosis(),
            'sharpe_ratio': self._calculate_sharpe_ratio(portfolio_returns)
        })
        
        # VaR and CVaR
        for confidence_level in self.confidence_levels:
            var_hist = self.calculate_var(portfolio_returns, confidence_level, 'historical')
            var_param = self.calculate_var(portfolio_returns, confidence_level, 'parametric')
            cvar = self.calculate_cvar(portfolio_returns, confidence_level)
            
            risk_metrics.update({
                f'var_{int(confidence_level*100)}_historical': var_hist,
                f'var_{int(confidence_level*100)}_parametric': var_param,
                f'cvar_{int(confidence_level*100)}': cvar
            })
            
        # Maximum drawdown
        drawdown_metrics = self.calculate_maximum_drawdown(portfolio_returns)
        risk_metrics.update(drawdown_metrics)
        
        # GARCH volatility prediction
        try:
            garch_volatility = self.estimate_garch_volatility(portfolio_returns)
            risk_metrics['garch_volatility_latest'] = garch_volatility[-1]
            risk_metrics['garch_volatility_mean'] = np.mean(garch_volatility[-30:])  # Last 30 days
        except Exception as e:
            logger.warning(f"GARCH volatility estimation failed: {e}")
            
        # ML-based predictions (if models available and features provided)
        if features is not None and self.var_model is not None:
            try:
                features_scaled = self.scaler.transform(features.iloc[-1:])  # Latest features
                
                if self.var_model:
                    predicted_var = self.var_model.predict(features_scaled)[0]
                    risk_metrics['predicted_var_95'] = predicted_var
                    
                if self.volatility_model_ml:
                    predicted_vol = self.volatility_model_ml.predict(features_scaled)[0]
                    risk_metrics['predicted_volatility'] = predicted_vol
                    
            except Exception as e:
                logger.warning(f"ML risk prediction failed: {e}")
                
        # Risk score (composite metric)
        risk_metrics['risk_score'] = self._calculate_risk_score(risk_metrics)
        
        return risk_metrics
        
    def assess_portfolio_concentration(self, weights: np.ndarray) -> Dict[str, float]:
        """
        Assess portfolio concentration risk.
        
        Args:
            weights: Portfolio weights
            
        Returns:
            Dictionary of concentration metrics
        """
        # Herfindahl-Hirschman Index
        hhi = np.sum(weights ** 2)
        
        # Effective number of assets
        effective_assets = 1 / hhi
        
        # Maximum weight
        max_weight = np.max(weights)
        
        # Concentration ratio (top 3 assets)
        top_3_weight = np.sum(np.sort(weights)[-3:])
        
        # Gini coefficient
        gini = self._calculate_gini_coefficient(weights)
        
        return {
            'herfindahl_index': hhi,
            'effective_num_assets': effective_assets,
            'max_weight': max_weight,
            'top_3_concentration': top_3_weight,
            'gini_coefficient': gini,
            'concentration_score': self._calculate_concentration_score(hhi, max_weight, gini)
        }
        
    def stress_test_portfolio(self, 
                            portfolio_returns: pd.Series,
                            scenarios: Dict[str, Dict] = None) -> Dict[str, Dict]:
        """
        Perform stress testing on portfolio.
        
        Args:
            portfolio_returns: Historical portfolio returns
            scenarios: Custom stress scenarios
            
        Returns:
            Dictionary of stress test results
        """
        if scenarios is None:
            scenarios = {
                'market_crash': {'return_shock': -0.20, 'volatility_multiplier': 2.0},
                'crypto_winter': {'return_shock': -0.50, 'volatility_multiplier': 3.0},
                'high_volatility': {'return_shock': 0.0, 'volatility_multiplier': 2.5},
                'regulatory_shock': {'return_shock': -0.30, 'volatility_multiplier': 1.8}
            }
            
        stress_results = {}
        
        base_return = portfolio_returns.mean()
        base_volatility = portfolio_returns.std()
        
        for scenario_name, scenario_params in scenarios.items():
            # Apply shocks
            shocked_return = base_return + scenario_params.get('return_shock', 0)
            shocked_volatility = base_volatility * scenario_params.get('volatility_multiplier', 1)
            
            # Simulate stressed returns
            np.random.seed(42)  # For reproducibility
            stressed_returns = np.random.normal(
                shocked_return, 
                shocked_volatility, 
                size=len(portfolio_returns)
            )
            
            # Calculate stressed metrics
            stressed_var_95 = np.percentile(stressed_returns, 5)
            stressed_cvar_95 = np.mean(stressed_returns[stressed_returns <= stressed_var_95])
            
            stress_results[scenario_name] = {
                'return_impact': shocked_return - base_return,
                'volatility_impact': shocked_volatility - base_volatility,
                'stressed_var_95': stressed_var_95,
                'stressed_cvar_95': stressed_cvar_95,
                'probability_of_loss': np.mean(stressed_returns < 0)
            }
            
        return stress_results
        
    def _align_data(self, features: np.ndarray, targets: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
        """Align features and targets by removing NaN values"""
        # Convert to DataFrame for easier handling
        features_df = pd.DataFrame(features, index=targets.index[:len(features)])
        
        # Remove rows with NaN values
        combined = pd.concat([features_df, targets], axis=1, join='inner')
        combined = combined.dropna()
        
        if len(combined) == 0:
            return np.array([]), np.array([])
            
        aligned_features = combined.iloc[:, :-1].values
        aligned_targets = combined.iloc[:, -1].values
        
        return aligned_features, aligned_targets
        
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        
    def _calculate_risk_score(self, risk_metrics: Dict[str, Any]) -> float:
        """Calculate composite risk score (0-100, higher = riskier)"""
        # Normalize key metrics
        volatility_score = min(100, risk_metrics.get('annualized_volatility', 0) * 100)
        var_score = min(100, abs(risk_metrics.get('var_95_historical', 0)) * 200)
        drawdown_score = min(100, abs(risk_metrics.get('max_drawdown', 0)) * 100)
        
        # Weighted combination
        risk_score = (
            volatility_score * 0.4 +
            var_score * 0.3 +
            drawdown_score * 0.3
        )
        
        return min(100, max(0, risk_score))
        
    def _calculate_gini_coefficient(self, weights: np.ndarray) -> float:
        """Calculate Gini coefficient for portfolio weights"""
        sorted_weights = np.sort(weights)
        n = len(weights)
        cumsum = np.cumsum(sorted_weights)
        
        return (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n
        
    def _calculate_concentration_score(self, hhi: float, max_weight: float, gini: float) -> float:
        """Calculate composite concentration score (0-100, higher = more concentrated)"""
        hhi_score = min(100, hhi * 100)
        max_weight_score = min(100, max_weight * 100)
        gini_score = gini * 100
        
        return (hhi_score * 0.4 + max_weight_score * 0.4 + gini_score * 0.2)
