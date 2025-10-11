# 🛒 UrSaviour - Smart Discount Shopping Assistant

[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com)
[![AWS](https://img.shields.io/badge/AWS-RDS%20%7C%20EC2%20%7C%20S3-orange.svg)](https://aws.amazon.com)

> **Start smart shopping with personalized discount information and AI recommendations!**

---

## 🚀 Quick Start

### Full System Deployment (Docker)
```bash
# Clone repository
git clone https://github.com/JustinCoKA/UrSaviour-Project.git
cd UrSaviour-Project

# Environment setup
cp .env.example .env
# Edit .env file with your API keys and database configuration

# Run all services
docker-compose up -d

# Access
# Frontend: http://localhost:3001
# Backend API: http://localhost:8000/docs
```

### Development Environment
```bash
# Run backend
cd backend
pip install -r requirements.txt
python main.py  # localhost:8000

# Run frontend (new terminal)
cd frontend/src
python -m http.server 3001  # localhost:3001
```

### AWS/EC2 Production Deployment
```bash
# Configure production environment variables
export DATABASE_URL="mysql://username:password@your-rds-endpoint.amazonaws.com/ursaviour"
export BACKEND_CORS_ORIGINS='["https://yourdomain.com"]'
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

# Deploy with production docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🎯 Key Features

### 🔍 **Real-time Price Comparison**
- Compare prices of identical products across multiple stores
- Discount information and special offer alerts
- Price history tracking

### ❤️ **Personalized Watchlist**
- Register and manage favorite products
- Automatic notifications when prices drop
- Personalized recommendations for each user

### 🤖 **AI Shopping Assistant**
- Natural language product search
- Personalized discount product recommendations
- Shopping pattern analysis and suggestions

### 📊 **Admin Dashboard**
- ETL process monitoring
- User and data management
- System logs and performance analysis

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "Frontend (Port 3001)"
        A[Web Browser] --> B[HTML/CSS/JS]
    end
    
    subgraph "Backend (Port 8000)"
        C[FastAPI] --> D[Business Logic]
        D --> E[Database ORM]
    end
    
    subgraph "Data Layer"
        F[MySQL DB/AWS RDS] 
        G[Redis Cache]
    end
    
    subgraph "External Services"
        H[OpenAI API]
        I[Email Service]
        J[AWS S3]
    end
    
    subgraph "Cloud Infrastructure"
        K[AWS EC2]
        L[AWS Lambda]
        M[AWS CloudFront]
    end
    
    B --> C
    E --> F
    D --> G
    D --> H
    D --> I
    C --> K
    L --> F
    J --> L
    B --> M
```

## 📁 Project Structure

```
UrSaviour-Project/
├── 🐳 docker-compose.yml      # Container orchestration
├── � docker-compose.prod.yml # Production deployment
├── �📝 .env                    # Environment variables
├── 📚 PROJECT_STRUCTURE.md    # 🆕 Detailed structure documentation
├── 📁 backend/                # FastAPI backend
│   ├── app/
│   │   ├── main.py           # App entry point
│   │   ├── api/v1/           # REST API endpoints
│   │   ├── services/         # Business logic
│   │   └── db/               # Database models
│   └── requirements.txt      # Python dependencies
├── 📁 frontend/               # Web frontend
│   └── src/
│       ├── *.html           # Web pages
│       ├── css/             # Stylesheets
│       ├── js/              # JavaScript logic
│       └── images/          # Image assets
├── 📁 data/                   # Dataset files
├── 📁 scripts/                # ETL and utilities
├── 📁 docs/                   # Project documentation
└── 📁 deployment/             # 🆕 AWS deployment configs
```

> 📖 **[View Detailed Structure Documentation](./PROJECT_STRUCTURE.md)** - Role description of all files and directories

---

## 🔧 Tech Stack

### Backend
- **Python 3.9+** - Main development language
- **FastAPI** - High-performance asynchronous web framework  
- **SQLAlchemy** - ORM and database abstraction
- **Alembic** - Database migration tool
- **JWT** - User authentication and session management
- **OpenAI API** - AI chatbot service

### Frontend  
- **Vanilla JavaScript** - Pure JS without frameworks
- **CSS Grid/Flexbox** - Responsive layout system
- **Fetch API** - REST API communication
- **LocalStorage** - Client-side data storage

### Database & Infrastructure
- **MySQL 8.0** - Primary database
- **Redis** - Caching and session storage
- **Docker Compose** - Container orchestration
- **AWS** (Production) - RDS, S3, Lambda, EC2

---

## 🌐 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Token refresh

### Product Management
- `GET /api/v1/products/products` - Get product list
- `GET /api/v1/products/search` - Product search
- `GET /api/v1/products/{id}` - Product details

### Watchlist
- `GET /api/v1/watchlist` - Get watchlist
- `POST /api/v1/watchlist/{product_id}` - Add to watchlist
- `DELETE /api/v1/watchlist/{product_id}` - Remove from watchlist

### AI Assistant
- `POST /api/v1/assistant/chat` - Chatbot conversation
- `GET /api/v1/assistant/recommendations` - Personalized recommendations

### Admin
- `POST /api/v1/admin/etl/run` - Execute ETL process
- `GET /api/v1/admin/logs` - System logs

> 📋 **[View API Documentation in Swagger UI](http://localhost:8000/docs)**

---

## 🚀 Deployment & Development

### Local Development Environment

#### Prerequisites
```bash
# Python 3.9+
python --version

# Docker & Docker Compose
docker --version
docker-compose --version

# MySQL (optional - not needed if using Docker)
```

#### Development Server Setup
```bash
# 1. Clone repository
git clone https://github.com/JustinCoKA/UrSaviour-Project.git
cd UrSaviour-Project

# 2. Virtual environment setup (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt

# 4. Environment configuration
cd ..
cp .env.example .env
# Edit .env file with your settings

# 5. Start database services (Docker)
docker-compose up -d mysql redis

# 6. Run backend
cd backend
python main.py  # http://localhost:8000

# 7. Run frontend (new terminal)
cd frontend/src
python -m http.server 3001  # http://localhost:3001
```

### Full System with Docker
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment
```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d

# AWS Deployment (example)
# 1. Push images to ECR
# 2. Deploy to ECS/EC2
# 3. Connect RDS database
# 4. Serve static assets via CloudFront + S3
```

---

## 📊 Data Management

### ETL Process
```bash
# Manual ETL execution
cd scripts
python process_etl.py

# Generate PDF pamphlets
python generate_pdf_pamphlet.py
```

### Database Migration
```bash
cd backend

# Create new migration
alembic revision -m "description"

# Run migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Sample Data
- `data/foundational_dataset_v1.csv` - Base product dataset (10,000+ items)
- `data/no.27week_special.pdf` - Sample discount pamphlet
- `schema_dump.txt` - Database schema

---

## 🧪 Testing

### API Testing
```bash
# Backend tests
cd backend
pytest

# Manual API endpoint testing
curl http://localhost:8000/api/v1/products/products
```

### Frontend Testing
```bash
# Access development debug page
http://localhost:3001/debug/debug-products.html
```

---

## 🔒 Security Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=mysql://user:password@localhost/ursaviour

# JWT Security
SECRET_KEY=your-super-secret-jwt-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI API
OPENAI_API_KEY=your-openai-api-key

# CORS Settings
BACKEND_CORS_ORIGINS=["http://localhost:3001"]

# Email Service
SMTP_SERVER=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Security Checklist
- [ ] Set `DEBUG=False` in production
- [ ] Enforce HTTPS
- [ ] Automate database backups
- [ ] Configure API Rate Limiting
- [ ] Set up log monitoring

---

## 📈 Monitoring & Logs

### Log Checking
```bash
# Docker container logs
docker-compose logs -f api
docker-compose logs -f web

# Application logs
tail -f backend/logs/app.log
```

### Performance Monitoring
- API response time: FastAPI built-in metrics
- Database queries: SQLAlchemy logging
- User behavior: Frontend analytics

---

## 🤝 Development Contribution

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Commit after development
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

### Code Style
- **Python**: Black, isort, flake8
- **JavaScript**: Prettier, ESLint
- **Commit**: Conventional Commits

---

## 🚨 Troubleshooting

### Common Issues

#### 1. **HTTP 404 Error in Production (API unreachable)**
This is the issue shown in your screenshot. Common causes and solutions:

```bash
# Check if backend service is running
docker-compose -f docker-compose.prod.yml ps

# Check backend health
curl http://localhost:8000/health

# Check nginx routing to backend
curl http://localhost/api/v1/products/products

# Verify CORS configuration for your domain
grep BACKEND_CORS_ORIGINS .env

# Check nginx logs for routing errors
sudo tail -f /var/log/nginx/error.log
```

**Solution for Production Deployment:**
```bash
# 1. Ensure nginx properly routes /api/ to backend
# 2. Update CORS origins to include your production domain
BACKEND_CORS_ORIGINS='["https://yourdomain.com"]'

# 3. Restart services
docker-compose -f docker-compose.prod.yml restart
```

#### 2. **CORS Errors**
```bash
# Check .env file
BACKEND_CORS_ORIGINS='["http://localhost:3001", "https://yourdomain.com"]'

# Restart backend
docker-compose restart api
```

#### 3. **Database Connection Failure**
For AWS RDS connection issues:
```bash
# Test RDS connection from EC2
mysql -h your-rds-endpoint.amazonaws.com -u admin -p

# Check security groups allow EC2 to RDS on port 3306
# Verify DATABASE_URL in .env
DATABASE_URL=mysql://admin:password@your-rds-endpoint.amazonaws.com:3306/ursaviour
```

#### 4. **Frontend Shows Static Data Only**
- Backend API server status check
- Network tab API call errors
- CORS configuration verification
- Check if running on correct port (3001 vs 63342)

### Development vs Production Environment

| Environment | URL | Status | Data Source | Backend |
|-------------|-----|--------|-------------|---------|
| **Local Development** | `localhost:3001` | ✅ Working | Live API | `localhost:8000` |
| **PyCharm Server** | `localhost:63342` | ❌ CORS blocked | Static fallback | CORS not configured |
| **Production AWS** | `yourdomain.com` | ⚠️ Need configuration | Should be Live API | Same origin `/api/` |

### Debugging Tools
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Debug Pages**: `debug/` folder
- **AWS RDS**: Use MySQL Workbench or phpMyAdmin
- **Production Logs**: `docker-compose logs -f`

---

## 📞 Support & Contact

- **Project Repository**: [GitHub Repository](https://github.com/JustinCoKA/UrSaviour-Project)
- **Issue Tracking**: [GitHub Issues](https://github.com/JustinCoKA/UrSaviour-Project/issues)
- **Documentation**: [Detailed Structure Documentation](./PROJECT_STRUCTURE.md)

---

## 📄 License

This project is distributed under the [MIT License](./LICENSE).

---

## 🎓 Academic Information

**Course:** NIT3003 – IT Capstone Project (2025 S1B4)  
**Team:** UrSaviour Development Team  
**Institution:** [Your Institution Name]

---

<div align="center">

### 🌟 Start Smart Shopping with UrSaviour! 🌟

[![GitHub Stars](https://img.shields.io/github/stars/JustinCoKA/UrSaviour-Project?style=social)](https://github.com/JustinCoKA/UrSaviour-Project)
[![GitHub Forks](https://img.shields.io/github/forks/JustinCoKA/UrSaviour-Project?style=social)](https://github.com/JustinCoKA/UrSaviour-Project)

</div>

---

## 📘 Introduction

### Background
Australian families face increasing grocery costs due to inflation and rising living expenses. UrSaviour provides a centralized web platform that simulates grocery discount pamphlets using internal datasets (not web scraping), ensuring legality and sustainability.

### Market Analysis
- AUD 125B grocery sector (2023)
- Users struggle to manually check promotions across platforms
- International consumers often lack access or understanding of promotions

### Competitor Analysis
- **Frugl:** Comprehensive, but relies on scraping
- **WhichGrocer:** Easy UI, limited features without subscription
- **Grocerize:** Fast, but lacks scalability

### Project Aims & Unique Value
UrSaviour is a lawful, ethical, and user-friendly discount tracking platform featuring:
- Personalized watchlists
- AI chatbot
- Internal fake data generation

---

## 🎯 Functional Requirements

- User Registration & Login
- PDF Scraping & ETL Management
- Product Info & Price Display
- Watchlist Management
- AI Assistant Integration
- Admin Login
- Database Management

---

## 🚦 Non-Functional Requirements

- Password complexity, secure login/session
- Responsive UI (<2–3 sec interaction time)
- Encrypted communication (HTTPS)
- Ethical data handling
- Resilient background notification and ETL process

---

## 💡 Use Case Descriptions

- **User Registration:** Validates and stores new users
- **Login:** Authenticates with secure sessions
- **View Product Info & Compare Prices:** Multi-store price comparison
- **Watchlist Management:** Monitor selected items and receive alerts
- **Chatbot (AI Assistant):** Query discounts via natural language
- **ETL Execution:** Parses weekly simulated PDFs for price updates
- **Admin Management:** Admin dashboard to manage data, users, ETL logs

---

## 🔄 Data Pipeline Architecture

1. **Foundational Dataset:** CSV/XLSX with product details stored in AWS S3
2. **PDF Generation:** Simulated weekly offers via ReportLab
3. **ETL Workflow:** AWS Lambda auto-triggers on S3 upload, parses PDF, updates RDS (MySQL)

```mermaid
graph TD
    subgraph "Users"
        U[User]
        A[Admin]
    end

    subgraph "UrSaviour Web Application"
        FE[("Front-End <br> HTML/CSS/JS")]
    end

    subgraph "UrSaviour Back-End (Python)"
        API[REST API]
        AI_GW[AI Assistant Gateway]
    end

    subgraph "Data & Storage (AWS)"
        RDS[("MySQL Database <br> Amazon RDS")]
        subgraph "Data Generation & ETL Pipeline"
            S3_DS[("Foundational Dataset <br> Amazon S3")]
            Script[("PDF Generation Script <br> EC2 / Lambda")]
            S3_PDF[("Simulated PDF Watch Folder <br> Amazon S3")]
            ETL[("ETL Process <br> Amazon Lambda")]
        end
    end

    subgraph "External Services"
        OpenAI[("OpenAI GPT API")]
        Email[Email Service]
    end

    U --> FE
    A --> FE
    FE --> API
    API --> RDS
    API --> AI_GW
    AI_GW --> OpenAI
    S3_DS --> Script
    Script --> S3_PDF
    S3_PDF -- S3 Event Trigger --> ETL
    ETL --> RDS
    API -- Triggers Notifications --> Email
    Email --> U
```

---

## 🛠️ Tools

- **Frontend:** HTML, CSS, JavaScript, WIX (for UI/UX)
- **Backend:** Python (FastAPI / Flask)
- **Database:** MySQL
- **Cloud & ETL:** AWS EC2, Lambda, S3
- **API Integration:** REST, OpenAI (Chatbot)

---

## 🔧 UI & Sequence Diagrams

- Wireframes and mockups for:
  - Registration
  - Login
  - Product Browsing
  - Watchlist
  - Chatbot Interface
  - Admin Dashboard

---

## 👥 Resource Management

- Task allocation across team
- Resource scheduling and contingency plans
- Evaluation metrics for project delivery

---

## ⚠️ Risk Management

- PDF parsing or data validation failure
- Email script or backend outages
- Database unavailability
- Ethical concerns with fake data generation

---

## 📅 Timeline (Gantt Chart)

Project timeline includes planning, development, testing, deployment, and report submission phases.

---

## 📚 References

- ABS Australia
- ACCC reports
- Woolworths & Coles API policies
- Industry analysis sources
