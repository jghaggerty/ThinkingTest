"""
Logging configuration for AI Bias Psychologist.

This module provides structured logging setup with proper formatting,
file rotation, and context-aware logging for probe execution and analysis.
"""

import logging
import logging.handlers
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import structlog
from structlog.stdlib import LoggerFactory


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


class ProbeContextFilter(logging.Filter):
    """Filter to add probe execution context to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add probe context to log record."""
        # Add probe context if available in the current context
        if hasattr(record, 'probe_context'):
            return True
        
        # Try to get context from structlog context
        try:
            context = structlog.get_logger()._context
            if context:
                record.probe_context = dict(context)
        except:
            pass
        
        return True


class LoggingManager:
    """Manages logging configuration and setup."""
    
    def __init__(self, 
                 log_level: str = "INFO",
                 log_dir: str = "./data/logs",
                 console_output: bool = True,
                 file_output: bool = True,
                 structured_logging: bool = True):
        self.log_level = log_level.upper()
        self.log_dir = Path(log_dir)
        self.console_output = console_output
        self.file_output = file_output
        self.structured_logging = structured_logging
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Set root logger level
        root_logger.setLevel(getattr(logging, self.log_level))
        
        # Configure structlog if enabled
        if self.structured_logging:
            self._setup_structlog()
        
        # Add console handler
        if self.console_output:
            self._add_console_handler()
        
        # Add file handlers
        if self.file_output:
            self._add_file_handlers()
    
    def _setup_structlog(self) -> None:
        """Configure structlog for structured logging."""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    def _add_console_handler(self) -> None:
        """Add console logging handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.log_level))
        
        if self.structured_logging:
            console_handler.setFormatter(JSONFormatter())
        else:
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
        
        # Add probe context filter
        console_handler.addFilter(ProbeContextFilter())
        
        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)
    
    def _add_file_handlers(self) -> None:
        """Add file logging handlers."""
        # Main application log
        app_log_file = self.log_dir / "ai_bias_psych.log"
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        app_handler.setLevel(getattr(logging, self.log_level))
        app_handler.setFormatter(JSONFormatter())
        app_handler.addFilter(ProbeContextFilter())
        
        # Probe execution log
        probe_log_file = self.log_dir / "probe_execution.log"
        probe_handler = logging.handlers.RotatingFileHandler(
            probe_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        probe_handler.setLevel(logging.INFO)
        probe_handler.setFormatter(JSONFormatter())
        probe_handler.addFilter(ProbeContextFilter())
        
        # Error log
        error_log_file = self.log_dir / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        error_handler.addFilter(ProbeContextFilter())
        
        root_logger = logging.getLogger()
        root_logger.addHandler(app_handler)
        root_logger.addHandler(probe_handler)
        root_logger.addHandler(error_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance."""
        return logging.getLogger(name)
    
    def get_structured_logger(self, name: str) -> structlog.BoundLogger:
        """Get a structured logger instance."""
        return structlog.get_logger(name)


