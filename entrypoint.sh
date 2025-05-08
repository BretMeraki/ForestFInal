#!/bin/bash
# Set Python path to include both /app and /app/forest_app
export PYTHONPATH=/app:/app/forest_app

# ------------------------------------
# MODE SELECTION (LOCAL OR CLOUD)
# ------------------------------------

# Set environment based on USE_CLOUD_MODE toggle
if [ "$USE_CLOUD_MODE" = "True" ]; then
  # CLOUD MODE SELECTED
  echo "========================================"
  echo "CLOUD MODE ACTIVATED"
  echo "========================================"
  
  # Set cloud environment variables
  export APP_ENV="production"
  export DEPLOYMENT_MODE="cloud"
  export CLOUD_RESOURCES="enabled"
  
  # Verify required cloud environment variables
  echo "\n[Environment] Checking required cloud variables:"
  
  # Check for database connection
  if [ -z "$DB_CONNECTION_STRING" ] && [ -z "$DATABASE_URL" ]; then
    echo "[Environment] WARNING: No DB_CONNECTION_STRING or DATABASE_URL provided"
  else
    echo "[Environment] ✓ Database connection string found"
  fi
  
  # Check for Google API key
  if [ -z "$GOOGLE_API_KEY" ]; then
    echo "[Environment] WARNING: GOOGLE_API_KEY is not set"
  else
    echo "[Environment] ✓ GOOGLE_API_KEY is set"
  fi
  
  # Check for GCP service account key
  if [ -z "$GCP_SA_KEY" ]; then
    echo "[Environment] WARNING: GCP_SA_KEY is not set"
  else
    echo "[Environment] ✓ GCP_SA_KEY is set"
    # Create service account key file if not running as a service account
    if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ] && [ -n "$GCP_SA_KEY" ]; then
      echo "[Environment] Creating service account key file"
      echo "$GCP_SA_KEY" > /tmp/gcp-sa-key.json
      export GOOGLE_APPLICATION_CREDENTIALS="/tmp/gcp-sa-key.json"
    fi
  fi
  
  # Check for app secret key
  if [ -z "$SECRET_KEY" ]; then
    echo "[Environment] WARNING: SECRET_KEY is not set"
  else
    echo "[Environment] ✓ SECRET_KEY is set"
  fi
  
  # Check for Sentry DSN
  if [ -z "$SENTRY_DSN" ]; then
    echo "[Environment] WARNING: SENTRY_DSN is not set, error tracking disabled"
  else
    echo "[Environment] ✓ SENTRY_DSN is set, error tracking enabled"  
  fi
  
  # Log platform information
  if [ -n "$K_SERVICE" ]; then
    echo "Running in Google Cloud Run: $K_SERVICE"
  elif [ -n "$KOYEB_APP_NAME" ]; then
    echo "Running in Koyeb: $KOYEB_APP_NAME"
    echo "Service: $KOYEB_SERVICE_NAME"
  elif [ -n "$RAILWAY_PROJECT_ID" ]; then
    echo "Running in Railway: $RAILWAY_PROJECT_NAME"
  elif [ -n "$RENDER_SERVICE_ID" ]; then
    echo "Running in Render: $RENDER_SERVICE_NAME"
  else
    echo "Running locally, but using cloud resources"
  fi
else
  # LOCAL MODE SELECTED (default if not specified)
  echo "========================================"
  echo "LOCAL MODE ACTIVATED"
  echo "========================================"
  
  # Set local environment variables
  export APP_ENV="development"
  export DEPLOYMENT_MODE="local"
  export CLOUD_RESOURCES="disabled"
  
  # Ensure cloud credentials are not used in local mode
  unset GOOGLE_APPLICATION_CREDENTIALS
  unset INSTANCE_CONNECTION_NAME
  
  echo "Using local resources only"
fi

# ------------------------------------
# DATABASE CONNECTION SETUP
# ------------------------------------
cd /app

echo "\n[Database] Setting up database connection"

if [ "$USE_CLOUD_MODE" = "True" ]; then
  # CLOUD DATABASE MODE
  echo "[Database] Using Cloud SQL database"
    
  if [ -n "$DATABASE_URL" ]; then
    # Use Koyeb's DATABASE_URL (or other PaaS providers like Heroku, Railway)
    echo "[Database] Using platform-provided DATABASE_URL"
    export DB_CONNECTION_STRING="$DATABASE_URL"
    export USE_DATABASE="True"
  elif [ -n "$DB_CONNECTION_STRING" ]; then
    # Use custom provided connection string
    echo "[Database] Using provided DB_CONNECTION_STRING"
    export USE_DATABASE="True"
  elif [ -n "$INSTANCE_CONNECTION_NAME" ]; then
    # Use Google Cloud SQL instance connection name
    echo "[Database] Using INSTANCE_CONNECTION_NAME: $INSTANCE_CONNECTION_NAME"
      
    # Create connection string for Cloud SQL Proxy
    # Format: postgresql://user:password@/dbname?host=/cloudsql/INSTANCE_CONNECTION_NAME
    if [ -n "$DB_USER" ] && [ -n "$DB_PASSWORD" ] && [ -n "$DB_NAME" ]; then
      export DB_CONNECTION_STRING="postgresql://$DB_USER:$DB_PASSWORD@/db?host=/cloudsql/$INSTANCE_CONNECTION_NAME"
      echo "[Database] Generated DB_CONNECTION_STRING for Cloud SQL"
      export USE_DATABASE="True"
    else
      echo "[Database] ERROR: Missing DB_USER, DB_PASSWORD, or DB_NAME for Cloud SQL"
      export USE_DATABASE="False"
    fi
  else
    echo "[Database] ERROR: No database connection information provided for Cloud SQL"
    echo "[Database] Set either DB_CONNECTION_STRING or INSTANCE_CONNECTION_NAME"
    export USE_DATABASE="False"
  fi
  
  # Run migrations if database is configured
  if [ "$USE_DATABASE" = "True" ]; then
    echo "[Database] Running Cloud SQL migrations..."
    alembic upgrade head || echo "[Database] WARNING: Migrations failed but continuing startup"
  fi
else
  # LOCAL DATABASE MODE
  echo "[Database] Using local PostgreSQL database"
    
  # Check if local PostgreSQL is available
  if nc -z localhost 5432 >/dev/null 2>&1; then
    echo "[Database] Found local PostgreSQL on localhost:5432"
      
    # Set a default local connection string if not provided
    if [ -z "$DB_CONNECTION_STRING" ]; then
      export DB_CONNECTION_STRING="postgresql://postgres:postgres@localhost:5432/forest_db"
      echo "[Database] Using default local database connection string"
    else
      echo "[Database] Using provided local DB_CONNECTION_STRING"
    fi
      
    export USE_DATABASE="True"
      
    # Run local database migrations
    echo "[Database] Running local database migrations..."
    alembic upgrade head || echo "[Database] WARNING: Migrations failed but continuing startup"
  else
    echo "[Database] WARNING: No local PostgreSQL detected on localhost:5432"
    echo "[Database] Database features will be unavailable"
    export USE_DATABASE="False"
  fi
fi

# Start the FastAPI application with appropriate settings
echo "Starting FastAPI application on port 8000..."
cd /app/forest_app

# In production, don't use --reload flag
if [ "$APP_ENV" = "production" ]; then
  uvicorn main:app --host 0.0.0.0 --port 8000
else
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi
