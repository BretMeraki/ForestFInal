#!/bin/bash

# Forest OS Launcher Script
# Usage: ./launch.sh [local|cloud] [up|down|build|logs]

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENV="local"
ACTION="up"

# Parse command line arguments
if [ $# -gt 0 ]; then
  if [ "$1" = "local" ] || [ "$1" = "cloud" ]; then
    ENV="$1"
    shift
  fi
  
  if [ $# -gt 0 ]; then
    ACTION="$1"
  fi
fi

echo -e "${BLUE}🌳 Forest OS - Environment: ${GREEN}$ENV${BLUE}, Action: ${GREEN}$ACTION${NC}"

# Set up the environment
echo -e "${BLUE}Setting up $ENV environment...${NC}"
./setup_environment.sh "$ENV"

if [ $? -ne 0 ]; then
  echo -e "${RED}Failed to set up $ENV environment${NC}"
  exit 1
fi

# Handle the action
case "$ACTION" in
  up)
    echo -e "${BLUE}Starting services...${NC}"
    if [ "$ENV" = "local" ]; then
      # For local environment, bring up the database first
      docker compose up -d db
      echo -e "${YELLOW}Waiting for database to initialize...${NC}"
      sleep 5
      # Then bring up the rest
      docker-compose up -d
    else
      # For cloud, just bring everything up
      docker-compose up -d
    fi
    
    # Show status
    echo -e "${BLUE}Services status:${NC}"
    docker compose ps
    
    if [ "$ENV" = "local" ]; then
      echo -e "\n${GREEN}Local Forest OS is running!${NC}"
      echo -e "Access the application at: ${BLUE}http://localhost:8501${NC}"
      echo -e "Backend API is available at: ${BLUE}http://localhost:8000${NC}"
    else
      echo -e "\n${GREEN}Cloud Forest OS is deployed!${NC}"
    fi
    ;;
    
  down)
    echo -e "${BLUE}Stopping services...${NC}"
    docker compose down
    ;;
    
  build)
    echo -e "${BLUE}Building services...${NC}"
    docker compose build
    ;;
    
  logs)
    echo -e "${BLUE}Showing logs...${NC}"
    docker compose logs -f
    ;;
    
  *)
    echo -e "${RED}Unknown action: $ACTION${NC}"
    echo -e "Valid actions: up, down, build, logs"
    exit 1
    ;;
esac

echo -e "${GREEN}Done!${NC}"
