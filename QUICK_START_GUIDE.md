# 🚀 Quick Start Guide - Run on Any Computer

## For New Team Members / New Computer Setup

### Prerequisites
- Python 3.9+ installed
- Git installed
- Internet connection (for AWS RDS)

---

## 🎯 Step-by-Step Setup (5 minutes)

### Step 1: Clone Repository
```bash
# Clone the project
git clone https://github.com/JustinCoKA/UrSaviour-Project.git
cd UrSaviour-Project

# Switch to the local development branch
git checkout feature/local-dev-setup
```

### Step 2: Configure Environment
```bash
# Copy the example environment file
cp backend/.env.local.example backend/.env

# Edit the file and add AWS RDS password
nano backend/.env
# or
code backend/.env
```

**Replace this line:**
```bash
DATABASE_URL=mysql+pymysql://admin:YOUR_RDS_PASSWORD@ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com:3306/ursaviourDb
```

**With:**
```bash
DATABASE_URL=mysql+pymysql://admin:Ursaviour2025@ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com:3306/ursaviourDb
```

### Step 3: Start Local Environment
```bash
# Make the startup script executable
chmod +x start-local-with-aws.sh

# Run the startup script
./start-local-with-aws.sh
```

**OR manually start services:**

```bash
# Terminal 1 - Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
python3 -m http.server 3001 --directory src
```

### Step 4: Access the Application
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 💻 How to Start/Stop Servers

### Start Servers (3 Options)

#### Option 1: Using Startup Script (Recommended)
```bash
./start-local-with-aws.sh
```

#### Option 2: Manual Start (Separate Terminals)
```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend  
cd frontend
python3 -m http.server 3001 --directory src
```

#### Option 3: Background Processes
```bash
# Start backend in background
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &

# Start frontend in background
cd frontend
python3 -m http.server 3001 --directory src &
```

### Stop Servers

#### Stop with Ctrl+C
- Press `Ctrl+C` in the terminal where servers are running

#### Kill Processes by Port
```bash
# Stop backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Stop frontend (port 3001)
lsof -ti:3001 | xargs kill -9

# Stop all at once
lsof -ti:8000,3001 | xargs kill -9
```

#### Stop All Python Processes (Be Careful!)
```bash
pkill -f uvicorn
pkill -f "http.server 3001"
```

---

## 🔄 Switch Between AWS RDS and Local MySQL

### Currently Using: AWS RDS ✓

### Switch to Local MySQL:

```bash
# 1. Edit backend/.env
nano backend/.env

# 2. Comment out AWS RDS line:
# DATABASE_URL=mysql+pymysql://admin:Ursaviour2025@ursaviour-db...

# 3. Uncomment local MySQL line:
DATABASE_URL=mysql+pymysql://root:rootpassword@localhost:3306/ursaviourDb

# 4. Start local MySQL
docker compose up -d mysql

# 5. Run database migrations
cd backend && source venv/bin/activate
alembic upgrade head

# 6. Restart backend
lsof -ti:8000 | xargs kill -9
uvicorn app.main:app --reload --port 8000
```

### Switch Back to AWS RDS:

```bash
# 1. Edit backend/.env
nano backend/.env

# 2. Uncomment AWS RDS line:
DATABASE_URL=mysql+pymysql://admin:Ursaviour2025@ursaviour-db...

# 3. Comment out local MySQL line:
# DATABASE_URL=mysql+pymysql://root:rootpassword@localhost:3306/ursaviourDb

# 4. Restart backend
lsof -ti:8000 | xargs kill -9
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

---

## 🖥️ Run on Different Computer (Same Steps)

### Any computer can run this setup by following the same steps:

1. **Clone the repository**
2. **Checkout the branch** (`feature/local-dev-setup`)
3. **Copy `.env.local.example` to `.env`**
4. **Add AWS RDS password** (Ursaviour2025)
5. **Run the startup script**

### Requirements for Each Computer:
- ✅ Python 3.9+
- ✅ Git
- ✅ Internet connection (for AWS RDS)
- ✅ Ports 8000 and 3001 available

### Network Requirements:
- **AWS RDS**: Each computer's IP must be whitelisted in AWS Security Group
- **Local MySQL**: No internet needed, but data is independent per computer

---

## 🔐 Security & IP Whitelisting

### Add New Computer IP to AWS RDS Security Group:

1. **Find your IP address:**
   ```bash
   curl https://ifconfig.me
   ```
   Or visit: https://whatismyipaddress.com/

2. **Ask project lead (Justin) to add IP to AWS RDS Security Group:**
   - Go to AWS Console → RDS → Security Groups
   - Select: `ursaviour-db-sg`
   - Edit Inbound Rules
   - Add Rule: MySQL/Aurora (3306) from `YOUR.IP.ADDRESS.HERE/32`

3. **Test connection:**
   ```bash
   mysql -h ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com -u admin -p
   # Password: Ursaviour2025
   ```

---

## 🧪 Verify Setup Works

### Test 1: Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

### Test 2: Database Connection
```bash
curl http://localhost:8000/ready
# Expected: {"ready":true}
```

### Test 3: Products API
```bash
curl http://localhost:8000/api/v1/products/ | python3 -m json.tool
# Expected: JSON array of products
```

### Test 4: Frontend
Open browser:
- http://localhost:3001/index.html
- http://localhost:3001/products.html
- Check browser console (F12) - no errors

---

## 🐛 Common Issues & Solutions

### Issue: "Port already in use"
```bash
# Kill process on port 8000 or 3001
lsof -ti:8000 | xargs kill -9
lsof -ti:3001 | xargs kill -9
```

### Issue: "Access denied" to AWS RDS
**Solution 1: Check password in `.env`**
```bash
# Make sure it's exactly: Ursaviour2025
nano backend/.env
```

**Solution 2: IP not whitelisted**
- Ask Justin to add your IP to AWS Security Group
- Find your IP: `curl https://ifconfig.me`

