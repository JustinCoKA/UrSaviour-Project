#!/bin/bash

echo "🔍 UrSaviour Database Diagnosis Script"
echo "======================================"
echo ""

# Method 1: Direct MySQL connection
echo "📋 Method 1: Direct MySQL Connection"
echo "-----------------------------------"
echo "# Connect to MySQL directly (if using RDS or external MySQL)"
echo "mysql -h <HOST> -u <USERNAME> -p<PASSWORD> <DATABASE_NAME>"
echo ""
echo "# Example queries to run:"
echo "USE ursaviour_db;"
echo "SHOW TABLES;"
echo "SELECT COUNT(*) as product_count FROM products;"
echo "SELECT COUNT(*) as store_count FROM stores;"
echo "SELECT COUNT(*) as base_price_count FROM store_base_prices;"
echo "SELECT COUNT(*) as offering_count FROM storeOfferings;"
echo ""
echo "SELECT productId, productName, categoryName FROM products LIMIT 3;"
echo "SELECT storeId, storeName FROM stores;"
echo "SELECT * FROM store_base_prices LIMIT 5;"
echo ""

# Method 2: Docker container MySQL access
echo "📋 Method 2: Docker Container MySQL Access"
echo "------------------------------------------"
echo "# If using MySQL in Docker container:"
echo "docker-compose -f docker-compose.prod.yml exec mysql mysql -u root -p"
echo ""
echo "# Or find MySQL container and connect:"
echo "docker ps | grep mysql"
echo "docker exec -it <mysql_container_name> mysql -u root -p"
echo ""

# Method 3: Python script for database diagnosis
echo "📋 Method 3: Python Database Diagnosis Script"
echo "---------------------------------------------"
echo "# Run this Python script on EC2:"
echo "python3 database_diagnosis.py"
echo ""