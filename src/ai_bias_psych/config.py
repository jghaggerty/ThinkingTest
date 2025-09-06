"""
Configuration management for AI Bias Psychologist.

This module provides configuration loading, validation, and management
for all application settings including probes, models, and app configuration.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field
from functools import lru_cache


class ConfigError(Exception):
    """Configuration-related errors."""
    pass


class AppConfig(BaseSettings):
    """Application configuration with environment variable support."""
    
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
    
    # API keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, "ANTHROPIC_API_KEY")
    
    # Dashboard settings
    dashboard_host: str = Field(default="0.0.0.0", env="DASHBOARD_HOST")
    dashboard_port: int = Field(default=8000, env="DASHBOARD_PORT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ConfigManager:
    """Manages configuration loading and access."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._probes_config: Optional[Dict[str, Any]] = None
        self._models_config: Optional[Dict[str, Any]] = None
        self._app_config: Optional[Dict[str, Any]] = None
        self._settings = AppConfig()
    
    def load_probes_config(self) -> Dict[str, Any]:
        """Load and cache probes configuration."""
        if self._probes_config is None:
            config_file = self.config_dir / "probes.yaml"
            if not config_file.exists():
                raise ConfigError(f"Probes configuration file not found: {config_file}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self._probes_config = yaml.safe_load(f)
        
        return self._probes_config
    
    def load_models_config(self) -> Dict[str, Any]:
        """Load and cache models configuration."""
        if self._models_config is None:
            config_file = self.config_dir / "models.yaml"
            if not config_file.exists():
                raise ConfigError(f"Models configuration file not found: {config_file}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self._models_config = yaml.safe_load(f)
        
        return self._models_config
    
    def load_app_config(self) -> Dict[str, Any]:
        """Load and cache application configuration."""
        if self._app_config is None:
            config_file = self.config_dir / "app.yaml"
            if not config_file.exists():
                raise ConfigError(f"App configuration file not found: {config_file}")
            
            with open(config_file, 'r', encoding='utf-8') as f:
                self._app_config = yaml.safe_load(f)
        
        return self._app_config
    
    def get_probe_config(self, probe_type: str) -> Dict[str, Any]:
        """Get configuration for a specific probe type."""
        probes_config = self.load_probes_config()
        if probe_type not in probes_config.get("probes", {}):
            raise ConfigError(f"Unknown probe type: {probe_type}")
        
        return probes_config["probes"][probe_type]
    
    def get_model_config(self, provider: str, model: str) -> Dict[str, Any]:
        """Get configuration for a specific model."""
        models_config = self.load_models_config()
        if provider not in models_config.get("providers", {}):
            raise ConfigError(f"Unknown provider: {provider}")
        
        provider_config = models_config["providers"][provider]
        if model not in provider_config.get("models", {}):
            raise ConfigError(f"Unknown model {model} for provider {provider}")
        
        return provider_config["models"][model]
    
    def get_available_probes(self) -> list[str]:
        """Get list of available probe types."""
        probes_config = self.load_probes_config()
        return list(probes_config.get("probes", {}).keys())
    
    def get_available_providers(self) -> list[str]:
        """Get list of available providers."""
        models_config = self.load_models_config()
        return list(models_config.get("providers", {}).keys())
    
    def get_available_models(self, provider: Optional[str] = None) -> Dict[str, list[str]]:
        """Get available models, optionally filtered by provider."""
        models_config = self.load_models_config()
        providers = models_config.get("providers", {})
        
        if provider:
            if provider not in providers:
                raise ConfigError(f"Unknown provider: {provider}")
            return {provider: list(providers[provider].get("models", {}).keys())}
        
        return {
            prov: list(config.get("models", {}).keys())
            for prov, config in providers.items()
        }
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default settings from configuration files."""
        probes_config = self.load_probes_config()
        models_config = self.load_models_config()
        
        return {
            "temperature": probes_config.get("settings", {}).get("default_temperature", 0.7),
            "max_tokens": probes_config.get("settings", {}).get("default_max_tokens", 1000),
            "timeout": probes_config.get("settings", {}).get("response_timeout", 30),
            "max_retries": probes_config.get("settings", {}).get("max_retries", 3),
            "provider": models_config.get("defaults", {}).get("provider", "openai"),
            "model": models_config.get("defaults", {}).get("model", "gpt-4"),
        }
    
    @property
    def settings(self) -> AppConfig:
        """Get application settings with environment variable support."""
        return self._settings
    
    def validate_config(self) -> bool:
        """Validate all configuration files."""
        try:
            # Load all configs to validate they exist and are valid YAML
            self.load_probes_config()
            self.load_models_config()
            self.load_app_config()
            
            # Validate probe configurations
            probes_config = self.load_probes_config()
            for probe_type, probe_config in probes_config.get("probes", {}).items():
                if "variants" not in probe_config:
                    raise ConfigError(f"Probe {probe_type} missing variants")
                
                for variant in probe_config["variants"]:
                    if "id" not in variant:
                        raise ConfigError(f"Probe {probe_type} variant missing id")
            
            # Validate model configurations
            models_config = self.load_models_config()
            for provider, provider_config in models_config.get("providers", {}).items():
                if "models" not in provider_config:
                    raise ConfigError(f"Provider {provider} missing models")
                
                for model, model_config in provider_config["models"].items():
                    required_fields = ["name", "max_tokens", "context_window"]
                    for field in required_fields:
                        if field not in model_config:
                            raise ConfigError(f"Model {model} missing {field}")
            
            return True
            
        except Exception as e:
            raise ConfigError(f"Configuration validation failed: {e}")


@lru_cache()
def get_config_manager() -> ConfigManager:
    """Get cached configuration manager instance."""
    return ConfigManager()


# Convenience functions
def get_probe_config(probe_type: str) -> Dict[str, Any]:
    """Get configuration for a specific probe type."""
    return get_config_manager().get_probe_config(probe_type)


def get_model_config(provider: str, model: str) -> Dict[str, Any]:
    """Get configuration for a specific model."""
    return get_config_manager().get_model_config(provider, model)


def get_available_probes() -> list[str]:
    """Get list of available probe types."""
    return get_config_manager().get_available_probes()


def get_available_models(provider: Optional[str] = None) -> Dict[str, list[str]]:
    """Get available models, optionally filtered by provider."""
    return get_config_manager().get_available_models(provider)


def get_app_settings() -> AppConfig:
    """Get application settings."""
    return get_config_manager().settings
