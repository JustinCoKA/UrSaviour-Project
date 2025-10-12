#!/bin/bash
# Advanced Debugging Script for UrSaviour API Issues
# This script helps diagnose production deployment problems

echo "🔍 UrSaviour Production Diagnostic Tool"
echo "======================================"

# Function to print colored output
print_status() {
    if [ "$2" = "OK" ]; then
        echo "✅ $1: $2"
    elif [ "$2" = "FAIL" ]; then
        echo "❌ $1: $2"
    else
        echo "ℹ️ $1: $2"
    fi
}

# 1. Check Docker containers
echo ""
echo "1️⃣ Checking Docker Container Status..."
echo "--------------------------------"
if docker ps | grep -q "api"; then
    print_status "API Container" "OK"
else
    print_status "API Container" "FAIL"
fi

if docker ps | grep -q "web\|nginx"; then
    print_status "Web Container" "OK"
else
    print_status "Web Container" "FAIL"
fi

# Show all containers
echo ""
echo "All containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 2. Test API directly (port 8000)
echo ""
echo "2️⃣ Testing Direct API Access..."
echo "-----------------------------"
API_DIRECT=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)
if [ "$API_DIRECT" = "200" ]; then
    print_status "Direct API (port 8000)" "OK ($API_DIRECT)"
else
    print_status "Direct API (port 8000)" "FAIL ($API_DIRECT)"
fi

# Test API endpoints
API_PRODUCTS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/products/products 2>/dev/null)
if [ "$API_PRODUCTS" = "200" ]; then
    print_status "Products Endpoint (direct)" "OK ($API_PRODUCTS)"
else
    print_status "Products Endpoint (direct)" "FAIL ($API_PRODUCTS)"
fi

# 3. Test through Nginx proxy
echo ""
echo "3️⃣ Testing Nginx Proxy..."
echo "------------------------"
NGINX_API=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/v1/products/products 2>/dev/null)
if [ "$NGINX_API" = "200" ]; then
    print_status "Nginx Proxy to API" "OK ($NGINX_API)"
else
    print_status "Nginx Proxy to API" "FAIL ($NGINX_API)"
fi

# 4. Check nginx configuration in container
echo ""
echo "4️⃣ Checking Nginx Configuration..."
echo "---------------------------------"
if docker ps | grep -q "web\|nginx"; then
    WEB_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "web|nginx" | head -1)
    echo "Web container: $WEB_CONTAINER"
    
    # Check if our config is loaded
    if docker exec "$WEB_CONTAINER" test -f /etc/nginx/nginx.conf; then
        print_status "Nginx config file" "OK"
        echo ""
        echo "Nginx config content (first 20 lines):"
        docker exec "$WEB_CONTAINER" head -20 /etc/nginx/nginx.conf
    else
        print_status "Nginx config file" "FAIL"
    fi
    
    # Check nginx status
    if docker exec "$WEB_CONTAINER" nginx -t 2>/dev/null; then
        print_status "Nginx config syntax" "OK"
    else
        print_status "Nginx config syntax" "FAIL"
        echo "Nginx config test output:"
        docker exec "$WEB_CONTAINER" nginx -t
    fi
else
    print_status "Web container check" "FAIL - No web container found"
fi

# 5. Check environment variables
echo ""
echo "5️⃣ Checking Environment Variables..."
echo "----------------------------------"
if docker ps | grep -q "api"; then
    API_CONTAINER=$(docker ps --format "{{.Names}}" | grep "api" | head -1)
    echo "API container: $API_CONTAINER"
    
    # Check CORS setting
    CORS_SETTING=$(docker exec "$API_CONTAINER" printenv BACKEND_CORS_ORIGINS 2>/dev/null || echo "NOT_SET")
    print_status "CORS Origins" "$CORS_SETTING"
    
    # Check database connection
    DB_URL=$(docker exec "$API_CONTAINER" printenv DATABASE_URL 2>/dev/null || echo "NOT_SET")
    if [ "$DB_URL" != "NOT_SET" ]; then
        print_status "Database URL" "SET"
    else
        print_status "Database URL" "NOT_SET"
    fi
else
    print_status "API container check" "FAIL - No API container found"
fi

# 6. Check logs for errors
echo ""
echo "6️⃣ Recent Error Logs..."
echo "----------------------"
echo "API container logs (last 10 lines):"
if docker ps | grep -q "api"; then
    API_CONTAINER=$(docker ps --format "{{.Names}}" | grep "api" | head -1)
    docker logs --tail 10 "$API_CONTAINER"
else
    echo "No API container found"
fi

echo ""
echo "Web container logs (last 10 lines):"
if docker ps | grep -q "web\|nginx"; then
    WEB_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "web|nginx" | head -1)
    docker logs --tail 10 "$WEB_CONTAINER"
else
    echo "No web container found"
fi

# 7. Network connectivity test
echo ""
echo "7️⃣ Network Connectivity..."
echo "-------------------------"
if docker ps | grep -q "web" && docker ps | grep -q "api"; then
    WEB_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "web|nginx" | head -1)
    
    # Test if web container can reach API container
    if docker exec "$WEB_CONTAINER" nc -z api 8000 2>/dev/null; then
        print_status "Web -> API connectivity" "OK"
    else
        print_status "Web -> API connectivity" "FAIL"
    fi
fi

echo ""
echo "🔧 Quick Fix Commands:"
echo "====================="
echo "1. Restart all services:    docker-compose -f docker-compose.prod.yml restart"
echo "2. Rebuild and restart:     docker-compose -f docker-compose.prod.yml up --build -d"
echo "3. Check detailed logs:     docker-compose -f docker-compose.prod.yml logs -f"
echo "4. Shell into API:          docker exec -it \$(docker ps -q --filter name=api) /bin/bash"
echo "5. Shell into Web:          docker exec -it \$(docker ps -q --filter name=web) /bin/bash"

echo ""
echo "📋 Summary Complete - Check the results above for issues!"