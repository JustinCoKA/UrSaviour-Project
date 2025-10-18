#!/bin/bash

echo "🚨 EMERGENCY FIX: Complete Rendering Failure"
echo "============================================"
echo ""

git add .
git commit -m "EMERGENCY FIX: Complete rendering failure debug

CRITICAL ISSUE: Products page shows no products at all
- Live debug works perfectly but products page completely broken
- Suspect: Dynamic script loading caused JavaScript execution failure

FIXES:
1. Revert to static script loading with new cache version
2. Add emergency debug logging to render() function  
3. Add fallback error display if no products render
4. Add 3-second delayed check for empty products

This will show exactly where rendering fails."

git push origin main

echo ""
echo "🚀 IMMEDIATE EC2 DEPLOYMENT:"
echo "============================="
echo ""
echo "git pull origin main"
echo "docker-compose -f docker-compose.prod.yml down"
echo "docker-compose -f docker-compose.prod.yml build --no-cache web"
echo "docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "🔍 DEBUGGING STEPS:"
echo "=================="
echo "1. Open: https://ursaviour.com/products.html"
echo "2. Open Console (F12)"
echo "3. Look for these messages:"
echo "   - '🚀 PRODUCTS PAGE SCRIPT LOADED!'"
echo "   - '🎯 [Render] EMERGENCY DEBUG'"
echo "   - Any red error messages"
echo ""
echo "4. If no products appear, emergency fallback will show:"
echo "   - Total PRODUCTS count"
echo "   - Filtered data count"
echo "   - Current filter settings"
echo ""
echo "💡 This will reveal the exact failure point!"