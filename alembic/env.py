# alembic/env.py

import os  # Import the os module
from logging.config import fileConfig

# Import necessary SQLAlchemy components
<<<<<<< HEAD
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import create_engine # Import create_engine explicitly

# Import Alembic context
from alembic import context

=======
from sqlalchemy import create_engine  # Import create_engine explicitly
from sqlalchemy import pool

# Import Alembic context
from alembic import context
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
# --- MODIFY THIS ---
# Import Base model directly from the models file
# This avoids importing from forest_app.__init__ which might have circular dependencies
from forest_app.persistence.models import Base
<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
# ---------------

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- MODIFY THIS ---
# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata
# -----------------

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Get the URL from the main Alembic configuration section in alembic.ini
    # This will resolve the %(DB_CONNECTION_STRING)s variable if needed for offline mode
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
<<<<<<< HEAD
        target_metadata=target_metadata, # Pass the metadata for offline checks
        literal_binds=True, # Render SQL statements with literal values
        dialect_opts={"paramstyle": "named"}, # Dialect-specific options
=======
        target_metadata=target_metadata,  # Pass the metadata for offline checks
        literal_binds=True,  # Render SQL statements with literal values
        dialect_opts={"paramstyle": "named"},  # Dialect-specific options
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    )

    # Run migrations within a transaction block
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # --- REVERTED TO EXPLICIT ENV VAR READING ---
    # Get the database URL directly from the environment variable
<<<<<<< HEAD
    db_url = os.environ.get('DB_CONNECTION_STRING') or \
           os.environ.get('DATABASE_URL') or \
           'postgresql://postgres:postgres@localhost:5432/forest_db'
=======
    db_url = (
        os.environ.get("DB_CONNECTION_STRING")
        or os.environ.get("DATABASE_URL")
        or "postgresql://postgres:postgres@localhost:5432/forest_db"
    )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    print(f"Using database connection string: {db_url[:20]}...")

    # Create the SQLAlchemy engine directly using the fetched URL
    # Pass poolclass=pool.NullPool to avoid hanging connections during migrations
    connectable = create_engine(db_url, poolclass=pool.NullPool)
    # --------------------------------------------

    # Establish connection using the configured engine
    with connectable.connect() as connection:
        # Configure the Alembic context with the connection and metadata
        context.configure(
            connection=connection,
<<<<<<< HEAD
            target_metadata=target_metadata # Pass the metadata for comparison
=======
            target_metadata=target_metadata,  # Pass the metadata for comparison
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        )

        # Run migrations within a transaction block
        with context.begin_transaction():
            context.run_migrations()


# --- Run the appropriate migration function based on context mode ---
# Checks if Alembic is invoked in offline mode (e.g., alembic upgrade --sql)
# or online mode (e.g., alembic upgrade head)
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
