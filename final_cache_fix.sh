#!/bin/bash

echo "🔧 Final fix for browser cache and missing API endpoints..."

git add .
git commit -m "Final fix: Browser cache busting and missing API endpoints

CRITICAL FIXES:
- Update cache busting version: v=2025101805 (force browser refresh)
- Add missing /api/health endpoint (404 → 200)
- Ensure all API routes are available

Changes:
- frontend/src/products.html: Update script version to force refresh
- backend/app/main.py: Add /api/health endpoint

This should resolve remaining cache and API availability issues."

echo "📤 Pushing final fixes..."
git push origin main

echo "✅ DEPLOYMENT INSTRUCTIONS:"
echo ""
echo "# EC2 Commands:"
echo "git pull origin main"
echo "docker-compose -f docker-compose.prod.yml down"
echo "docker-compose -f docker-compose.prod.yml build --no-cache"
echo "docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "# Browser instructions after deployment:"
echo "1. Open: https://www.ursaviour.com/products.html"
echo "2. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)"
echo "3. Or: F12 → Right-click refresh → 'Empty Cache and Hard Reload'"
echo ""
echo "🎯 Expected: Products page should now load 100 products successfully!"