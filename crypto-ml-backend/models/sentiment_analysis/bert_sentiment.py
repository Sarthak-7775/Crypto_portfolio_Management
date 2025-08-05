"""
BERT-based sentiment analysis for cryptocurrency content.
Uses pre-trained transformers fine-tuned for financial sentiment.
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    Trainer, TrainingArguments, EarlyStoppingCallback
)
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)

class CryptoSentimentDataset(Dataset):
    """Dataset class for crypto sentiment data"""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.texts)
        
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class BERTSentimentAnalyzer:
    """
    BERT-based sentiment analyzer for cryptocurrency content.
    Fine-tuned for financial and crypto-specific sentiment.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Model parameters
        self.model_name = config.get('model_name', 'cardiffnlp/twitter-roberta-base-sentiment-latest')
        self.num_labels = config.get('num_labels', 3)  # negative, neutral, positive
        self.max_length = config.get('max_length', 512)
        self.learning_rate = config.get('learning_rate', 2e-5)
        self.batch_size = config.get('batch_size', 16)
        self.num_epochs = config.get('num_epochs', 3)
        
        # Initialize model and tokenizer
        self.tokenizer = None
        self.model = None
        self.is_trained = False
        
        # Label mapping
        self.label_mapping = {0: 'negative', 1: 'neutral', 2: 'positive'}
        self.reverse_label_mapping = {'negative': 0, 'neutral': 1, 'positive': 2}
        
        # Device setup
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
    def initialize_model(self):
        """Initialize tokenizer and model"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=self.num_labels
            )
            self.model.to(self.device)
            
            logger.info(f"Initialized BERT model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            raise
            
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for sentiment analysis.
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        # Clean and normalize text
        text = str(text).lower()
        
        # Replace crypto-specific terms
        crypto_replacements = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
            'hodl': 'hold',
            'fud': 'fear uncertainty doubt',
            'fomo': 'fear of missing out',
            'ath': 'all time high',
            'atl': 'all time low',
            'moon': 'price increase',
            'dump': 'price decrease',
            'pump': 'price increase',
            'rekt': 'loss'
        }
        
        for old, new in crypto_replacements.items():
            text = text.replace(old, new)
            
        return text
        
    def train(self, 
             train_texts: List[str],
             train_labels: List[str],
             val_texts: List[str] = None,
             val_labels: List[str] = None) -> Dict[str, Any]:
        """
        Fine-tune BERT model on crypto sentiment data.
        
        Args:
            train_texts: Training texts
            train_labels: Training labels
            val_texts: Validation texts
            val_labels: Validation labels
            
        Returns:
            Training metrics
        """
        if self.model is None:
            self.initialize_model()
            
        # Preprocess texts
        train_texts = [self.preprocess_text(text) for text in train_texts]
        
        # Convert labels to integers
        train_labels_int = [self.reverse_label_mapping.get(label, 1) for label in train_labels]
        
        # Create datasets
        train_dataset = CryptoSentimentDataset(
            train_texts, train_labels_int, self.tokenizer, self.max_length
        )
        
        val_dataset = None
        if val_texts and val_labels:
            val_texts = [self.preprocess_text(text) for text in val_texts]
            val_labels_int = [self.reverse_label_mapping.get(label, 1) for label in val_labels]
            val_dataset = CryptoSentimentDataset(
                val_texts, val_labels_int, self.tokenizer, self.max_length
            )
            
        # Training arguments
        training_args = TrainingArguments(
            output_dir='./crypto_sentiment_model',
            num_train_epochs=self.num_epochs,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=100,
            evaluation_strategy='steps' if val_dataset else 'no',
            eval_steps=500 if val_dataset else None,
            save_strategy='steps',
            save_steps=1000,
            load_best_model_at_end=True if val_dataset else False,
            metric_for_best_model='eval_accuracy' if val_dataset else None,
            learning_rate=self.learning_rate,
        )
        
        # Metrics computation
        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            predictions = np.argmax(predictions, axis=1)
            
            precision, recall, f1, _ = precision_recall_fscore_support(
                labels, predictions, average='weighted'
            )
            accuracy = accuracy_score(labels, predictions)
            
            return {
                'accuracy': accuracy,
                'f1': f1,
                'precision': precision,
                'recall': recall
            }
            
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=2)] if val_dataset else None,
        )
        
        # Train model
        logger.info("Starting BERT fine-tuning...")
        train_result = trainer.train()
        
        self.is_trained = True
        
        # Evaluate on validation set
        training_metrics = {
            'train_loss': train_result.training_loss,
            'train_steps': train_result.global_step,
        }
        
        if val_dataset:
            eval_result = trainer.evaluate()
            training_metrics.update({
                'eval_loss': eval_result['eval_loss'],
                'eval_accuracy': eval_result['eval_accuracy'],
                'eval_f1': eval_result['eval_f1'],
                'eval_precision': eval_result['eval_precision'],
                'eval_recall': eval_result['eval_recall']
            })
            
        logger.info(f"BERT training completed. Train loss: {training_metrics['train_loss']:.4f}")
        
        return training_metrics
        
    def predict(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Predict sentiment for texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of prediction dictionaries
        """
        if not self.is_trained:
            logger.warning("Model not fine-tuned. Using pre-trained weights.")
            if self.model is None:
                self.initialize_model()
                
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        predictions = []
        
        # Process in batches
        for i in range(0, len(processed_texts), self.batch_size):
            batch_texts = processed_texts[i:i + self.batch_size]
            
            # Tokenize batch
            inputs = self.tokenizer(
                batch_texts,
                truncation=True,
                padding=True,
                max_length=self.max_length,
                return_tensors='pt'
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
                predicted_classes = torch.argmax(logits, dim=-1)
                
            # Process results
            for j in range(len(batch_texts)):
                prediction = {
                    'text': texts[i + j],
                    'predicted_label': self.label_mapping[predicted_classes[j].item()],
                    'confidence': float(torch.max(probabilities[j])),
                    'probabilities': {
                        'negative': float(probabilities[j][0]),
                        'neutral': float(probabilities[j][1]),
                        'positive': float(probabilities[j][2])
                    },
                    'sentiment_score': float(probabilities[j][2] - probabilities[j][0])  # positive - negative
                }
                predictions.append(prediction)
                
        return predictions
        
    def predict_single(self, text: str) -> Dict[str, Any]:
        """
        Predict sentiment for a single text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Prediction dictionary
        """
        predictions = self.predict([text])
        return predictions[0]
        
    def analyze_crypto_mentions(self, texts: List[str], crypto_symbols: List[str]) -> Dict[str, Dict]:
        """
        Analyze sentiment for specific cryptocurrency mentions.
        
        Args:
            texts: List of texts
            crypto_symbols: List of crypto symbols to analyze
            
        Returns:
            Dictionary of sentiment analysis per crypto
        """
        crypto_sentiments = {symbol: [] for symbol in crypto_symbols}
        
        # Predict sentiment for all texts
        predictions = self.predict(texts)
        
        # Filter by crypto mentions
        for pred in predictions:
            text_lower = pred['text'].lower()
            for symbol in crypto_symbols:
                if symbol.lower() in text_lower or f'${symbol.lower()}' in text_lower:
                    crypto_sentiments[symbol].append(pred)
                    
        # Aggregate sentiments
        results = {}
        for symbol, sentiments in crypto_sentiments.items():
            if sentiments:
                avg_sentiment = np.mean([s['sentiment_score'] for s in sentiments])
                sentiment_counts = {
                    'positive': sum(1 for s in sentiments if s['predicted_label'] == 'positive'),
                    'neutral': sum(1 for s in sentiments if s['predicted_label'] == 'neutral'),
                    'negative': sum(1 for s in sentiments if s['predicted_label'] == 'negative')
                }
                
                results[symbol] = {
                    'average_sentiment': avg_sentiment,
                    'sentiment_counts': sentiment_counts,
                    'total_mentions': len(sentiments),
                    'confidence': np.mean([s['confidence'] for s in sentiments])
                }
            else:
                results[symbol] = {
                    'average_sentiment': 0.0,
                    'sentiment_counts': {'positive': 0, 'neutral': 0, 'negative': 0},
                    'total_mentions': 0,
                    'confidence': 0.0
                }
                
        return results
        
    def save_model(self, filepath: str) -> bool:
        """Save fine-tuned model"""
        try:
            if self.model and self.tokenizer:
                self.model.save_pretrained(filepath)
                self.tokenizer.save_pretrained(filepath)
                
                # Save configuration
                import json
                config = {
                    'model_name': self.model_name,
                    'num_labels': self.num_labels,
                    'max_length': self.max_length,
                    'is_trained': self.is_trained,
                    'label_mapping': self.label_mapping
                }
                
                with open(f"{filepath}/config.json", 'w') as f:
                    json.dump(config, f, indent=2)
                    
                logger.info(f"Model saved to {filepath}")
                return True
            else:
                logger.error("No model to save")
                return False
                
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
            
    def load_model(self, filepath: str) -> bool:
        """Load fine-tuned model"""
        try:
            # Load configuration
            import json
            with open(f"{filepath}/config.json", 'r') as f:
                config = json.load(f)
                
            # Update configuration
            self.model_name = config.get('model_name', self.model_name)
            self.num_labels = config.get('num_labels', self.num_labels)
            self.max_length = config.get('max_length', self.max_length)
            self.is_trained = config.get('is_trained', False)
            self.label_mapping = config.get('label_mapping', self.label_mapping)
            
            # Load model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(filepath)
            self.model = AutoModelForSequenceClassification.from_pretrained(filepath)
            self.model.to(self.device)
            
            logger.info(f"Model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
            
    def evaluate_model(self, test_texts: List[str], test_labels: List[str]) -> Dict[str, float]:
        """
        Evaluate model performance.
        
        Args:
            test_texts: Test texts
            test_labels: True labels
            
        Returns:
            Evaluation metrics
        """
        predictions = self.predict(test_texts)
        predicted_labels = [p['predicted_label'] for p in predictions]
        
        from ..utils.evaluation_metrics import ModelEvaluator
        return ModelEvaluator.evaluate_sentiment_model(
            [self.reverse_label_mapping[label] for label in test_labels],
            [self.reverse_label_mapping[label] for label in predicted_labels]
        )
