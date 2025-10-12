#!/bin/bash

# Update deployment script for UrSaviour project
# This script updates the running Docker containers with the latest code changes

set -e

echo "🚀 Updating UrSaviour deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📥 Pulling latest changes from repository...${NC}"
git pull origin main

echo -e "${YELLOW}🔄 Rebuilding and restarting containers...${NC}"

# Stop containers
echo "Stopping containers..."
docker compose -f docker-compose.prod.yml down

# Rebuild images with latest code
echo "Rebuilding images..."
docker compose -f docker-compose.prod.yml build --no-cache

# Start containers
echo "Starting containers..."
docker compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

# Check container status
echo -e "${YELLOW}📊 Checking container status...${NC}"
docker compose -f docker-compose.prod.yml ps

# Test API health
echo -e "${YELLOW}🔍 Testing API health...${NC}"
if curl -f http://localhost:8000/api/v1/products/products?limit=1 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ API is responding correctly${NC}"
else
    echo -e "${RED}❌ API is not responding${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Deployment update completed successfully!${NC}"
echo -e "${GREEN}🌐 Website: http://3.27.159.7${NC}"
echo -e "${GREEN}📋 Products: http://3.27.159.7/products.html${NC}"
echo -e "${GREEN}🔌 API: http://3.27.159.7/api/v1/products/products${NC}"