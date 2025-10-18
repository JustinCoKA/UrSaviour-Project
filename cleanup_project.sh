#!/bin/bash

echo "🧹 Project Cleanup: Removing test and debug files"
echo "================================================"

# Remove deployment and debug scripts (keeping only essential ones)
rm -f \
  aws-deploy.sh \
  critical_cache_fix.sh \
  database_connection_guide.sh \
  debug-deploy-guide.sh \
  deploy_definitive_solution.sh \
  deploy_foundational_v2.sh \
  deploy_multi_store_system.sh \
  deploy_nginx_proxy_fix.sh \
  deploy_products_fix.sh \
  deploy_store_pricing.sh \
  ec2_deployment_guide.sh \
  ec2_diagnosis_setup.sh \
  emergency_render_fix.sh \
  final_cache_fix.sh \
  fix_data_parsing.sh \
  fix_frontend_deployment.sh \
  load_data_ec2.sh \
  load_data.sh \
  ultimate_cache_fix.sh \
  update-deployment.sh

# Remove test/debug Python files
rm -f \
  api_diagnosis.py \
  database_diagnosis.py \
  fix_offerings.py \
  load_foundational_*.py \
  load_data_*.py \
  migration_store_base_prices.py \
  setup_foundational_definitive.py

# Remove debug HTML files
rm -f \
  frontend/src/debug.html \
  frontend/src/api-debug.html \
  frontend/src/api-test-debug.html \
  frontend/src/debug-analysis.html \
  frontend/src/live-debug.html

# Remove test components
rm -f frontend/src/components/test.html

echo "✅ Cleanup completed!"
echo ""
echo "📊 Essential files kept:"
echo "- docker-compose.prod.yml (production)"
echo "- docker-compose.yml (development)" 
echo "- deploy.sh (main deployment script)"
echo "- safe-deploy.sh (backup deployment)"
echo "- start-dev.sh (development server)"
echo ""
echo "🗑️ Removed files:"
echo "- All debug/test scripts"
echo "- Temporary Python files"
echo "- Debug HTML pages"
echo "- Test components"