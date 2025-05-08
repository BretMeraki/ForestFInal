"""Database configuration with cloud/local mode toggle functionality."""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()

def get_database_url():
    """Get database URL based on cloud mode."""
    use_cloud_mode = os.getenv("USE_CLOUD_MODE", "False").lower() in ["true", "1", "yes"]
    
    if use_cloud_mode:
        # Cloud mode uses Google Cloud SQL
        logger.info("Using cloud database configuration")
        
        # Get cloud database configuration from environment variables
        db_user = os.getenv("DB_USER", "postgres")
        db_pass = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME", "forestapp")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT", "5432")
        
        # Construct connection string
        if not all([db_pass, db_host]):
            logger.error("Missing required cloud database configuration")
            raise ValueError("Missing required cloud database configuration")
            
        connection_string = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        return connection_string
    else:
        # Local mode uses local PostgreSQL or environment variable
        logger.info("Using local database configuration")
        
        # Check for explicit connection string
        connection_string = os.getenv("DB_CONNECTION_STRING")
        if connection_string:
            return connection_string
            
        # Use local PostgreSQL defaults
        db_user = os.getenv("LOCAL_DB_USER", "postgres")
        db_pass = os.getenv("LOCAL_DB_PASSWORD", "postgres")
        db_name = os.getenv("LOCAL_DB_NAME", "forestapp")
        db_host = os.getenv("LOCAL_DB_HOST", "localhost")
        db_port = os.getenv("LOCAL_DB_PORT", "5432")
        
        return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

# Get database URL
SQLALCHEMY_DATABASE_URL = get_database_url()

# Create engine with appropriate configuration
def create_db_engine():
    """Create database engine with appropriate configuration."""
    use_cloud_mode = os.getenv("USE_CLOUD_MODE", "False").lower() in ["true", "1", "yes"]
    
    logger.info(f"Connecting to database: {SQLALCHEMY_DATABASE_URL}")
    
    # Create engine with appropriate parameters
    if "sqlite" in SQLALCHEMY_DATABASE_URL:
        # SQLite specific configuration
        return create_engine(
            SQLALCHEMY_DATABASE_URL, 
            connect_args={"check_same_thread": False}
        )
    else:
        # PostgreSQL configuration with connection pool
        return create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
        )

# Create engine
engine = create_db_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()