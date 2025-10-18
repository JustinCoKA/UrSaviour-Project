#!/bin/bash

# UrSaviour Safe AWS Deployment Script
# Problem solving and step-by-step deployment

set -e

echo "🔧 UrSaviour deployment troubleshooting in progress..."

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Check current location
log_info "Checking current directory..."
pwd
ls -la

# 2. Update latest code
log_info "Fetching latest code..."
git pull origin main

# 3. Check if nginx config file exists in frontend
log_info "Checking nginx configuration file..."
if [ ! -f "frontend/default.conf" ]; then
    log_warn "frontend/default.conf not found. Copying from deployment..."
    if [ -f "deployment/default.conf" ]; then
        cp deployment/default.conf frontend/
        log_info "nginx configuration file copied successfully"
    else
        log_error "deployment/default.conf file not found!"
        exit 1
    fi
else
    log_info "nginx configuration file already exists"
fi

# 4. Check environment variables file
log_info "Checking environment variables file..."
if [ ! -f ".env" ]; then
    if [ -f ".env.aws.production" ]; then
        log_info "Copying .env.aws.production to .env"
        cp .env.aws.production .env
    else
        log_error ".env file not found!"
        exit 1
    fi
fi

# 5. Clean up existing containers
log_info "Cleaning up existing containers..."
docker compose -f docker-compose.prod.yml down --remove-orphans || true
docker system prune -f || true

# 6. Build images (rebuild without cache)
log_info "Building Docker images..."
docker compose -f docker-compose.prod.yml build --no-cache

# 7. Start services
log_info "Starting services..."
docker compose -f docker-compose.prod.yml up -d

# 8. Check service status
log_info "Checking service status..."
sleep 10
docker compose -f docker-compose.prod.yml ps

# 9. Health check
log_info "Performing health check..."
sleep 30

# API health check
for i in {1..10}; do
    log_info "API health check attempt $i/10..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "✅ API server is running normally!"
        break
    else
        if [ $i -eq 10 ]; then
            log_error "❌ API server health check failed"
            docker compose -f docker-compose.prod.yml logs api
            exit 1
        fi
        log_warn "API server starting... retrying in 5 seconds"
        sleep 5
    fi
done

# Web server check
if curl -f http://localhost > /dev/null 2>&1; then
    log_info "✅ Web server is running normally!"
else
    log_warn "⚠️ There may be an issue accessing the web server"
    docker compose -f docker-compose.prod.yml logs web
fi

# 10. Output final status
log_info "🎉 Deployment complete! Current status:"
echo ""
docker compose -f docker-compose.prod.yml ps
echo ""
log_info "🌐 Website: http://$(curl -s ifconfig.me || echo 'YOUR-EC2-IP')"
log_info "🔧 API: http://$(curl -s ifconfig.me || echo 'YOUR-EC2-IP'):8000"
log_info "📊 Health check: http://$(curl -s ifconfig.me || echo 'YOUR-EC2-IP'):8000/health"
echo ""
log_info "🔍 Log check commands:"
echo "   docker compose -f docker-compose.prod.yml logs -f api"
echo "   docker compose -f docker-compose.prod.yml logs -f web"

log_info "✅ Deployment completed successfully!"