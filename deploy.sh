#!/bin/bash
# UrSaviour Production Deployment Script
# Run this on your production server (EC2 instance)

set -e  # Exit on any error

echo "🚀 UrSaviour Production Deployment Starting..."

# =============================================
# STEP 1: Pre-deployment Checks
# =============================================

echo "📋 Step 1: Checking prerequisites..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed. Please log out and log back in to apply group changes."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed."
fi

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Installing Git..."
    sudo apt-get update && sudo apt-get install -y git
    echo "✅ Git installed."
fi

echo "✅ Prerequisites check completed."

# =============================================
# STEP 2: Clone/Update Repository  
# =============================================

echo "📥 Step 2: Setting up project repository..."

PROJECT_DIR="/opt/ursaviour"
if [ -d "$PROJECT_DIR" ]; then
    echo "🔄 Updating existing repository..."
    cd $PROJECT_DIR
    git pull origin main
else
    echo "📦 Cloning repository..."
    sudo mkdir -p /opt
    sudo git clone https://github.com/JustinCoKA/UrSaviour-Project.git $PROJECT_DIR
    sudo chown -R $USER:$USER $PROJECT_DIR
    cd $PROJECT_DIR
fi

echo "✅ Repository setup completed."

# =============================================
# STEP 3: Environment Configuration
# =============================================

echo "⚙️  Step 3: Setting up environment variables..."

if [ ! -f ".env" ]; then
    echo "📝 Creating production .env file..."
    cp .env.production .env
    
    echo "⚠️  IMPORTANT: Please update the following in .env file:"
    echo "   - DATABASE_URL (your RDS connection string)"
    echo "   - SECRET_KEY (generate a secure key)"  
    echo "   - BACKEND_CORS_ORIGINS (your domain)"
    echo "   - AWS credentials if using S3"
    echo ""
    echo "Press Enter when you have updated the .env file..."
    read -p ""
else
    echo "✅ .env file already exists."
fi

echo "✅ Environment configuration completed."

# =============================================
# STEP 4: Build and Start Services
# =============================================

echo "🏗️  Step 4: Building and starting Docker services..."

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Build and start services
echo "🏗️  Building containers..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Docker services started."

# =============================================
# STEP 5: Health Checks
# =============================================

echo "🔍 Step 5: Running health checks..."

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 30

# Check container status
echo "📊 Container status:"
docker-compose -f docker-compose.prod.yml ps

# Test API health endpoint
echo "🏥 Testing API health..."
for i in {1..10}; do
    if curl -f http://localhost:8000/health; then
        echo "✅ API health check passed!"
        break
    else
        echo "⏳ Attempt $i/10 - API not ready yet, waiting..."
        sleep 10
    fi
done

# Test web server
echo "🌐 Testing web server..."
if curl -f http://localhost:80; then
    echo "✅ Web server is running!"
else
    echo "❌ Web server health check failed!"
fi

# =============================================
# STEP 6: Display Final Status
# =============================================

echo "📊 Final deployment status:"
docker-compose -f docker-compose.prod.yml ps

echo "📋 Service URLs:"
echo "   - Web: http://$(curl -s ifconfig.me) (or your domain)"  
echo "   - API: http://$(curl -s ifconfig.me):8000"
echo "   - Health: http://$(curl -s ifconfig.me):8000/health"

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📝 Next steps:"
echo "1. Configure your domain DNS to point to this server"
echo "2. Set up SSL certificates (Let's Encrypt recommended)"  
echo "3. Configure firewall rules (ports 80, 443)"
echo "4. Set up monitoring and backups"

echo ""
echo "🔧 Troubleshooting:"
echo "   - View logs: docker-compose -f docker-compose.prod.yml logs"
echo "   - Restart services: docker-compose -f docker-compose.prod.yml restart"
echo "   - Check individual service: docker-compose -f docker-compose.prod.yml logs api"