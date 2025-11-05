#!/bin/bash

# Complete UrSaviour EC2 Deployment Script
echo "🚀 UrSaviour Complete EC2 Deployment"

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

# Check if running on EC2
if [ ! -f /sys/hypervisor/uuid ] || [ "$(head -c 3 /sys/hypervisor/uuid)" != "ec2" ]; then
    log_warn "This doesn't appear to be an EC2 instance, but continuing anyway..."
fi

log_step "1/8 - Setting up MySQL..."
if [ -f setup-ec2-mysql.sh ]; then
    ./setup-ec2-mysql.sh
    if [ $? -ne 0 ]; then
        log_error "MySQL setup failed"
        exit 1
    fi
else
    log_error "setup-ec2-mysql.sh not found!"
    exit 1
fi

log_step "2/8 - Installing nginx..."
if command -v apt-get &> /dev/null; then
    sudo apt update
    sudo apt install -y nginx
elif command -v yum &> /dev/null; then
    sudo yum install -y nginx
else
    log_error "Could not install nginx"
    exit 1
fi

log_step "3/8 - Setting up web directory..."
sudo mkdir -p /var/www/ursaviour
sudo cp -r frontend /var/www/ursaviour/
sudo chown -R www-data:www-data /var/www/ursaviour 2>/dev/null || sudo chown -R nginx:nginx /var/www/ursaviour

log_step "4/8 - Configuring nginx..."
sudo cp nginx-ec2.conf /etc/nginx/sites-available/ursaviour 2>/dev/null || sudo cp nginx-ec2.conf /etc/nginx/conf.d/ursaviour.conf

# Enable site for Ubuntu/Debian
if [ -d /etc/nginx/sites-enabled ]; then
    sudo ln -sf /etc/nginx/sites-available/ursaviour /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
fi

# Test nginx configuration
sudo nginx -t
if [ $? -ne 0 ]; then
    log_error "nginx configuration test failed"
    exit 1
fi

log_step "5/8 - Starting nginx..."
sudo systemctl enable nginx
sudo systemctl restart nginx

log_step "6/8 - Setting up systemd service for backend..."
sudo tee /etc/systemd/system/ursaviour-backend.service > /dev/null << EOF
[Unit]
Description=UrSaviour FastAPI Backend
After=network.target mysql.service
Wants=mysql.service

[Service]
Type=exec
User=$USER
WorkingDirectory=$PWD/backend
Environment=PATH=$PWD/backend:/home/$USER/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

log_step "7/8 - Starting backend service..."
sudo systemctl daemon-reload
sudo systemctl enable ursaviour-backend
sudo systemctl start ursaviour-backend

# Wait a moment for service to start
sleep 3

# Check service status
if systemctl is-active --quiet ursaviour-backend; then
    log_info "✅ Backend service started successfully"
else
    log_error "❌ Backend service failed to start"
    sudo systemctl status ursaviour-backend
    exit 1
fi

log_step "8/8 - Final checks..."

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")

# Test backend
if curl -s "http://localhost:8000/docs" > /dev/null; then
    log_info "✅ Backend is responding"
else
    log_error "❌ Backend is not responding"
fi

# Test nginx
if curl -s "http://localhost/" > /dev/null; then
    log_info "✅ Frontend is responding"
else
    log_error "❌ Frontend is not responding"
fi

log_info ""
log_info "🎉 UrSaviour deployment completed!"
log_info ""
log_info "📋 Access Information:"
log_info "   Frontend: http://$PUBLIC_IP"
log_info "   Backend API: http://$PUBLIC_IP:8000"
log_info "   API Documentation: http://$PUBLIC_IP:8000/docs"
log_info ""
log_info "🔧 Management Commands:"
log_info "   Check backend status: sudo systemctl status ursaviour-backend"
log_info "   Restart backend: sudo systemctl restart ursaviour-backend"
log_info "   Check backend logs: sudo journalctl -u ursaviour-backend -f"
log_info "   Check nginx status: sudo systemctl status nginx"
log_info "   Check nginx logs: sudo tail -f /var/log/nginx/error.log"
log_info ""
log_warn "⚠️  Security Note:"
log_info "   Don't forget to configure your EC2 security group to allow:"
log_info "   - HTTP (port 80) from 0.0.0.0/0"
log_info "   - HTTPS (port 443) from 0.0.0.0/0 (for SSL later)"