"""
Database operations for cryptocurrency ML pipeline.
Supports PostgreSQL with async operations and connection pooling.
"""

import asyncio
import asyncpg
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Async PostgreSQL database manager for cryptocurrency data.
    Handles connections, CRUD operations, and data retrieval.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None
        
        # Database configuration
        self.db_config = {
            'host': config.get('host', 'localhost'),
            'port': config.get('port', 5432),
            'database': config.get('database', 'crypto_ml'),
            'user': config.get('user', 'postgres'),
            'password': config.get('password', ''),
            'min_size': config.get('min_pool_size', 5),
            'max_size': config.get('max_pool_size', 20),
            'command_timeout': config.get('command_timeout', 60),
        }
        
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                min_size=self.db_config['min_size'],
                max_size=self.db_config['max_size'],
                command_timeout=self.db_config['command_timeout'],
            )
            
            logger.info("Database connection pool initialized successfully")
            
            # Create tables if they don't exist
            await self.create_tables()
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
            
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connections closed")
            
    @asynccontextmanager
    async def get_connection(self):
        """Context manager for database connections"""
        async with self.pool.acquire() as conn:
            yield conn
            
    async def create_tables(self):
        """Create database tables for cryptocurrency data"""
        
        create_tables_sql = """
        -- Market data table
        CREATE TABLE IF NOT EXISTS market_data (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            timestamp TIMESTAMPTZ NOT NULL,
            open_price DECIMAL(20, 8),
            high_price DECIMAL(20, 8),
            low_price DECIMAL(20, 8),
            close_price DECIMAL(20, 8),
            volume DECIMAL(30, 8),
            market_cap DECIMAL(30, 2),
            exchange VARCHAR(50),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(symbol, timestamp, exchange)
        );
        
        -- News articles table
        CREATE TABLE IF NOT EXISTS news_articles (
            id SERIAL PRIMARY KEY,
            article_id VARCHAR(100) UNIQUE NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            url TEXT,
            source VARCHAR(100),
            author VARCHAR(200),
            published_at TIMESTAMPTZ,
            sentiment_score DECIMAL(5, 3),
            sentiment_label VARCHAR(20),
            relevance_score DECIMAL(5, 3),
            crypto_mentions TEXT[], -- Array of mentioned cryptocurrencies
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        -- Social media posts table
        CREATE TABLE IF NOT EXISTS social_posts (
            id SERIAL PRIMARY KEY,
            post_id VARCHAR(100) UNIQUE NOT NULL,
            platform VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            author VARCHAR(200),
            timestamp TIMESTAMPTZ,
            sentiment_score DECIMAL(5, 3),
            sentiment_label VARCHAR(20),
            engagement_metrics JSONB,
            crypto_mentions TEXT[],
            influence_score DECIMAL(5, 3),
            hashtags TEXT[],
            url TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        -- On-chain metrics table
        CREATE TABLE IF NOT EXISTS onchain_metrics (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            timestamp TIMESTAMPTZ NOT NULL,
            active_addresses INTEGER,
            new_addresses INTEGER,
            transaction_count INTEGER,
            transaction_volume DECIMAL(30, 8),
            network_hash_rate DECIMAL(30, 8),
            difficulty DECIMAL(30, 8),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(symbol, timestamp)
        );
        
        -- Model predictions table
        CREATE TABLE IF NOT EXISTS model_predictions (
            id SERIAL PRIMARY KEY,
            model_name VARCHAR(100) NOT NULL,
            symbol VARCHAR(20) NOT NULL,
            prediction_timestamp TIMESTAMPTZ NOT NULL,
            prediction_horizon INTEGER NOT NULL, -- hours ahead
            predicted_value DECIMAL(20, 8),
            actual_value DECIMAL(20, 8),
            prediction_type VARCHAR(50), -- 'price', 'returns', 'direction'
            confidence_score DECIMAL(5, 3),
            model_version VARCHAR(50),
            features_used TEXT[],
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        -- User portfolio data table
        CREATE TABLE IF NOT EXISTS user_portfolios (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(100) NOT NULL,
            symbol VARCHAR(20) NOT NULL,
            quantity DECIMAL(30, 8) NOT NULL,
            average_buy_price DECIMAL(20, 8),
            last_updated TIMESTAMPTZ DEFAULT NOW(),
            exchange VARCHAR(50),
            UNIQUE(user_id, symbol, exchange)
        );
        
        -- Feature store table
        CREATE TABLE IF NOT EXISTS feature_store (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            timestamp TIMESTAMPTZ NOT NULL,
            feature_name VARCHAR(200) NOT NULL,
            feature_value DECIMAL(20, 8),
            feature_group VARCHAR(100), -- 'technical', 'sentiment', 'onchain'
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(symbol, timestamp, feature_name)
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp ON market_data(symbol, timestamp);
        CREATE INDEX IF NOT EXISTS idx_news_published_at ON news_articles(published_at);
        CREATE INDEX IF NOT EXISTS idx_social_posts_timestamp ON social_posts(timestamp);
        CREATE INDEX IF NOT EXISTS idx_onchain_symbol_timestamp ON onchain_metrics(symbol, timestamp);
        CREATE INDEX IF NOT EXISTS idx_predictions_symbol_timestamp ON model_predictions(symbol, prediction_timestamp);
        CREATE INDEX IF NOT EXISTS idx_features_symbol_timestamp ON feature_store(symbol, timestamp);
        """
        
        async with self.get_connection() as conn:
            await conn.execute(create_tables_sql)
            
        logger.info("Database tables created successfully")
        
    async def insert_market_data(self, data: List[Dict[str, Any]]) -> int:
        """Insert market data records"""
        try:
            async with self.get_connection() as conn:
                insert_sql = """
                INSERT INTO market_data (symbol, timestamp, open_price, high_price, low_price, 
                                       close_price, volume, market_cap, exchange)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (symbol, timestamp, exchange) 
                DO UPDATE SET
                    open_price = EXCLUDED.open_price,
                    high_price = EXCLUDED.high_price,
                    low_price = EXCLUDED.low_price,
                    close_price = EXCLUDED.close_price,
                    volume = EXCLUDED.volume,
                    market_cap = EXCLUDED.market_cap
                """
                
                records = [
                    (
                        d['symbol'], d['timestamp'], d.get('open'), d.get('high'),
                        d.get('low'), d['close'], d.get('volume', 0), 
                        d.get('market_cap', 0), d.get('exchange', 'unknown')
                    )
                    for d in data
                ]
                
                await conn.executemany(insert_sql, records)
                
            logger.info(f"Inserted {len(records)} market data records")
            return len(records)
            
        except Exception as e:
            logger.error(f"Error inserting market data: {e}")
            raise
            
    async def insert_news_articles(self, articles: List[Dict[str, Any]]) -> int:
        """Insert news articles"""
        try:
            async with self.get_connection() as conn:
                insert_sql = """
                INSERT INTO news_articles (article_id, title, content, url, source, author,
                                         published_at, sentiment_score, sentiment_label, 
                                         relevance_score, crypto_mentions)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (article_id) DO NOTHING
                """
                
                records = [
                    (
                        a['article_id'], a['title'], a.get('content', ''), a.get('url', ''),
                        a.get('source', ''), a.get('author', ''), a['published_at'],
                        a.get('sentiment_score', 0), a.get('sentiment_label', 'neutral'),
                        a.get('relevance_score', 0), a.get('crypto_mentions', [])
                    )
                    for a in articles
                ]
                
                await conn.executemany(insert_sql, records)
                
            logger.info(f"Inserted {len(records)} news articles")
            return len(records)
            
        except Exception as e:
            logger.error(f"Error inserting news articles: {e}")
            raise
            
    async def get_market_data(self, 
                            symbol: str,
                            start_time: datetime,
                            end_time: datetime,
                            exchange: Optional[str] = None) -> pd.DataFrame:
        """Retrieve market data for analysis"""
        try:
            async with self.get_connection() as conn:
                sql = """
                SELECT symbol, timestamp, open_price, high_price, low_price, 
                       close_price, volume, market_cap, exchange
                FROM market_data 
                WHERE symbol = $1 AND timestamp >= $2 AND timestamp <= $3
                """
                params = [symbol, start_time, end_time]
                
                if exchange:
                    sql += " AND exchange = $4"
                    params.append(exchange)
                    
                sql += " ORDER BY timestamp"
                
                rows = await conn.fetch(sql, *params)
                
            # Convert to DataFrame
            if rows:
                df = pd.DataFrame([dict(row) for row in rows])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                
                # Rename columns for consistency
                df.rename(columns={
                    'open_price': 'open',
                    'high_price': 'high', 
                    'low_price': 'low',
                    'close_price': 'close'
                }, inplace=True)
                
                logger.info(f"Retrieved {len(df)} market data records for {symbol}")
                return df
            else:
                logger.warning(f"No market data found for {symbol}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error retrieving market data: {e}")
            raise
            
    async def get_sentiment_data(self,
                               symbols: List[str],
                               start_time: datetime,
                               end_time: datetime,
                               source_type: str = 'all') -> pd.DataFrame:
        """Retrieve sentiment data"""
        try:
            async with self.get_connection() as conn:
                if source_type == 'news':
                    sql = """
                    SELECT published_at as timestamp, sentiment_score, sentiment_label,
                           source, crypto_mentions
                    FROM news_articles 
                    WHERE published_at >= $1 AND published_at <= $2
                    AND crypto_mentions && $3
                    ORDER BY published_at
                    """
                elif source_type == 'social':
                    sql = """
                    SELECT timestamp, sentiment_score, sentiment_label,
                           platform as source, crypto_mentions, influence_score
                    FROM social_posts 
                    WHERE timestamp >= $1 AND timestamp <= $2
                    AND crypto_mentions && $3
                    ORDER BY timestamp
                    """
                else:  # all
                    sql = """
                    SELECT timestamp, sentiment_score, sentiment_label, 
                           source, crypto_mentions, NULL as influence_score
                    FROM (
                        SELECT published_at as timestamp, sentiment_score, sentiment_label,
                               source, crypto_mentions
                        FROM news_articles 
                        WHERE published_at >= $1 AND published_at <= $2
                        AND crypto_mentions && $3
                        UNION ALL
                        SELECT timestamp, sentiment_score, sentiment_label,
                               platform as source, crypto_mentions
                        FROM social_posts 
                        WHERE timestamp >= $1 AND timestamp <= $2
                        AND crypto_mentions && $3
                    ) combined
                    ORDER BY timestamp
                    """
                
                rows = await conn.fetch(sql, start_time, end_time, symbols)
                
            if rows:
                df = pd.DataFrame([dict(row) for row in rows])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                logger.info(f"Retrieved {len(df)} sentiment records")
                return df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error retrieving sentiment data: {e}")
            raise
            
    async def store_features(self, 
                           symbol: str,
                           timestamp: datetime,
                           features: Dict[str, float],
                           feature_group: str = 'technical') -> int:
        """Store engineered features"""
        try:
            async with self.get_connection() as conn:
                insert_sql = """
                INSERT INTO feature_store (symbol, timestamp, feature_name, feature_value, feature_group)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (symbol, timestamp, feature_name)
                DO UPDATE SET feature_value = EXCLUDED.feature_value
                """
                
                records = [
                    (symbol, timestamp, feature_name, feature_value, feature_group)
                    for feature_name, feature_value in features.items()
                    if not pd.isna(feature_value) and not np.isinf(feature_value)
                ]
                
                await conn.executemany(insert_sql, records)
                
            logger.info(f"Stored {len(records)} features for {symbol}")
            return len(records)
            
        except Exception as e:
            logger.error(f"Error storing features: {e}")
            raise
            
    async def get_features(self,
                         symbol: str,
                         start_time: datetime,
                         end_time: datetime,
                         feature_group: Optional[str] = None) -> pd.DataFrame:
        """Retrieve stored features"""
        try:
            async with self.get_connection() as conn:
                sql = """
                SELECT timestamp, feature_name, feature_value, feature_group
                FROM feature_store
                WHERE symbol = $1 AND timestamp >= $2 AND timestamp <= $3
                """
                params = [symbol, start_time, end_time]
                
                if feature_group:
                    sql += " AND feature_group = $4"
                    params.append(feature_group)
                    
                sql += " ORDER BY timestamp, feature_name"
                
                rows = await conn.fetch(sql, *params)
                
            if rows:
                df = pd.DataFrame([dict(row) for row in rows])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Pivot to wide format
                features_df = df.pivot(index='timestamp', columns='feature_name', values='feature_value')
                
                logger.info(f"Retrieved {features_df.shape[0]} rows and {features_df.shape[1]} features")
                return features_df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error retrieving features: {e}")
            raise
            
    async def store_predictions(self, predictions: List[Dict[str, Any]]) -> int:
        """Store model predictions"""
        try:
            async with self.get_connection() as conn:
                insert_sql = """
                INSERT INTO model_predictions (model_name, symbol, prediction_timestamp,
                                             prediction_horizon, predicted_value, prediction_type,
                                             confidence_score, model_version, features_used)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """
                
                records = [
                    (
                        p['model_name'], p['symbol'], p['prediction_timestamp'],
                        p['prediction_horizon'], p['predicted_value'], p['prediction_type'],
                        p.get('confidence_score', 0), p.get('model_version', '1.0'),
                        p.get('features_used', [])
                    )
                    for p in predictions
                ]
                
                await conn.executemany(insert_sql, records)
                
            logger.info(f"Stored {len(records)} predictions")
            return len(records)
            
        except Exception as e:
            logger.error(f"Error storing predictions: {e}")
            raise
            
    async def get_latest_data(self, symbol: str, limit: int = 100) -> Dict[str, pd.DataFrame]:
        """Get latest data for a symbol from all tables"""
        try:
            result = {}
            
            # Latest market data
            market_data = await self.get_market_data(
                symbol,
                datetime.utcnow() - timedelta(days=30),
                datetime.utcnow()
            )
            result['market_data'] = market_data.tail(limit)
            
            # Latest sentiment data
            sentiment_data = await self.get_sentiment_data(
                [symbol],
                datetime.utcnow() - timedelta(days=7),
                datetime.utcnow()
            )
            result['sentiment_data'] = sentiment_data.tail(limit)
            
            # Latest features
            features_data = await self.get_features(
                symbol,
                datetime.utcnow() - timedelta(days=7),
                datetime.utcnow()
            )
            result['features_data'] = features_data.tail(limit)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting latest data: {e}")
            raise
            
    async def cleanup_old_data(self, days_to_keep: int = 365):
        """Clean up old data to maintain database performance"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            async with self.get_connection() as conn:
                # Clean up old market data
                await conn.execute(
                    "DELETE FROM market_data WHERE timestamp < $1", cutoff_date
                )
                
                # Clean up old news articles
                await conn.execute(
                    "DELETE FROM news_articles WHERE published_at < $1", cutoff_date
                )
                
                # Clean up old social posts
                await conn.execute(
                    "DELETE FROM social_posts WHERE timestamp < $1", cutoff_date
                )
                
                # Clean up old features
                await conn.execute(
                    "DELETE FROM feature_store WHERE timestamp < $1", cutoff_date
                )
                
                # Vacuum tables to reclaim space
                await conn.execute("VACUUM ANALYZE")
                
            logger.info(f"Cleaned up data older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            raise
