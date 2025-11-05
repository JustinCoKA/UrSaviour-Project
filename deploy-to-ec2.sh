#!/bin/bash

# UrSaviour EC2 Remote Deployment Script
# Usage: ./deploy-to-ec2.sh

EC2_IP="3.27.159.7"
PEM_FILE="ur.pem"
EC2_USER="ubuntu"  # or "ec2-user" for Amazon Linux

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

# Check if pem file exists
if [ ! -f "$PEM_FILE" ]; then
    log_error "PEM file '$PEM_FILE' not found!"
    echo ""
    log_info "Please follow these steps:"
    echo "1. Get 'ur.pem' file from your team leader"
    echo "2. Place it in the current directory: $(pwd)"
    echo "3. Set proper permissions: chmod 400 ur.pem"
    echo "4. Run this script again"
    exit 1
fi

# Check pem file permissions
PEM_PERMS=$(stat -f "%A" "$PEM_FILE" 2>/dev/null || stat -c "%a" "$PEM_FILE" 2>/dev/null)
if [ "$PEM_PERMS" != "400" ]; then
    log_warn "Setting correct permissions for PEM file..."
    chmod 400 "$PEM_FILE"
fi

log_step "1/5 - Testing EC2 connection..."

# Test SSH connection
ssh -i "$PEM_FILE" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$EC2_USER@$EC2_IP" "echo 'Connection successful!'" 

if [ $? -ne 0 ]; then
    log_error "Cannot connect to EC2 instance!"
    echo ""
    log_info "Troubleshooting steps:"
    echo "1. Check if EC2 instance is running"
    echo "2. Verify security group allows SSH (port 22) from your IP"
    echo "3. Confirm the correct username (ubuntu/ec2-user)"
    echo "4. Verify the PEM file is correct"
    exit 1
fi

log_info "✅ EC2 connection successful!"

log_step "2/5 - Checking if project exists on EC2..."

# Check if project directory exists
PROJECT_EXISTS=$(ssh -i "$PEM_FILE" "$EC2_USER@$EC2_IP" "[ -d 'UrSaviour-Project' ] && echo 'yes' || echo 'no'")

if [ "$PROJECT_EXISTS" = "no" ]; then
    log_info "Cloning project to EC2..."
    ssh -i "$PEM_FILE" "$EC2_USER@$EC2_IP" << 'EOF'
        git clone https://github.com/JustinCoKA/UrSaviour-Project.git
        cd UrSaviour-Project
        git checkout feature/connect-db
EOF
else
    log_info "Updating existing project..."
    ssh -i "$PEM_FILE" "$EC2_USER@$EC2_IP" << 'EOF'
        cd UrSaviour-Project
        git fetch origin
        git checkout feature/connect-db
        git pull origin feature/connect-db
EOF
fi

log_step "3/5 - Setting up permissions..."

ssh -i "$PEM_FILE" "$EC2_USER@$EC2_IP" << 'EOF'
    cd UrSaviour-Project
    chmod +x *.sh
EOF

log_step "4/5 - Running deployment..."

log_info "Starting full deployment on EC2..."
log_warn "This may take 5-10 minutes. Please be patient..."

ssh -i "$PEM_FILE" "$EC2_USER@$EC2_IP" << 'EOF'
    cd UrSaviour-Project
    ./deploy-ec2-full.sh
EOF

DEPLOY_STATUS=$?

log_step "5/5 - Checking deployment status..."

if [ $DEPLOY_STATUS -eq 0 ]; then
    log_info "🎉 Deployment completed successfully!"
    echo ""
    log_info "🌐 Access your application:"
    echo "   Frontend: http://$EC2_IP"
    echo "   Backend API: http://$EC2_IP:8000"
    echo "   API Docs: http://$EC2_IP:8000/docs"
    echo ""
    log_info "🔧 Management commands (run on EC2):"
    echo "   ssh -i $PEM_FILE $EC2_USER@$EC2_IP"
    echo "   sudo systemctl status ursaviour-backend"
    echo "   sudo journalctl -u ursaviour-backend -f"
else
    log_error "❌ Deployment failed!"
    echo ""
    log_info "To troubleshoot:"
    echo "1. Connect to EC2: ssh -i $PEM_FILE $EC2_USER@$EC2_IP"
    echo "2. Check logs: cd UrSaviour-Project && ./start-ec2-app.sh"
    echo "3. Manual setup: ./setup-ec2-mysql.sh"
fi

# Test the deployment
log_info "Testing deployment..."

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://$EC2_IP" || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
    log_info "✅ Frontend is responding!"
else
    log_warn "⚠️  Frontend test failed (HTTP $HTTP_STATUS)"
fi

API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://$EC2_IP:8000/docs" || echo "000")

if [ "$API_STATUS" = "200" ]; then
    log_info "✅ Backend API is responding!"
else
    log_warn "⚠️  Backend API test failed (HTTP $API_STATUS)"
fi

echo ""
log_info "🎯 Quick verification:"
echo "   curl http://$EC2_IP"
echo "   curl http://$EC2_IP:8000/docs"