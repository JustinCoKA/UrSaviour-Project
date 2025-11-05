#!/bin/bash

# Team Database Connection Test
echo "🔗 UrSaviour Team Database Connection Test"

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo ""
log_info "Testing connection to Mimi's local database..."
echo "   Host: 172.16.38.147"
echo "   Port: 3306"
echo "   User: ursaviouruser"
echo "   Database: ursaviour"
echo ""

# Test with Python
log_info "Testing Python connection..."
python3 << 'EOF'
import pymysql
import sys

try:
    connection = pymysql.connect(
        host='172.16.38.147',
        user='ursaviouruser',
        password='securepassword',
        database='ursaviour',
        port=3306,
        connect_timeout=10
    )
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT 'Connection successful!' as message, NOW() as current_time;")
        result = cursor.fetchone()
        print(f"✅ {result[0]} (Server time: {result[1]})")
        
        # Show existing users
        cursor.execute("SELECT COUNT(*) as user_count FROM user;")
        count = cursor.fetchone()
        print(f"📊 Database has {count[0]} users")
    
    connection.close()
    print("✅ Python connection test passed!")
    
except Exception as e:
    print(f"❌ Python connection failed: {e}")
    print("")
    print("💡 Troubleshooting tips:")
    print("   1. Make sure Mimi's computer is on the same network")
    print("   2. Check if Mimi's firewall is blocking port 3306")
    print("   3. Verify the IP address hasn't changed")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    log_info "🎉 Database connection successful!"
    echo ""
    log_info "Next steps:"
    echo "   1. Copy .env.teammate to .env:"
    echo "      cp .env.teammate .env"
    echo ""
    echo "   2. Install Python dependencies:"
    echo "      cd backend && pip install -r requirements.txt"
    echo ""
    echo "   3. Start the backend:"
    echo "      cd backend && python -m uvicorn app.main:app --reload --port 8001"
    echo ""
    echo "   4. Access the application:"
    echo "      http://localhost:8001/docs"
else
    echo ""
    log_error "Connection failed. Please contact Mimi for troubleshooting."
fi