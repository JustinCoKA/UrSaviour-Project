#!/bin/bash

echo "🔧 Fixing frontend data parsing for new API structure..."

git add .
git commit -m "Critical fix: Frontend data parsing for new API structure

MAJOR FIX: Product display issues resolved
- Map new API fields: productId → id, productName → name, categoryName → category
- Map store fields: store_name → brand, final_price → price  
- Handle defaultImageUrl → image mapping
- Update cache busting: v=2025101806

API Structure Handled:
- productId, productName, categoryName, defaultImageUrl
- stores[].store_name, stores[].final_price, stores[].original_price

This resolves 'Unknown Product $0.00' display issues."

echo "📤 Pushing frontend data parsing fixes..."
git push origin main

echo "✅ DEPLOYMENT INSTRUCTIONS:"
echo ""
echo "# EC2 Commands:"
echo "git pull origin main"
echo "docker-compose -f docker-compose.prod.yml down"
echo "docker-compose -f docker-compose.prod.yml build --no-cache"
echo "docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "🎯 Expected results:"
echo "- Products show real names: 'Mineral Water', 'Lettuce', etc."
echo "- Real prices: $11.94, $4.99, etc. instead of $0.00"
echo "- Real categories: 'Frozen', 'Fruit', etc. instead of 'Uncategorized'"
echo "- 100 properly displayed products with store-specific pricing"