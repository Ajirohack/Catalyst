#!/bin/bash
# =============================================================================
# Catalyst Backend - Docker Deployment Scripts
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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

# Check if Docker is installed and running
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "Docker is installed and running"
}

# Check if docker-compose is available
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        log_error "Docker Compose is not available. Please install docker-compose."
        exit 1
    fi
    
    log_success "Docker Compose is available: $COMPOSE_CMD"
}

# Build images
build_images() {
    local target=${1:-production}
    log_info "Building Docker images for $target environment..."
    
    $COMPOSE_CMD build --build-arg BUILDKIT_INLINE_CACHE=1 catalyst-backend
    
    log_success "Docker images built successfully"
}

# Start services in production mode
start_production() {
    log_info "Starting Catalyst Backend in production mode..."
    
    # Check if .env.docker exists
    if [ ! -f ".env.docker" ]; then
        log_warning ".env.docker not found. Creating from template..."
        cp .env.template .env.docker
        log_warning "Please edit .env.docker with your production values before continuing."
        exit 1
    fi
    
    # Start services
    $COMPOSE_CMD up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check service status
    $COMPOSE_CMD ps
    
    log_success "Catalyst Backend started in production mode"
    log_info "API available at: http://localhost:8000"
    log_info "API docs available at: http://localhost:8000/docs"
}

# Start services in development mode
start_development() {
    log_info "Starting Catalyst Backend in development mode..."
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        log_warning ".env not found. Creating from template..."
        cp .env.template .env
        log_warning "Please edit .env with your development values before continuing."
        exit 1
    fi
    
    # Start development services
    $COMPOSE_CMD -f docker-compose.yml -f docker-compose.dev.yml up -d
    
    # Show logs
    log_info "Services started. Showing logs..."
    $COMPOSE_CMD logs -f catalyst-backend
}

# Stop services
stop_services() {
    log_info "Stopping Catalyst Backend services..."
    $COMPOSE_CMD down
    log_success "Services stopped"
}

# Clean up (remove containers, networks, volumes)
cleanup() {
    log_warning "This will remove all containers, networks, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "Cleaning up Docker resources..."
        $COMPOSE_CMD down -v --remove-orphans
        docker system prune -f
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Show logs
show_logs() {
    local service=${1:-catalyst-backend}
    $COMPOSE_CMD logs -f "$service"
}

# Health check
health_check() {
    log_info "Checking service health..."
    
    # Check if backend is responding
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "Backend is healthy"
    else
        log_error "Backend is not responding"
        return 1
    fi
    
    # Show service status
    $COMPOSE_CMD ps
}

# Show help
show_help() {
    echo "Catalyst Backend Docker Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build [target]     Build Docker images (target: production|development)"
    echo "  start              Start services in production mode"
    echo "  start-dev          Start services in development mode"
    echo "  stop               Stop all services"
    echo "  restart            Restart all services"
    echo "  logs [service]     Show logs for service (default: catalyst-backend)"
    echo "  health             Check service health"
    echo "  cleanup            Remove all containers, networks, and volumes"
    echo "  help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build production"
    echo "  $0 start"
    echo "  $0 start-dev"
    echo "  $0 logs catalyst-backend"
    echo "  $0 health"
}

# Main script logic
main() {
    # Check prerequisites
    check_docker
    check_docker_compose
    
    # Parse command
    case "${1:-help}" in
        "build")
            build_images "${2:-production}"
            ;;
        "start")
            start_production
            ;;
        "start-dev")
            start_development
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            start_production
            ;;
        "logs")
            show_logs "$2"
            ;;
        "health")
            health_check
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
