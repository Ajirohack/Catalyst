#!/bin/bash
set -e

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Catalyst Backend Deployment Script ===${NC}"
echo -e "${YELLOW}Starting deployment process...${NC}"

# Set environment variables
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env.docker"

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: $ENV_FILE file not found${NC}"
    echo -e "Creating a sample $ENV_FILE file..."
    cat > "$ENV_FILE" << EOL
# Database settings
DATABASE_URL=sqlite:///./catalyst.db
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=catalyst

# API settings
API_HOST=0.0.0.0
API_PORT=8000
API_URL_PREFIX=/api
SECRET_KEY=your-secret-key-here

# Redis settings
REDIS_HOST=redis
REDIS_PORT=6379

# File storage settings
STORAGE_PATH=/app/storage
EOL
    echo -e "${YELLOW}Created sample $ENV_FILE file. Please edit it with your configuration and run this script again.${NC}"
    exit 1
fi

# Create required directories
echo -e "${YELLOW}Creating required directories...${NC}"
mkdir -p ./storage/uploads
mkdir -p ./storage/knowledge_base
mkdir -p ./logs

# Stop running containers
echo -e "${YELLOW}Stopping any running containers...${NC}"
docker-compose -f $COMPOSE_FILE down

# Build the Docker image with retries
echo -e "${YELLOW}Building Docker images...${NC}"
max_retries=3
retry_count=0
build_success=false

while [ $retry_count -lt $max_retries ] && [ "$build_success" = false ]; do
    echo -e "${YELLOW}Build attempt $(($retry_count + 1))/${max_retries}...${NC}"
    
    if docker-compose -f $COMPOSE_FILE build --no-cache; then
        build_success=true
        echo -e "${GREEN}Docker build successful!${NC}"
    else
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            echo -e "${YELLOW}Build failed. Waiting 10 seconds before retrying...${NC}"
            sleep 10
        else
            echo -e "${RED}Failed to build Docker images after $max_retries attempts.${NC}"
            echo -e "${YELLOW}Trying alternative build approach...${NC}"
            
            # Try building with network host mode
            if docker-compose -f $COMPOSE_FILE build --no-cache --network=host; then
                build_success=true
                echo -e "${GREEN}Docker build successful with network=host!${NC}"
            else
                echo -e "${RED}All build attempts failed. Please check your internet connection and Docker configuration.${NC}"
                exit 1
            fi
        fi
    fi
done

# Start the containers
echo -e "${YELLOW}Starting containers...${NC}"
docker-compose -f $COMPOSE_FILE up -d

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}The API should be available shortly at http://localhost:8000${NC}"
