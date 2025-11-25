# Docker Setup Guide

This document provides detailed information about the Docker setup for the AI Bias & Heuristics Diagnostic Tool.

## Quick Start

```bash
# Start all services
docker-compose up

# Or run in background
docker-compose up -d
```

Access the application:
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Architecture

### Services

1. **Backend** (`bias-tool-backend`)
   - Base Image: `python:3.11-slim`
   - Port: 8000
   - Database: SQLite with persistent volume
   - Health Check: HTTP GET to `/health` endpoint

2. **Frontend** (`bias-tool-frontend`)
   - Build Stage: `node:20-alpine`
   - Runtime: `nginx:alpine`
   - Port: 80
   - Features: Production build, gzip compression, React Router support

### Networking

All services run on a dedicated bridge network (`app-network`) allowing:
- Service-to-service communication via service names
- Isolation from other Docker networks
- Easy horizontal scaling

### Data Persistence

The SQLite database is persisted using a Docker volume:
```yaml
volumes:
  backend-data:/app/data
```

This ensures data survives container restarts and rebuilds.

## Common Commands

### Starting Services

```bash
# Build and start all services
docker-compose up --build

# Start in background (detached mode)
docker-compose up -d

# Start specific service
docker-compose up backend
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
```

### Stopping Services

```bash
# Stop all services (keeps containers)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (DELETES DATABASE)
docker-compose down -v

# Stop and remove everything including images
docker-compose down --rmi all -v
```

### Rebuilding

```bash
# Rebuild services after code changes
docker-compose build

# Force rebuild without cache
docker-compose build --no-cache

# Rebuild and restart
docker-compose up --build
```

### Inspecting Services

```bash
# List running containers
docker-compose ps

# Execute command in running container
docker-compose exec backend bash
docker-compose exec frontend sh

# View resource usage
docker stats
```

## Development Workflow

### Making Backend Changes

1. Edit Python files in `./backend/app/`
2. Rebuild backend:
   ```bash
   docker-compose build backend
   docker-compose up -d backend
   ```

### Making Frontend Changes

1. Edit TypeScript/React files in `./frontend/src/`
2. Rebuild frontend:
   ```bash
   docker-compose build frontend
   docker-compose up -d frontend
   ```

### Database Reset

To start with a fresh database:

```bash
# Stop services and remove volumes
docker-compose down -v

# Start again (creates new database)
docker-compose up
```

## Environment Variables

### Backend Configuration

Environment variables can be set in `docker-compose.yml`:

```yaml
environment:
  - DATABASE_URL=sqlite:///./data/bias_tool.db
  - API_HOST=0.0.0.0
  - API_PORT=8000
  - CORS_ORIGINS=http://localhost
```

### Frontend Configuration

Build-time variables for the frontend:

```yaml
build:
  args:
    - VITE_API_BASE_URL=http://localhost:8000
```

## Health Checks

Both services include health checks:

**Backend**:
- Checks `/health` endpoint every 30 seconds
- 10-second timeout, 3 retries
- 40-second startup grace period

**Frontend**:
- Wget request to root path every 30 seconds
- 10-second timeout, 3 retries
- 40-second startup grace period

View health status:
```bash
docker-compose ps
```

## Troubleshooting

### Port Already in Use

If port 80 or 8000 is already in use, edit `docker-compose.yml`:

```yaml
ports:
  - "8080:80"  # Frontend on port 8080 instead of 80
  - "8001:8000"  # Backend on port 8001 instead of 8000
```

### Container Won't Start

Check logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

Rebuild without cache:
```bash
docker-compose build --no-cache
```

### Database Issues

Reset the database:
```bash
docker-compose down -v
docker-compose up
```

### Permission Denied

On Linux, you may need to run with sudo:
```bash
sudo docker-compose up
```

Or add your user to the docker group:
```bash
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

### Out of Disk Space

Clean up Docker resources:
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything not in use
docker system prune -a
```

## Production Considerations

### Security

1. **Change default ports** - Don't expose on standard ports
2. **Add authentication** - Implement JWT or OAuth
3. **Use secrets** - Don't hardcode credentials in docker-compose.yml
4. **Update base images** - Regularly update for security patches
5. **Non-root user** - Run containers as non-root user

### Performance

1. **Use PostgreSQL** instead of SQLite for better concurrency
2. **Add Redis** for caching
3. **Enable gzip** in nginx (already configured)
4. **Optimize image size** - Use multi-stage builds (already implemented)
5. **Resource limits**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

### Monitoring

Add logging and monitoring services:

```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

## Docker Compose Reference

### Version

Using `version: '3.8'` which supports:
- Health checks
- Build arguments
- Named volumes
- Bridge networks
- Restart policies

### Service Dependencies

```yaml
depends_on:
  - backend  # Frontend waits for backend to start
```

Note: This doesn't wait for backend to be "ready", only for it to start. Use health checks for readiness.

### Restart Policies

All services use `restart: unless-stopped`:
- Containers restart automatically if they crash
- Won't restart if manually stopped
- Will restart on system reboot

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build and test
        run: |
          docker-compose build
          docker-compose up -d
          docker-compose ps
          docker-compose down
```

### Kubernetes Migration

To deploy to Kubernetes:

1. Convert docker-compose to k8s manifests:
   ```bash
   kompose convert
   ```

2. Create Deployment, Service, and PersistentVolumeClaim manifests

3. Deploy:
   ```bash
   kubectl apply -f .
   ```

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)

## Support

For issues related to the Docker setup, please:
1. Check this documentation
2. Review logs: `docker-compose logs`
3. Open an issue on GitHub with logs and error messages
