# forest_app/persistence/database.py (Refactored with get_db and Pydantic settings)

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os
from typing import Generator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

# --- Settings Import (Using Pydantic settings object) ---
try:
    # Import the central settings object
    from forest_app.config.settings import settings
    # Access the connection string via the settings object attribute
    db_connection_string = settings.DB_CONNECTION_STRING
except ImportError as e:
    logging.getLogger(__name__).critical(f"Failed to import settings object: {e}", exc_info=True)
    raise
except AttributeError as e:
    logging.getLogger(__name__).critical(f"Failed to access attribute on settings object (DB_CONNECTION_STRING?): {e}", exc_info=True)
    raise # Raise error if required setting is missing attribute
except Exception as e:
    logging.getLogger(__name__).critical(f"Error during import or access of settings: {e}", exc_info=True)
    raise
# --- End Settings Import ---

logger = logging.getLogger(__name__)

# --- Define Dummy Session Factory (for early import safety) ---
def _dummy_session_factory():
    logger.error("Attempted to get DB session via dummy, but database is not connected or failed to initialize.")
    raise RuntimeError("Database connection not initialized. Check configuration and logs.")

# --- Initialize SessionLocal with the dummy function ---
SessionLocal: sessionmaker[Session] = _dummy_session_factory
logger.info("SessionLocal initialized with a dummy factory (will be replaced upon successful DB connection).")

# --- Initialize SQLAlchemy engine and Base ---
engine = None
Base = declarative_base()

# --- Attempt to Create SQLAlchemy Engine and Redefine SessionLocal ---
# Check deployment mode to determine database connection approach
deployment_mode = os.getenv('DEPLOYMENT_MODE', 'local').lower()
logger.info(f"Running in {deployment_mode.upper()} deployment mode")

# Get database connection string based on deployment mode
if deployment_mode == 'cloud':
    # For cloud mode, check for cloud SQL connection string first
    db_connection_string = os.getenv('GOOGLE_CLOUD_SQL_CONNECTION_STRING')
    if db_connection_string:
        logger.info("Using Google Cloud SQL connection string for database")
    else:
        # Fall back to standard connection strings if cloud-specific one is not found
        db_connection_string = os.getenv('DB_CONNECTION_STRING')
        if not db_connection_string:
            db_connection_string = os.getenv('SQLALCHEMY_DATABASE_URL')
            if not db_connection_string:
                db_connection_string = os.getenv('DATABASE_URL')
                if not db_connection_string:
                    logger.error("No database connection string found for CLOUD mode")
                    raise ValueError("Cloud deployment requires a database connection string")
                else:
                    logger.info("Using DATABASE_URL for cloud database connection")
            else:
                logger.info("Using SQLALCHEMY_DATABASE_URL for cloud database connection")
        else:
            logger.info("Using DB_CONNECTION_STRING for cloud database connection")
            
    # Log instance connection name for cloud deployment
    instance_name = os.getenv('INSTANCE_CONNECTION_NAME')
    if instance_name:
        logger.info(f"Using Cloud SQL instance: {instance_name}")
    else:
        logger.warning("INSTANCE_CONNECTION_NAME not found in environment variables")

else:  # Local mode
    # Get database connection string from environment variables
    db_connection_string = os.getenv('DB_CONNECTION_STRING')
    
    # If not found, try alternative environment variables
    if not db_connection_string:
        db_connection_string = os.getenv('SQLALCHEMY_DATABASE_URL')
        if not db_connection_string:
            db_connection_string = os.getenv('DATABASE_URL')
            if not db_connection_string:
                # Fallback to a local SQLite database if no connection string is found
                db_connection_string = 'sqlite:///./forest_app.db'
                logger.warning(f"No database connection string found in environment variables. Using fallback: {db_connection_string}")
            else:
                logger.info(f"Using DATABASE_URL for local database connection")
        else:
            logger.info(f"Using SQLALCHEMY_DATABASE_URL for local database connection")
    else:
        logger.info(f"Using DB_CONNECTION_STRING for local database connection")

# Log the connection string (with password redacted)
if 'postgresql' in db_connection_string:
    safe_connection_string = db_connection_string.replace(db_connection_string.split('@')[0].split(':')[-1], '******')
    logger.info(f"Database connection string: {safe_connection_string}")

if db_connection_string:
    try:
        SQLALCHEMY_DATABASE_URL = db_connection_string
        engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=1800, pool_pre_ping=True)
        logger.info("SQLAlchemy engine creation attempt successful using URL from settings.")

        # Test connection immediately after creating engine
        try:
            with engine.connect() as connection:
                logger.info("Database connection test successful.")

            # --- IMPORTANT: Redefine SessionLocal with the working engine ---
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            logger.info("SessionLocal redefined successfully with the database engine.")

        except Exception as conn_test_e:
            logger.critical(f"CRITICAL: Engine created but connection test failed: {conn_test_e}", exc_info=True)
            engine = None # Reset engine
            # SessionLocal remains the dummy factory

    except Exception as e:
        logger.critical(f"CRITICAL: Failed during engine creation: {e}", exc_info=True)
        engine = None # Ensure engine is None
        # SessionLocal remains the dummy factory

else:
    # This condition might be hit if DB_CONNECTION_STRING is set but empty in environment
    logger.critical("CRITICAL: DB_CONNECTION_STRING is missing or empty in settings. Database engine cannot be created.")
    engine = None # Ensure engine is None
    # SessionLocal remains the dummy factory

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy session and ensures it's closed.
    Uses the globally defined `SessionLocal`.
    """
    if SessionLocal is _dummy_session_factory:
         logger.error("Database not connected: Cannot create session using dummy factory.")
         raise RuntimeError("Database connection failed or not established during startup.")

    db = SessionLocal()
    try:
        yield db
    finally:
        logger.debug("Closing database session.")
        db.close()

def create_database_tables():
    """Creates database tables if the engine was successfully created."""
    if engine:
        try:
            logger.info("Attempting to create database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables checked/created successfully.")
        except Exception as e:
            logger.exception(f"CRITICAL: Failed to create database tables: {e}")
    else:
        logger.error("Cannot create database tables: SQLAlchemy engine is not initialized.")

def init_db():
    """Initializes the database by attempting to create tables."""
    create_database_tables()
