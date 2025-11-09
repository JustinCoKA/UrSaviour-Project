#!/bin/bash

# ========================================
# Start Local Development with AWS RDS
# ========================================
# This script starts the backend and frontend locally
# while connecting to AWS RDS database (no EC2 needed)

set -e  # Exit on error

echo "🚀 Starting UrSaviour Local Development (AWS RDS)"
echo "=================================================="

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env not found"
    echo "Please copy backend/.env.local.example to backend/.env"
    echo "Then update YOUR_RDS_PASSWORD with the actual password"
    exit 1
fi

# Check if DATABASE_URL contains AWS RDS
if ! grep -q "ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com" backend/.env | grep -v "^#"; then
    echo "⚠️  Warning: AWS RDS URL is commented out in .env"
    echo "Please uncomment the AWS RDS DATABASE_URL line"
    echo "Current active DATABASE_URL:"
    grep "^DATABASE_URL=" backend/.env || echo "  (none found)"
    exit 1
fi

# Check if password is still placeholder
if grep -q "YOUR_RDS_PASSWORD" backend/.env | grep -v "^#"; then
    echo "❌ Error: Please replace YOUR_RDS_PASSWORD in backend/.env"
    echo "Ask team lead for the actual AWS RDS password"
    exit 1
fi

echo ""
echo "📦 Step 1: Installing backend dependencies..."
cd backend
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

echo ""
echo "🗄️  Step 2: Running database migrations..."
alembic upgrade head
echo "✅ Database schema up to date"

echo ""
echo "🔧 Step 3: Starting backend server..."
echo "Backend will run at: http://localhost:8000"
echo "API Docs available at: http://localhost:8000/docs"
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

echo ""
echo "🌐 Step 4: Starting frontend server..."
echo "Frontend will run at: http://localhost:3001"
cd frontend
python3 -m http.server 3001 --directory src &
FRONTEND_PID=$!
cd ..

echo ""
echo "=================================================="
echo "✅ Local development environment is running!"
echo "=================================================="
echo ""
echo "📍 Access points:"
echo "  - Frontend:   http://localhost:3001"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs:    http://localhost:8000/docs"
echo "  - Database:    AWS RDS (ursaviour-db...)"
echo ""
echo "🔄 Database: Connected to AWS RDS"
echo "   - Same data as production"
echo "   - Shared with team members"
echo "   - No EC2 deployment needed"
echo ""
echo "🛑 To stop servers:"
echo "   Press Ctrl+C or run:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "💡 To switch to local MySQL:"
echo "   1. Edit backend/.env"
echo "   2. Comment AWS RDS line, uncomment local MySQL line"
echo "   3. Run: docker compose up -d mysql"
echo "   4. Restart this script"
echo ""

# Wait for user interrupt
wait
