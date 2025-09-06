#!/usr/bin/env python3
"""
Simple test script for environment configuration without external dependencies.
"""

import sys
import os
from pathlib import Path

def test_env_file_creation():
    """Test that .env.example file exists and has content."""
    print("Testing .env.example file...")
    
    env_example_file = Path(".env.example")
    if not env_example_file.exists():
        print("❌ .env.example file not found")
        return False
    
    content = env_example_file.read_text(encoding='utf-8')
    if len(content) < 100:
        print("❌ .env.example file appears to be empty or too short")
        return False
    
    # Check for key sections
    required_sections = [
        "APPLICATION SETTINGS",
        "DATABASE CONFIGURATION", 
        "LLM API KEYS",
        "DASHBOARD CONFIGURATION"
    ]
    
    for section in required_sections:
        if section not in content:
            print(f"❌ Missing section: {section}")
            return False
        print(f"✓ Found section: {section}")
    
    print("✓ .env.example file is properly configured")
    return True


def test_basic_env_variables():
    """Test basic environment variable handling."""
    print("\nTesting basic environment variable handling...")
    
    # Test setting and getting environment variables
    test_key = "TEST_AI_BIAS_PSYCH_VAR"
    test_value = "test_value_123"
    
    # Set environment variable
    os.environ[test_key] = test_value
    
    # Get environment variable
    retrieved_value = os.environ.get(test_key)
    
    if retrieved_value == test_value:
        print("✓ Environment variable set and retrieved successfully")
    else:
        print(f"❌ Environment variable mismatch: {retrieved_value} != {test_value}")
        return False
    
    # Test default value
    default_value = os.environ.get("NON_EXISTENT_VAR", "default")
    if default_value == "default":
        print("✓ Default value handling works")
    else:
        print("❌ Default value handling failed")
        return False
    
    # Clean up
    del os.environ[test_key]
    
    return True


def test_env_file_parsing():
    """Test manual .env file parsing."""
    print("\nTesting .env file parsing...")
    
    # Create a test .env file
    test_env_content = """# Test environment file
APP_NAME="Test App"
DEBUG=true
DASHBOARD_PORT=9000
CORS_ORIGINS="localhost,127.0.0.1"
DEFAULT_TEMPERATURE=0.5
"""
    
    test_env_file = Path("test.env")
    try:
        # Write test file
        test_env_file.write_text(test_env_content, encoding='utf-8')
        
        # Parse the file manually
        env_vars = {}
        with open(test_env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    env_vars[key] = value
        
        # Test parsed values
        expected_values = {
            'APP_NAME': 'Test App',
            'DEBUG': 'true',
            'DASHBOARD_PORT': '9000',
            'CORS_ORIGINS': 'localhost,127.0.0.1',
            'DEFAULT_TEMPERATURE': '0.5'
        }
        
        for key, expected_value in expected_values.items():
            if key in env_vars and env_vars[key] == expected_value:
                print(f"✓ Parsed {key} = {expected_value}")
            else:
                print(f"❌ Failed to parse {key}: {env_vars.get(key)} != {expected_value}")
                return False
        
        return True
        
    finally:
        # Clean up test file
        if test_env_file.exists():
            test_env_file.unlink()


def test_configuration_structure():
    """Test that configuration files have proper structure."""
    print("\nTesting configuration file structure...")
    
    config_files = [
        "config/probes.yaml",
        "config/models.yaml", 
        "config/app.yaml",
        "config/logging.yaml"
    ]
    
    for config_file in config_files:
        file_path = Path(config_file)
        if not file_path.exists():
            print(f"❌ Configuration file not found: {config_file}")
            return False
        
        content = file_path.read_text(encoding='utf-8')
        if len(content) < 50:
            print(f"❌ Configuration file appears empty: {config_file}")
            return False
        
        print(f"✓ Configuration file exists and has content: {config_file}")
    
    return True


def test_directory_structure():
    """Test that required directories exist."""
    print("\nTesting directory structure...")
    
    required_dirs = [
        "config",
        "data",
        "data/responses",
        "data/database", 
        "data/exports",
        "data/logs",
        "src/ai_bias_psych",
        "scripts"
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists() or not path.is_dir():
            print(f"❌ Required directory not found: {dir_path}")
            return False
        print(f"✓ Directory exists: {dir_path}")
    
    return True


def main():
    """Main test function."""
    print("AI Bias Psychologist - Simple Environment Configuration Test")
    print("=" * 65)
    
    tests = [
        test_env_file_creation,
        test_basic_env_variables,
        test_env_file_parsing,
        test_configuration_structure,
        test_directory_structure,
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
    
    print("\n" + "=" * 65)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All environment configuration tests passed!")
        print("\nEnvironment configuration is ready!")
        print("Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your API keys in .env")
        print("3. Install dependencies: pip install -r requirements.txt")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
