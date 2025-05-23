# forest_app/persistence/database.py (Refactored with get_db and Pydantic settings)

import logging
<<<<<<< HEAD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator # Import Generator for type hint
=======
from contextlib import asynccontextmanager
from typing import Generator  # Import Generator for type hint

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

# --- Settings Import (Using Pydantic settings object) ---
print(">>> DEBUG DB: Importing from Pydantic settings.py")
try:
    # Import the central settings object
    from forest_app.config.settings import settings
<<<<<<< HEAD
    print(">>> DEBUG DB: Successfully imported settings object.")
    # Access the connection string via the settings object attribute
    db_connection_string = settings.DB_CONNECTION_STRING
    print(f">>> DEBUG DB: DB Connection String Type via settings: {type(db_connection_string)}")
except ImportError as e:
    print(f"CRITICAL: Failed to import settings object: {e}")
    logging.getLogger(__name__).critical(f"Failed to import settings object: {e}", exc_info=True)
    raise
except AttributeError as e:
    print(f"CRITICAL: Failed to access attribute on settings object (DB_CONNECTION_STRING?): {e}")
    logging.getLogger(__name__).critical(f"Failed to access attribute on settings object (DB_CONNECTION_STRING?): {e}", exc_info=True)
    raise # Raise error if required setting is missing attribute
except Exception as e:
    print(f"CRITICAL: Error during import or access of settings: {e}")
    logging.getLogger(__name__).critical(f"Error during import or access of settings: {e}", exc_info=True)
=======

    print(">>> DEBUG DB: Successfully imported settings object.")
    # Access the connection string via the settings object attribute
    db_connection_string = settings.DB_CONNECTION_STRING
    print(
        f">>> DEBUG DB: DB Connection String Type via settings: {type(db_connection_string)}"
    )
except ImportError as e:
    print(f"CRITICAL: Failed to import settings object: {e}")
    logging.getLogger(__name__).critical(
        f"Failed to import settings object: {e}", exc_info=True
    )
    raise
except AttributeError as e:
    print(
        f"CRITICAL: Failed to access attribute on settings object (DB_CONNECTION_STRING?): {e}"
    )
    logging.getLogger(__name__).critical(
        f"Failed to access attribute on settings object (DB_CONNECTION_STRING?): {e}",
        exc_info=True,
    )
    raise  # Raise error if required setting is missing attribute
except Exception as e:
    print(f"CRITICAL: Error during import or access of settings: {e}")
    logging.getLogger(__name__).critical(
        f"Error during import or access of settings: {e}", exc_info=True
    )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    raise
# --- End Settings Import ---

logger = logging.getLogger(__name__)

<<<<<<< HEAD
# --- Define Dummy Session Factory (for early import safety) ---
def _dummy_session_factory():
    logger.error("Attempted to get DB session via dummy, but database is not connected or failed to initialize.")
    raise RuntimeError("Database connection not initialized. Check configuration and logs.")

# --- Initialize SessionLocal with the dummy function ---
SessionLocal: sessionmaker[Session] = _dummy_session_factory
logger.info("SessionLocal initialized with a dummy factory (will be replaced upon successful DB connection).")
=======

# --- Define Dummy Session Factory (for early import safety) ---
def _dummy_session_factory():
    logger.error(
        "Attempted to get DB session via dummy, but database is not connected or failed to initialize."
    )
    raise RuntimeError(
        "Database connection not initialized. Check configuration and logs."
    )


# --- Initialize SessionLocal with the dummy function ---
SessionLocal: sessionmaker[Session] = _dummy_session_factory
logger.info(
    "SessionLocal initialized with a dummy factory (will be replaced upon successful DB connection)."
)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

# --- Initialize SQLAlchemy engine and Base ---
engine = None
Base = declarative_base()

# --- Attempt to Create SQLAlchemy Engine and Redefine SessionLocal ---
# Check if the connection string was successfully retrieved from settings
if db_connection_string:
    try:
<<<<<<< HEAD
        SQLALCHEMY_DATABASE_URL = db_connection_string # Use the retrieved string
        engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=1800, pool_pre_ping=True)
        logger.info("SQLAlchemy engine creation attempt successful using URL from settings.") # Log source
