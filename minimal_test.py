#!/usr/bin/env python3
"""
Simple Basic Test Script

This script tests ONLY the essential components needed for a basic smart home system.
No complex integrations, no real APIs, just the core functionality.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} - Need Python 3.8+")
        return False

def check_virtual_env():
    """Check if running in virtual environment"""
    print("\n📦 Checking virtual environment...")
    
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if in_venv:
        print("✅ Virtual environment active")
        return True
    else:
        print("⚠️  Virtual environment not detected")
        print("   Recommended: python -m venv venv && source venv/bin/activate")
        return False

def test_basic_imports():
    """Test that basic modules can be imported"""
    print("\n📥 Testing basic imports...")
    
    try:
        # Test pathlib (built-in)
        from pathlib import Path
        print("✅ pathlib - OK")
        
        # Test os (built-in)
        import os
        print("✅ os - OK")
        
        # Test sys (built-in)
        import sys
        print("✅ sys - OK")
        
        return True
    except ImportError as e:
        print(f"❌ Basic import failed: {e}")
        return False

def test_flask_import():
    """Test Flask import"""
    print("\n🌐 Testing Flask import...")
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__} - OK")
        
        from flask import Flask, jsonify, request
        print("✅ Flask components - OK")
        
        return True
    except ImportError:
        print("❌ Flask not installed")
        print("   Install with: pip install flask")
        return False

def test_config_module():
    """Test configuration module"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from src.config import config
        
        # Check basic attributes
        app_name = getattr(config, 'APP_NAME', 'Unknown')
        app_version = getattr(config, 'APP_VERSION', '0.0.0')
        debug = getattr(config, 'DEBUG', False)
        
        print(f"✅ App Name: {app_name}")
        print(f"✅ Version: {app_version}")
        print(f"✅ Debug Mode: {debug}")
        
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_logger():
    """Test logging system"""
    print("\n📝 Testing logging...")
    
    try:
        from src.utils.logger import logger
        
        # Test log message
        logger.info("Test log message from basic test")
        print("✅ Logger working")
        
        return True
    except Exception as e:
        print(f"❌ Logger error: {e}")
        return False

def test_flask_app():
    """Test Flask app creation"""
    print("\n🚀 Testing Flask app creation...")
    
    try:
        from src.api.routes import create_flask_app
        
        app = create_flask_app()
        print("✅ Flask app created")
        
        # Test basic endpoints
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint - OK")
                
                data = response.get_json()
                status = data.get('status', 'unknown')
                print(f"   Status: {status}")
                
                if status == 'healthy':
                    print("✅ Health check - PASSED")
                else:
                    print("⚠️  Health check status not 'healthy'")
            else:
                print(f"❌ Health endpoint failed: HTTP {response.status_code}")
                return False
            
            # Test info endpoint
            response = client.get('/info')
            if response.status_code == 200:
                print("✅ Info endpoint - OK")
            else:
                print(f"⚠️  Info endpoint: HTTP {response.status_code}")
            
            # Test voice command endpoint
            response = client.post('/voice/command', 
                                 json={'text': 'привет'},
                                 content_type='application/json')
            if response.status_code == 200:
                print("✅ Voice command endpoint - OK")
                
                data = response.get_json()
                response_text = data.get('response', '')
                print(f"   Response: {response_text}")
            else:
                print(f"⚠️  Voice command endpoint: HTTP {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """Test that required files exist"""
    print("\n📁 Checking file structure...")
    
    required_files = [
        "src/config.py",
        "src/utils/logger.py",
        "src/api/routes.py",
        "src/main.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def create_basic_env_file():
    """Create basic .env file if it doesn't exist"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("\n📝 Creating basic .env file...")
        
        env_content = """# Basic Smart Home Configuration
APP_NAME=SmartHomeSystem
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

# Network
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

# Test mode
TEST_MODE=true
MOCK_DEVICES=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file with basic settings")
    else:
        print("✅ .env file already exists")

def create_logs_directory():
    """Create logs directory if it doesn't exist"""
    logs_dir = Path('logs')
    if not logs_dir.exists():
        logs_dir.mkdir()
        print("✅ Created logs directory")
    else:
        print("✅ Logs directory exists")

def main():
    """Run all basic tests"""
    print("🏠 SMART HOME BASIC TEST")
    print("=" * 50)
    print("Testing only essential components for basic functionality")
    print()
    
    tests = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_env),
        ("Basic Imports", test_basic_imports),
        ("Flask Import", test_flask_import),
        ("File Structure", test_file_structure),
    ]
    
    # Setup basic files
    create_basic_env_file()
    create_logs_directory()
    
    passed = 0
    total = len(tests)
    
    # Run tests
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Additional tests that require setup
    print("\n" + "=" * 30)
    print("ADVANCED TESTS")
    print("=" * 30)
    
    advanced_tests = [
        ("Configuration", test_config_module),
        ("Logging", test_logger),
        ("Flask App", test_flask_app),
    ]
    
    for test_name, test_func in advanced_tests:
        try:
            if test_func():
                passed += 1
            total += 1
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            total += 1
    
    # Results
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYour basic smart home system is ready!")
        print("\nNext steps:")
        print("1. Run: python src/main.py")
        print("2. Open browser: http://127.0.0.1:5000/health")
        print("3. Test API: curl http://127.0.0.1:5000/health")
        return True
    else:
        failed = total - passed
        print(f"\n⚠️  {failed} test(s) failed")
        print("\nFix the issues above before proceeding")
        
        if passed >= 5:  # Basic tests passed
            print("\nBasic setup looks OK - try running anyway:")
            print("python src/main.py")
        
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 50)
    
    if success:
        print("✅ Ready to start your smart home system!")
    else:
        print("❌ Please fix the issues and try again")
    
    sys.exit(0 if success else 1)