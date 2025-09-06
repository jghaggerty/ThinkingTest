#!/usr/bin/env python3
"""
Test script for environment configuration.

This script tests the environment configuration system to ensure
it properly loads and validates environment variables.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_basic_env_config():
    """Test basic environment configuration without external dependencies."""
    print("Testing basic environment configuration...")
    
    # Test with default values
    from ai_bias_psych.env_config import EnvironmentConfig
    
    config = EnvironmentConfig()
    
    # Test basic get operations
    app_name = config.get('APP_NAME', 'AI Bias Psychologist')
    print(f"✓ App name: {app_name}")
    
    debug = config.get_bool('DEBUG', False)
    print(f"✓ Debug mode: {debug}")
    
    port = config.get_int('DASHBOARD_PORT', 8000)
    print(f"✓ Dashboard port: {port}")
    
    # Test list parsing
    cors_origins = config.get_list('CORS_ORIGINS', ['*'])
    print(f"✓ CORS origins: {cors_origins}")
    
    # Test type casting
    temperature = config.get_float('DEFAULT_TEMPERATURE', 0.7)
    print(f"✓ Default temperature: {temperature}")
    
    return True


def test_env_file_parsing():
    """Test .env file parsing."""
    print("\nTesting .env file parsing...")
    
    # Create a test .env file
    test_env_content = """
# Test environment file
APP_NAME="Test App"
DEBUG=true
DASHBOARD_PORT=9000
CORS_ORIGINS="localhost,127.0.0.1"
DEFAULT_TEMPERATURE=0.5
"""
    
    test_env_file = Path("test.env")
    try:
        with open(test_env_file, 'w', encoding='utf-8') as f:
            f.write(test_env_content)
        
        from ai_bias_psych.env_config import EnvironmentConfig
        
        config = EnvironmentConfig(str(test_env_file))
        
        # Test values from .env file
        assert config.get('APP_NAME') == 'Test App'
        print("✓ APP_NAME loaded from .env file")
        
        assert config.get_bool('DEBUG') == True
        print("✓ DEBUG loaded from .env file")
        
        assert config.get_int('DASHBOARD_PORT') == 9000
        print("✓ DASHBOARD_PORT loaded from .env file")
        
        cors_origins = config.get_list('CORS_ORIGINS')
        assert cors_origins == ['localhost', '127.0.0.1']
        print("✓ CORS_ORIGINS parsed as list")
        
        assert config.get_float('DEFAULT_TEMPERATURE') == 0.5
        print("✓ DEFAULT_TEMPERATURE loaded from .env file")
        
        return True
        
    finally:
        # Clean up test file
        if test_env_file.exists():
            test_env_file.unlink()


def test_config_validation():
    """Test configuration validation."""
    print("\nTesting configuration validation...")
    
    from ai_bias_psych.env_config import validate_environment
    
    # Test with valid configuration
    if validate_environment():
        print("✓ Environment validation passed")
    else:
        print("✗ Environment validation failed")
        return False
    
    return True


def test_config_summary():
    """Test configuration summary printing."""
    print("\nTesting configuration summary...")
    
    from ai_bias_psych.env_config import print_config_summary
    
    try:
        print_config_summary()
        print("✓ Configuration summary printed successfully")
        return True
    except Exception as e:
        print(f"✗ Configuration summary failed: {e}")
        return False


def test_required_variables():
    """Test required variable validation."""
    print("\nTesting required variable validation...")
    
    from ai_bias_psych.env_config import EnvironmentConfig
    
    config = EnvironmentConfig()
    
    # Test with missing required variables
    try:
        config.validate_required(['NON_EXISTENT_VAR'])
        print("✗ Should have failed with missing required variable")
        return False
    except ValueError:
        print("✓ Correctly failed with missing required variable")
    
    # Test with existing variables
    try:
        config.validate_required(['APP_NAME'])
        print("✓ Validation passed with existing variable")
    except ValueError:
        print("✗ Should have passed with existing variable")
        return False
    
    return True


def test_get_all_config():
    """Test getting all configuration as dictionary."""
    print("\nTesting get_all_config...")
    
    from ai_bias_psych.env_config import EnvironmentConfig
    
    config = EnvironmentConfig()
    all_config = config.get_all_config()
    
    # Check that we have expected keys
    expected_keys = [
        'app_name', 'app_version', 'debug', 'log_level',
        'database_url', 'base_dir', 'dashboard_host', 'dashboard_port'
    ]
    
    for key in expected_keys:
        if key in all_config:
            print(f"✓ Found config key: {key}")
        else:
            print(f"✗ Missing config key: {key}")
            return False
    
    print(f"✓ Configuration dictionary contains {len(all_config)} keys")
    return True


def main():
    """Main test function."""
    print("AI Bias Psychologist - Environment Configuration Test")
    print("=" * 60)
    
    tests = [
        test_basic_env_config,
        test_env_file_parsing,
        test_config_validation,
        test_config_summary,
        test_required_variables,
        test_get_all_config,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All environment configuration tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
