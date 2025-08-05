"""
File storage manager for cryptocurrency ML pipeline.
Handles model artifacts, datasets, and large file operations.
"""

import os
import shutil
import pickle
import joblib
import asyncio
import aiofiles
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime
import json
import zipfile
import tempfile

logger = logging.getLogger(__name__)

class FileStorageManager:
    """
    File storage manager for ML models, datasets, and artifacts.
    Supports local storage with organization and versioning.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_path = Path(config.get('base_path', './ml_storage'))
        
        # Storage directories
        self.directories = {
            'models': self.base_path / 'models',
            'datasets': self.base_path / 'datasets', 
            'features': self.base_path / 'features',
            'predictions': self.base_path / 'predictions',
            'logs': self.base_path / 'logs',
            'artifacts': self.base_path / 'artifacts',
            'backups': self.base_path / 'backups',
            'temp': self.base_path / 'temp'
        }
        
        # File formats
        self.supported_formats = {
            'dataframe': ['.pkl', '.parquet', '.csv', '.h5'],
            'model': ['.pkl', '.joblib', '.h5', '.onnx'],
            'numpy': ['.npy', '.npz'],
            'json': ['.json'],
            'text': ['.txt', '.log']
        }
        
    async def initialize(self):
        """Initialize storage directories"""
        try:
            for name, path in self.directories.items():
                path.mkdir(parents=True, exist_ok=True)
                
            logger.info(f"File storage initialized at: {self.base_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize file storage: {e}")
            raise
            
    def _get_versioned_path(self, 
                          directory: str,
                          filename: str,
                          version: Optional[str] = None) -> Path:
        """Get versioned file path"""
        base_dir = self.directories[directory]
        
        if version:
            versioned_dir = base_dir / f"v{version}"
            versioned_dir.mkdir(exist_ok=True)
            return versioned_dir / filename
        else:
            # Use timestamp as version
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            versioned_dir = base_dir / f"v{timestamp}"
            versioned_dir.mkdir(exist_ok=True)
            return versioned_dir / filename
            
    async def save_dataframe(self, 
                           df: pd.DataFrame,
                           filename: str,
                           directory: str = 'datasets',
                           format: str = 'parquet',
                           version: Optional[str] = None) -> str:
        """Save DataFrame to file"""
        try:
            if format not in ['parquet', 'csv', 'pickle', 'h5']:
                raise ValueError(f"Unsupported format: {format}")
                
            file_path = self._get_versioned_path(directory, f"{filename}.{format}", version)
            
            if format == 'parquet':
                df.to_parquet(file_path)
            elif format == 'csv':
                df.to_csv(file_path)
            elif format == 'pickle':
                df.to_pickle(file_path)
            elif format == 'h5':
                df.to_hdf(file_path, key='data', mode='w')
                
            logger.info(f"Saved DataFrame to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving DataFrame: {e}")
            raise
            
    async def load_dataframe(self, 
                           filename: str,
                           directory: str = 'datasets',
                           format: str = 'parquet',
                           version: Optional[str] = None) -> pd.DataFrame:
        """Load DataFrame from file"""
        try:
            if version:
                file_path = self._get_versioned_path(directory, f"{filename}.{format}", version)
            else:
                # Get latest version
                file_path = await self._get_latest_file(directory, filename, format)
                
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            if format == 'parquet':
                df = pd.read_parquet(file_path)
            elif format == 'csv':
                df = pd.read_csv(file_path, index_col=0)
            elif format == 'pickle':
                df = pd.read_pickle(file_path)
            elif format == 'h5':
                df = pd.read_hdf(file_path, key='data')
            else:
                raise ValueError(f"Unsupported format: {format}")
                
            logger.info(f"Loaded DataFrame from: {file_path}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading DataFrame: {e}")
            raise
            
    async def save_model(self, 
                       model: Any,
                       model_name: str,
                       metadata: Optional[Dict] = None,
                       format: str = 'joblib',
                       version: Optional[str] = None) -> str:
        """Save ML model with metadata"""
        try:
            model_path = self._get_versioned_path('models', f"{model_name}.{format}", version)
            
            if format == 'joblib':
                joblib.dump(model, model_path)
            elif format == 'pickle':
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
            else:
                raise ValueError(f"Unsupported model format: {format}")
                
            # Save metadata
            if metadata:
                metadata_path = model_path.with_suffix('.json')
                async with aiofiles.open(metadata_path, 'w') as f:
                    await f.write(json.dumps(metadata, indent=2, default=str))
                    
            logger.info(f"Saved model to: {model_path}")
            return str(model_path)
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise
            
    async def load_model(self, 
                       model_name: str,
                       format: str = 'joblib',
                       version: Optional[str] = None) -> tuple[Any, Optional[Dict]]:
        """Load ML model with metadata"""
        try:
            if version:
                model_path = self._get_versioned_path('models', f"{model_name}.{format}", version)
            else:
                model_path = await self._get_latest_file('models', model_name, format)
                
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found: {model_path}")
                
            # Load model
            if format == 'joblib':
                model = joblib.load(model_path)
            elif format == 'pickle':
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
            else:
                raise ValueError(f"Unsupported model format: {format}")
                
            # Load metadata if exists
            metadata = None
            metadata_path = model_path.with_suffix('.json')
            if metadata_path.exists():
                async with aiofiles.open(metadata_path, 'r') as f:
                    content = await f.read()
                    metadata = json.loads(content)
                    
            logger.info(f"Loaded model from: {model_path}")
            return model, metadata
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
            
    async def save_predictions(self, 
                             predictions: Dict[str, Any],
                             model_name: str,
                             symbol: str,
                             timestamp: Optional[datetime] = None) -> str:
        """Save model predictions"""
        try:
            if timestamp is None:
                timestamp = datetime.now()
                
            filename = f"{model_name}_{symbol}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            file_path = self.directories['predictions'] / filename
            
            # Add metadata
            predictions_with_meta = {
                'model_name': model_name,
                'symbol': symbol,
                'timestamp': timestamp.isoformat(),
                'predictions': predictions
            }
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(predictions_with_meta, indent=2, default=str))
                
            logger.info(f"Saved predictions to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving predictions: {e}")
            raise
            
    async def save_features(self, 
                          features: pd.DataFrame,
                          symbol: str,
                          feature_type: str,
                          timestamp: Optional[datetime] = None) -> str:
        """Save engineered features"""
        try:
            if timestamp is None:
                timestamp = datetime.now()
                
            filename = f"{symbol}_{feature_type}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
            return await self.save_dataframe(
                features, 
                filename, 
                directory='features',
                format='parquet'
            )
            
        except Exception as e:
            logger.error(f"Error saving features: {e}")
            raise
            
    async def backup_model(self, 
                         model_name: str,
                         version: Optional[str] = None) -> str:
        """Create compressed backup of model and its artifacts"""
        try:
            # Find model files
            if version:
                model_dir = self.directories['models'] / f"v{version}"
            else:
                # Find latest version
                model_versions = [d for d in self.directories['models'].iterdir() if d.is_dir()]
                if not model_versions:
                    raise FileNotFoundError(f"No versions found for model: {model_name}")
                model_dir = max(model_versions, key=lambda x: x.stat().st_mtime)
                
            # Create backup archive
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{model_name}_backup_{timestamp}.zip"
            backup_path = self.directories['backups'] / backup_filename
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in model_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(model_dir)
                        zipf.write(file_path, arcname)
                        
            logger.info(f"Created model backup: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Error creating model backup: {e}")
            raise
            
    async def restore_model(self, backup_path: str, target_version: Optional[str] = None) -> str:
        """Restore model from backup"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
                
            # Extract model name from backup filename
            model_name = backup_file.stem.split('_backup_')[0]
            
            if target_version is None:
                target_version = datetime.now().strftime("%Y%m%d_%H%M%S")
                
            restore_dir = self.directories['models'] / f"v{target_version}"
            restore_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(restore_dir)
                
            logger.info(f"Restored model to: {restore_dir}")
            return str(restore_dir)
            
        except Exception as e:
            logger.error(f"Error restoring model: {e}")
            raise
            
    async def _get_latest_file(self, 
                             directory: str, 
                             filename: str, 
                             format: str) -> Path:
        """Get latest version of a file"""
        base_dir = self.directories[directory]
        
        # Find all version directories
        version_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith('v')]
        
        if not version_dirs:
            raise FileNotFoundError(f"No versions found for {filename}")
            
        # Sort by modification time
        latest_dir = max(version_dirs, key=lambda x: x.stat().st_mtime)
        
        return latest_dir / f"{filename}.{format}"
        
    async def list_files(self, 
                       directory: str,
                       pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in directory with metadata"""
        try:
            base_dir = self.directories[directory]
            files = []
            
            for file_path in base_dir.rglob('*'):
                if file_path.is_file():
                    if pattern and pattern not in file_path.name:
                        continue
                        
                    stat = file_path.stat()
                    files.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'created': datetime.fromtimestamp(stat.st_ctime)
                    })
                    
            return sorted(files, key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
            
    async def cleanup_old_files(self, 
                              directory: str,
                              days_to_keep: int = 30,
                              keep_latest: int = 3) -> int:
        """Clean up old files while keeping recent ones"""
        try:
            base_dir = self.directories[directory]
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            files = await self.list_files(directory)
            files_to_delete = []
            
            # Group files by base name
            file_groups = {}
            for file_info in files:
                base_name = file_info['name'].split('_')[0]  # Assuming timestamp suffix
                if base_name not in file_groups:
                    file_groups[base_name] = []
                file_groups[base_name].append(file_info)
                
            # For each group, keep latest N files and delete old ones
            deleted_count = 0
            for base_name, group_files in file_groups.items():
                sorted_files = sorted(group_files, key=lambda x: x['modified'], reverse=True)
                
                # Keep latest N files regardless of age
                files_to_check = sorted_files[keep_latest:]
                
                for file_info in files_to_check:
                    if file_info['modified'] < cutoff_date:
                        file_path = Path(file_info['path'])
                        if file_path.exists():
                            file_path.unlink()
                            deleted_count += 1
                            
            logger.info(f"Cleaned up {deleted_count} old files from {directory}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")
            return 0
            
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        try:
            stats = {}
            
            for name, directory in self.directories.items():
                if directory.exists():
                    total_size = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
                    file_count = len([f for f in directory.rglob('*') if f.is_file()])
                    
                    stats[name] = {
                        'total_size_mb': round(total_size / (1024 * 1024), 2),
                        'file_count': file_count,
                        'path': str(directory)
                    }
                else:
                    stats[name] = {
                        'total_size_mb': 0,
                        'file_count': 0,
                        'path': str(directory)
                    }
                    
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}
