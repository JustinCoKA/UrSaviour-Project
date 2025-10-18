#!/bin/bash

echo "🚀 Deploying new foundational data structure..."

# Commit the new structure
git add .
git commit -m "Implement separate base pricing structure

BREAKING CHANGE: Separated foundational pricing from ETL discounts

New Structure:
- foundational_dataset_v1.csv → store_base_prices (매장별 기본가격)
- ETL weekly data → storeOfferings (할인정보만)
- API now uses store_base_prices for base pricing
- storeOfferings reserved for weekly discount ETL

Benefits:
- Clear separation of foundational vs discount pricing
- Easy to verify ETL discount application
- Maintains data integrity between base prices and discounts"

echo "📤 Pushing to GitHub..."
git push origin main

echo "✅ Code pushed. Deploy on EC2 with:"
echo ""
echo "# EC2 Deployment Commands:"
echo "git pull origin main"
echo "docker-compose -f docker-compose.prod.yml down"
echo "docker-compose -f docker-compose.prod.yml build --no-cache api"
echo "docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "# Load foundational data:"
echo "docker cp load_foundational_v2.py ursaviour-api-1:/app/"
echo "docker cp data/foundational_dataset_v1.csv ursaviour-api-1:/app/"
echo "docker exec ursaviour-api-1 python load_foundational_v2.py"
echo ""
echo "# Verify results:"
echo "curl http://localhost:8000/api/v1/products/debug/counts"
echo "curl http://localhost:8000/api/v1/products/ | jq '.total_count'"
echo ""
echo "🎯 Expected Results:"
echo "- store_base_prices_count: 400 (100 products × 4 stores)"
echo "- store_offerings_count: 0 (reserved for ETL)"
echo "- total_count: 100 (all products with store-specific base prices)"