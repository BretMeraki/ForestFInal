#!/usr/bin/env python
"""
Test script for Task 0.1 validation
Verifies basic functionality and environment configuration
"""
<<<<<<< HEAD
import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_core_setup")

def main():
    logger.info("Starting Task 0.1 validation")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        logger.error(".env file not found!")
        return False
        
    # Load environment variables from .env file
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
    
    # Check SECRET_KEY
    secret_key = os.getenv('SECRET_KEY')
=======

import logging
import os
import sys

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_core_setup")


def main():
    logger.info("Starting Task 0.1 validation")

    # Check if .env file exists
    if not os.path.exists(".env"):
        logger.error(".env file not found!")
        return False

    # Load environment variables from .env file
    load_dotenv()
    logger.info("Loaded environment variables from .env file")

    # Check SECRET_KEY
    secret_key = os.getenv("SECRET_KEY")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    if secret_key:
        logger.info("SECRET_KEY is configured")
    else:
        logger.error("SECRET_KEY is not set!")
        return False
<<<<<<< HEAD
    
    # Check DB connection string
    db_connection = os.getenv('DB_CONNECTION_STRING') or os.getenv('DATABASE_URL')
=======

    # Check DB connection string
    db_connection = os.getenv("DB_CONNECTION_STRING") or os.getenv("DATABASE_URL")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    if db_connection:
        logger.info(f"Database connection string: {db_connection[:20]}...")
    else:
        logger.error("Database connection string not found!")
        return False
<<<<<<< HEAD
        
    # Check feature flags
    core_onboarding = os.getenv('FEATURE_ENABLE_CORE_ONBOARDING')
    core_hta = os.getenv('FEATURE_ENABLE_CORE_HTA')
    core_task_engine = os.getenv('FEATURE_ENABLE_CORE_TASK_ENGINE')
    
    logger.info(f"Feature flags: CORE_ONBOARDING={core_onboarding}, CORE_HTA={core_hta}, CORE_TASK_ENGINE={core_task_engine}")
    
    # Check if Python version is correct
    python_version = sys.version_info
    logger.info(f"Running Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
=======

    # Check feature flags
    core_onboarding = os.getenv("FEATURE_ENABLE_CORE_ONBOARDING")
    core_hta = os.getenv("FEATURE_ENABLE_CORE_HTA")
    core_task_engine = os.getenv("FEATURE_ENABLE_CORE_TASK_ENGINE")

    logger.info(
        f"Feature flags: CORE_ONBOARDING={core_onboarding}, CORE_HTA={core_hta}, CORE_TASK_ENGINE={core_task_engine}"
    )

    # Check if Python version is correct
    python_version = sys.version_info
    logger.info(
        f"Running Python {python_version.major}.{python_version.minor}.{python_version.micro}"
    )

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Check if documentation files exist
    docs_files = [
        "PERFORMANCE_STANDARDS.md",
        "DEVELOPER_QUICKSTART.md",
<<<<<<< HEAD
        "DATA_VALIDATION_CATALOG.md"
    ]
    
=======
        "DATA_VALIDATION_CATALOG.md",
    ]

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    for doc_file in docs_files:
        if os.path.exists(doc_file):
            logger.info(f"Documentation file found: {doc_file}")
        else:
            logger.error(f"Documentation file not found: {doc_file}")
            return False
<<<<<<< HEAD
    
    logger.info("Task 0.1 validation completed successfully!")
    return True

=======

    logger.info("Task 0.1 validation completed successfully!")
    return True


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
