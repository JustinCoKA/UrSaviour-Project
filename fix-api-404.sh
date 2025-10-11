#!/bin/bash
# Quick Fix Script for HTTP 404 API Errors
# Run this on your production server where the application is deployed

echo "🔧 UrSaviour API Fix - Resolving HTTP 404 Errors"
echo "================================================"

# 1. Check if services are running
echo "1️⃣ Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# 2. Stop all services
echo "2️⃣ Stopping all services..."
docker-compose -f docker-compose.prod.yml down

# 3. Update CORS configuration
echo "3️⃣ Updating CORS configuration..."
if [ ! -f .env ]; then
    echo "Creating .env file from production template..."
    cp .env.production .env
fi

# Update CORS origins for ursaviour.com
sed -i 's|BACKEND_CORS_ORIGINS=.*|BACKEND_CORS_ORIGINS=["https://ursaviour.com", "http://ursaviour.com"]|' .env

# 4. Restart services in correct order
echo "4️⃣ Starting services in correct order..."

# Start API first
echo "Starting API service..."
docker-compose -f docker-compose.prod.yml up -d api
sleep 15

# Test API health
echo "Testing API health..."
curl -f http://localhost:8000/health || echo "⚠️ API health check failed"

# Start web service
echo "Starting web service..."
docker-compose -f docker-compose.prod.yml up -d web
sleep 5

# 5. Test the complete setup
echo "5️⃣ Testing complete setup..."
curl -f http://localhost/api/v1/products/products || echo "⚠️ API proxy test failed"

echo "✅ Fix completed! Check your website now."
echo "If issues persist, check logs with: docker-compose -f docker-compose.prod.yml logs"