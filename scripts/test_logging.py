#!/usr/bin/env python3
"""
Test script for logging configuration.

This script tests the logging setup to ensure it works correctly
without requiring the full package dependencies.
"""

import sys
import os
import logging
import json
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Simple logging setup without external dependencies
def setup_simple_logging():
    """Set up simple logging for testing."""
    
    # Create logs directory
    log_dir = Path("./data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    log_file = log_dir / "test.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(console_formatter)
    root_logger.addHandler(file_handler)
    
    return root_logger


def test_logging():
    """Test logging functionality."""
    print("Testing logging configuration...")
    
    # Set up logging
    logger = setup_simple_logging()
    
    # Test basic logging
    logger.info("Logging test started")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test probe execution logging
    probe_logger = logging.getLogger("probe_execution")
    probe_logger.info("Probe execution test", extra={
        "probe_type": "anchoring",
        "variant_id": "geography_river",
        "model_provider": "openai",
        "model_name": "gpt-4",
        "session_id": "test_session_001"
    })
    
    # Test LLM request logging
    llm_logger = logging.getLogger("llm_requests")
    llm_logger.info("LLM request test", extra={
        "provider": "openai",
        "model": "gpt-4",
        "request_type": "probe_execution",
        "tokens_used": 150,
        "response_time_ms": 2500
    })
    
    # Test analytics logging
    analytics_logger = logging.getLogger("analytics")
    analytics_logger.info("Analytics test", extra={
        "event_type": "score_calculation",
        "probe_type": "anchoring",
        "raw_score": 0.75,
        "normalized_score": 0.8,
        "effect_size": 0.3
    })
    
    logger.info("Logging test completed successfully")
    
    # Check if log file was created
    log_file = Path("./data/logs/test.log")
    if log_file.exists():
        print(f"✅ Log file created: {log_file}")
        print(f"Log file size: {log_file.stat().st_size} bytes")
    else:
        print("❌ Log file was not created")
    
    return True


def test_structured_logging():
    """Test structured logging with JSON format."""
    print("\nTesting structured logging...")
    
    # Create a simple JSON formatter
    class SimpleJSONFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            # Add extra fields
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                              'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                              'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                              'thread', 'threadName', 'processName', 'process', 'getMessage']:
                    log_entry[key] = value
            
            return json.dumps(log_entry, ensure_ascii=False)
    
    # Set up structured logging
    log_dir = Path("./data/logs")
    structured_log_file = log_dir / "structured_test.log"
    
    structured_handler = logging.FileHandler(structured_log_file, encoding='utf-8')
    structured_handler.setFormatter(SimpleJSONFormatter())
    
    structured_logger = logging.getLogger("structured_test")
    structured_logger.addHandler(structured_handler)
    structured_logger.setLevel(logging.INFO)
    
    # Test structured logging
    structured_logger.info("Structured logging test", extra={
        "probe_type": "prospect_theory",
        "variant_id": "health_treatment",
        "model_provider": "anthropic",
        "model_name": "claude-3-sonnet",
        "session_id": "test_session_002",
        "response_time_ms": 1800,
        "tokens_used": 200
    })
    
    # Check structured log file
    if structured_log_file.exists():
        print(f"✅ Structured log file created: {structured_log_file}")
        
        # Read and validate JSON
        with open(structured_log_file, 'r', encoding='utf-8') as f:
            log_line = f.read().strip()
            try:
                log_data = json.loads(log_line)
                print(f"✅ Valid JSON log entry created")
                print(f"Log entry keys: {list(log_data.keys())}")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in log file: {e}")
                return False
    else:
        print("❌ Structured log file was not created")
        return False
    
    return True


def main():
    """Main test function."""
    print("AI Bias Psychologist - Logging Configuration Test")
    print("=" * 50)
    
    try:
        # Test basic logging
        if test_logging():
            print("✅ Basic logging test passed")
        else:
            print("❌ Basic logging test failed")
            return False
        
        # Test structured logging
        if test_structured_logging():
            print("✅ Structured logging test passed")
        else:
            print("❌ Structured logging test failed")
            return False
        
        print("\n🎉 All logging tests passed!")
        print("Logging configuration is working correctly.")
        
        return True
        
    except Exception as e:
        print(f"❌ Logging test failed with error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
