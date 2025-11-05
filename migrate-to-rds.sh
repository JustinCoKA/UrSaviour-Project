#!/bin/bash

# Data Migration from Local Docker to AWS RDS
echo "🔄 UrSaviour Data Migration: Local Docker → AWS RDS"

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

# Check if RDS endpoint is configured
if [ -z "$RDS_ENDPOINT" ]; then
    log_error "RDS_ENDPOINT environment variable not set!"
    echo ""
    echo "Please set the following environment variables:"
    echo "export RDS_ENDPOINT=your-rds-endpoint.region.rds.amazonaws.com"
    echo "export RDS_USERNAME=admin"
    echo "export RDS_PASSWORD=your-rds-password"
    echo "export RDS_DATABASE=ursaviour"
    exit 1
fi

log_step "1/4 - Creating database dump from local Docker MySQL..."

# Create dump from Docker MySQL
docker exec db mysqldump -u ursaviouruser -psecurepassword ursaviour > ursaviour_dump.sql

if [ $? -eq 0 ]; then
    log_info "✅ Local database dump created: ursaviour_dump.sql"
else
    log_error "❌ Failed to create database dump"
    exit 1
fi

log_step "2/4 - Testing RDS connection..."

# Test RDS connection
mysql -h "$RDS_ENDPOINT" -u "$RDS_USERNAME" -p"$RDS_PASSWORD" -e "SELECT 1;" 2>/dev/null

if [ $? -eq 0 ]; then
    log_info "✅ RDS connection successful"
else
    log_error "❌ RDS connection failed. Please check your credentials."
    exit 1
fi

log_step "3/4 - Creating database on RDS..."

# Create database on RDS
mysql -h "$RDS_ENDPOINT" -u "$RDS_USERNAME" -p"$RDS_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $RDS_DATABASE;"

log_step "4/4 - Importing data to RDS..."

# Import data to RDS
mysql -h "$RDS_ENDPOINT" -u "$RDS_USERNAME" -p"$RDS_PASSWORD" "$RDS_DATABASE" < ursaviour_dump.sql

if [ $? -eq 0 ]; then
    log_info "✅ Data migration completed successfully!"
    
    # Clean up
    rm ursaviour_dump.sql
    
    echo ""
    log_info "🎉 Migration Summary:"
    echo "   Source: Local Docker MySQL"
    echo "   Target: AWS RDS ($RDS_ENDPOINT)"
    echo "   Database: $RDS_DATABASE"
    echo ""
    log_info "📋 Team Configuration:"
    echo "   Update your .env file with:"
    echo "   DATABASE_URL=mysql+pymysql://$RDS_USERNAME:$RDS_PASSWORD@$RDS_ENDPOINT:3306/$RDS_DATABASE"
    
else
    log_error "❌ Data migration failed"
    exit 1
fi