**Solution 3: Switch to local MySQL**
```bash
# Use local database instead
docker compose up -d mysql
# Edit .env to use local MySQL
```

### Issue: "Module not found"
```bash
# Reinstall dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Frontend shows no products
**Check:**
1. Backend running? → `curl http://localhost:8000/health`
2. Database connected? → Check backend terminal for errors
3. CORS enabled? → Check `backend/.env` has `CORS_ORIGINS`
4. Browser console? → Open F12 and check for errors

---

## 📊 Daily Development Workflow

### Morning - Start Work
```bash
cd UrSaviour-Project

# Pull latest changes
git pull origin feature/local-dev-setup

# Start servers
./start-local-with-aws.sh

# Or manually:
# Terminal 1: cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000
# Terminal 2: cd frontend && python3 -m http.server 3001 --directory src
```

### During Development
- **Backend changes**: Auto-reloads (no restart needed)
- **Frontend changes**: Refresh browser (Cmd+R or F5)
- **Environment changes**: Restart backend
- **Database schema changes**: Run `alembic upgrade head`

### Evening - End Work
```bash
# Stop servers
Ctrl+C

# Or kill processes
lsof -ti:8000,3001 | xargs kill -9

# Commit changes
git add .
git commit -m "feat: your changes"
git push origin feature/local-dev-setup
```

---

## 🤝 Team Collaboration

### Using AWS RDS (Recommended for Team):
- ✅ Everyone sees same data
- ✅ No data sync needed
- ✅ Real production data
- ⚠️ Need internet
- ⚠️ IP must be whitelisted

### Using Local MySQL (For Offline/Independent Work):
- ✅ Works offline
- ✅ Independent testing
- ✅ Fast queries
- ❌ Data not shared
- ❌ Need to manually sync

### Switch Between Databases:
Just edit one line in `backend/.env` and restart backend!

---

## 📝 Environment File Quick Reference

**AWS RDS (Default):**
```bash
DATABASE_URL=mysql+pymysql://admin:Ursaviour2025@ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com:3306/ursaviourDb
```

**Local MySQL:**
```bash
DATABASE_URL=mysql+pymysql://root:rootpassword@localhost:3306/ursaviourDb
```

---

## ✅ Setup Checklist

Before first run on new computer:
- [ ] Python 3.9+ installed (`python3 --version`)
- [ ] Git installed (`git --version`)
- [ ] Repository cloned
- [ ] Switched to `feature/local-dev-setup` branch
- [ ] Created `backend/.env` from example
- [ ] Added AWS RDS password to `.env`
- [ ] (If using AWS RDS) IP whitelisted in Security Group
- [ ] Ports 8000 and 3001 available

After running:
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] API docs accessible at localhost:8000/docs
- [ ] Frontend loads at localhost:3001
- [ ] Products page shows data
- [ ] No CORS errors in browser console

---

## 🎓 Summary

### To Run on ANY Computer:
1. Clone repo
2. Checkout `feature/local-dev-setup` branch
3. Copy `.env.local.example` → `.env`
4. Add password: `Ursaviour2025`
5. Run: `./start-local-with-aws.sh`

### To Start/Stop:
- **Start**: `./start-local-with-aws.sh` or manually start backend + frontend
- **Stop**: `Ctrl+C` or `lsof -ti:8000,3001 | xargs kill -9`

### To Switch Database:
- Edit `backend/.env`
- Comment/uncomment database URL
- Restart backend

---

**That's it! Same process on every computer! 🎉**
