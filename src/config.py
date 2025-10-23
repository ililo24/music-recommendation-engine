"""
Configuration management for the music recommendation engine.

This module provides centralized configuration management with support for:
- Environment-based configuration
- Default settings
- Configuration validation
- Logging setup
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ModelConfig:
    """Model configuration settings"""
    n_estimators: int = 200
    random_state: int = 42
    test_split: float = 0.2
    cv_folds: int = 5
    feature_weights: tuple = (0.6, 0.7)
    model_name: Optional[str] = None


@dataclass
class DataConfig:
    """Data processing configuration"""
    required_columns: list = None
    optional_columns: list = None
    timestamp_column: str = 'ts'
    target_column: str = 'preference_score'
    max_memory_usage_mb: int = 1000
    
    def __post_init__(self):
        if self.required_columns is None:
            self.required_columns = ['ts', 'ms_played', 'duration_ms', 'id']
        if self.optional_columns is None:
            self.optional_columns = [
                'track', 'artist', 'popularity', 'danceability', 'energy',
                'key', 'loudness', 'mode', 'speechiness', 'acousticness',
                'instrumentalness', 'valence', 'tempo', 'liveness',
                'time_signature', 'reason_start', 'reason_end', 'skipped'
            ]


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file_path: Optional[str] = None
    max_file_size_mb: int = 10
    backup_count: int = 5


@dataclass
class WebConfig:
    """Web application configuration"""
    host: str = '0.0.0.0'
    port: int = 5000
    debug: bool = False
    secret_key: str = 'your-secret-key-change-in-production'


class Config:
    """Main configuration class"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration"""
        self.config_file = config_file or 'config.json'
        self.model = ModelConfig()
        self.data = DataConfig()
        self.logging = LoggingConfig()
        self.web = WebConfig()
        
        # Load configuration
        self.load_config()
        
        # Setup logging
        self.setup_logging()
    
    def load_config(self):
        """Load configuration from file or environment variables"""
        # Load from file if exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    self._update_from_dict(config_data)
            except Exception as e:
                logging.warning(f"Failed to load config file: {e}")
        
        # Override with environment variables
        self._load_from_env()
    
    def _update_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration from dictionary"""
        if 'model' in config_data:
            model_data = config_data['model']
            self.model = ModelConfig(**{k: v for k, v in model_data.items() 
                                       if k in ModelConfig.__annotations__})
        
        if 'data' in config_data:
            data_data = config_data['data']
            self.data = DataConfig(**{k: v for k, v in data_data.items() 
                                    if k in DataConfig.__annotations__})
        
        if 'logging' in config_data:
            logging_data = config_data['logging']
            self.logging = LoggingConfig(**{k: v for k, v in logging_data.items() 
                                           if k in LoggingConfig.__annotations__})
        
        if 'web' in config_data:
            web_data = config_data['web']
            self.web = WebConfig(**{k: v for k, v in web_data.items() 
                                  if k in WebConfig.__annotations__})
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Model settings
        if os.getenv('MODEL_N_ESTIMATORS'):
            self.model.n_estimators = int(os.getenv('MODEL_N_ESTIMATORS'))
        if os.getenv('MODEL_RANDOM_STATE'):
            self.model.random_state = int(os.getenv('MODEL_RANDOM_STATE'))
        if os.getenv('TEST_SPLIT'):
            self.model.test_split = float(os.getenv('TEST_SPLIT'))
        
        # Data settings
        if os.getenv('MAX_MEMORY_USAGE_MB'):
            self.data.max_memory_usage_mb = int(os.getenv('MAX_MEMORY_USAGE_MB'))
        
        # Logging settings
        if os.getenv('LOG_LEVEL'):
            self.logging.level = os.getenv('LOG_LEVEL')
        if os.getenv('LOG_FILE'):
            self.logging.file_path = os.getenv('LOG_FILE')
        
        # Web settings
        if os.getenv('WEB_HOST'):
            self.web.host = os.getenv('WEB_HOST')
        if os.getenv('WEB_PORT'):
            self.web.port = int(os.getenv('WEB_PORT'))
        if os.getenv('WEB_DEBUG'):
            self.web.debug = os.getenv('WEB_DEBUG').lower() == 'true'
        if os.getenv('SECRET_KEY'):
            self.web.secret_key = os.getenv('SECRET_KEY')
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory
        if self.logging.file_path:
            log_dir = Path(self.logging.file_path).parent
            log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self.logging.level.upper()),
            format=self.logging.format,
            handlers=self._get_log_handlers()
        )
        
        # Set specific loggers
        logging.getLogger('matplotlib').setLevel(logging.WARNING)
        logging.getLogger('seaborn').setLevel(logging.WARNING)
    
    def _get_log_handlers(self):
        """Get log handlers based on configuration"""
        handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.logging.level.upper()))
        console_handler.setFormatter(logging.Formatter(self.logging.format))
        handlers.append(console_handler)
        
        # File handler
        if self.logging.file_path:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                self.logging.file_path,
                maxBytes=self.logging.max_file_size_mb * 1024 * 1024,
                backupCount=self.logging.backup_count
            )
            file_handler.setLevel(getattr(logging, self.logging.level.upper()))
            file_handler.setFormatter(logging.Formatter(self.logging.format))
            handlers.append(file_handler)
        
        return handlers
    
    def save_config(self, file_path: Optional[str] = None):
        """Save current configuration to file"""
        config_data = {
            'model': asdict(self.model),
            'data': asdict(self.data),
            'logging': asdict(self.logging),
            'web': asdict(self.web)
        }
        
        save_path = file_path or self.config_file
        with open(save_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        logging.info(f"Configuration saved to {save_path}")
    
    def validate_config(self) -> bool:
        """Validate configuration settings"""
        errors = []
        
        # Validate model config
        if self.model.n_estimators <= 0:
            errors.append("n_estimators must be positive")
        if not 0 < self.model.test_split < 1:
            errors.append("test_split must be between 0 and 1")
        if self.model.cv_folds < 2:
            errors.append("cv_folds must be at least 2")
        
        # Validate data config
        if self.data.max_memory_usage_mb <= 0:
            errors.append("max_memory_usage_mb must be positive")
        
        # Validate logging config
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging.level.upper() not in valid_levels:
            errors.append(f"log_level must be one of {valid_levels}")
        
        # Validate web config
        if self.web.port <= 0 or self.web.port > 65535:
            errors.append("web port must be between 1 and 65535")
        
        if errors:
            for error in errors:
                logging.error(f"Configuration error: {error}")
            return False
        
        return True
    
    def get_model_params(self) -> Dict[str, Any]:
        """Get model parameters for sklearn"""
        return {
            'n_estimators': self.model.n_estimators,
            'random_state': self.model.random_state,
            'n_jobs': -1
        }
    
    def get_feature_weights(self) -> tuple:
        """Get feature weights for preference score calculation"""
        return self.model.feature_weights


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance"""
    return config


def setup_logging():
    """Setup logging with current configuration"""
    config.setup_logging()


def create_sample_config():
    """Create a sample configuration file"""
    sample_config = {
        "model": {
            "n_estimators": 200,
            "random_state": 42,
            "test_split": 0.2,
            "cv_folds": 5,
            "feature_weights": [0.6, 0.7],
            "model_name": "music_recommendation_model"
        },
        "data": {
            "required_columns": ["ts", "ms_played", "duration_ms", "id"],
            "optional_columns": ["track", "artist", "popularity", "danceability", "energy"],
            "timestamp_column": "ts",
            "target_column": "preference_score",
            "max_memory_usage_mb": 1000
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file_path": "logs/music_recommendation.log",
            "max_file_size_mb": 10,
            "backup_count": 5
        },
        "web": {
            "host": "0.0.0.0",
            "port": 5000,
            "debug": false,
            "secret_key": "change-this-in-production"
        }
    }
    
    with open('config.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("Sample configuration file created: config.json")


if __name__ == "__main__":
    # Create sample config if run directly
    create_sample_config()
    print("Configuration management module loaded successfully.")
