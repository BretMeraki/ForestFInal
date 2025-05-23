"""
Deployment script for Forest App.
Runs all checks and handles deployment process.
"""

<<<<<<< HEAD
import os
import sys
import logging
import subprocess
from datetime import datetime
from typing import Optional
import pre_deploy_check

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

=======
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Optional

import pre_deploy_check

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def run_command(command: str, cwd: Optional[str] = None) -> bool:
    """Run a shell command and return success status."""
    try:
        subprocess.run(
            command,
            shell=True,
            check=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
<<<<<<< HEAD
            text=True
=======
            text=True,
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {command}")
        logger.error(f"Error output: {e.stderr}")
        return False

<<<<<<< HEAD
def backup_database() -> bool:
    """Create a backup of the database before deployment."""
    logger.info("Creating database backup...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"db_backup_{timestamp}.sql"
    
=======

def backup_database() -> bool:
    """Create a backup of the database before deployment."""
    logger.info("Creating database backup...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"db_backup_{timestamp}.sql"

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Get database URL from environment
    db_url = os.getenv("DB_CONNECTION_STRING", "")
    if not db_url:
        logger.error("Database URL not found in environment variables!")
        return False
<<<<<<< HEAD
    
    # Create backups directory if it doesn't exist
    os.makedirs("backups", exist_ok=True)
    
=======

    # Create backups directory if it doesn't exist
    os.makedirs("backups", exist_ok=True)

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Run database backup command (adjust based on your database type)
    if "postgresql" in db_url.lower():
        cmd = f"pg_dump {db_url} > backups/{backup_file}"
    elif "mysql" in db_url.lower():
        cmd = f"mysqldump {db_url} > backups/{backup_file}"
    else:
        logger.error("Unsupported database type!")
        return False
<<<<<<< HEAD
    
    return run_command(cmd)

def update_dependencies() -> bool:
    """Update project dependencies."""
    logger.info("Updating dependencies...")
    
    # Install/update dependencies
    if not run_command("pip install -r requirements.txt"):
        return False
    
=======

    return run_command(cmd)


def update_dependencies() -> bool:
    """Update project dependencies."""
    logger.info("Updating dependencies...")

    # Install/update dependencies
    if not run_command("pip install -r requirements.txt"):
        return False

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Install/update development dependencies if they exist
    if os.path.exists("requirements_dev.txt"):
        if not run_command("pip install -r requirements_dev.txt"):
            return False
<<<<<<< HEAD
    
    return True

=======

    return True


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def run_database_migrations() -> bool:
    """Run database migrations."""
    logger.info("Running database migrations...")
    return run_command("alembic upgrade head")

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def run_tests() -> bool:
    """Run the test suite."""
    logger.info("Running tests...")
    return run_command("pytest")

<<<<<<< HEAD
def build_assets() -> bool:
    """Build frontend assets if needed."""
    logger.info("Building frontend assets...")
    
=======

def build_assets() -> bool:
    """Build frontend assets if needed."""
    logger.info("Building frontend assets...")

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    if os.path.exists("package.json"):
        # Install npm dependencies
        if not run_command("npm install"):
            return False
<<<<<<< HEAD
        
        # Build assets
        if not run_command("npm run build"):
            return False
    
    return True

=======

        # Build assets
        if not run_command("npm run build"):
            return False

    return True


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def collect_static() -> bool:
    """Collect static files."""
    logger.info("Collecting static files...")
    return run_command("python manage.py collectstatic --noinput")

<<<<<<< HEAD
def restart_services() -> bool:
    """Restart application services."""
    logger.info("Restarting services...")
    
    services = [
        "gunicorn",
        "celery",
        "nginx"
    ]
    
    for service in services:
        if not run_command(f"sudo systemctl restart {service}"):
            return False
    
    return True

=======

def restart_services() -> bool:
    """Restart application services."""
    logger.info("Restarting services...")

    services = ["gunicorn", "celery", "nginx"]

    for service in services:
        if not run_command(f"sudo systemctl restart {service}"):
            return False

    return True


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def deploy() -> bool:
    """
    Run the deployment process.
    Returns True if deployment was successful, False otherwise.
    """
    deployment_steps = [
        ("Pre-deployment checks", lambda: pre_deploy_check.main() == 0),
        ("Database backup", backup_database),
        ("Update dependencies", update_dependencies),
        ("Database migrations", run_database_migrations),
        ("Run tests", run_tests),
        ("Build assets", build_assets),
        ("Collect static", collect_static),
<<<<<<< HEAD
        ("Restart services", restart_services)
    ]
    
=======
        ("Restart services", restart_services),
    ]

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    for step_name, step_func in deployment_steps:
        logger.info(f"\nExecuting: {step_name}")
        try:
            if not step_func():
                logger.error(f"{step_name} failed!")
                return False
            logger.info(f"✓ {step_name} completed successfully")
        except Exception as e:
            logger.error(f"Error during {step_name}: {e}")
            return False
<<<<<<< HEAD
    
    return True

def main():
    """Main deployment entry point."""
    logger.info("Starting deployment process...")
    
=======

    return True


def main():
    """Main deployment entry point."""
    logger.info("Starting deployment process...")

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Check if running in correct environment
    env = os.getenv("FOREST_APP_ENV", "").lower()
    if env not in ["staging", "production"]:
        logger.error(f"Invalid deployment environment: {env}")
        logger.error("Set FOREST_APP_ENV to 'staging' or 'production'")
        sys.exit(1)
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Run deployment
    if deploy():
        logger.info("\n✅ Deployment completed successfully!")
        sys.exit(0)
    else:
        logger.error("\n❌ Deployment failed!")
        sys.exit(1)

<<<<<<< HEAD
if __name__ == "__main__":
    main() 
=======

if __name__ == "__main__":
    main()
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
