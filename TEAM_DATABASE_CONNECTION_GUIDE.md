# 🔗 Team Database Connection Guide

## How to Connect to Mio's Local MySQL Database

This guide explains how team members can connect to the shared local MySQL database running on Mio's computer.

---

## 📋 Prerequisites

1. **Network Connection**: You must be on the same local network as Mio's computer
2. **Git Access**: Make sure you have the latest code from the repository
3. **Python Environment**: Python 3.9+ installed

---

## 🚀 Quick Setup Steps

### Step 1: Get the Latest Code
```bash
git clone https://github.com/JustinCoKA/UrSaviour-Project.git
cd UrSaviour-Project

# OR if you already have it:
git pull origin main
```

### Step 2: Create Environment File
```bash
# Copy the example environment file
cp .env.example .env
```

### Step 3: Configure Database Connection
Edit the `.env` file and use these settings:

```bash
# Database Configuration - Team Shared Database
DATABASE_URL=mysql+pymysql://ursaviouruser:securepassword@172.16.38.147:3306/ursaviour

# JWT Configuration (keep these as-is)
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AWS Configuration
AWS_REGION=ap-southeast-2

# Optional: OpenAI API (if you have a key)
# OPENAI_API_KEY=your-openai-api-key-here

# Optional: Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
```

### Step 4: Install Dependencies
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt
```

### Step 5: Test Database Connection
```bash
# Test the connection (from project root)
python -c "
import pymysql
try:
    connection = pymysql.connect(
        host='172.16.38.147',
        user='ursaviouruser', 
        password='securepassword',
        database='ursaviour',
        port=3306,
        connect_timeout=10
    )
    print('✅ Database connection successful!')
    connection.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

### Step 6: Start the Backend
```bash
# From the backend directory
cd backend
python -m uvicorn app.main:app --reload --port 8001
```

### Step 7: Access the Application
- **API Documentation**: http://localhost:8001/docs
- **Backend API**: http://localhost:8001/api/v1/

---

## 🗄️ Database Connection Details

| Parameter | Value |
|-----------|-------|
| **Host** | `172.16.38.147` |
| **Port** | `3306` |
| **Database** | `ursaviour` |
| **Username** | `ursaviouruser` |
| **Password** | `securepassword` |

---

## 🔧 Troubleshooting

### ❌ Connection Timeout or Refused
1. **Check Network**: Make sure you're on the same WiFi/network as Mio
2. **Check Mio's Computer**: Ensure Mio's computer is on and the Docker containers are running
3. **Firewall**: Mio might need to allow port 3306 through firewall

### ❌ Authentication Failed
- Double-check the username and password in your `.env` file
- Make sure there are no extra spaces in the DATABASE_URL

### ❌ Database Not Found
- The database name should be `ursaviour` (not `ursaviour_db`)
- Contact Mio to verify the database is running

### 🔍 Check Mio's Database Status
Mio can run this to check if the database is accessible:
```bash
# Check if Docker containers are running
docker ps

# Check if port 3306 is listening
netstat -an | grep 3306

# Test local connection
mysql -h localhost -P 3306 -u ursaviouruser -p
```

---

## 🌐 Network Requirements

- **Same Local Network**: All team members must be connected to the same WiFi/LAN
- **Port Access**: Port 3306 must be accessible from Mio's computer
- **IP Address**: If `172.16.38.147` doesn't work, ask Mio for the current IP

---

## 💡 Tips for Team Development

1. **Coordinate Changes**: Since everyone shares the same database, coordinate schema changes
2. **Backup Important Data**: Ask Mio to backup before major changes
3. **Use Different Ports**: Run your backend on different ports (8001, 8002, etc.) to avoid conflicts
4. **Test Data**: Create test users with unique usernames to avoid conflicts

---

## 📞 Need Help?

If you're having trouble connecting:
1. Check this troubleshooting guide first
2. Verify you're on the same network as Mio
3. Contact Mio to verify database status
4. Share the specific error message you're getting

---

**Happy Coding! 🚀**