#!/bin/bash
# Quick Fix Script for HTTP 404 API Errors
# Run this on your production server where the application is deployed

echo "🔧 UrSaviour API Fix - Resolving HTTP 404 Errors"
echo "================================================"

# 1. Check if services are running
echo "1️⃣ Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# 2. Stop all services and remove containers
echo "2️⃣ Stopping all services and removing containers..."
docker-compose -f docker-compose.prod.yml down --remove-orphans

# 3. Remove old images to force rebuild
echo "3️⃣ Removing old images to force rebuild..."
docker-compose -f docker-compose.prod.yml down --rmi local 2>/dev/null || true

# 4. Update CORS configuration
echo "4️⃣ Updating CORS configuration..."
if [ ! -f .env ]; then
    echo "Creating .env file from production template..."
    cp .env.production .env
fi

# Update CORS origins for ursaviour.com
sed -i 's|BACKEND_CORS_ORIGINS=.*|BACKEND_CORS_ORIGINS=["https://ursaviour.com", "http://ursaviour.com"]|' .env

# 5. Rebuild and start services
echo "5️⃣ Rebuilding and starting services..."

# Build and start services with forced rebuild
echo "Building and starting all services..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Test API health
echo "Testing API health..."
for i in {1..5}; do
    if curl -f http://localhost:8000/health 2>/dev/null; then
        echo "✅ API is healthy"
        break
    else
        echo "⏳ Waiting for API... (attempt $i/5)"
        sleep 10
    fi
done

# 6. Test the complete setup
echo "6️⃣ Testing complete setup..."

# Test nginx proxy
echo "Testing nginx proxy to API..."
for i in {1..3}; do
    if curl -f http://localhost/api/v1/products/products 2>/dev/null; then
        echo "✅ Nginx proxy is working correctly"
        break
    else
        echo "⏳ Testing proxy... (attempt $i/3)"
        sleep 5
    fi
done

# Final status check
echo ""
echo "📊 Final Status Check:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "✅ Fix completed! Your website should now work at: http://ursaviour.com/products.html"
echo ""
echo "🔍 If issues persist, run the diagnostic script:"
echo "   ./diagnose-api-issues.sh"
echo ""
echo "📋 Or check logs with:"
echo "   docker-compose -f docker-compose.prod.yml logs -f