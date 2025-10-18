# 🚀 UrSaviour Production Deployment Guide

## Current Issues
- **Backend Docker container not running on production server**
- Health check `/health` → HTTP 404 response
- Frontend works normally but API connection fails

## Immediate Commands to Execute

### 1️⃣ Server Access and Project Verification
```bash
# After SSH connection to server
cd /opt/ursaviour  # or path where project is located

# Check current status
docker ps -a
docker-compose ps
```

### 2️⃣ Start Docker Services (Most Important!)
```bash
# Stop existing containers
docker-compose -f docker-compose.prod.yml down

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 3️⃣ Immediate Checks Required
```bash
# API server status
curl http://localhost:8000/health
# Expected response: {"status":"ok"}

# Check container logs
docker-compose -f docker-compose.prod.yml logs api

# Check ports
netstat -tlnp | grep 8000
```

### 4️⃣ Environment Variables Check
```bash
# Check .env file existence
ls -la .env

# Check key environment variables (excluding sensitive info)
grep -v PASSWORD .env | grep -v SECRET | head -10
```

## 🔧 Problem Resolution by Scenario

### Scenario 1: Docker not installed
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Logout and re-login required
```

### Scenario 2: Docker Compose missing
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Scenario 3: Environment variables issue
```bash
# Copy production environment file
cp .env.production .env

# Set required environment variables
nano .env
# Check/modify DATABASE_URL, SECRET_KEY, BACKEND_CORS_ORIGINS
```

### Scenario 4: Port conflict
```bash
# Check processes using port 8000
sudo lsof -i :8000
# Kill the process if necessary
```

### Scenario 5: Network issues
```bash
# Reset Docker network
docker network prune
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

## ✅ Success Verification Checklist

When completed, all of the following should work normally:

1. **Docker Container Status**
   ```bash
   $ docker-compose -f docker-compose.prod.yml ps
   NAME     COMMAND            SERVICE   STATUS    PORTS
   api      "uvicorn..."       api       Up        8000/tcp
   web      "nginx -g..."      web       Up        80/tcp, 443/tcp
   ```

2. **Health Check**
   ```bash
   $ curl http://localhost:8000/health
   {"status":"ok"}
   ```

3. **Website Access**
   - Access https://ursaviour.com/products.html
   - Products load normally
   - No errors in console

## 🆘 Emergency Contact
- Development Team Slack: #dev-emergency
- Share screenshots and docker logs when reporting issues

---
**⏰ Expected Recovery Time: 5-15 minutes**
**👥 Required Permissions: Server SSH access, Docker execution rights**