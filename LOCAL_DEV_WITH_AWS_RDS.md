# 🏠 Local Development with AWS RDS Guide

## Overview
This setup allows you to run the **backend and frontend locally on your machine** (localhost) while connecting to the **AWS RDS database** - no EC2 deployment needed!

---

## ✨ What This Setup Does

```
Your Computer (localhost)
├── Backend (localhost:8000) ────┐
├── Frontend (localhost:3001) ───┤
                                 │
                                 └──→ AWS RDS Database (Cloud)
```

**Benefits:**
- ✅ Run everything locally (no EC2 needed)
- ✅ Connect to real AWS RDS database
- ✅ Same data as production
- ✅ Fast local development
- ✅ Easy to switch between AWS RDS and local MySQL
- ✅ No deployment required for testing

---

## 🚀 Quick Start (3 Steps)

### Step 1: Update AWS RDS Password
```bash
# Edit backend/.env and replace YOUR_RDS_PASSWORD
nano backend/.env

# Find this line and add the real password:
DATABASE_URL=mysql+pymysql://admin:YOUR_RDS_PASSWORD@ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com:3306/ursaviourDb
```

### Step 2: Make Sure You Have IP Access
Your IP needs to be whitelisted in AWS RDS Security Group. Ask team lead to add:
```
Your IP: Visit https://whatismyipaddress.com/
```

### Step 3: Run the Startup Script
```bash
./start-local-with-aws.sh
```

That's it! 🎉

---

## 📍 Access Points

Once running:
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: AWS RDS (automatic connection)

---

## 🔄 Switching Between AWS RDS and Local MySQL

### Currently Using: AWS RDS ✓

To switch to **Local MySQL**:
```bash
# 1. Edit backend/.env
nano backend/.env

# 2. Comment out AWS RDS line:
# DATABASE_URL=mysql+pymysql://admin:password@ursaviour-db...

# 3. Uncomment local MySQL line:
DATABASE_URL=mysql+pymysql://root:rootpassword@localhost:3306/ursaviourDb

# 4. Start local MySQL
docker compose up -d mysql

# 5. Restart backend
pkill -f uvicorn
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

To switch back to **AWS RDS**:
```bash
# 1. Edit backend/.env
nano backend/.env

# 2. Uncomment AWS RDS line:
DATABASE_URL=mysql+pymysql://admin:password@ursaviour-db...

# 3. Comment out local MySQL line:
# DATABASE_URL=mysql+pymysql://root:rootpassword@localhost:3306/ursaviourDb

# 4. Restart backend
pkill -f uvicorn
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

---

## 🛠️ Manual Setup (Alternative)

If you prefer to start services manually:

### Backend:
```bash
cd backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Run migrations (when schema changes)
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --port 8000
```

### Frontend:
```bash
# In a new terminal
cd frontend
python3 -m http.server 3001 --directory src
```

---

## 🧪 Testing Your Setup

### 1. Test Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### 2. Test Database Connection
```bash
curl http://localhost:8000/ready
# Expected: {"ready":true}
```

### 3. Test Products API
```bash
curl http://localhost:8000/api/v1/products/
# Expected: JSON array of products from AWS RDS
```

### 4. Test Frontend
Open browser: http://localhost:3001/products.html
- Should load products from AWS RDS
- Check browser console (F12) for any errors

---

## 🐛 Troubleshooting

### ❌ Error: Can't connect to AWS RDS
**Symptoms:** Connection timeout or refused
**Solutions:**
1. Check your internet connection
2. Verify your IP is whitelisted in AWS Security Group
3. Check AWS RDS password in backend/.env
4. Test connection manually:
```bash
mysql -h ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com -u admin -p
```

### ❌ Error: CORS issues in browser
**Symptoms:** Frontend can't call backend API
**Solutions:**
1. Check backend/.env has correct CORS settings:
```bash
CORS_ORIGINS=http://localhost:3001,http://localhost:3000,http://127.0.0.1:3001
```
2. Restart backend server
3. Clear browser cache (Cmd+Shift+R)

### ❌ Error: Port already in use
**Symptoms:** "Address already in use" error
**Solutions:**
```bash
# Find and kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Find and kill process on port 3001 (frontend)
lsof -ti:3001 | xargs kill -9

# Restart servers
./start-local-with-aws.sh
```

### ❌ Error: No products showing
**Symptoms:** Frontend loads but shows no products
**Solutions:**
1. Check backend is running: http://localhost:8000/health
2. Check API returns data: http://localhost:8000/api/v1/products/
3. Check browser console for errors (F12)
4. Verify AWS RDS has data:
```bash
mysql -h ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com -u admin -p
USE ursaviourDb;
SELECT COUNT(*) FROM products;
```

