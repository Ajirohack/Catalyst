#!/bin/bash
# ==============================================================================
# Catalyst Backend - Production Deployment Script
# ==============================================================================

# Set script to exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions for logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    log_info "Checking if Docker is running..."
    
    if ! docker info &>/dev/null; then
        log_warning "Docker is not running. Attempting to start Docker..."
        
        # macOS specific (try to start Docker Desktop)
        if [ -d "/Applications/Docker.app" ]; then
            log_info "Found Docker Desktop, trying to start it..."
            open -a Docker
            
            # Wait for Docker to start (with timeout)
            local timeout=60
            local start_time=$(date +%s)
            local current_time
            
            log_info "Waiting for Docker to start (timeout: ${timeout}s)..."
            
            while ! docker info &>/dev/null; do
                current_time=$(date +%s)
                if [ $((current_time - start_time)) -gt $timeout ]; then
                    log_error "Docker startup timed out after ${timeout} seconds."
                    log_error "Please start Docker manually and run this script again."
                    exit 1
                fi
                
                log_info "Docker is starting... ($(($timeout - (current_time - start_time)))s remaining)"
                sleep 5
            done
        else
            log_error "Docker is not running and could not be started automatically."
            log_error "Please start Docker manually and run this script again."
            exit 1
        fi
    fi
    
    log_success "Docker is running!"
}

# Function to check and create required directories
create_directories() {
    log_info "Creating required directories..."
    
    directories=("data" "logs" "reports" "storage" "config/nginx" "config/redis")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            log_info "Creating directory: $dir"
            mkdir -p "$dir"
        else
            log_info "Directory already exists: $dir"
        fi
    done
    
    # Create Redis config if not exists
    if [ ! -f "config/redis/redis.conf" ]; then
        log_info "Creating Redis configuration file..."
        cat > config/redis/redis.conf << EOF
# Redis Configuration for Catalyst Backend
# Basic production configuration

# Network
bind 127.0.0.1 0.0.0.0
port 6379
protected-mode no

# General
timeout 300
tcp-keepalive 60
tcp-backlog 511
databases 16

# Memory management
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /data

# Logging
loglevel notice
logfile ""
EOF
    fi
    
    log_success "All required directories and configuration files are ready!"
}

# Function to deploy using docker-compose
deploy_with_compose() {
    log_info "Deploying with docker-compose..."
    
    # Check for docker-compose
    local compose_cmd
    if command -v docker-compose &>/dev/null; then
        compose_cmd="docker-compose"
    elif docker compose version &>/dev/null; then
        compose_cmd="docker compose"
    else
        log_error "Neither docker-compose nor docker compose are available."
        log_error "Please install docker-compose and try again."
        exit 1
    fi
    
    log_info "Using command: $compose_cmd"
    
    # Pull latest images
    log_info "Pulling latest images..."
    $compose_cmd pull
    
    # Build and start services
    log_info "Building and starting services..."
    $compose_cmd up --build -d
    
    # Check if services are healthy
    log_info "Checking service health..."
    sleep 10 # Give services time to start
    
    if $compose_cmd ps | grep -q "catalyst-backend" && $compose_cmd ps | grep -i -v "exit"; then
        log_success "Services are running!"
        
        # Get service details
        log_info "Service details:"
        $compose_cmd ps
        
        log_info "Catalyst Backend is accessible at: http://localhost:8000"
        log_info "API documentation is available at: http://localhost:8000/docs"
        
        if $compose_cmd ps | grep -q "catalyst-nginx"; then
            log_info "Nginx is running at: http://localhost:80"
        fi
    else
        log_error "Some services failed to start. Please check the logs:"
        $compose_cmd logs
        exit 1
    fi
}

# Main execution
main() {
    log_info "Starting Catalyst Backend Production Deployment"
    log_info "================================================"
    
    # Check if we're in the right directory
    if [ ! -f "docker-compose.yml" ] || [ ! -f "Dockerfile" ]; then
        log_error "docker-compose.yml or Dockerfile not found."
        log_error "Please run this script from the root of the Catalyst backend directory."
        exit 1
    fi
    
    # Check if the .env.docker file exists
    if [ ! -f ".env.docker" ]; then
        log_error ".env.docker file not found."
        log_error "Please create the .env.docker file with production configuration."
        exit 1
    fi
    
    # Steps to deploy
    check_docker
    create_directories
    deploy_with_compose
    
    log_success "Catalyst Backend has been successfully deployed to production!"
    log_success "==============================================================="
}

# Run the main function
main
