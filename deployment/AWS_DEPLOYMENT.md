# 🚀 AWS/EC2 Production Deployment Guide

This guide will help you deploy the UrSaviour application to AWS EC2 with RDS database.

## 📋 Prerequisites

### AWS Resources Required
- **EC2 Instance** (t3.medium or larger recommended)
- **RDS MySQL Instance** (db.t3.micro for testing, db.t3.small+ for production)
- **S3 Bucket** for file storage and ETL processing
- **ElastiCache Redis** (optional, for caching)
- **Route 53** for DNS (optional)
- **CloudFront** for CDN (optional)

### Local Requirements
- Docker & Docker Compose
- AWS CLI configured
- SSH access to EC2 instance

## 🔧 Step 1: AWS Infrastructure Setup

### 1.1 Create RDS MySQL Database
```bash
# Create RDS MySQL instance
aws rds create-db-instance \
    --db-instance-identifier ursaviour-prod \
    --db-instance-class db.t3.small \
    --engine mysql \
    --engine-version 8.0 \
    --master-username admin \
    --master-user-password 'YourSecurePassword123!' \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --db-subnet-group-name your-db-subnet-group \
    --backup-retention-period 7 \
    --multi-az \
    --storage-encrypted
```

### 1.2 Create S3 Bucket
```bash
# Create S3 bucket for file storage
aws s3 mb s3://ursaviour-pamphlets-prod --region ap-southeast-2

# Set bucket policy for Lambda access (optional)
aws s3api put-bucket-policy --bucket ursaviour-pamphlets-prod --policy file://s3-bucket-policy.json
```

### 1.3 Create EC2 Instance
```bash
# Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0abcdef1234567890 \
    --count 1 \
    --instance-type t3.medium \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx \
    --subnet-id subnet-xxxxxxxxx \
    --user-data file://ec2-user-data.sh
```

## 🐳 Step 2: EC2 Server Setup

### 2.1 Connect to EC2 and Install Docker
```bash
# SSH to EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# Install additional tools
sudo apt install nginx certbot python3-certbot-nginx -y
```

### 2.2 Clone and Configure Application
```bash
# Clone repository
git clone https://github.com/JustinCoKA/UrSaviour-Project.git
cd UrSaviour-Project

# Copy production environment file
cp .env.production .env

# Edit environment variables
nano .env
```

## ⚙️ Step 3: Environment Configuration

### 3.1 Configure Database Connection
Edit `.env` file with your RDS details:
```bash
DATABASE_URL=mysql://admin:YourSecurePassword123!@ursaviour-prod.cluster-xxxx.ap-southeast-2.rds.amazonaws.com:3306/ursaviour?charset=utf8mb4&ssl_mode=REQUIRED
```

### 3.2 Configure CORS and Domain
```bash
# Replace with your actual domain
BACKEND_CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
```

### 3.3 Configure AWS Credentials
```bash
# Add AWS credentials for S3 access
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-southeast-2
S3_BUCKET_NAME=ursaviour-pamphlets-prod
```

## 🚀 Step 4: Deploy Application

### 4.1 Build and Start Services
```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d --build

# Check service status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 4.2 Initialize Database
```bash
# Run database migrations
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# Load initial data (optional)
docker-compose -f docker-compose.prod.yml exec api python /app/scripts/load_initial_data.py
```

### 4.3 Configure Nginx (if not using container nginx)
```bash
# Copy nginx configuration
sudo cp deployment/nginx.conf /etc/nginx/sites-available/ursaviour
sudo ln -s /etc/nginx/sites-available/ursaviour /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## 🔒 Step 5: SSL Certificate Setup

### 5.1 Install SSL Certificate with Certbot
```bash
# Install SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### 5.2 Configure SSL in nginx (manual method)
```bash
# Edit nginx configuration to include SSL
sudo nano /etc/nginx/sites-available/ursaviour

# Add SSL configuration:
# listen 443 ssl http2;
# ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
```

## 🔍 Step 6: Health Checks and Monitoring

### 6.1 Verify Services
```bash
# Check application health
curl http://localhost:8000/health
curl http://localhost:8000/ready

# Check frontend
curl http://localhost/

# Check API through nginx
curl http://localhost/api/v1/products/products
```

### 6.2 Monitor Application
```bash
# Monitor docker containers
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f web

# Monitor system resources
htop
df -h
```

## 🔧 Step 7: Common Troubleshooting

### Database Connection Issues
```bash
# Test database connection from EC2
mysql -h ursaviour-prod.cluster-xxxx.ap-southeast-2.rds.amazonaws.com -u admin -p

# Check security groups allow:
# - EC2 to RDS on port 3306
# - Internet to EC2 on ports 80, 443
# - Internet to EC2 on port 22 (SSH) from your IP only
```

### CORS Issues
```bash
# Check that BACKEND_CORS_ORIGINS includes your domain
# Restart API service after changing CORS settings
docker-compose -f docker-compose.prod.yml restart api
```

### 404 Errors on API Endpoints
```bash
# Check nginx configuration routes /api/ to backend
# Verify backend is running and healthy
curl http://localhost:8000/health

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

## 📊 Step 8: Performance Optimization

### 8.1 Enable Caching
```bash
# Configure Redis for caching
REDIS_URL=redis://your-elasticache-endpoint.cache.amazonaws.com:6379/0
```

### 8.2 Configure CloudFront (Optional)
- Create CloudFront distribution
- Point to your domain
- Configure caching for static assets
- Update CORS settings to include CloudFront domain

### 8.3 Database Optimization
```sql
-- Add indexes for better performance
ALTER TABLE products ADD INDEX idx_category (category);
ALTER TABLE products ADD INDEX idx_name (name);
ALTER TABLE watchlist ADD INDEX idx_user_product (user_id, product_id);
```

## 🔄 Step 9: Backup and Maintenance

### 9.1 Database Backups
```bash
# Manual backup
mysqldump -h your-rds-endpoint -u admin -p ursaviour > backup_$(date +%Y%m%d).sql

# Automated backups are enabled by default on RDS
```

### 9.2 Log Rotation
```bash
# Configure log rotation
sudo nano /etc/logrotate.d/ursaviour

# Add:
# /var/log/ursaviour/*.log {
#     daily
#     missingok
#     rotate 14
#     compress
#     notifempty
#     create 644 root root
# }
```

## 🚨 Emergency Procedures

### Service Recovery
```bash
# Restart all services
docker-compose -f docker-compose.prod.yml restart

# Rebuild if code changed
docker-compose -f docker-compose.prod.yml up -d --build

# Check service health
docker-compose -f docker-compose.prod.yml exec api curl http://localhost:8000/health
```

### Rollback Deployment
```bash
# Rollback to previous version
git checkout previous-stable-tag
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 📞 Support

For deployment issues:
1. Check application logs: `docker-compose logs`
2. Check nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Check system resources: `htop`, `df -h`
4. Verify AWS resources in AWS Console

## 🔗 Useful Commands

```bash
# View all containers
docker ps -a

# View container logs
docker logs container_name

# Execute commands in container
docker exec -it container_name /bin/bash

# Monitor resources
docker stats

# Clean up unused containers/images
docker system prune -a
```