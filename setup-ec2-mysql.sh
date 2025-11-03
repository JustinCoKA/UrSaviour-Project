#!/bin/bash

# UrSaviour EC2 MySQL Setup Script
echo "🚀 UrSaviour EC2 + MySQL Setup"

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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_error "Please don't run as root. Use sudo when needed."
    exit 1
fi

log_step "1/6 - Updating system packages..."

# Detect OS and install MySQL
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    log_info "Detected Ubuntu/Debian"
    
    sudo apt update
    sudo apt install -y mysql-server python3-pip python3-dev default-libmysqlclient-dev build-essential git
    
    # Start MySQL service
    sudo systemctl start mysql
    sudo systemctl enable mysql
    
elif command -v yum &> /dev/null; then
    # Amazon Linux 2/CentOS/RHEL
    log_info "Detected Amazon Linux/CentOS"
    
    # Install MySQL 8.0 repository
    sudo yum install -y https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm
    sudo yum install -y mysql-community-server python3-pip python3-devel mysql-devel gcc git
    
    # Start MySQL service
    sudo systemctl start mysqld
    sudo systemctl enable mysqld
    
    # Get temporary password for Amazon Linux
    if [ -f /var/log/mysqld.log ]; then
        temp_password=$(sudo grep 'temporary password' /var/log/mysqld.log | tail -1 | awk '{print $NF}')
        if [ ! -z "$temp_password" ]; then
            log_warn "MySQL temporary password: $temp_password"
            log_warn "You'll need this for the next step!"
        fi
    fi
    
else
    log_error "Unsupported operating system"
    exit 1
fi

log_step "2/6 - Installing Python dependencies..."

# Install Python MySQL connector
pip3 install --user pymysql mysql-connector-python python-dotenv

log_step "3/6 - Configuring MySQL..."

# Create a temporary MySQL script
cat > /tmp/mysql_setup.sql << 'EOF'
-- Create database
CREATE DATABASE IF NOT EXISTS ursaviour;

-- Create user (modify password as needed)
CREATE USER IF NOT EXISTS 'ursaviouruser'@'localhost' IDENTIFIED BY 'securepassword123!';

-- Grant privileges
GRANT ALL PRIVILEGES ON ursaviour.* TO 'ursaviouruser'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Show result
SHOW DATABASES;
SELECT User, Host FROM mysql.user WHERE User = 'ursaviouruser';
EOF

log_warn "Please enter MySQL root password when prompted:"
log_info "If this is a fresh MySQL installation, the password might be empty (just press Enter)"

# Execute MySQL setup
mysql -u root -p < /tmp/mysql_setup.sql

if [ $? -eq 0 ]; then
    log_info "✅ MySQL database setup completed successfully!"
else
    log_error "❌ MySQL setup failed. Please check the error above."
    exit 1
fi

# Clean up
rm /tmp/mysql_setup.sql

log_step "4/6 - Testing database connection..."

# Test connection
python3 << 'EOF'
import pymysql
import sys

try:
    connection = pymysql.connect(
        host='localhost',
        user='ursaviouruser',
        password='securepassword123!',
        database='ursaviour',
        port=3306
    )
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT 'Connection successful!' as message;")
        result = cursor.fetchone()
        print(f"✅ {result[0]}")
    
    connection.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    log_info "✅ Database connection test passed!"
else
    log_error "❌ Database connection test failed!"
    exit 1
fi

log_step "5/6 - Updating application configuration..."

# Update .env file for EC2
if [ -f .env ]; then
    # Comment out Docker database URL
    sed -i.bak 's/^DATABASE_URL=mysql+pymysql:\/\/ursaviouruser:securepassword@db:3306\/ursaviour/#&/' .env
    
    # Uncomment EC2 database URL
    sed -i 's/^# DATABASE_URL=mysql+pymysql:\/\/ursaviouruser:securepassword123!@localhost:3306\/ursaviour/DATABASE_URL=mysql+pymysql:\/\/ursaviouruser:securepassword123!@localhost:3306\/ursaviour/' .env
    
    log_info "Updated .env file for EC2 configuration"
else
    log_warn ".env file not found in current directory"
fi

log_step "6/6 - Final setup..."

log_info "🎉 EC2 + MySQL setup completed!"
echo ""
log_info "📋 Configuration Summary:"
echo "   Database Host: localhost"
echo "   Database Name: ursaviour"
echo "   Database User: ursaviouruser"
echo "   Database Password: securepassword123!"
echo ""
log_info "🚀 Next Steps:"
echo "   1. Make sure your .env file has the correct DATABASE_URL"
echo "   2. Install your Python application dependencies:"
echo "      pip3 install -r backend/requirements.txt"
echo "   3. Run database migrations if needed"
echo "   4. Start your FastAPI application:"
echo "      cd backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
log_info "🔧 Troubleshooting:"
echo "   - Check MySQL status: sudo systemctl status mysql"
echo "   - Check MySQL logs: sudo tail -f /var/log/mysql/error.log"
echo "   - Test connection: mysql -u ursaviouruser -p ursaviour"