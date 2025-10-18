#!/bin/bash

echo "🚀 Deploying products page fix to EC2..."

# Commit changes
git add .
git commit -m "Fix: Show all 100 products regardless of storeOfferings availability

- Modified products_new.py to display all products from products table
- If no storeOfferings exist, show basePrice across all stores
- ETL functionality preserved but not required for basic product display
- Addresses issue where only 2 products were showing due to missing storeOfferings"

echo "📤 Pushing to GitHub..."
git push origin main

echo "✅ Code pushed to GitHub. Now deploy on EC2 with:"
echo ""
echo "# Run these commands on your EC2 server:"
echo "git pull origin main"
echo "docker-compose -f docker-compose.prod.yml down"
echo "docker-compose -f docker-compose.prod.yml build --no-cache api"
echo "docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "# Then test:"
echo "curl http://localhost:8000/api/v1/products/ | jq '.total_count'"
echo "curl http://localhost:8000/api/v1/products/debug/counts"

echo ""
echo "🎯 Expected results:"
echo "- total_count should be 100 (not 2)"
echo "- All products displayed with basePrice across all stores"
echo "- storeOfferings will enhance prices when available via ETL later"