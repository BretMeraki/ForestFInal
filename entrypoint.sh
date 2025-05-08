#!/bin/bash
# Set Python path to include both /app and /app/forest_app
export PYTHONPATH=/app:/app/forest_app

# Determine environment (Cloud vs Local)
if [ -n "$K_SERVICE" ]; then
  echo "CLOUD DEPLOYMENT MODE"
  export USE_CLOUD_SQL_PROXY="True"
  
  # In Cloud environment, use production settings
  export APP_ENV="production"
  
  # Check for Cloud SQL instance configuration
  if [ -n "$INSTANCE_CONNECTION_NAME" ]; then
    echo "Using Cloud SQL instance: $INSTANCE_CONNECTION_NAME"
  fi
else
  echo "LOCAL DEVELOPMENT MODE"
  unset GOOGLE_APPLICATION_CREDENTIALS
  unset INSTANCE_CONNECTION_NAME
  export USE_CLOUD_SQL_PROXY="False"
  export APP_ENV="development"
  echo "Using local database connection"
fi

# Run database migrations
echo "Running database migrations..."
cd /app
alembic upgrade head
echo "Database migrations finished."

# Start the FastAPI application with appropriate settings
echo "Starting FastAPI application on port 8000..."
cd /app/forest_app

# In production, don't use --reload flag
if [ "$APP_ENV" = "production" ]; then
  uvicorn main:app --host 0.0.0.0 --port 8000
else
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi
