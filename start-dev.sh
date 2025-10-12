#!/bin/bash
# Local Development Setup Script for UrSaviour (without Docker)

echo "🚀 Starting UrSaviour Local Development Environment"
echo "================================================="

# Kill any existing processes on the ports we need
echo "🧹 Cleaning up existing processes..."
pkill -f "python.*local_api_server.py" 2>/dev/null || true
pkill -f "python.*http.server 3001" 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Start API server in background
echo "🔧 Starting API server on port 8001..."
cd "$(dirname "$0")"
nohup ./.venv/bin/python local_api_server.py > nohup.out 2>&1 &
API_PID=$!

# Wait for API to start
sleep 3

# Test API
if curl -f http://localhost:8001/health 2>/dev/null > /dev/null; then
    echo "✅ API server started successfully on http://localhost:8001"
else
    echo "❌ Failed to start API server"
    exit 1
fi

# Start frontend server in background
echo "🌐 Starting frontend server on port 3001..."
cd frontend/src
nohup python3 -m http.server 3001 > ../../frontend_nohup.out 2>&1 &
FRONTEND_PID=$!
cd ../..

# Wait for frontend to start
sleep 2

# Test frontend
if curl -I http://localhost:3001 2>/dev/null | grep -q "200 OK"; then
    echo "✅ Frontend server started successfully on http://localhost:3001"
else
    echo "⚠️ Frontend server may not be ready yet, but continuing..."
fi

echo ""
echo "🎉 Development environment is ready!"
echo "=================================="
echo ""
echo "📱 Frontend: http://localhost:3001"
echo "🔧 API:      http://localhost:8001"
echo "📊 Products: http://localhost:3001/products.html"
echo ""
echo "📝 Process IDs:"
echo "   API:      $API_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo "🛑 To stop all services:"
echo "   pkill -f 'python.*local_api_server.py'"
echo "   pkill -f 'python.*http.server 3001'"
echo ""
echo "📋 Logs:"
echo "   API:      tail -f nohup.out"
echo "   Frontend: tail -f frontend_nohup.out"