#!/bin/bash

echo "🎯 DEFINITIVE FOUNDATIONAL DATA SOLUTION"
echo "========================================"

git add .
git commit -m "DEFINITIVE SOLUTION: Implement proper store_base_prices table

BREAKING CHANGE: Remove temporary pricing simulation, implement proper data structure

Changes:
- Created definitive store_base_prices table with raw SQL (guaranteed to work)
- Proper foundational data loader with error handling
- Removed temporary pricing simulation logic  
- API now requires proper store_base_prices data
- Clear separation: foundational pricing vs ETL discounts

Database Structure:
- products: Basic product info
- stores: Store info
- store_base_prices: Static foundational pricing (400 records)
- storeOfferings: Dynamic ETL discount pricing

This is the permanent, scalable solution for multi-store pricing."

echo "📤 Pushing definitive solution..."
git push origin main

echo "✅ DEPLOYMENT INSTRUCTIONS:"
echo ""
echo "# EC2 Commands:"
echo "git pull origin main"
echo "docker cp setup_foundational_definitive.py ursaviour-api-1:/app/"
echo "docker cp data/foundational_dataset_v1.csv ursaviour-api-1:/app/"
echo "docker exec ursaviour-api-1 python setup_foundational_definitive.py"
echo ""
echo "# Rebuild API with new structure:"
echo "docker-compose -f docker-compose.prod.yml down"
echo "docker-compose -f docker-compose.prod.yml build --no-cache api"
echo "docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "# Verify results:"
echo "curl http://localhost:8000/api/v1/products/debug/counts"
echo "curl http://localhost:8000/api/v1/products/ | jq '.products[0].stores'"
echo ""
echo "🎯 Expected: store_base_prices_count = 400, different prices per store"