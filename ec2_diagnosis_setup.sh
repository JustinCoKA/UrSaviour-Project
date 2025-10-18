#!/bin/bash

echo "🚀 EC2 Database & API Diagnosis Setup"
echo "======================================"
echo ""

# Deploy diagnosis scripts
echo "📤 Deploying diagnosis scripts to EC2..."
git add .
git commit -m "Add comprehensive database and API diagnosis scripts

- database_diagnosis.py: Direct database connection and data analysis
- api_diagnosis.py: API endpoint testing and response analysis
- database_connection_guide.sh: Manual connection instructions

Use these scripts on EC2 to identify the root cause of Unknown Product issue."

git push origin main

echo ""
echo "📋 EC2 EXECUTION INSTRUCTIONS"
echo "=============================="
echo ""
echo "1️⃣ SSH to EC2 and pull latest code:"
echo "   ssh -i your-key.pem ubuntu@your-ec2-ip"
echo "   cd /path/to/UrSaviour-Project"
echo "   git pull origin main"
echo ""
echo "2️⃣ Make scripts executable:"
echo "   chmod +x *.sh *.py"
echo ""
echo "3️⃣ Install Python dependencies (if needed):"
echo "   pip3 install sqlalchemy pymysql requests"
echo ""
echo "4️⃣ Run database diagnosis:"
echo "   python3 database_diagnosis.py"
echo ""
echo "5️⃣ Run API diagnosis:"
echo "   python3 api_diagnosis.py"
echo ""
echo "6️⃣ Alternative: Manual database connection:"
echo "   # Check what's running"
echo "   docker-compose -f docker-compose.prod.yml ps"
echo ""
echo "   # Connect to MySQL container"
echo "   docker-compose -f docker-compose.prod.yml exec mysql mysql -u root -p"
echo ""
echo "   # Or find container name and connect"
echo "   docker ps | grep mysql"
echo "   docker exec -it <mysql_container_name> mysql -u root -p"
echo ""
echo "7️⃣ Manual API testing:"
echo "   curl http://localhost:8000/api/health"
echo "   curl http://localhost:8000/api/v1/products/?limit=3 | jq '.'"
echo ""
echo "🎯 EXPECTED OUTPUTS:"
echo "==================="
echo "✅ Database diagnosis should show:"
echo "   - products: 100 records"
echo "   - stores: 4 records" 
echo "   - store_base_prices: 400 records"
echo "   - Sample product names, not 'Unknown Product'"
echo ""
echo "✅ API diagnosis should show:"
echo "   - Status: 200 for all endpoints"
echo "   - products array with real productName values"
echo "   - stores array with store_name and final_price"
echo ""
echo "🚨 If you see issues, copy the output and share it!"