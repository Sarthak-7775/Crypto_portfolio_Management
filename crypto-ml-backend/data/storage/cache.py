"""
Redis-based caching for cryptocurrency ML pipeline.
Provides high-performance caching for frequently accessed data.
"""

import asyncio
import aioredis
import pickle
import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import timedelta
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Redis-based cache manager for cryptocurrency data.
    Supports serialization of pandas DataFrames and numpy arrays.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis: Optional[aioredis.Redis] = None
        
        # Redis configuration
        self.redis_config = {
            'host': config.get('host', 'localhost'),
            'port': config.get('port', 6379),
            'db': config.get('db', 0),
            'password': config.get('password'),
            'decode_responses': False,  # We'll handle encoding ourselves
            'max_connections': config.get('max_connections', 20),
        }
        
        # Default TTL settings (in seconds)
        self.default_ttl = {
            'market_data': 300,      # 5 minutes
            'news_data': 1800,       # 30 minutes
            'social_data': 900,      # 15 minutes
            'features': 3600,        # 1 hour
            'predictions': 7200,     # 2 hours
            'models': 86400,         # 24 hours
        }
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis = aioredis.from_url(
                f"redis://{self.redis_config['host']}:{self.redis_config['port']}/{self.redis_config['db']}",
                password=self.redis_config.get('password'),
                max_connections=self.redis_config['max_connections']
            )
            
            # Test connection
            await self.redis.ping()
            logger.info("Redis cache initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            raise
            
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")
            
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for Redis storage"""
        if isinstance(data, pd.DataFrame):
            # Use pickle for DataFrames to preserve index and dtypes
            return pickle.dumps({
                'type': 'dataframe',
                'data': data.to_dict('split'),
                'index_name': data.index.name,
                'dtypes': data.dtypes.to_dict()
            })
        elif isinstance(data, np.ndarray):
            return pickle.dumps({
                'type': 'numpy',
                'data': data.tolist(),
                'shape': data.shape,
                'dtype': str(data.dtype)
            })
        elif isinstance(data, (dict, list)):
            return json.dumps(data).encode('utf-8')
        else:
            return pickle.dumps(data)
            
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from Redis"""
        try:
            # Try JSON first (faster)
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            obj = pickle.loads(data)
            
            if isinstance(obj, dict):
                if obj.get('type') == 'dataframe':
                    df = pd.DataFrame.from_dict(obj['data'], orient='split')
                    df.index.name = obj.get('index_name')
                    # Restore dtypes
                    for col, dtype in obj.get('dtypes', {}).items():
                        try:
                            df[col] = df[col].astype(dtype)
                        except:
                            pass
                    return df
                elif obj.get('type') == 'numpy':
                    return np.array(obj['data'], dtype=obj['dtype']).reshape(obj['shape'])
                    
            return obj
            
    async def set(self, 
                  key: str, 
                  value: Any, 
                  ttl: Optional[int] = None,
                  data_type: str = 'general') -> bool:
        """Set a value in cache"""
        try:
            if ttl is None:
                ttl = self.default_ttl.get(data_type, 3600)
                
            serialized_data = self._serialize_data(value)
            await self.redis.setex(key, ttl, serialized_data)
            
            logger.debug(f"Cached data with key: {key}, TTL: {ttl}s")
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
            
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        try:
            data = await self.redis.get(key)
            if data is None:
                return None
                
            return self._deserialize_data(data)
            
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
            
    async def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        try:
            result = await self.redis.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
            
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
            
    async def get_ttl(self, key: str) -> int:
        """Get remaining TTL for a key"""
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL for key {key}: {e}")
            return -1
            
    async def cache_market_data(self, 
                              symbol: str, 
                              timeframe: str,
                              data: pd.DataFrame) -> bool:
        """Cache market data with structured key"""
        key = f"market_data:{symbol}:{timeframe}"
        return await self.set(key, data, data_type='market_data')
        
    async def get_market_data(self, 
                            symbol: str, 
                            timeframe: str) -> Optional[pd.DataFrame]:
        """Get cached market data"""
        key = f"market_data:{symbol}:{timeframe}"
        return await self.get(key)
        
    async def cache_features(self, 
                           symbol: str,
                           feature_type: str,
                           features: pd.DataFrame) -> bool:
        """Cache engineered features"""
        key = f"features:{symbol}:{feature_type}"
        return await self.set(key, features, data_type='features')
        
    async def get_features(self, 
                         symbol: str,
                         feature_type: str) -> Optional[pd.DataFrame]:
        """Get cached features"""
        key = f"features:{symbol}:{feature_type}"
        return await self.get(key)
        
    async def cache_predictions(self, 
                              model_name: str,
                              symbol: str,
                              predictions: Dict[str, Any]) -> bool:
        """Cache model predictions"""
        key = f"predictions:{model_name}:{symbol}"
        return await self.set(key, predictions, data_type='predictions')
        
    async def get_predictions(self, 
                            model_name: str,
                            symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached predictions"""
        key = f"predictions:{model_name}:{symbol}"
        return await self.get(key)
        
    async def cache_sentiment_data(self, 
                                 symbol: str,
                                 timeframe: str,
                                 sentiment_data: List[Dict]) -> bool:
        """Cache sentiment analysis data"""
        key = f"sentiment:{symbol}:{timeframe}"
        return await self.set(key, sentiment_data, data_type='social_data')
        
    async def get_sentiment_data(self, 
                               symbol: str,
                               timeframe: str) -> Optional[List[Dict]]:
        """Get cached sentiment data"""
        key = f"sentiment:{symbol}:{timeframe}"
        return await self.get(key)
        
    async def cache_model(self, 
                        model_name: str,
                        model_data: bytes) -> bool:
        """Cache serialized ML model"""
        key = f"model:{model_name}"
        try:
            await self.redis.setex(key, self.default_ttl['models'], model_data)
            logger.info(f"Cached model: {model_name}")
            return True
        except Exception as e:
            logger.error(f"Error caching model {model_name}: {e}")
            return False
            
    async def get_model(self, model_name: str) -> Optional[bytes]:
        """Get cached model"""
        key = f"model:{model_name}"
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Error getting cached model {model_name}: {e}")
            return None
            
    async def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info(f"Invalidated {deleted} keys matching pattern: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error invalidating pattern {pattern}: {e}")
            return 0
            
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = await self.redis.info()
            return {
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': info.get('keyspace_hits', 0) / max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0))
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
            
    async def flush_cache(self, pattern: Optional[str] = None) -> bool:
        """Flush cache (all keys or matching pattern)"""
        try:
            if pattern:
                deleted = await self.invalidate_pattern(pattern)
                logger.info(f"Flushed {deleted} keys matching pattern: {pattern}")
            else:
                await self.redis.flushdb()
                logger.info("Flushed entire cache database")
            return True
        except Exception as e:
            logger.error(f"Error flushing cache: {e}")
            return False
            
    async def get_all_keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern"""
        try:
            keys = await self.redis.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            logger.error(f"Error getting keys: {e}")
            return []
