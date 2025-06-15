# Docker Deployment Guide

This guide explains how to deploy the Catalyst backend using Docker for local development and testing.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)
- At least 2GB of available RAM
- Port 8000 available on your system

## Quick Start

### 1. Clone and Navigate
```bash
cd /path/to/Catalyst
```

### 2. Build and Run
```bash
# Build and start the backend
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### 3. Access the Application
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Docker Commands

### Basic Operations
```bash
# Build and start services
docker-compose up --build

# Start services (without rebuilding)
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (⚠️ removes data)
docker-compose down -v

# View logs
docker-compose logs -f backend

# Restart a service
docker-compose restart backend
```

### Development Commands
```bash
# Rebuild only the backend
docker-compose build backend

# Run a command inside the container
docker-compose exec backend python -c "print('Hello from container')"

# Access container shell
docker-compose exec backend bash

# View container status
docker-compose ps
```

## Configuration

### Environment Variables

Create a `.env` file in the project root or modify `backend/.env.docker`:

```bash
# Copy the template
cp backend/.env.docker .env

# Edit as needed
vim .env
```

### Key Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | Host to bind the API |
| `API_PORT` | `8000` | Port for the API |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `ALLOWED_ORIGINS` | `localhost:3000` | CORS allowed origins |

## Development vs Production

### Development Setup
```yaml
# In docker-compose.yml, keep this volume mount:
volumes:
  - ./backend:/app  # Live code reloading
```

### Production Setup
```yaml
# Remove the volume mount for security:
volumes:
  # - ./backend:/app  # Comment out this line
  - catalyst_data:/app/data
  - catalyst_logs:/app/logs
```

## Adding Database Services

Uncomment the database services in `docker-compose.yml`:

### PostgreSQL
```yaml
postgres:
  image: postgres:15-alpine
  container_name: catalyst-postgres
  environment:
    POSTGRES_DB: catalyst
    POSTGRES_USER: catalyst_user
    POSTGRES_PASSWORD: catalyst_password
  ports:
    - "5432:5432"
  volumes:
    - catalyst_postgres:/var/lib/postgresql/data
```

### Redis
```yaml
redis:
  image: redis:7-alpine
  container_name: catalyst-redis
  ports:
    - "6379:6379"
  volumes:
    - catalyst_redis:/data
```

## Monitoring and Logs

### Health Checks
```bash
# Check container health
docker-compose ps

# Manual health check
curl http://localhost:8000/health
```

### Viewing Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend

# Follow logs (real-time)
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   
   # Change port in docker-compose.yml
   ports:
     - "8001:8000"  # Use port 8001 instead
   ```

2. **Permission denied**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER ./backend
   ```

3. **Container won't start**
   ```bash
   # Check logs for errors
   docker-compose logs backend
   
   # Rebuild from scratch
   docker-compose down
   docker-compose build --no-cache backend
   docker-compose up
   ```

4. **Out of disk space**
   ```bash
   # Clean up Docker
   docker system prune -a
   docker volume prune
   ```

### Debug Mode

For debugging, modify the environment:

```yaml
environment:
  - DEBUG=true
  - LOG_LEVEL=DEBUG
```

## Performance Optimization

### Multi-stage Build (Advanced)

For production, consider a multi-stage Dockerfile:

```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["python", "main.py"]
```

### Resource Limits

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

## Security Considerations

1. **Use non-root user** ✅ (Already implemented)
2. **Limit container capabilities**
3. **Use secrets for sensitive data**
4. **Regular security updates**
5. **Network isolation** ✅ (Already implemented)

## Next Steps

1. **Add SSL/TLS** for HTTPS
2. **Implement database migrations**
3. **Add monitoring** (Prometheus/Grafana)
4. **Set up CI/CD** pipeline
5. **Deploy to cloud** (AWS/GCP/Azure)

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs backend`
2. Verify health: `curl http://localhost:8000/health`
3. Review this guide
4. Check Docker Desktop status

For more help, refer to the main project README or create an issue in the repository.