# 🐳 Catalyst Backend - Docker Deployment Guide

This guide provides comprehensive instructions for deploying the Catalyst Backend using Docker and Docker Compose.

## 📋 **Prerequisites**

- **Docker Engine** 20.10+
- **Docker Compose** 2.0+ (or `docker-compose` 1.29+)
- **Minimum System Requirements**:
  - CPU: 2 cores
  - RAM: 4GB
  - Storage: 10GB free space

## 🚀 **Quick Start**

### **1. Clone and Setup**

```bash
git clone <repository-url>
cd catalyst/backend
```

### **2. Environment Configuration**

```bash
# Copy environment template
cp .env.template .env.docker

# Edit with your configuration
nano .env.docker
```

### **3. Deploy with Script**

```bash
# Make deployment script executable
chmod +x scripts/docker-deploy.sh

# Build and start production
./scripts/docker-deploy.sh build
./scripts/docker-deploy.sh start
```

## 🏗️ **Docker Architecture**

### **Services Overview**

| Service | Purpose | Port | Dependencies |
|---------|---------|------|--------------|
| **catalyst-backend** | Main FastAPI application | 8000 | postgres, redis |
| **postgres** | PostgreSQL database | 5432 | - |
| **redis** | Caching and session storage | 6379 | - |
| **nginx** | Reverse proxy (optional) | 80, 443 | catalyst-backend |

### **Network Architecture**

```
Internet → Nginx (80/443) → FastAPI Backend (8000)
                            ↓
                     PostgreSQL (5432) + Redis (6379)
```

## 🔧 **Configuration**

### **Environment Files**

| File | Purpose | Usage |
|------|---------|-------|
| `.env.docker` | Production configuration | Docker production deployment |
| `.env` | Development configuration | Local development |
| `.env.template` | Configuration template | Base template for new setups |

### **Key Configuration Sections**

#### **1. API Server**

```bash
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
ENVIRONMENT=production
```

#### **2. Database**

```bash
DATABASE_URL=postgresql://catalyst_user:catalyst_password@postgres:5432/catalyst
```

#### **3. AI Providers**

```bash
OPENAI_API_KEY=your-api-key-here
ANTHROPIC_API_KEY=your-api-key-here
GOOGLE_AI_API_KEY=your-api-key-here
# ... other providers
```

## 📦 **Deployment Options**

### **Option 1: Using Deployment Script (Recommended)**

```bash
# Production deployment
./scripts/docker-deploy.sh start

# Development deployment
./scripts/docker-deploy.sh start-dev

# Check health
./scripts/docker-deploy.sh health

# View logs
./scripts/docker-deploy.sh logs

# Stop services
./scripts/docker-deploy.sh stop
```

### **Option 2: Manual Docker Compose**

#### **Production Deployment**

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f catalyst-backend
```

#### **Development Deployment**

```bash
# Start with development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs with auto-reload
docker-compose logs -f catalyst-backend
```

## 🛠️ **Advanced Configuration**

### **Custom Build Arguments**

```bash
# Build with specific Python version
docker build --build-arg PYTHON_VERSION=3.13 .

# Build development image
docker build --target development .

# Build production image  
docker build --target production .
```

### **Resource Limits**

Modify `docker-compose.yml` to adjust resource limits:

```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '2.0'
    reservations:
      memory: 1G
      cpus: '1.0'
```

### **Volume Mounting**

```yaml
volumes:
  - ./data:/app/data           # Persistent data
  - ./logs:/app/logs           # Application logs
  - ./storage:/app/storage     # File uploads
  - ./reports:/app/reports     # Generated reports
```

## 📊 **Monitoring and Health Checks**

### **Health Check Endpoints**

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/health` | Overall health | Service status |
| `/health/db` | Database connectivity | DB status |
| `/health/redis` | Redis connectivity | Cache status |

### **Container Health Checks**

