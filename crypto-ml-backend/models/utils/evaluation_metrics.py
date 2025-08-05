"""
Comprehensive evaluation metrics for ML models.
Provides financial and statistical metrics for model assessment.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns

class ModelEvaluator:
    """Comprehensive model evaluation class"""
    
    @staticmethod
    def evaluate_price_prediction(y_true: np.ndarray, 
                                y_pred: np.ndarray,
                                prices: np.ndarray = None) -> Dict[str, float]:
        """
        Evaluate price prediction models with financial metrics.
        
        Args:
            y_true: True values (returns or prices)
            y_pred: Predicted values
            prices: Original prices for return calculation
            
        Returns:
            Dictionary of evaluation metrics
        """
        # Basic regression metrics
        mse = np.mean((y_true - y_pred) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y_true - y_pred))
        mape = np.mean(np.abs((y_true - y_pred) / np.abs(y_true))) * 100
        
        # R-squared
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = 1 - (ss_res / ss_tot)
        
        # Directional accuracy
        direction_true = np.sign(np.diff(y_true))
        direction_pred = np.sign(np.diff(y_pred))
        directional_accuracy = np.mean(direction_true == direction_pred)
        
        # Hit rate (for classification-like interpretation)
        hit_rate = np.mean(np.abs(y_true - y_pred) < np.std(y_true))
        
        metrics = {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'mape': mape,
            'r2': r2,
            'directional_accuracy': directional_accuracy,
            'hit_rate': hit_rate
        }
        
        # Financial metrics if prices provided
        if prices is not None:
            try:
                # Calculate returns
                true_returns = np.diff(prices) / prices[:-1]
                
                # Simulate trading based on predictions
                trading_signals = np.sign(y_pred[1:])  # Buy/sell signals
                strategy_returns = trading_signals * true_returns
                
                # Performance metrics
                total_return = np.prod(1 + strategy_returns) - 1
                annualized_return = (1 + total_return) ** (252 / len(strategy_returns)) - 1
                volatility = np.std(strategy_returns) * np.sqrt(252)
                sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
                
                # Maximum drawdown
                cumulative_returns = np.cumprod(1 + strategy_returns)
                running_max = np.maximum.accumulate(cumulative_returns)
                drawdown = (cumulative_returns - running_max) / running_max
                max_drawdown = np.min(drawdown)
                
                metrics.update({
                    'total_return': total_return,
                    'annualized_return': annualized_return,
                    'volatility': volatility,
                    'sharpe_ratio': sharpe_ratio,
                    'max_drawdown': max_drawdown,
                    'win_rate': np.mean(strategy_returns > 0)
                })
                
            except Exception as e:
                print(f"Warning: Could not calculate financial metrics: {e}")
                
        return metrics
        
    @staticmethod
    def evaluate_classification(y_true: np.ndarray, 
                              y_pred: np.ndarray,
                              y_pred_proba: np.ndarray = None) -> Dict[str, any]:
        """
        Evaluate classification models.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities (optional)
            
        Returns:
            Dictionary of evaluation metrics
        """
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted'),
            'recall': recall_score(y_true, y_pred, average='weighted'),
            'f1': f1_score(y_true, y_pred, average='weighted'),
        }
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm
        
        # Classification report
        metrics['classification_report'] = classification_report(y_true, y_pred)
        
        # ROC AUC if probabilities provided
        if y_pred_proba is not None:
            try:
                from sklearn.metrics import roc_auc_score
                if len(np.unique(y_true)) == 2:  # Binary classification
                    metrics['roc_auc'] = roc_auc_score(y_true, y_pred_proba[:, 1])
                else:  # Multi-class
                    metrics['roc_auc'] = roc_auc_score(y_true, y_pred_proba, 
                                                     multi_class='ovr', average='weighted')
            except Exception as e:
                print(f"Warning: Could not calculate ROC AUC: {e}")
                
        return metrics
        
    @staticmethod
    def evaluate_sentiment_model(y_true: np.ndarray,
                               y_pred: np.ndarray,
                               sentiment_labels: List[str] = None) -> Dict[str, any]:
        """
        Evaluate sentiment analysis models.
        
        Args:
            y_true: True sentiment labels
            y_pred: Predicted sentiment labels
            sentiment_labels: Label names for reporting
            
        Returns:
            Dictionary of evaluation metrics
        """
        if sentiment_labels is None:
            sentiment_labels = ['negative', 'neutral', 'positive']
            
        metrics = ModelEvaluator.evaluate_classification(y_true, y_pred)
        
        # Sentiment-specific metrics
        per_class_precision = precision_score(y_true, y_pred, average=None)
        per_class_recall = recall_score(y_true, y_pred, average=None)
        per_class_f1 = f1_score(y_true, y_pred, average=None)
        
        for i, label in enumerate(sentiment_labels):
            if i < len(per_class_precision):
                metrics[f'{label}_precision'] = per_class_precision[i]
                metrics[f'{label}_recall'] = per_class_recall[i]
                metrics[f'{label}_f1'] = per_class_f1[i]
                
        return metrics
        
    @staticmethod
    def evaluate_portfolio_model(predicted_weights: np.ndarray,
                               returns: np.ndarray,
                               benchmark_returns: np.ndarray = None) -> Dict[str, float]:
        """
        Evaluate portfolio optimization models.
        
        Args:
            predicted_weights: Portfolio weights over time
            returns: Asset returns matrix
            benchmark_returns: Benchmark returns for comparison
            
        Returns:
            Dictionary of portfolio metrics
        """
        # Calculate portfolio returns
        portfolio_returns = np.sum(predicted_weights * returns, axis=1)
        
        # Portfolio metrics
        total_return = np.prod(1 + portfolio_returns) - 1
        annualized_return = (1 + total_return) ** (252 / len(portfolio_returns)) - 1
        volatility = np.std(portfolio_returns) * np.sqrt(252)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = np.cumprod(1 + portfolio_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdown)
        
        # Sortino ratio
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_deviation = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = annualized_return / downside_deviation if downside_deviation > 0 else 0
        
        # Calmar ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        metrics = {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'win_rate': np.mean(portfolio_returns > 0)
        }
        
        # Benchmark comparison if provided
        if benchmark_returns is not None:
            benchmark_total_return = np.prod(1 + benchmark_returns) - 1
            excess_return = total_return - benchmark_total_return
            
            # Information ratio
            tracking_error = np.std(portfolio_returns - benchmark_returns) * np.sqrt(252)
            information_ratio = excess_return / tracking_error if tracking_error > 0 else 0
            
            # Beta
            covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
            benchmark_variance = np.var(benchmark_returns)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
            
            # Alpha (Jensen's alpha)
            risk_free_rate = 0.02  # Assume 2% risk-free rate
            alpha = annualized_return - (risk_free_rate + beta * 
                    (np.mean(benchmark_returns) * 252 - risk_free_rate))
            
            metrics.update({
                'excess_return': excess_return,
                'information_ratio': information_ratio,
                'beta': beta,
                'alpha': alpha,
                'tracking_error': tracking_error
            })
            
        return metrics
        
    @staticmethod
    def plot_prediction_results(y_true: np.ndarray,
                              y_pred: np.ndarray,
                              title: str = "Prediction Results",
                              timestamps: pd.DatetimeIndex = None) -> None:
        """
        Plot prediction results for visual evaluation.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            title: Plot title
            timestamps: Timestamps for x-axis
        """
        plt.figure(figsize=(12, 6))
        
        if timestamps is not None:
            plt.plot(timestamps, y_true, label='Actual', alpha=0.8)
            plt.plot(timestamps, y_pred, label='Predicted', alpha=0.8)
        else:
            plt.plot(y_true, label='Actual', alpha=0.8)
            plt.plot(y_pred, label='Predicted', alpha=0.8)
            
        plt.title(title)
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
        
    @staticmethod
    def plot_confusion_matrix(y_true: np.ndarray,
                            y_pred: np.ndarray,
                            labels: List[str] = None,
                            title: str = "Confusion Matrix") -> None:
        """
        Plot confusion matrix for classification models.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            labels: Class labels
            title: Plot title
        """
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=labels, yticklabels=labels)
        plt.title(title)
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        plt.show()
        
    @staticmethod
    def create_evaluation_report(model_name: str,
                               metrics: Dict[str, float],
                               model_type: str = "regression") -> str:
        """
        Create a formatted evaluation report.
        
        Args:
            model_name: Name of the model
            metrics: Dictionary of metrics
            model_type: Type of model for formatting
            
        Returns:
            Formatted report string
        """
        report = f"\n{'='*50}\n"
        report += f"Model Evaluation Report: {model_name}\n"
        report += f"{'='*50}\n\n"
        
        if model_type == "regression":
            report += "Regression Metrics:\n"
            report += f"  R² Score: {metrics.get('r2', 0):.4f}\n"
            report += f"  RMSE: {metrics.get('rmse', 0):.4f}\n"
            report += f"  MAE: {metrics.get('mae', 0):.4f}\n"
            report += f"  MAPE: {metrics.get('mape', 0):.2f}%\n"
            report += f"  Directional Accuracy: {metrics.get('directional_accuracy', 0):.4f}\n"
            
            if 'sharpe_ratio' in metrics:
                report += "\nFinancial Metrics:\n"
                report += f"  Total Return: {metrics.get('total_return', 0):.2%}\n"
                report += f"  Annualized Return: {metrics.get('annualized_return', 0):.2%}\n"
                report += f"  Volatility: {metrics.get('volatility', 0):.2%}\n"
                report += f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.4f}\n"
                report += f"  Max Drawdown: {metrics.get('max_drawdown', 0):.2%}\n"
                
        elif model_type == "classification":
            report += "Classification Metrics:\n"
            report += f"  Accuracy: {metrics.get('accuracy', 0):.4f}\n"
            report += f"  Precision: {metrics.get('precision', 0):.4f}\n"
            report += f"  Recall: {metrics.get('recall', 0):.4f}\n"
            report += f"  F1 Score: {metrics.get('f1', 0):.4f}\n"
            
            if 'roc_auc' in metrics:
                report += f"  ROC AUC: {metrics.get('roc_auc', 0):.4f}\n"
                
        report += f"\n{'='*50}\n"
        
        return report