=======
        SQLALCHEMY_DATABASE_URL = db_connection_string  # Use the retrieved string
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL, pool_recycle=1800, pool_pre_ping=True
        )
        logger.info(
            "SQLAlchemy engine creation attempt successful using URL from settings."
        )  # Log source
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

        # Test connection immediately after creating engine
        try:
            with engine.connect() as connection:
                logger.info("Database connection test successful.")

            # --- IMPORTANT: Redefine SessionLocal with the working engine ---
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            logger.info("SessionLocal redefined successfully with the database engine.")

        except Exception as conn_test_e:
<<<<<<< HEAD
            logger.critical(f"CRITICAL: Engine created but connection test failed: {conn_test_e}", exc_info=True)
            engine = None # Reset engine
=======
            logger.critical(
                f"CRITICAL: Engine created but connection test failed: {conn_test_e}",
                exc_info=True,
            )
            engine = None  # Reset engine
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            # SessionLocal remains the dummy factory

    except Exception as e:
        logger.critical(f"CRITICAL: Failed during engine creation: {e}", exc_info=True)
<<<<<<< HEAD
        engine = None # Ensure engine is None
=======
        engine = None  # Ensure engine is None
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        # SessionLocal remains the dummy factory

else:
    # This condition might be hit if DB_CONNECTION_STRING is set but empty in environment
<<<<<<< HEAD
    logger.critical("CRITICAL: DB_CONNECTION_STRING is missing or empty in settings. Database engine cannot be created.")
    engine = None # Ensure engine is None
    # SessionLocal remains the dummy factory

=======
    logger.critical(
        "CRITICAL: DB_CONNECTION_STRING is missing or empty in settings. Database engine cannot be created."
    )
    engine = None  # Ensure engine is None
    # SessionLocal remains the dummy factory


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
# +++ NEW Standard FastAPI DB Dependency Function +++
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy session and ensures it's closed.
    Uses the globally defined `SessionLocal`.
    """
    if SessionLocal is _dummy_session_factory:
<<<<<<< HEAD
         logger.error("Database not connected: Cannot create session using dummy factory.")
         raise RuntimeError("Database connection failed or not established during startup.")
=======
        logger.error(
            "Database not connected: Cannot create session using dummy factory."
        )
        raise RuntimeError(
            "Database connection failed or not established during startup."
        )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    db = SessionLocal()
    try:
        yield db
    finally:
        logger.debug("Closing database session.")
        db.close()
<<<<<<< HEAD
# +++ END NEW Dependency Function +++

=======


# +++ END NEW Dependency Function +++


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
# --- Optional: Function to Create Tables (Keep as is) ---
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
<<<<<<< HEAD
        logger.error("Cannot create database tables: SQLAlchemy engine is not initialized.")
=======
        logger.error(
            "Cannot create database tables: SQLAlchemy engine is not initialized."
        )

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

# --- Define init_db for potential use during startup (e.g., in main.py) ---
def init_db():
    """Initializes the database by attempting to create tables."""
    create_database_tables()

<<<<<<< HEAD
# --- Async Context Manager for Transaction-Protected Sessions ---
from contextlib import asynccontextmanager

=======

# --- Async Context Manager for Transaction-Protected Sessions ---
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
@asynccontextmanager
async def get_db_session() -> Generator[Session, None, None]:
    """
    Async context manager that yields a SQLAlchemy session and ensures it's closed.
    Used with transaction_protected decorator for async database operations.
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    Example:
        async with get_db_session() as session:
            # Use session with transaction protection
            session.add(model)
            await session.commit()
    """
    if SessionLocal is _dummy_session_factory:
<<<<<<< HEAD
        logger.error("Database not connected: Cannot create session using dummy factory.")
        raise RuntimeError("Database connection failed or not established during startup.")
=======
        logger.error(
            "Database not connected: Cannot create session using dummy factory."
        )
        raise RuntimeError(
            "Database connection failed or not established during startup."
        )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error in database session context manager: {e}")
        db.rollback()
        raise
    finally:
        logger.debug("Closing database session.")
        db.close()
<<<<<<< HEAD
        
print(">>> DEBUG DB: END OF database.py execution (Refactored with get_db and Pydantic settings)")
=======


print(
    ">>> DEBUG DB: END OF database.py execution (Refactored with get_db and Pydantic settings)"
)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
