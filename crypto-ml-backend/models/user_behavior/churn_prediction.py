"""
Churn prediction model for cryptocurrency trading platform users.
Predicts likelihood of user leaving the platform based on behavior patterns.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from typing import Dict, List, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ChurnPredictor:
    """
    Predicts user churn based on trading behavior, portfolio metrics, and engagement patterns.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Model parameters
        self.prediction_horizon = config.get('prediction_horizon', 30)  # days
        self.feature_lookback = config.get('feature_lookback', 90)  # days
        self.churn_threshold = config.get('churn_threshold', 30)  # days of inactivity = churn
        
        # Models
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        # Feature importance
        self.feature_importance = {}
        
    def create_user_features(self, user_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Create features for churn prediction from user data.
        
        Args:
            user_data: Dictionary containing user information and activity
            
        Returns:
            Dictionary of engineered features
        """
        features = {}
        
        # Account features
        features['account_age_days'] = user_data.get('account_age_days', 0)
        features['is_verified'] = float(user_data.get('is_verified', False))
        features['kyc_level'] = user_data.get('kyc_level', 0)
        
        # Trading activity features
        trading_data = user_data.get('trading_activity', {})
        features['total_trades'] = trading_data.get('total_trades', 0)
        features['trades_last_30d'] = trading_data.get('trades_last_30d', 0)
        features['trades_last_7d'] = trading_data.get('trades_last_7d', 0)
        features['avg_trade_size'] = trading_data.get('avg_trade_size', 0)
        features['total_volume'] = trading_data.get('total_volume', 0)
        features['volume_last_30d'] = trading_data.get('volume_last_30d', 0)
        features['days_since_last_trade'] = trading_data.get('days_since_last_trade', 999)
        
        # Portfolio features
        portfolio_data = user_data.get('portfolio', {})
        features['portfolio_value'] = portfolio_data.get('total_value', 0)
        features['num_assets'] = portfolio_data.get('num_assets', 0)
        features['portfolio_diversity'] = portfolio_data.get('diversity_score', 0)
        features['unrealized_pnl'] = portfolio_data.get('unrealized_pnl', 0)
        features['realized_pnl'] = portfolio_data.get('realized_pnl', 0)
        features['total_deposits'] = portfolio_data.get('total_deposits', 0)
        features['total_withdrawals'] = portfolio_data.get('total_withdrawals', 0)
        
        # Engagement features
        engagement_data = user_data.get('engagement', {})
        features['login_frequency'] = engagement_data.get('logins_last_30d', 0)
        features['session_duration_avg'] = engagement_data.get('avg_session_duration', 0)
        features['days_since_last_login'] = engagement_data.get('days_since_last_login', 999)
        features['app_opens_last_7d'] = engagement_data.get('app_opens_last_7d', 0)
        features['push_notifications_enabled'] = float(engagement_data.get('push_enabled', False))
        
        # Behavioral patterns
        behavior_data = user_data.get('behavior_patterns', {})
        features['risk_tolerance'] = behavior_data.get('risk_score', 0.5)
        features['trading_frequency_trend'] = behavior_data.get('frequency_trend', 0)  # increasing/decreasing
        features['volume_trend'] = behavior_data.get('volume_trend', 0)
        features['profit_loss_ratio'] = behavior_data.get('win_rate', 0.5)
        
        # Support and issues
        support_data = user_data.get('support', {})
        features['support_tickets'] = support_data.get('total_tickets', 0)
        features['support_tickets_last_30d'] = support_data.get('tickets_last_30d', 0)
        features['unresolved_issues'] = support_data.get('unresolved_count', 0)
        
        # Market conditions impact
        market_data = user_data.get('market_context', {})
        features['performance_vs_market'] = market_data.get('relative_performance', 0)
        features['active_during_bull_market'] = float(market_data.get('bull_market_activity', False))
        features['active_during_bear_market'] = float(market_data.get('bear_market_activity', False))
        
        # Derived features
        if features['total_trades'] > 0:
            features['avg_days_between_trades'] = features['account_age_days'] / features['total_trades']
            features['trade_size_consistency'] = 1.0 / (1.0 + trading_data.get('trade_size_std', 1.0))
        else:
            features['avg_days_between_trades'] = 999
            features['trade_size_consistency'] = 0
            
        if features['total_deposits'] > 0:
            features['withdrawal_ratio'] = features['total_withdrawals'] / features['total_deposits']
        else:
            features['withdrawal_ratio'] = 0
            
        # Activity decay features
        features['login_decay'] = np.exp(-features['days_since_last_login'] / 7)  # Exponential decay
        features['trading_decay'] = np.exp(-features['days_since_last_trade'] / 14)
        
        # Engagement score
        features['engagement_score'] = (
            features['login_decay'] * 0.3 +
            features['trading_decay'] * 0.4 +
            min(1.0, features['app_opens_last_7d'] / 7) * 0.3
        )
        
        return features
        
    def prepare_training_data(self, user_history: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare training data from user history.
        
        Args:
            user_history: List of user data snapshots with churn labels
            
        Returns:
            Tuple of (features_df, labels_series)
        """
        features_list = []
        labels_list = []
        
        for user_snapshot in user_history:
            # Extract features
            features = self.create_user_features(user_snapshot)
            features_list.append(features)
            
            # Extract label (churned or not)
            is_churned = user_snapshot.get('churned', False)
            labels_list.append(int(is_churned))
            
        # Create DataFrames
        features_df = pd.DataFrame(features_list)
        labels_series = pd.Series(labels_list)
        
        # Handle missing values
        features_df = features_df.fillna(0)
        
        # Encode categorical features if any
        categorical_features = ['kyc_level']  # Add more if needed
        for feature in categorical_features:
            if feature in features_df.columns:
                if feature not in self.label_encoders:
                    self.label_encoders[feature] = LabelEncoder()
                    
                features_df[feature] = self.label_encoders[feature].fit_transform(
                    features_df[feature].astype(str)
                )
                
        logger.info(f"Prepared training data: {len(features_df)} samples, {len(features_df.columns)} features")
        logger.info(f"Churn rate: {labels_series.mean():.3f}")
        
        return features_df, labels_series
        
    def train(self, 
             features_df: pd.DataFrame,
             labels_series: pd.Series,
             test_size: float = 0.2) -> Dict[str, Any]:
        """
        Train the churn prediction model.
        
        Args:
            features_df: Feature matrix
            labels_series: Target labels
            test_size: Proportion of data for testing
            
        Returns:
            Training metrics and model performance
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features_df, labels_series,
            test_size=test_size,
            random_state=42,
            stratify=labels_series
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Try different models
        models = {
            'random_forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                class_weight='balanced'
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            ),
            'logistic_regression': LogisticRegression(
                random_state=42,
                class_weight='balanced',
                max_iter=1000
            )
        }
        
        best_model = None
        best_score = 0
        model_scores = {}
        
        # Evaluate models using cross-validation
        for model_name, model in models.items():
            try:
                if model_name == 'logistic_regression':
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='roc_auc')
                else:
                    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='roc_auc')
                    
                mean_score = cv_scores.mean()
                model_scores[model_name] = {
                    'cv_score': mean_score,
                    'cv_std': cv_scores.std()
                }
                
                if mean_score > best_score:
                    best_score = mean_score
                    best_model = model
                    
                logger.info(f"{model_name}: CV ROC-AUC = {mean_score:.4f} (+/- {cv_scores.std() * 2:.4f})")
                
            except Exception as e:
                logger.warning(f"Error training {model_name}: {e}")
                
        if best_model is None:
            raise ValueError("No model could be trained successfully")
            
        # Train best model on full training data
        if isinstance(best_model, LogisticRegression):
            best_model.fit(X_train_scaled, y_train)
            y_pred = best_model.predict(X_test_scaled)
            y_pred_proba = best_model.predict_proba(X_test_scaled)[:, 1]
        else:
            best_model.fit(X_train, y_train)
            y_pred = best_model.predict(X_test)
            y_pred_proba = best_model.predict_proba(X_test)[:, 1]
            
        self.model = best_model
        
        # Calculate test metrics
        test_auc = roc_auc_score(y_test, y_pred_proba)
        
        # Feature importance
        if hasattr(best_model, 'feature_importances_'):
            feature_names = features_df.columns.tolist()
            importances = best_model.feature_importances_
            self.feature_importance = dict(zip(feature_names, importances))
            
        # Generate classification report
        class_report = classification_report(y_test, y_pred, output_dict=True)
        
        training_results = {
            'best_model': type(best_model).__name__,
            'cv_scores': model_scores,
            'test_auc': test_auc,
            'classification_report': class_report,
            'feature_importance': self.feature_importance,
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
        
        logger.info(f"Best model: {type(best_model).__name__} with ROC-AUC: {test_auc:.4f}")
        
        return training_results
        
    def predict_churn_probability(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict churn probability for a single user.
        
        Args:
            user_data: User data dictionary
            
        Returns:
            Prediction results
        """
        if self.model is None:
            raise ValueError("Model must be trained before prediction")
            
        # Create features
        features = self.create_user_features(user_data)
        features_df = pd.DataFrame([features])
        
        # Handle categorical encoding
        for feature, encoder in self.label_encoders.items():
            if feature in features_df.columns:
                try:
                    features_df[feature] = encoder.transform(features_df[feature].astype(str))
                except ValueError:
                    # Handle unseen categories
                    features_df[feature] = 0
                    
        # Scale features if using logistic regression
        if isinstance(self.model, LogisticRegression):
            features_scaled = self.scaler.transform(features_df)
            churn_proba = self.model.predict_proba(features_scaled)[0, 1]
        else:
            churn_proba = self.model.predict_proba(features_df)[0, 1]
            
        # Risk assessment
        if churn_proba >= 0.8:
            risk_level = 'HIGH'
        elif churn_proba >= 0.5:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
            
        # Identify key risk factors
        risk_factors = self._identify_risk_factors(features)
        
        return {
            'churn_probability': float(churn_proba),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'user_features': features,
            'recommendation': self._generate_retention_recommendation(churn_proba, risk_factors)
        }
        
    def batch_predict(self, users_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Predict churn probability for multiple users.
        
        Args:
            users_data: List of user data dictionaries
            
        Returns:
            List of prediction results
        """
        predictions = []
        
        for user_data in users_data:
            try:
                prediction = self.predict_churn_probability(user_data)
                prediction['user_id'] = user_data.get('user_id', 'unknown')
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Error predicting for user {user_data.get('user_id', 'unknown')}: {e}")
                
        return predictions
        
    def _identify_risk_factors(self, features: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify key factors contributing to churn risk"""
        risk_factors = []
        
        # Days since last login
        if features.get('days_since_last_login', 0) > 14:
            risk_factors.append({
                'factor': 'Inactivity',
                'description': f"{features['days_since_last_login']:.0f} days since last login",
                'severity': 'HIGH' if features['days_since_last_login'] > 30 else 'MEDIUM'
            })
            
        # Days since last trade
        if features.get('days_since_last_trade', 0) > 21:
            risk_factors.append({
                'factor': 'No Trading Activity',
                'description': f"{features['days_since_last_trade']:.0f} days since last trade",
                'severity': 'HIGH' if features['days_since_last_trade'] > 45 else 'MEDIUM'
            })
            
        # Low engagement score
        if features.get('engagement_score', 0) < 0.3:
            risk_factors.append({
                'factor': 'Low Engagement',
                'description': f"Engagement score: {features['engagement_score']:.2f}",
                'severity': 'MEDIUM'
            })
            
        # Negative P&L
        if features.get('unrealized_pnl', 0) < -0.1:  # More than 10% loss
            risk_factors.append({
                'factor': 'Portfolio Losses',
                'description': f"Unrealized P&L: {features['unrealized_pnl']:.1%}",
                'severity': 'HIGH'
            })
            
        # Support issues
        if features.get('unresolved_issues', 0) > 0:
            risk_factors.append({
                'factor': 'Unresolved Support Issues',
                'description': f"{features['unresolved_issues']:.0f} open tickets",
                'severity': 'HIGH'
            })
            
        return risk_factors
        
    def _generate_retention_recommendation(self, 
                                         churn_probability: float,
                                         risk_factors: List[Dict]) -> List[str]:
        """Generate retention recommendations based on churn probability and risk factors"""
        recommendations = []
        
        if churn_probability >= 0.8:
            recommendations.append("URGENT: Contact user immediately with personalized offer")
            recommendations.append("Provide dedicated account manager support")
            
        if churn_probability >= 0.5:
            recommendations.append("Send targeted retention campaign")
            recommendations.append("Offer trading fee discount or bonus")
            
        # Specific recommendations based on risk factors
        risk_factor_types = [rf['factor'] for rf in risk_factors]
        
        if 'Inactivity' in risk_factor_types:
            recommendations.append("Send re-engagement email with market updates")
            recommendations.append("Offer educational content or webinar invitation")
            
        if 'No Trading Activity' in risk_factor_types:
            recommendations.append("Provide trading insights and market opportunities")
            recommendations.append("Offer demo trading or paper trading features")
            
        if 'Portfolio Losses' in risk_factor_types:
            recommendations.append("Provide risk management education")
            recommendations.append("Suggest portfolio rebalancing or diversification")
            
        if 'Unresolved Support Issues' in risk_factor_types:
            recommendations.append("Escalate support tickets immediately")
            recommendations.append("Provide direct line to senior support")
            
        return recommendations
        
    def get_feature_importance(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """Get top N most important features for churn prediction"""
        if not self.feature_importance:
            return []
            
        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_features[:top_n]
