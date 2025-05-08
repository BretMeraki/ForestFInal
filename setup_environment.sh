#!/bin/bash

# Script to set up either local or cloud environment configurations
# Usage: ./setup_environment.sh [local|cloud]

set -e

ENV_TYPE=$1

if [ "$ENV_TYPE" != "local" ] && [ "$ENV_TYPE" != "cloud" ]; then
  echo "Error: Please specify environment type as either 'local' or 'cloud'"
  echo "Usage: ./setup_environment.sh [local|cloud]"
  exit 1
fi

# Create necessary directories if they don't exist
mkdir -p .streamlit
mkdir -p configs

echo "Setting up $ENV_TYPE environment configuration..."

# Copy appropriate .env file
cp configs/.env.$ENV_TYPE .env
echo "✅ Copied .env.$ENV_TYPE to .env"

# Copy appropriate secrets.toml file
cp configs/secrets.$ENV_TYPE.toml .streamlit/secrets.toml
echo "✅ Copied secrets.$ENV_TYPE.toml to .streamlit/secrets.toml"

# Copy appropriate docker-compose file
cp configs/docker-compose.$ENV_TYPE.yml docker-compose.yml
echo "✅ Copied docker-compose.$ENV_TYPE.yml to docker-compose.yml"

# Apply appropriate entrypoint script
cp configs/entrypoint.$ENV_TYPE.sh entrypoint.sh
chmod +x entrypoint.sh
echo "✅ Copied entrypoint.$ENV_TYPE.sh to entrypoint.sh"

echo "🎉 Environment setup complete for $ENV_TYPE deployment!"
echo "Run 'docker-compose up -d' to start services for this environment."
