#!/bin/bash

echo "🎯 FINAL FIX: Cache Busting + Production Deployment"
echo "=================================================="
echo ""

# 완전히 새로운 캐시 버스팅 버전으로 커밋
git add .
git commit -m "CRITICAL FIX: Force cache busting v=2025101808

API diagnosis confirms backend works perfectly:
✅ API returns: productName='Mineral Water', categoryName='Frozen'
✅ API returns: store_name='Justin Groceries', final_price=4.99

Issue: Frontend caching prevents updated normalization code from loading
Solution: Force complete cache refresh with new version

Cache busting: v=2025101807 → v=2025101808"

git push origin main

echo ""
echo "🚀 IMMEDIATE EC2 DEPLOYMENT:"
echo "============================="
echo ""
echo "# 1. Pull and force rebuild (NO CACHE!)"
echo "git pull origin main"
echo "docker-compose -f docker-compose.prod.yml down"
echo "docker-compose -f docker-compose.prod.yml build --no-cache web"
echo "docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "# 2. Clear nginx cache (if any)"
echo "docker-compose -f docker-compose.prod.yml exec web nginx -s reload"
echo ""
echo "# 3. Verify deployment"
echo "curl -I https://ursaviour.com/js/product_page.js?v=2025101808"
echo ""
echo "🎯 EXPECTED RESULTS:"
echo "==================="
echo "After deployment, products should immediately show:"
echo "✅ Names: 'Mineral Water', 'Lettuce', 'Custard' (not 'Unknown Product')"
echo "✅ Categories: 'Frozen', 'Fruit', 'Meat' (not 'Uncategorized')"
echo "✅ Prices: \$4.99, \$8.09, \$8.12 (not \$0.00)"
echo ""
echo "💡 If still broken after deployment:"
echo "- Clear browser cache completely (Ctrl+Shift+Delete)"
echo "- Try incognito/private browsing mode"
echo "- Check browser console for JavaScript errors"