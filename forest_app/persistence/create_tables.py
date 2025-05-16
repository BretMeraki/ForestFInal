# create_tables.py
<<<<<<< HEAD
from forest_app.persistence import init_db  # Make sure your path/import works
import logging  # Optional: add logging

=======
import logging  # Optional: add logging

from forest_app.persistence import init_db  # Make sure your path/import works

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Attempting to create database tables...")
try:
    init_db()
    logger.info("Database tables should be created successfully (check for forest.db).")
except Exception as e:
    logger.exception("Error creating database tables: %s", e)
