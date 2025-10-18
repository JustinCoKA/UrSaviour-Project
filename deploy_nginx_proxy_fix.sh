#!/bin/bash

echo "🔧 Deploying API connectivity fixes..."

git add .
git commit -m "Fix: Use nginx proxy for production API calls

CRITICAL FIX: Production API connectivity
- Use relative paths in production (empty API_BASE)
- Nginx proxy handles /api/ routes to backend
- Added API debug page for testing connectivity
- Resolves Mixed Content and CORS issues

Changes:
- frontend/src/js/product_page.js: Use nginx proxy in production
- frontend/src/api-debug.html: Debug page for API testing

This should resolve the 'Failed to fetch' error by using proper nginx routing."

echo "📤 Pushing API fixes..."
git push origin main

echo "✅ DEPLOYMENT INSTRUCTIONS:"
echo ""
echo "# EC2 Commands:"
echo "git pull origin main"
echo "docker-compose -f docker-compose.prod.yml down"
echo "docker-compose -f docker-compose.prod.yml build --no-cache"
echo "docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "# Test API connectivity:"
echo "curl http://localhost:8000/api/v1/products/health"
echo "curl http://localhost/api/v1/products/health"
echo ""
echo "🔧 Debug URLs:"
echo "- https://www.ursaviour.com/api-debug.html (API connectivity test)"
echo "- https://www.ursaviour.com/products.html (main products page)"
echo ""
echo "🎯 Expected: API calls should work through nginx proxy"