class ProbeLogger:
    """Specialized logger for probe execution with context."""
    
    def __init__(self, logger_name: str = "probe_execution"):
        self.logger = logging.getLogger(logger_name)
        self.structured_logger = structlog.get_logger(logger_name)
    
    def log_probe_start(self, 
                       probe_type: str,
                       variant_id: str,
                       model_provider: str,
                       model_name: str,
                       session_id: str,
                       **kwargs) -> None:
        """Log probe execution start."""
        context = {
            "event": "probe_start",
            "probe_type": probe_type,
            "variant_id": variant_id,
            "model_provider": model_provider,
            "model_name": model_name,
            "session_id": session_id,
            **kwargs
        }
        
        self.structured_logger.info("Probe execution started", **context)
    
    def log_probe_response(self,
                          probe_type: str,
                          variant_id: str,
                          model_provider: str,
                          model_name: str,
                          response_time_ms: int,
                          tokens_used: int,
                          response_length: int,
                          **kwargs) -> None:
        """Log probe response received."""
        context = {
            "event": "probe_response",
            "probe_type": probe_type,
            "variant_id": variant_id,
            "model_provider": model_provider,
            "model_name": model_name,
            "response_time_ms": response_time_ms,
            "tokens_used": tokens_used,
            "response_length": response_length,
            **kwargs
        }
        
        self.structured_logger.info("Probe response received", **context)
    
    def log_probe_error(self,
                       probe_type: str,
                       variant_id: str,
                       model_provider: str,
                       model_name: str,
                       error_message: str,
                       **kwargs) -> None:
        """Log probe execution error."""
        context = {
            "event": "probe_error",
            "probe_type": probe_type,
            "variant_id": variant_id,
            "model_provider": model_provider,
            "model_name": model_name,
            "error_message": error_message,
            **kwargs
        }
        
        self.structured_logger.error("Probe execution failed", **context)
    
    def log_bias_score(self,
                      probe_type: str,
                      variant_id: str,
                      model_provider: str,
                      model_name: str,
                      raw_score: float,
                      normalized_score: float,
                      effect_size: Optional[float] = None,
                      **kwargs) -> None:
        """Log bias score calculation."""
        context = {
            "event": "bias_score",
            "probe_type": probe_type,
            "variant_id": variant_id,
            "model_provider": model_provider,
            "model_name": model_name,
            "raw_score": raw_score,
            "normalized_score": normalized_score,
            "effect_size": effect_size,
            **kwargs
        }
        
        self.structured_logger.info("Bias score calculated", **context)
    
    def log_session_start(self, session_id: str, **kwargs) -> None:
        """Log session start."""
        context = {
            "event": "session_start",
            "session_id": session_id,
            **kwargs
        }
        
        self.structured_logger.info("Session started", **context)
    
    def log_session_end(self, session_id: str, total_probes: int, **kwargs) -> None:
        """Log session end."""
        context = {
            "event": "session_end",
            "session_id": session_id,
            "total_probes": total_probes,
            **kwargs
        }
        
        self.structured_logger.info("Session completed", **context)


# Global logging manager instance
_logging_manager: Optional[LoggingManager] = None


def setup_logging(log_level: str = "INFO",
                 log_dir: str = "./data/logs",
                 console_output: bool = True,
                 file_output: bool = True,
                 structured_logging: bool = True) -> LoggingManager:
    """Set up logging configuration."""
    global _logging_manager
    _logging_manager = LoggingManager(
        log_level=log_level,
        log_dir=log_dir,
        console_output=console_output,
        file_output=file_output,
        structured_logging=structured_logging
    )
    return _logging_manager


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    if _logging_manager is None:
        setup_logging()
    return _logging_manager.get_logger(name)


def get_structured_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    if _logging_manager is None:
        setup_logging()
    return _logging_manager.get_structured_logger(name)


def get_probe_logger() -> ProbeLogger:
    """Get a probe execution logger."""
    return ProbeLogger()


# Convenience functions for common logging patterns
def log_probe_execution(probe_type: str, 
                       variant_id: str,
                       model_provider: str,
                       model_name: str,
                       event: str,
                       **kwargs) -> None:
    """Log probe execution event."""
    logger = get_structured_logger("probe_execution")
    context = {
        "probe_type": probe_type,
        "variant_id": variant_id,
        "model_provider": model_provider,
        "model_name": model_name,
        "event": event,
        **kwargs
    }
    logger.info(f"Probe execution: {event}", **context)


def log_llm_request(provider: str,
                   model: str,
                   request_type: str,
                   **kwargs) -> None:
    """Log LLM API request."""
    logger = get_structured_logger("llm_requests")
    context = {
        "provider": provider,
        "model": model,
        "request_type": request_type,
        **kwargs
    }
    logger.info(f"LLM request: {request_type}", **context)


def log_analytics_event(event_type: str, **kwargs) -> None:
    """Log analytics and scoring event."""
    logger = get_structured_logger("analytics")
    context = {
        "event_type": event_type,
        **kwargs
    }
    logger.info(f"Analytics: {event_type}", **context)