```bash
# Check container health
docker-compose ps

# Detailed health status
docker inspect --format='{{.State.Health.Status}}' catalyst-backend

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' catalyst-backend
```

### **Monitoring Commands**

```bash
# Resource usage
docker stats

# Container logs
docker-compose logs -f --tail=100 catalyst-backend

# Database logs
docker-compose logs postgres

# Redis logs
docker-compose logs redis
```

## 🔒 **Security Configuration**

### **Production Security Checklist**

- [ ] **Change default passwords** in `.env.docker`
- [ ] **Set strong SECRET_KEY** for JWT tokens
- [ ] **Configure CORS origins** for your domain
- [ ] **Enable Redis password** protection
- [ ] **Use SSL certificates** with Nginx
- [ ] **Set proper file permissions** on sensitive files

### **Secure Environment Setup**

```bash
# Secure file permissions
chmod 600 .env.docker
chmod 600 config/redis.conf

# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Port Already in Use**

```bash
# Check what's using port 8000
lsof -i :8000

# Use different port
docker-compose -e API_PORT=8001 up -d
```

#### **2. Database Connection Issues**

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Test database connection
docker-compose exec postgres psql -U catalyst_user -d catalyst -c "SELECT 1;"
```

#### **3. Memory Issues**

```bash
# Check memory usage
docker stats --no-stream

# Increase memory limits in docker-compose.yml
# Or add swap space to host system
```

#### **4. SSL/Certificate Issues**

```bash
# Check nginx configuration
docker-compose exec nginx nginx -t

# View nginx logs
docker-compose logs nginx
```

### **Debug Mode**

```bash
# Start with debug logging
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Connect to running container
docker-compose exec catalyst-backend bash

# Check application logs
docker-compose exec catalyst-backend tail -f /app/logs/catalyst.log
```

## 📈 **Performance Optimization**

### **Production Optimizations**

1. **Gunicorn Configuration**
   - Workers: 2x CPU cores
   - Worker class: `uvicorn.workers.UvicornWorker`
   - Timeout: 120 seconds

2. **Database Optimization**
   - Connection pooling: 10-20 connections
   - Query optimization
   - Index configuration

3. **Redis Configuration**
   - Memory policy: `allkeys-lru`
   - Persistence: AOF enabled
   - Connection pooling

4. **Nginx Optimization**
   - Gzip compression
   - Static file serving
   - Load balancing (if multiple instances)

### **Scaling Considerations**

```bash
# Scale backend instances
docker-compose up -d --scale catalyst-backend=3

# Use external load balancer
# Configure nginx upstream servers

# Use external databases for larger deployments
# Configure PostgreSQL cluster
# Use Redis cluster
```

## 🔄 **Backup and Recovery**

### **Database Backup**

```bash
# Create database backup
docker-compose exec postgres pg_dump -U catalyst_user catalyst > backup.sql

# Restore database
docker-compose exec -T postgres psql -U catalyst_user catalyst < backup.sql
```

### **Volume Backup**

```bash
# Backup data volumes
docker run --rm -v catalyst_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore data volumes
docker run --rm -v catalyst_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

## 📞 **Support and Maintenance**

### **Regular Maintenance Tasks**

```bash
# Update containers
docker-compose pull
docker-compose up -d

# Clean up unused resources
docker system prune -f

# Update application code
git pull
docker-compose build
docker-compose up -d
```

### **Log Rotation**

Configure log rotation to prevent disk space issues:

```bash
# Add to crontab
0 0 * * * docker-compose exec catalyst-backend find /app/logs -name "*.log" -mtime +7 -delete
```

---

## 🎯 **Next Steps**

1. **Configure your environment** variables in `.env.docker`
2. **Add your AI provider API keys**
3. **Deploy using the deployment script**
4. **Configure monitoring** and alerting
5. **Set up automated backups**
6. **Configure SSL certificates** for production

For additional support or advanced configurations, refer to the main documentation or create an issue in the repository.
