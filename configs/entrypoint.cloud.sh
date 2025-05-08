#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

# --- Cloud Deployment Entrypoint ---

# Configuration
KEY_FILE_PATH="/tmp/gcp_key.json"
INSTANCE_CONNECTION_NAME=${INSTANCE_CONNECTION_NAME:-"winged-verbena-457705-p3:us-central1:forestapp"}

# Set Python path to include both /app and /app/forest_app
export PYTHONPATH=/app:/app/forest_app

echo "CLOUD DEPLOYMENT MODE"

# Check if GCP_SA_KEY environment variable is set
if [ -z "$GCP_SA_KEY" ]; then
  echo "Error: GCP_SA_KEY environment variable is not set. Cannot authenticate proxy."
  exit 1
fi

# Write the content of the GCP_SA_KEY secret to the key file
echo "$GCP_SA_KEY" > "$KEY_FILE_PATH"
echo "GCP Service Account key file created at $KEY_FILE_PATH"

# Set the standard Google Cloud environment variable for authentication
export GOOGLE_APPLICATION_CREDENTIALS="$KEY_FILE_PATH"
echo "GOOGLE_APPLICATION_CREDENTIALS environment variable set."

# Start the Cloud SQL Auth Proxy in the background
echo "Starting Cloud SQL Auth Proxy for $INSTANCE_CONNECTION_NAME..."
/usr/local/bin/cloud-sql-proxy "$INSTANCE_CONNECTION_NAME" &
PROXY_PID=$!

# Wait a moment for the proxy to establish the connection tunnel
echo "Waiting for proxy to initialize..."
sleep 5

# Check if proxy started successfully
if ! kill -0 $PROXY_PID > /dev/null 2>&1; then
    echo "Error: Cloud SQL Auth Proxy failed to start."
    rm "$KEY_FILE_PATH" # Clean up key file
    exit 1
fi
echo "Cloud SQL Auth Proxy started successfully (PID: $PROXY_PID)."

# Run database migrations
echo "Running database migrations..."
cd /app
alembic upgrade head
echo "Database migrations finished."

# Start the FastAPI application
echo "Starting FastAPI application on port 8000..."
cd /app/forest_app
uvicorn main:app --host 0.0.0.0 --port 8000
