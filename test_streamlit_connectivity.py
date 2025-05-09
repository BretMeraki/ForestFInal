import os
import sys
import logging
import traceback
import json

# Ensure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/Users/bretmeraki/Downloads/ForestFInal-main-16/streamlit_detailed_test.log',
    filemode='w'
)

# Create a console handler for immediate visibility
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(formatter)

# Get the root logger and add the console handler
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/Users/bretmeraki/Downloads/ForestFInal-main-16/streamlit_test.log'
)
logger = logging.getLogger(__name__)

def test_environment_variables():
    """Comprehensive test of environment variables and system configuration"""
    logger.info("Starting comprehensive environment and system configuration test")
    
    # Detailed environment variable checks
    critical_vars = [
        'BACKEND_URL', 'DATABASE_URL', 'SECRET_KEY', 'DB_CONNECTION_STRING',
        'APP_HOST', 'APP_PORT', 'LOG_LEVEL'
    ]
    
    # Collect environment details
    env_details = {}
    for var in critical_vars:
        value = os.getenv(var)
        env_details[var] = value
        
        if not value:
            logger.error(f"CRITICAL: {var} environment variable is NOT SET")
        else:
            logger.info(f"{var} is set to: {value}")
    
    # System and Python environment details
    logger.info("System Environment Details:")
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Python Executable: {sys.executable}")
    logger.info(f"Current Working Directory: {os.getcwd()}")
    
    # Virtual environment check
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.info("Virtual environment is active")
    else:
        logger.warning("Not running in a virtual environment")
    
    # Write environment details to a JSON file for further inspection
    try:
        with open('/Users/bretmeraki/Downloads/ForestFInal-main-16/env_diagnostics.json', 'w') as f:
            json.dump({
                'environment_variables': env_details,
                'python_version': sys.version,
                'python_executable': sys.executable,
                'current_directory': os.getcwd()
            }, f, indent=2)
        logger.info("Environment details written to env_diagnostics.json")
    except Exception as e:
        logger.error(f"Failed to write environment details: {e}")

def test_backend_connectivity():
    """Test backend API connectivity"""
    try:
        import requests
        
        # Get backend URL from environment
        backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
        logger.info(f"Attempting to connect to backend: {backend_url}")
        
        # Test connection
        response = requests.get(f"{backend_url}/health", timeout=5)
        
        if response.status_code == 200:
            logger.info("Backend health check successful")
            logger.info(f"Response: {response.text}")
        else:
            logger.error(f"Backend health check failed. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
    
    except Exception as e:
        logger.error("Failed to connect to backend")
        logger.error(traceback.format_exc())

def test_streamlit_imports():
    """Test Streamlit and application imports"""
    try:
        import streamlit as st
        logger.info(f"Streamlit version: {st.__version__}")
        
        # Test application-specific imports
        from forest_app.front_end import streamlit_app
        from forest_app.front_end import auth_ui
        from forest_app.front_end import api_client
        
        logger.info("All critical Streamlit imports successful")
    
    except ImportError as e:
        logger.error("Import error:")
        logger.error(traceback.format_exc())
    except Exception as e:
        logger.error("Unexpected error during import:")
        logger.error(traceback.format_exc())

def main():
    """Run all diagnostic tests"""
    logger.info("Starting Streamlit Diagnostic Tests")
    
    test_environment_variables()
    test_backend_connectivity()
    test_streamlit_imports()
    
    logger.info("Diagnostic Tests Completed")

if __name__ == "__main__":
    main()
