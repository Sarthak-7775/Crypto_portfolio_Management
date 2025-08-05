"""
Multi-source sentiment aggregator for comprehensive market sentiment analysis.
Combines news, social media, and other sentiment sources.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from collections import defaultdict

from .bert_sentiment import BERTSentimentAnalyzer

logger = logging.getLogger(__name__)

class SentimentAggregator:
    """
    Aggregates sentiment from multiple sources to provide comprehensive market sentiment.
    Handles temporal aggregation, source weighting, and confidence scoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Source weights
        self.source_weights = config.get('source_weights', {
            'news': 0.4,
            'twitter': 0.3,
            'reddit': 0.2,
            'telegram': 0.1
        })
        
        # Temporal weights (recent data gets higher weight)
        self.temporal_decay = config.get('temporal_decay', 0.1)  # per hour
        
        # Sentiment analyzers
        self.analyzers = {}
        
        # Initialize BERT analyzer
        bert_config = config.get('bert_config', {})
        self.bert_analyzer = BERTSentimentAnalyzer(bert_config)
        
        # Aggregation parameters
        self.min_confidence = config.get('min_confidence', 0.5)
        self.sentiment_threshold = config.get('sentiment_threshold', 0.1)
        
    def add_analyzer(self, name: str, analyzer) -> None:
        """Add a sentiment analyzer"""
        self.analyzers[name] = analyzer
        
    def process_batch_sentiment(self, 
                              data: List[Dict[str, Any]],
                              analyzer_name: str = 'bert') -> List[Dict[str, Any]]:
        """
        Process a batch of texts for sentiment analysis.
        
        Args:
            data: List of dictionaries with 'text', 'source', 'timestamp' keys
            analyzer_name: Name of analyzer to use
            
        Returns:
            List of sentiment analysis results
        """
        # Extract texts
        texts = [item['text'] for item in data]
        
        # Analyze sentiment
        if analyzer_name == 'bert':
            predictions = self.bert_analyzer.predict(texts)
        elif analyzer_name in self.analyzers:
            predictions = self.analyzers[analyzer_name].predict(texts)
        else:
            logger.error(f"Unknown analyzer: {analyzer_name}")
            return []
            
        # Combine with original data
        results = []
        for i, (original, prediction) in enumerate(zip(data, predictions)):
            result = {
                **original,  # Original data
                **prediction,  # Sentiment prediction
                'analyzer': analyzer_name,
                'processed_at': datetime.utcnow()
            }
            results.append(result)
            
        return results
        
    def calculate_temporal_weight(self, timestamp: datetime, reference_time: datetime = None) -> float:
        """
        Calculate temporal weight based on how recent the data is.
        
        Args:
            timestamp: Timestamp of the data
            reference_time: Reference time (default: now)
            
        Returns:
            Temporal weight (0-1)
        """
        if reference_time is None:
            reference_time = datetime.utcnow()
            
        # Calculate hours difference
        time_diff = (reference_time - timestamp).total_seconds() / 3600
        
        # Apply exponential decay
        weight = np.exp(-self.temporal_decay * time_diff)
        
        return min(1.0, max(0.0, weight))  # Clamp to [0, 1]
        
    def aggregate_sentiment(self, 
                          sentiment_data: List[Dict[str, Any]],
                          crypto_symbol: str = None,
                          time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Aggregate sentiment from multiple sources and time periods.
        
        Args:
            sentiment_data: List of sentiment analysis results
            crypto_symbol: Specific crypto to analyze (None for general sentiment)
            time_window_hours: Time window for analysis
            
        Returns:
            Aggregated sentiment metrics
        """
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(hours=time_window_hours)
        
        # Filter by time window and crypto symbol
        filtered_data = []
        for item in sentiment_data:
            # Check time window
            timestamp = item.get('timestamp')
            if isinstance(timestamp, str):
                timestamp = pd.to_datetime(timestamp)
            
            if timestamp < cutoff_time:
                continue
                
            # Check crypto symbol if specified
            if crypto_symbol:
                text_lower = item.get('text', '').lower()
                symbol_lower = crypto_symbol.lower()
                if symbol_lower not in text_lower and f'${symbol_lower}' not in text_lower:
                    continue
                    
            # Check confidence threshold
            if item.get('confidence', 0) < self.min_confidence:
                continue
                
            filtered_data.append(item)
            
        if not filtered_data:
            return self._get_neutral_sentiment()
            
        # Group by source
        source_sentiments = defaultdict(list)
        for item in filtered_data:
            source = item.get('source', 'unknown')
            source_sentiments[source].append(item)
            
        # Calculate weighted sentiment for each source
        source_scores = {}
        total_weight = 0
        
        for source, items in source_sentiments.items():
            source_weight = self.source_weights.get(source, 0.1)
            
            # Calculate temporal-weighted sentiment for this source
            weighted_scores = []
            weights = []
            
            for item in items:
                timestamp = item.get('timestamp')
                if isinstance(timestamp, str):
                    timestamp = pd.to_datetime(timestamp)
                    
                temporal_weight = self.calculate_temporal_weight(timestamp, current_time)
                confidence = item.get('confidence', 0.5)
                sentiment_score = item.get('sentiment_score', 0)
                
                # Combined weight: source * temporal * confidence
                combined_weight = source_weight * temporal_weight * confidence
                
                weighted_scores.append(sentiment_score * combined_weight)
                weights.append(combined_weight)
                
            if weights:
                source_avg = sum(weighted_scores) / sum(weights)
                source_scores[source] = {
                    'sentiment': source_avg,
                    'weight': source_weight,
                    'count': len(items),
                    'avg_confidence': np.mean([item.get('confidence', 0) for item in items])
                }
                total_weight += source_weight
                
        # Calculate overall aggregated sentiment
        if not source_scores:
            return self._get_neutral_sentiment()
            
        overall_sentiment = sum(
            scores['sentiment'] * scores['weight'] 
            for scores in source_scores.values()
        ) / total_weight
        
        # Calculate additional metrics
        all_scores = [item.get('sentiment_score', 0) for item in filtered_data]
        all_confidences = [item.get('confidence', 0) for item in filtered_data]
        
        # Sentiment distribution
        positive_count = sum(1 for score in all_scores if score > self.sentiment_threshold)
        negative_count = sum(1 for score in all_scores if score < -self.sentiment_threshold)
        neutral_count = len(all_scores) - positive_count - negative_count
        
        # Volatility (standard deviation of sentiment scores)
        sentiment_volatility = np.std(all_scores) if len(all_scores) > 1 else 0
        
        # Momentum (recent vs older sentiment)
        recent_cutoff = current_time - timedelta(hours=6)
        recent_scores = [
            item.get('sentiment_score', 0) for item in filtered_data
            if pd.to_datetime(item.get('timestamp')) > recent_cutoff
        ]
        older_scores = [
            item.get('sentiment_score', 0) for item in filtered_data
            if pd.to_datetime(item.get('timestamp')) <= recent_cutoff
        ]
        
        sentiment_momentum = 0
        if recent_scores and older_scores:
            sentiment_momentum = np.mean(recent_scores) - np.mean(older_scores)
            
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_label': self._score_to_label(overall_sentiment),
            'confidence': np.mean(all_confidences),
            'total_mentions': len(filtered_data),
            'source_breakdown': source_scores,
            'sentiment_distribution': {
                'positive': positive_count,
                'neutral': neutral_count,
                'negative': negative_count,
                'positive_pct': positive_count / len(all_scores) * 100,
                'negative_pct': negative_count / len(all_scores) * 100,
                'neutral_pct': neutral_count / len(all_scores) * 100
            },
            'sentiment_volatility': sentiment_volatility,
            'sentiment_momentum': sentiment_momentum,
            'analysis_period': f"{time_window_hours} hours",
            'crypto_symbol': crypto_symbol,
            'timestamp': current_time.isoformat()
        }
        
    def analyze_multiple_cryptos(self, 
                               sentiment_data: List[Dict[str, Any]],
                               crypto_symbols: List[str],
                               time_window_hours: int = 24) -> Dict[str, Dict[str, Any]]:
        """
        Analyze sentiment for multiple cryptocurrencies.
        
        Args:
            sentiment_data: List of sentiment analysis results
            crypto_symbols: List of crypto symbols to analyze
            time_window_hours: Time window for analysis
            
        Returns:
            Dictionary of sentiment analysis per crypto
        """
        results = {}
        
        for symbol in crypto_symbols:
            results[symbol] = self.aggregate_sentiment(
                sentiment_data, symbol, time_window_hours
            )
            
        # Add market-wide sentiment (no specific crypto filter)
        results['MARKET_OVERALL'] = self.aggregate_sentiment(
            sentiment_data, None, time_window_hours
        )
        
        return results
        
    def get_sentiment_signals(self, 
                            aggregated_sentiment: Dict[str, Any],
                            signal_thresholds: Dict[str, float] = None) -> List[Dict[str, Any]]:
        """
        Generate trading signals based on sentiment analysis.
        
        Args:
            aggregated_sentiment: Aggregated sentiment data
            signal_thresholds: Custom thresholds for signal generation
            
        Returns:
            List of trading signals
        """
        if signal_thresholds is None:
            signal_thresholds = {
                'strong_bullish': 0.5,
                'bullish': 0.2,
                'bearish': -0.2,
                'strong_bearish': -0.5,
                'high_volatility': 0.3,
                'momentum_threshold': 0.1
            }
            
        signals = []
        sentiment_score = aggregated_sentiment.get('overall_sentiment', 0)
        volatility = aggregated_sentiment.get('sentiment_volatility', 0)
        momentum = aggregated_sentiment.get('sentiment_momentum', 0)
        confidence = aggregated_sentiment.get('confidence', 0)
        
        # Sentiment-based signals
        if sentiment_score >= signal_thresholds['strong_bullish']:
            signals.append({
                'type': 'sentiment',
                'signal': 'STRONG_BULLISH',
                'strength': min(1.0, sentiment_score),
                'confidence': confidence,
                'description': f"Very positive sentiment detected ({sentiment_score:.3f})"
            })
        elif sentiment_score >= signal_thresholds['bullish']:
            signals.append({
                'type': 'sentiment',
                'signal': 'BULLISH',
                'strength': sentiment_score,
                'confidence': confidence,
                'description': f"Positive sentiment detected ({sentiment_score:.3f})"
            })
        elif sentiment_score <= signal_thresholds['strong_bearish']:
            signals.append({
                'type': 'sentiment',
                'signal': 'STRONG_BEARISH',
                'strength': min(1.0, abs(sentiment_score)),
                'confidence': confidence,
                'description': f"Very negative sentiment detected ({sentiment_score:.3f})"
            })
        elif sentiment_score <= signal_thresholds['bearish']:
            signals.append({
                'type': 'sentiment',
                'signal': 'BEARISH',
                'strength': abs(sentiment_score),
                'confidence': confidence,
                'description': f"Negative sentiment detected ({sentiment_score:.3f})"
            })
            
        # Volatility-based signals
        if volatility >= signal_thresholds['high_volatility']:
            signals.append({
                'type': 'volatility',
                'signal': 'HIGH_VOLATILITY',
                'strength': min(1.0, volatility),
                'confidence': confidence,
                'description': f"High sentiment volatility detected ({volatility:.3f})"
            })
            
        # Momentum-based signals
        if abs(momentum) >= signal_thresholds['momentum_threshold']:
            direction = 'POSITIVE' if momentum > 0 else 'NEGATIVE'
            signals.append({
                'type': 'momentum',
                'signal': f'{direction}_MOMENTUM',
                'strength': min(1.0, abs(momentum)),
                'confidence': confidence,
                'description': f"Sentiment momentum shift detected ({momentum:.3f})"
            })
            
        return signals
        
    def _get_neutral_sentiment(self) -> Dict[str, Any]:
        """Return neutral sentiment structure"""
        return {
            'overall_sentiment': 0.0,
            'sentiment_label': 'neutral',
            'confidence': 0.0,
            'total_mentions': 0,
            'source_breakdown': {},
            'sentiment_distribution': {
                'positive': 0,
                'neutral': 0,
                'negative': 0,
                'positive_pct': 0,
                'negative_pct': 0,
                'neutral_pct': 0
            },
            'sentiment_volatility': 0.0,
            'sentiment_momentum': 0.0,
            'analysis_period': '24 hours',
            'crypto_symbol': None,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    def _score_to_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > self.sentiment_threshold:
            return 'positive'
        elif score < -self.sentiment_threshold:
            return 'negative'
        else:
            return 'neutral'
            
    def create_sentiment_report(self, 
                              crypto_results: Dict[str, Dict[str, Any]]) -> str:
        """
        Create a formatted sentiment analysis report.
        
        Args:
            crypto_results: Results from analyze_multiple_cryptos
            
        Returns:
            Formatted report string
        """
        report = "\n" + "="*60 + "\n"
        report += "CRYPTOCURRENCY SENTIMENT ANALYSIS REPORT\n"
        report += "="*60 + "\n\n"
        
        for crypto, data in crypto_results.items():
            if crypto == 'MARKET_OVERALL':
                report += f"📊 OVERALL MARKET SENTIMENT\n"
            else:
                report += f"💰 {crypto.upper()} SENTIMENT\n"
                
            report += f"   Overall Score: {data['overall_sentiment']:.3f} ({data['sentiment_label'].upper()})\n"
            report += f"   Confidence: {data['confidence']:.1%}\n"
            report += f"   Total Mentions: {data['total_mentions']}\n"
            
            # Distribution
            dist = data['sentiment_distribution']
            report += f"   Distribution: {dist['positive_pct']:.1f}% pos, "
            report += f"{dist['neutral_pct']:.1f}% neu, {dist['negative_pct']:.1f}% neg\n"
            
            # Volatility and momentum
            report += f"   Volatility: {data['sentiment_volatility']:.3f}\n"
            report += f"   Momentum: {data['sentiment_momentum']:.3f}\n"
            
            # Source breakdown
            if data['source_breakdown']:
                report += "   Sources:\n"
                for source, info in data['source_breakdown'].items():
                    report += f"     {source}: {info['sentiment']:.3f} ({info['count']} mentions)\n"
                    
            report += "\n"
            
        report += "="*60 + "\n"
        
        return report
