#!/bin/bash

# 전체 데이터베이스 구조 업그레이드 및 배포 스크립트
# 사용법: ./deploy_multi_store_system.sh

set -e

echo "🚀 Starting UrSaviour Multi-Store System Deployment..."

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 1. Commit local changes
log_step "1. Commit and push local changes"
git add .
git status
read -p "Do you want to commit the changes? (y/N): " commit_confirm

if [[ $commit_confirm == "y" || $commit_confirm == "Y" ]]; then
    git commit -m "feat: Multi-store pricing system implementation

    - Add products_new.py with store-specific pricing API
    - Add foundational dataset loader script  
    - Update router to use new products API
    - Support 400 product-store combinations from CSV data
    
    Features:
    - Multi-store price comparison
    - Category and search filtering  
    - Price range filtering
    - Discount/sale filtering
    - Store-specific filtering
    - Detailed price analysis"
    
    git push origin main
    log_info "Changes have been pushed to GitHub."
else
    log_warn "Skipping commit. Please commit manually later."
fi

# 2. Database backup (Important!)
log_step "2. Create current database backup"
echo "⚠️  You should create a backup before modifying the production database."
echo "Execute the following commands on your EC2 server:"
echo ""
echo "# RDS 백업 생성 (AWS CLI 필요)"
echo "aws rds create-db-snapshot \\"
echo "  --db-snapshot-identifier ursaviour-backup-\$(date +%Y%m%d-%H%M%S) \\"
echo "  --db-instance-identifier your-rds-instance-name"
echo ""
echo "Or create MySQL dump:"
echo "mysqldump -h your-rds-endpoint -u admin -p ursaviour > backup_\$(date +%Y%m%d).sql"
echo ""

read -p "Is the backup completed? Do you want to continue? (y/N): " backup_confirm
if [[ $backup_confirm != "y" && $backup_confirm != "Y" ]]; then
    log_error "Please complete the backup first."
    exit 1
fi

# 3. Output EC2 deployment guide
log_step "3. EC2 Server Deployment Commands"
cat << 'EOF'

Now execute the following commands in order on your EC2 server:

🔑 1. Connect to EC2:
ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip

📁 2. Update project:
cd /opt/ursaviour
git pull origin main

💾 3. Load foundational data to database:
cd /opt/ursaviour
python3 load_foundational_data.py

🐳 4. Restart Docker services:
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache api
docker-compose -f docker-compose.prod.yml up -d

✅ 5. Check service status:
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs api

🔍 6. Test API:
curl http://localhost:8000/api/v1/products/health
curl http://localhost:8000/api/v1/products/ | jq '.total_count'

EOF

# 4. Local testing suggestion
log_step "4. Local Testing"
echo ""
log_info "You can test locally first:"
echo ""
echo "# Load data to local database (optional)"
echo "python3 load_foundational_data.py"
echo ""
echo "# Run local backend server"  
echo "cd backend"
echo "python -m uvicorn app.main:app --reload --port 8000"
echo ""
echo "# Check in browser"
echo "http://localhost:8000/api/v1/products/"
echo "http://localhost:8000/docs"
echo ""

# 5. Expected results guide
log_step "5. Expected Results"
cat << 'EOF'

🎉 Expected results after deployment completion:

✅ API response example:
{
  "products": [
    {
      "productId": "P0001",
      "productName": "Mineral Water", 
      "categoryName": "Frozen",
      "stores": [
        {
          "store_id": 3,
          "store_name": "Austin Fresh",
          "final_price": 11.73,
          "original_price": 11.73,
          "discount_percentage": 0
        },
        {
          "store_id": 1,
          "store_name": "Justin Groceries", 
          "final_price": 11.94,
          "original_price": 11.94,
          "discount_percentage": 0
        }
      ],
      "lowest_price": 11.73,
      "best_deal": {
        "store_name": "Austin Fresh",
        "final_price": 11.73
      }
    }
  ],
  "total_count": 100
}

📊 Data Overview:
- 100 products
- 4 stores (Justin Groceries, Mio Mart, Austin Fresh, Aadarsh Deals)  
- 400 product-store price combinations
- Real-time price comparison and lowest price display

🌟 New Features:
- Multi-store price comparison
- Category/search filtering
- Price range filtering  
- Sale/discount filtering
- Store-specific filtering
- Detailed price analysis

EOF

# 6. Troubleshooting guide
log_step "6. Troubleshooting Guide"
cat << 'EOF'

🚨 Troubleshooting Solutions:

1️⃣ Data loading failure:
- Check Python path: export PYTHONPATH=/opt/ursaviour:$PYTHONPATH
- Verify database connection: mysql -h your-rds-endpoint -u admin -p
- Check table existence: SHOW TABLES;

2️⃣ API response errors:
- Check logs: docker-compose -f docker-compose.prod.yml logs api
- Check container status: docker ps -a
- Verify database connection

3️⃣ Frontend display errors:
- Check browser developer tools network tab
- Verify API response structure matches frontend expectations
- Check CORS settings

4️⃣ Recovery methods:
- Rollback with backup: mysql -h endpoint -u admin -p < backup_file.sql
- Recover to previous code: git checkout previous-commit-hash
- Rebuild containers: docker-compose -f docker-compose.prod.yml build --no-cache

EOF

log_info "Deployment guide generation completed! 📋"
log_warn "Please execute the above commands in order on your EC2 server."

echo ""
echo "🚀 Happy Deployment! 🎉"