#!/bin/bash
# Local development - skip cloud authentication
echo "Local development mode - skipping cloud authentication"
# Set Python path to include both /app and /app/forest_app
export PYTHONPATH=/app:/app/forest_app

echo "LOCAL DEVELOPMENT MODE"

unset GOOGLE_APPLICATION_CREDENTIALS
unset INSTANCE_CONNECTION_NAME

# Override with local configuration
echo "Using local database connection"
export USE_CLOUD_SQL_PROXY="False"

# Run database migrations
echo "Running database migrations..."
cd /app
alembic upgrade head
echo "Database migrations finished."

# Start the FastAPI application
echo "Starting FastAPI application on port 8000..."
cd /app/forest_app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
