#!/bin/bash

# UrSaviour EC2 Application Startup Script
echo "🚀 Starting UrSaviour on EC2"

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

# Check if MySQL is running
if ! systemctl is-active --quiet mysql; then
    log_error "MySQL is not running. Please start it with:"
    echo "sudo systemctl start mysql"
    exit 1
fi

log_info "✅ MySQL is running"

# Check if .env file exists
if [ ! -f .env ]; then
    log_error ".env file not found!"
    exit 1
fi

log_info "✅ .env file found"

# Install Python dependencies
log_info "Installing Python dependencies..."
cd backend
pip3 install --user -r requirements.txt

if [ $? -ne 0 ]; then
    log_error "Failed to install dependencies"
    exit 1
fi

log_info "✅ Dependencies installed"

# Test database connection
log_info "Testing database connection..."
python3 -c "
from app.db.session import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    log_error "Database connection test failed"
    exit 1
fi

# Create tables if needed
log_info "Creating database tables..."
python3 -c "
from app.db.models import base
from app.db.session import engine
base.Base.metadata.create_all(bind=engine)
print('✅ Database tables created/updated')
"

# Start the application
log_info "🚀 Starting FastAPI application..."
log_info "Access URLs:"
log_info "  - API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
log_info "  - Docs: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/docs"
log_info ""
log_warn "Press Ctrl+C to stop the application"
log_info ""

# Start with auto-reload for development
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload