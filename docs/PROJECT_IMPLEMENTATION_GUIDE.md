# UrSaviour Project Implementation Guide

## Project Overview
UrSaviour is a grocery discount assistant that helps users find the best deals on their favorite products. This guide provides detailed implementation instructions for each team member.

## Project Structure
```
UrSaviour-Project/
├── backend/                    # Backend Development
│   ├── app/
│   │   ├── api/               # API Endpoints
│   │   │   ├── auth/          # [Auth Team]
│   │   │   ├── products/      # [Product Team]
│   │   │   ├── watchlist/     # [Watchlist Team]
│   │   │   └── assistant/     # [AI Team]
│   │   │
│   │   ├── core/             # Core Configuration
│   │   ├── db/               # Database
│   │   ├── schemas/          # Pydantic Schemas
│   │   └── services/         # Business Logic
│   │
│   └── tests/                # Test Files
│
├── frontend/                  # Frontend Development
│   ├── src/
│   │   ├── js/              # JavaScript Files
│   │   ├── css/            # Stylesheets
│   │   └── assets/         # Static Assets
│   │
│   └── index.html          # Main HTML file
│
├── docs/                    # Documentation
│   ├── api/                # API Documentation
│   ├── setup/             # Setup Guides
│   └── design/            # Design Documentation
│
└── data/                  # Data Files
```

## Team Responsibilities

### Auth Team
**Purpose**: Handle user authentication and authorization

**Files to Modify**:
1. backend/app/api/auth/*
   - login.py: User authentication
   - register.py: User registration
   - profile.py: User profile management

2. backend/app/core/security.py
   - JWT implementation
   - Password hashing
   - Security middleware

3. backend/app/db/models/user.py
   - User database schema
   - User relationships

4. backend/app/db/crud/user.py
   - User CRUD operations
   - User search functionality

5. backend/app/schemas/user.py
   - User data validation
   - Request/response schemas

6. backend/app/services/auth.py
   - Authentication business logic
   - Session management

7. backend/tests/api/test_auth.py
   - Authentication API tests
   - Security tests

8. frontend/src/js/auth/*
   - Login implementation
   - Registration implementation
   - Profile management

9. docs/api/auth.md
   - API documentation
   - Authentication flow

### Product Team
**Purpose**: Product data management and PDF processing

**Files to Modify**:
1. backend/app/api/products/*
   - search.py: Product search
   - details.py: Product details
   - categories.py: Category management

2. backend/app/db/models/product.py
   - Product database schema
   - Product relationships

3. backend/app/db/crud/product.py
   - Product CRUD operations
   - Search functionality

4. backend/app/schemas/product.py
   - Product data validation
   - Search parameters

5. backend/app/services/etl.py
   - PDF parsing
   - Data extraction
   - Data cleaning

6. backend/tests/api/test_products.py
   - Product API tests
   - Search functionality tests

7. backend/tests/services/test_etl.py
   - ETL service tests
   - PDF processing tests

8. frontend/src/js/products/*
   - Product search
   - Product display
   - Category navigation

9. docs/api/products.md
   - Product API documentation
   - Search parameters

### Watchlist Team
**Purpose**: User watchlist and price alerts

**Files to Modify**:
1. backend/app/api/watchlist/*
   - add.py: Add to watchlist
   - remove.py: Remove from watchlist
   - list.py: Get watchlist

2. backend/app/db/models/watchlist.py
   - Watchlist database schema
   - Alert settings

3. backend/app/db/crud/watchlist.py
   - Watchlist CRUD operations
   - Alert management

4. backend/app/schemas/watchlist.py
   - Watchlist data validation
   - Alert parameters

5. backend/app/services/notification.py
   - Price alert system
   - Notification service

6. backend/tests/api/test_watchlist.py
   - Watchlist API tests
   - Alert system tests

7. frontend/src/js/watchlist/*
   - Watchlist management
   - Alert settings
   - Price tracking

8. docs/api/watchlist.md
   - Watchlist API documentation
   - Alert system documentation

### AI Team
**Purpose**: AI assistant implementation

**Files to Modify**:
1. backend/app/api/assistant/*
   - chat.py: AI chat interface
   - suggest.py: Product suggestions

2. backend/app/services/ai.py
   - OpenAI integration
   - Response processing
   - Context management

3. backend/tests/services/test_ai.py
   - AI service tests
   - Integration tests

### UI Team
**Purpose**: Frontend implementation and design

**Files to Modify**:
1. frontend/src/css/*
   - main.css: Global styles
   - components/*: Component styles

2. frontend/src/assets/*
   - images/: Image assets
   - icons/: Icon assets

3. frontend/index.html
   - Main HTML structure
   - Resource loading

4. docs/setup/frontend.md
   - Frontend setup guide
   - Development workflow

5. docs/design/ui_guide.md
   - Design system
   - UI/UX guidelines

### DevOps Team
**Purpose**: Infrastructure and deployment

**Files to Modify**:
1. backend/app/core/config.py
   - Environment configuration
   - Service settings

2. backend/app/core/logging.py
   - Logging system
   - Error tracking

3. backend/app/core/exceptions.py
   - Custom exceptions
   - Error handling

4. backend/app/db/base.py
   - Database configuration
   - Connection management

5. backend/app/db/session.py
   - Session management
   - Transaction handling

6. backend/app/db/crud/base.py
   - Base CRUD operations
   - Query optimization

7. backend/tests/conftest.py
   - Test configuration
   - Test fixtures

8. docs/setup/backend.md
   - Backend setup guide
   - Deployment guide

## Development Workflow

### Branch Naming Convention
- Feature: `feature/team-name/feature-description`
- Bugfix: `bugfix/team-name/bug-description`
- Hotfix: `hotfix/issue-description`

### Commit Message Format
```
[Team] Action: Description

- Detailed changes
- Related files
```

### Code Review Process
1. Create feature branch
2. Implement changes
3. Write/update tests
4. Update documentation
5. Create pull request
6. Code review by team lead
7. Merge to main

### Testing Requirements
- Unit tests for all new features
- Integration tests for API endpoints
- Test coverage > 80%
- All tests must pass before merge

### Documentation Requirements
- API documentation for all endpoints
- Setup instructions for new features
- Code comments for complex logic
- Update README.md for major changes 