### ⚠️ Warning: Working offline
If you need to work without internet:
1. Switch to local MySQL (see "Switching" section above)
2. Your local database will be independent
3. Data won't sync with team until you switch back

---

## 🛑 Stopping Servers

### Option 1: Graceful Stop
Press `Ctrl+C` in the terminal where script is running

### Option 2: Kill Processes
```bash
# Stop backend
pkill -f uvicorn

# Stop frontend
pkill -f "http.server 3001"

# Or stop all Python processes (be careful!)
pkill -f python
```

### Option 3: Use Process IDs
If script shows PIDs:
```bash
kill <BACKEND_PID> <FRONTEND_PID>
```

---

## 📊 Development Workflow

### Daily Development:
```bash
# Morning - Start development
./start-local-with-aws.sh

# Work on your features...
# Backend auto-reloads on changes
# Frontend needs manual refresh

# Evening - Stop servers
Ctrl+C
```

### Making Changes:
- **Backend code**: Auto-reloads (thanks to `--reload` flag)
- **Frontend code**: Refresh browser (Cmd+R)
- **Database schema**: Run `alembic upgrade head` in backend directory
- **Dependencies**: Run `pip install -r requirements.txt` in backend directory

### Git Workflow:
```bash
# Pull latest changes
git pull origin main

# If requirements changed
cd backend && source venv/bin/activate
pip install -r requirements.txt

# If database schema changed
alembic upgrade head

# Make your changes and commit
git add .
git commit -m "feat: your feature"
git push origin your-branch
```

---

## 🤝 Team Collaboration

### With AWS RDS (Current Setup):
- ✅ Everyone sees the same data
- ✅ No need to sync databases
- ✅ Test with real production data
- ⚠️ Coordinate schema changes
- ⚠️ Need internet connection
- ⚠️ IP must be whitelisted

### With Local MySQL:
- ✅ Works offline
- ✅ Independent testing
- ✅ Fast local queries
- ❌ Data not shared with team
- ❌ Need to sync manually
- ❌ Different from production

---

## 📝 Environment File Reference

Your `backend/.env` should look like:
```bash
# Active: AWS RDS (for local dev with cloud database)
DATABASE_URL=mysql+pymysql://admin:REAL_PASSWORD@ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com:3306/ursaviourDb

# Alternative: Local MySQL (uncomment to switch)
# DATABASE_URL=mysql+pymysql://root:rootpassword@localhost:3306/ursaviourDb

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
ENVIRONMENT=local

# CORS (for local frontend)
CORS_ORIGINS=http://localhost:3001,http://localhost:3000,http://127.0.0.1:3001

# JWT
JWT_SECRET_KEY=local-dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

---

## 🔐 Security Notes

1. **Never commit .env file** - it's in .gitignore
2. **Keep AWS RDS password private**
3. **Don't share .env file publicly**
4. **Use different JWT secret in production**
5. **IP whitelist is for security** - don't open to 0.0.0.0/0

---

## 📞 Need Help?

**Before asking:**
- [ ] Checked troubleshooting section above
- [ ] Verified AWS RDS password is correct
- [ ] Confirmed IP is whitelisted
- [ ] Tested backend health endpoint
- [ ] Checked browser console for errors

**Contact:**
- Justin (Project Lead) - AWS access, RDS password
- Austin - Frontend issues
- Mio - Auth/Login issues
- Aadarsh - Watchlist features

**Resources:**
- API Documentation: http://localhost:8000/docs (when backend running)
- Team Setup Guide: `TEAM_LOCAL_SETUP.md`
- Database Connection Guide: `TEAM_DATABASE_CONNECTION_GUIDE.md`
- Project README: `README.md`

---

## ✅ Setup Checklist

Before first run:
- [ ] Git repository cloned
- [ ] Python 3.9+ installed
- [ ] AWS RDS password updated in backend/.env
- [ ] Your IP whitelisted in AWS Security Group
- [ ] Internet connection available

After running script:
- [ ] Backend starts without errors (localhost:8000)
- [ ] Frontend starts without errors (localhost:3001)
- [ ] API docs accessible (localhost:8000/docs)
- [ ] Products page loads (localhost:3001/products.html)
- [ ] No CORS errors in browser console
- [ ] Database queries work (test API endpoints)

---

**You're ready to develop! 🎉**

**Remember:** You're running locally but using AWS RDS database - best of both worlds!
