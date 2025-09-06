"""
Environment configuration management for AI Bias Psychologist.

This module provides environment variable handling, validation,
and configuration management with support for .env files.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union, List
from functools import lru_cache
import logging

try:
    from pydantic import BaseSettings, Field, validator
    from pydantic_settings import BaseSettings as PydanticBaseSettings
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseSettings = object
    Field = lambda default=None, **kwargs: default
    validator = lambda *args, **kwargs: lambda func: func

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class EnvironmentConfig:
    """Environment configuration manager with fallback support."""
    
    def __init__(self, env_file: Optional[str] = None):
        self.env_file = env_file or ".env"
        self._config_cache: Dict[str, Any] = {}
        self._load_environment()
    
    def _load_environment(self) -> None:
        """Load environment variables from .env file if available."""
        if DOTENV_AVAILABLE and Path(self.env_file).exists():
            load_dotenv(self.env_file)
            logging.info(f"Loaded environment variables from {self.env_file}")
        elif Path(self.env_file).exists():
            # Fallback: manually parse .env file
            self._parse_env_file()
    
    def _parse_env_file(self) -> None:
        """Manually parse .env file without python-dotenv."""
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key not in os.environ:
                            os.environ[key] = value
        except Exception as e:
            logging.warning(f"Failed to parse .env file: {e}")
    
    def get(self, key: str, default: Any = None, cast_type: type = str) -> Any:
        """Get environment variable with type casting."""
        if key in self._config_cache:
            return self._config_cache[key]
        
        value = os.environ.get(key, default)
        
        if value is None:
            return default
        
        # Type casting
        try:
            if cast_type == bool:
                if isinstance(value, str):
                    value = value.lower() in ('true', '1', 'yes', 'on')
                else:
                    value = bool(value)
            elif cast_type == int:
                value = int(value)
            elif cast_type == float:
                value = float(value)
            elif cast_type == list:
                if isinstance(value, str):
                    value = [item.strip() for item in value.split(',')]
                else:
                    value = list(value) if value else []
            else:
                value = str(value)
        except (ValueError, TypeError) as e:
            logging.warning(f"Failed to cast {key}={value} to {cast_type}: {e}")
            return default
        
        self._config_cache[key] = value
        return value
    
    def get_required(self, key: str, cast_type: type = str) -> Any:
        """Get required environment variable, raise error if missing."""
        value = self.get(key, cast_type=cast_type)
        if value is None:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def get_list(self, key: str, default: List[str] = None, separator: str = ',') -> List[str]:
        """Get environment variable as list."""
        if default is None:
            default = []
        
        value = self.get(key, default=default)
        if isinstance(value, str):
            return [item.strip() for item in value.split(separator) if item.strip()]
        return value if isinstance(value, list) else default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get environment variable as boolean."""
        return self.get(key, default=default, cast_type=bool)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get environment variable as integer."""
        return self.get(key, default=default, cast_type=int)
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get environment variable as float."""
        return self.get(key, default=default, cast_type=float)
    
    def validate_required(self, required_keys: List[str]) -> None:
        """Validate that all required environment variables are set."""
        missing_keys = []
        for key in required_keys:
            if not self.get(key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        config = {}
        
        # Application settings
        config.update({
            'app_name': self.get('APP_NAME', 'AI Bias Psychologist'),
            'app_version': self.get('APP_VERSION', '0.1.0'),
            'debug': self.get_bool('DEBUG', False),
            'log_level': self.get('LOG_LEVEL', 'INFO'),
        })
        
        # Database settings
        config.update({
            'database_url': self.get('DATABASE_URL', 'sqlite:///./data/database/bias_psych.db'),
        })
        
        # Storage paths
        config.update({
            'base_dir': self.get('BASE_DIR', './data'),
            'responses_dir': self.get('RESPONSES_DIR', './data/responses'),
            'exports_dir': self.get('EXPORTS_DIR', './data/exports'),
            'logs_dir': self.get('LOGS_DIR', './data/logs'),
        })
        
        # API keys
        config.update({
            'openai_api_key': self.get('OPENAI_API_KEY'),
            'openai_org_id': self.get('OPENAI_ORG_ID'),
            'anthropic_api_key': self.get('ANTHROPIC_API_KEY'),
        })
        
        # Dashboard settings
        config.update({
            'dashboard_host': self.get('DASHBOARD_HOST', '0.0.0.0'),
            'dashboard_port': self.get_int('DASHBOARD_PORT', 8000),
            'cors_origins': self.get_list('CORS_ORIGINS', ['*']),
        })
        
        # Security settings
        config.update({
            'api_key_required': self.get_bool('API_KEY_REQUIRED', False),
            'rate_limit_requests_per_minute': self.get_int('RATE_LIMIT_REQUESTS_PER_MINUTE', 60),
        })
        
        # Performance settings
        config.update({
            'max_concurrent_requests': self.get_int('MAX_CONCURRENT_REQUESTS', 10),
            'request_timeout': self.get_int('REQUEST_TIMEOUT', 30),
            'cache_responses': self.get_bool('CACHE_RESPONSES', True),
            'cache_ttl': self.get_int('CACHE_TTL', 3600),
        })
        
        # Analytics settings
        config.update({
            'effect_size_threshold': self.get_float('EFFECT_SIZE_THRESHOLD', 0.2),
            'significance_level': self.get_float('SIGNIFICANCE_LEVEL', 0.05),
            'confidence_interval': self.get_float('CONFIDENCE_INTERVAL', 0.90),
        })
        
        # Feature flags
        config.update({
            'real_time_dashboard': self.get_bool('REAL_TIME_DASHBOARD', True),
            'batch_processing': self.get_bool('BATCH_PROCESSING', True),
            'model_comparison': self.get_bool('MODEL_COMPARISON', True),
            'trend_analysis': self.get_bool('TREND_ANALYSIS', True),
            'export_functionality': self.get_bool('EXPORT_FUNCTIONALITY', True),
            'educational_content': self.get_bool('EDUCATIONAL_CONTENT', True),
            'bias_mitigation_recommendations': self.get_bool('BIAS_MITIGATION_RECOMMENDATIONS', False),
        })
        
        # Development settings
        config.update({
            'hot_reload': self.get_bool('HOT_RELOAD', False),
            'mock_llm_responses': self.get_bool('MOCK_LLM_RESPONSES', False),
            'test_mode': self.get_bool('TEST_MODE', False),
        })
        
        # Ollama settings
        config.update({
            'ollama_base_url': self.get('OLLAMA_BASE_URL', 'http://localhost:11434'),
            'default_local_model': self.get('DEFAULT_LOCAL_MODEL', 'llama3'),
        })
        
        # Advanced settings
        config.update({
            'default_temperature': self.get_float('DEFAULT_TEMPERATURE', 0.7),
            'default_max_tokens': self.get_int('DEFAULT_MAX_TOKENS', 1000),
            'default_timeout': self.get_int('DEFAULT_TIMEOUT', 30),
            'max_retries': self.get_int('MAX_RETRIES', 3),
            'retry_delay': self.get_float('RETRY_DELAY', 1.0),
        })
        
        return config


# Pydantic-based settings class (if available)
if PYDANTIC_AVAILABLE:
    class Settings(PydanticBaseSettings):
        """Pydantic-based settings with validation."""
        
        # Application settings
        app_name: str = Field(default="AI Bias Psychologist", env="APP_NAME")
        app_version: str = Field(default="0.1.0", env="APP_VERSION")
        debug: bool = Field(default=False, env="DEBUG")
        log_level: str = Field(default="INFO", env="LOG_LEVEL")
        
        # Database settings
        database_url: str = Field(default="sqlite:///./data/database/bias_psych.db", env="DATABASE_URL")
        
        # Storage paths
        base_dir: str = Field(default="./data", env="BASE_DIR")
        responses_dir: str = Field(default="./data/responses", env="RESPONSES_DIR")
        exports_dir: str = Field(default="./data/exports", env="EXPORTS_DIR")
        logs_dir: str = Field(default="./data/logs", env="LOGS_DIR")
        
        # API keys
        openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
        openai_org_id: Optional[str] = Field(default=None, env="OPENAI_ORG_ID")
        anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
        
        # Dashboard settings
        dashboard_host: str = Field(default="0.0.0.0", env="DASHBOARD_HOST")
        dashboard_port: int = Field(default=8000, env="DASHBOARD_PORT")
        cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
        
        # Security settings
        api_key_required: bool = Field(default=False, env="API_KEY_REQUIRED")
        rate_limit_requests_per_minute: int = Field(default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
        
        # Performance settings
        max_concurrent_requests: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")
        request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
        cache_responses: bool = Field(default=True, env="CACHE_RESPONSES")
        cache_ttl: int = Field(default=3600, env="CACHE_TTL")
        
        # Analytics settings
        effect_size_threshold: float = Field(default=0.2, env="EFFECT_SIZE_THRESHOLD")
        significance_level: float = Field(default=0.05, env="SIGNIFICANCE_LEVEL")
        confidence_interval: float = Field(default=0.90, env="CONFIDENCE_INTERVAL")
        
        # Feature flags
        real_time_dashboard: bool = Field(default=True, env="REAL_TIME_DASHBOARD")
        batch_processing: bool = Field(default=True, env="BATCH_PROCESSING")
        model_comparison: bool = Field(default=True, env="MODEL_COMPARISON")
        trend_analysis: bool = Field(default=True, env="TREND_ANALYSIS")
        export_functionality: bool = Field(default=True, env="EXPORT_FUNCTIONALITY")
        educational_content: bool = Field(default=True, env="EDUCATIONAL_CONTENT")
        bias_mitigation_recommendations: bool = Field(default=False, env="BIAS_MITIGATION_RECOMMENDATIONS")
        
        # Development settings
        hot_reload: bool = Field(default=False, env="HOT_RELOAD")
        mock_llm_responses: bool = Field(default=False, env="MOCK_LLM_RESPONSES")
        test_mode: bool = Field(default=False, env="TEST_MODE")
        
        # Ollama settings
        ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
        default_local_model: str = Field(default="llama3", env="DEFAULT_LOCAL_MODEL")
        
        # Advanced settings
        default_temperature: float = Field(default=0.7, env="DEFAULT_TEMPERATURE")
        default_max_tokens: int = Field(default=1000, env="DEFAULT_MAX_TOKENS")
        default_timeout: int = Field(default=30, env="DEFAULT_TIMEOUT")
        max_retries: int = Field(default=3, env="MAX_RETRIES")
        retry_delay: float = Field(default=1.0, env="RETRY_DELAY")
        
        @validator('cors_origins', pre=True)
        def parse_cors_origins(cls, v):
            if isinstance(v, str):
                return [item.strip() for item in v.split(',')]
            return v
        
        @validator('log_level')
        def validate_log_level(cls, v):
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if v.upper() not in valid_levels:
                raise ValueError(f'log_level must be one of {valid_levels}')
            return v.upper()
        
        @validator('dashboard_port')
        def validate_dashboard_port(cls, v):
            if not 1 <= v <= 65535:
                raise ValueError('dashboard_port must be between 1 and 65535')
            return v
        
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False


# Global configuration instances
_env_config: Optional[EnvironmentConfig] = None
_settings: Optional[Settings] = None


@lru_cache()
def get_env_config(env_file: str = ".env") -> EnvironmentConfig:
    """Get cached environment configuration instance."""
    global _env_config
    if _env_config is None:
        _env_config = EnvironmentConfig(env_file)
    return _env_config


def get_settings() -> Union[Settings, EnvironmentConfig]:
    """Get settings instance (Pydantic if available, fallback to basic)."""
    global _settings
    if _settings is None and PYDANTIC_AVAILABLE:
        _settings = Settings()
        return _settings
    elif _settings is None:
        return get_env_config()
    return _settings


def validate_environment() -> bool:
    """Validate environment configuration."""
    try:
        config = get_env_config()
        
        # Check for required API keys if not in test mode
        if not config.get_bool('TEST_MODE', False):
            required_for_providers = {
                'openai': ['OPENAI_API_KEY'],
                'anthropic': ['ANTHROPIC_API_KEY'],
            }
            
            # Only validate if the provider is being used
            # This is a basic check - more sophisticated validation can be added later
            pass
        
        # Validate numeric ranges
        dashboard_port = config.get_int('DASHBOARD_PORT', 8000)
        if not 1 <= dashboard_port <= 65535:
            raise ValueError(f"Invalid dashboard port: {dashboard_port}")
        
        log_level = config.get('LOG_LEVEL', 'INFO')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {log_level}")
        
        return True
        
    except Exception as e:
        logging.error(f"Environment validation failed: {e}")
        return False


def print_config_summary() -> None:
    """Print a summary of current configuration."""
    config = get_env_config()
    
    print("AI Bias Psychologist - Configuration Summary")
    print("=" * 50)
    
    # Application info
    print(f"Application: {config.get('APP_NAME', 'AI Bias Psychologist')} v{config.get('APP_VERSION', '0.1.0')}")
    print(f"Debug Mode: {config.get_bool('DEBUG', False)}")
    print(f"Log Level: {config.get('LOG_LEVEL', 'INFO')}")
    
    # Database
    print(f"Database: {config.get('DATABASE_URL', 'sqlite:///./data/database/bias_psych.db')}")
    
    # API Keys
    openai_key = config.get('OPENAI_API_KEY')
    anthropic_key = config.get('ANTHROPIC_API_KEY')
    print(f"OpenAI API Key: {'✓ Set' if openai_key else '✗ Not set'}")
    print(f"Anthropic API Key: {'✓ Set' if anthropic_key else '✗ Not set'}")
    
    # Dashboard
    print(f"Dashboard: http://{config.get('DASHBOARD_HOST', '0.0.0.0')}:{config.get_int('DASHBOARD_PORT', 8000)}")
    
    # Feature flags
    features = [
        'real_time_dashboard', 'batch_processing', 'model_comparison',
        'trend_analysis', 'export_functionality', 'educational_content'
    ]
    enabled_features = [f for f in features if config.get_bool(f.upper(), True)]
    print(f"Enabled Features: {', '.join(enabled_features)}")
    
    print("=" * 50)
