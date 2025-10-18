#!/bin/bash

echo "🔧 Fixing frontend deployment API connection issues..."

git add .
git commit -m "Fix: Frontend API connection and CORS issues

FIXES:
- Correct API endpoint URLs: /api/v1/products → /api/v1/products/ (trailing slash)
- Add production CORS origins: www.ursaviour.com, ursaviour.com
- Support both HTTP and HTTPS for domain transition
- Fix Mixed Content warnings for HTTPS sites

Changes:
- frontend/src/js/product_page.js: Fix API endpoint URLs
- backend/app/main.py: Add production domains to CORS

This resolves the 'Backend service unavailable: Failed to fetch' error."

echo "📤 Pushing frontend fixes..."
git push origin main

echo "✅ DEPLOYMENT INSTRUCTIONS:"
echo ""
echo "# EC2 Commands:"
echo "git pull origin main"
echo "docker-compose -f docker-compose.prod.yml down"
echo "docker-compose -f docker-compose.prod.yml build --no-cache"
echo "docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "# Test API connection:"
echo "curl http://localhost:8000/api/v1/products/ | jq '.total_count'"
echo ""
echo "🎯 Expected results:"
echo "- Frontend should now load products successfully"
echo "- No more CORS errors in browser console"
echo "- Products page displays 100 products with store-specific pricing"