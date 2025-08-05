"""
ML Models package for cryptocurrency portfolio management.
Provides price prediction, sentiment analysis, portfolio optimization, and user behavior models.
"""

from .price_prediction import LSTMPredictor, XGBoostPredictor, EnsemblePredictor
from .sentiment_analysis import NewseSentimentAnalyzer, SocialSentimentAnalyzer, SentimentAggregator
from .portfolio_analysis import RiskAssessment, PortfolioOptimizer, PerformanceAnalyzer
from .user_behavior import ChurnPredictor, RecommendationEngine, TradingPatternAnalyzer

__version__ = "1.0.0"
__all__ = [
    "LSTMPredictor", "XGBoostPredictor", "EnsemblePredictor",
    "NewsSentimentAnalyzer", "SocialSentimentAnalyzer", "SentimentAggregator",
    "RiskAssessment", "PortfolioOptimizer", "PerformanceAnalyzer",
    "ChurnPredictor", "RecommendationEngine", "TradingPatternAnalyzer"
]
