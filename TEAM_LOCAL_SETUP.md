# 🚀 Local Development Setup Guide for Team Members

## Quick Start (3 Steps)

```bash
# 1. Clone and setup
git clone https://github.com/JustinCoKA/UrSaviour-Project.git
cd UrSaviour-Project

# 2. Choose your database setup (see options below)
cp backend/.env.local.example backend/.env
# Edit backend/.env and uncomment your preferred database option

# 3. Start development
docker-compose up -d mysql     # If using local MySQL
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && python3 -m http.server 3001 --directory src
```

---

## 📊 Database Options

### Option 1: AWS RDS (Team Shared Database) - RECOMMENDED

**✅ Advantages:**
- Same data across all team members
- No need to sync data
- Same as production environment
- Always up-to-date with latest data

**❌ Requirements:**
- Internet connection required
- Need VPN or IP whitelisting in AWS
- Slightly slower than local (network latency)

**Setup:**
```bash
# 1. Get AWS RDS password from team lead (Justin)
# 2. Edit backend/.env:
DATABASE_URL=mysql+pymysql://admin:YOUR_PASSWORD@ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com:3306/ursaviourDb

# 3. Test connection:
mysql -h ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com -u admin -p
```

**AWS Security Group Setup (Ask Justin to add your IP):**
```
Your IP: Visit https://whatismyipaddress.com/
Send to Justin: "Please add my IP: XXX.XXX.XXX.XXX to RDS security group"
```

---

### Option 2: Local MySQL (Docker) - FOR OFFLINE WORK

**✅ Advantages:**
- Works offline
- Fast (no network latency)
- Independent environment
- No conflicts with other team members

**❌ Requirements:**
- Need to seed initial data
- Data not synced with team
- Docker required

**Setup:**
```bash
# 1. Start MySQL container
docker-compose up -d mysql

# 2. Edit backend/.env:
DATABASE_URL=mysql+pymysql://root:rootpassword@localhost:3306/ursaviourDb

# 3. Run migrations:
cd backend
alembic upgrade head

# 4. Seed sample data:
python seed_data.py  # (Create if needed)
```

---

## 🛠️ Complete Setup Instructions

### Prerequisites

```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check Docker (if using local MySQL)
docker --version
docker-compose --version

# Check MySQL client (optional, for testing)
mysql --version
```

### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.local.example .env
nano .env  # Edit with your database choice

# 5. Run database migrations
alembic upgrade head

# 6. Start backend server
uvicorn app.main:app --reload --port 8000
```

**Backend should now be running at:** http://localhost:8000

**Check API docs:** http://localhost:8000/docs

---

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Start static file server
python3 -m http.server 3001 --directory src

# Alternative using Node.js:
# npx http-server src -p 3001 -c-1
```

**Frontend should now be running at:** http://localhost:3001

---

## 🔍 Testing Your Setup

### 1. Test Backend Health

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}
```

### 2. Test Database Connection

```bash
# Check database
curl http://localhost:8000/ready

# Expected response:
# {"ready":true}
```

### 3. Test Products API

```bash
# Get products
curl http://localhost:8000/api/v1/products/

# Expected: JSON array of products
```

### 4. Test Frontend

Open browser:
- http://localhost:3001/index.html
- http://localhost:3001/products.html

Check browser console (F12) - should see:
```
[DEBUG] Local mode - using local backend
[Products] Fetching from: http://localhost:8000/api/v1/products/
```

---

## 🐛 Troubleshooting

### Problem: Backend can't connect to database

**If using AWS RDS:**
```bash
# Test connection manually
mysql -h ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com -u admin -p

# If fails: Ask Justin to add your IP to security group
```

**If using Local MySQL:**
```bash
# Check MySQL is running
docker-compose ps

# Restart MySQL
docker-compose restart mysql

# Check logs
docker-compose logs mysql
```

---

### Problem: CORS errors in browser

**Solution:** Check backend CORS settings in `backend/.env`:
```bash
CORS_ORIGINS=http://localhost:3001,http://localhost:3000,http://127.0.0.1:3001
```

Restart backend after changing.

---

### Problem: Frontend shows "No products"

**Check:**
1. Backend is running: http://localhost:8000/health
2. Database has data:
   ```bash
   # For AWS RDS:
   mysql -h ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com -u admin -p
   USE ursaviourDb;
   SELECT COUNT(*) FROM products;
   
   # For Local:
   docker exec -it ursaviour-mysql mysql -uroot -prootpassword
   USE ursaviourDb;
   SELECT COUNT(*) FROM products;
   ```
3. API returns data: http://localhost:8000/api/v1/products/

---

### Problem: "Module not found" errors

```bash
# Reinstall dependencies
cd backend
pip install --upgrade -r requirements.txt

# Or recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📋 Daily Development Workflow

```bash
# Morning - Start development
cd UrSaviour-Project

# Option A: Using AWS RDS (most common)
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
cd ../frontend && python3 -m http.server 3001 --directory src &

# Option B: Using Local MySQL
docker-compose up -d mysql
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
cd ../frontend && python3 -m http.server 3001 --directory src &

# Work on your tasks...

# Evening - Stop development
pkill -f uvicorn
pkill -f http.server
docker-compose down  # If using local MySQL
```

---

## 🔄 Switching Between Database Options

### From AWS RDS to Local MySQL:

```bash
# 1. Start local MySQL
docker-compose up -d mysql

# 2. Change backend/.env:
DATABASE_URL=mysql+pymysql://root:rootpassword@localhost:3306/ursaviourDb

# 3. Restart backend
pkill -f uvicorn
cd backend
uvicorn app.main:app --reload --port 8000
```

### From Local MySQL to AWS RDS:

```bash
# 1. Change backend/.env:
DATABASE_URL=mysql+pymysql://admin:PASSWORD@ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com:3306/ursaviourDb

# 2. Restart backend
pkill -f uvicorn
cd backend
uvicorn app.main:app --reload --port 8000

# 3. Stop local MySQL (optional)
docker-compose down mysql
```

---

## 🤝 Team Collaboration Tips

1. **Commit your changes frequently**
   ```bash
   git add .
   git commit -m "feat: add product filter"
   git push origin your-branch
   ```

2. **Pull latest changes daily**
   ```bash
   git pull origin main
   ```

3. **Don't commit `.env` file**
   - It's in .gitignore
   - Keep passwords private
   - Each team member has their own `.env`

4. **Share database schema changes**
   - Create Alembic migrations
   - Commit migration files
   - Team members run: `alembic upgrade head`

5. **Communication**
   - AWS RDS: Coordinate data changes
   - Local MySQL: Independent, no coordination needed

---

## 📞 Get Help

**Contact:**
- Justin (Project Lead) - AWS RDS access, deployment
- Austin - Frontend, AI Agent
- Mio - Auth System, Login
- Aadarsh - Watchlist, Admin

**Resources:**
- Project README: `README.md`
- API Docs: http://localhost:8000/docs
- GitHub Issues: https://github.com/JustinCoKA/UrSaviour-Project/issues

---

## ✅ Setup Checklist

- [ ] Git repository cloned
- [ ] Python 3.9+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database option chosen (AWS RDS or Local MySQL)
- [ ] `.env` file configured
- [ ] Database migrations run (`alembic upgrade head`)
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Products page loads correctly
- [ ] Browser console shows no errors

---

**Ready to develop! 🎉**
