"""
Data management package for cryptocurrency ML pipeline.
Provides data collection, processing, validation, and storage capabilities.
"""

from .collectors import CryptoDataCollector, NewsDataCollector, SocialDataCollector
from .processors import FeatureEngineer, DataValidator, DataTransformer
from .storage import DatabaseManager, CacheManager, FileStorageManager

__version__ = "1.0.0"
__all__ = [
    "CryptoDataCollector",
    "NewsDataCollector", 
    "SocialDataCollector",
    "FeatureEngineer",
    "DataValidator",
    "DataTransformer",
    "DatabaseManager",
    "CacheManager",
    "FileStorageManager"
]   
