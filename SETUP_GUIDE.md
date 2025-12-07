# AutoList AI - Phase 1 Setup Guide

Complete guide to set up and run the AutoList AI MVP locally.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Database Setup](#database-setup)
6. [Environment Configuration](#environment-configuration)
7. [Running the Application](#running-the-application)
8. [Testing](#testing)
9. [Usage Walkthrough](#usage-walkthrough)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Ensure you have the following installed:

| Software | Version | Check Command |
|----------|---------|---------------|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| MongoDB | 6.0+ | `mongod --version` |
| Git | 2.0+ | `git --version` |

### Installing Prerequisites

#### macOS (using Homebrew)
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Install Node.js
brew install node

# Install MongoDB
brew tap mongodb/brew
brew install mongodb-community@7.0

# Start MongoDB
brew services start mongodb-community@7.0
```

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Install MongoDB
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] http://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### Windows
```powershell
# Install Chocolatey if not installed
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Python
choco install python311

# Install Node.js
choco install nodejs

# Install MongoDB
choco install mongodb

# Start MongoDB (run as Administrator)
net start MongoDB
```

---

## Quick Start

For those who want to get running quickly:

```bash
# Clone the repository (if not already done)
cd /path/to/AUTOLIST_AI_NEW_MVP

# Run the setup script
chmod +x setup.sh
./setup.sh

# Or manually:
# Terminal 1: Start MongoDB
mongod

# Terminal 2: Start Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3: Start Frontend
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173 in your browser.

---

## Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Create Environment File

```bash
# Copy example env file
cp .env.example .env

# Or create manually:
cat > .env << 'EOF'
# Application
APP_NAME=AutoList AI
APP_VERSION=1.0.0
DEBUG=True

# Security
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=autolist_ai

# Shopify
SHOPIFY_API_VERSION=2024-01

# Claude AI (optional - for AI-assisted mapping)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Encryption (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=
EOF
```

### Step 5: Generate Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy the output and paste it as ENCRYPTION_KEY in .env
```

### Step 6: Verify Installation

```bash
# Check if FastAPI app loads correctly
python -c "from app.main import app; print('Backend ready!')"
```

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Create Environment File (Optional)

```bash
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000
EOF
```

### Step 4: Verify Installation

```bash
npm run build
# Should complete without errors
```

---

## Database Setup

### Step 1: Start MongoDB

```bash
# macOS (Homebrew)
brew services start mongodb-community

# Ubuntu/Debian
sudo systemctl start mongod

# Windows (run as Administrator)
net start MongoDB

# Or run directly
mongod --dbpath /path/to/data/db
```

### Step 2: Verify MongoDB is Running

```bash
# Connect to MongoDB
mongosh

# Should show MongoDB shell
# Type 'exit' to quit
```

### Step 3: Seed Template Schemas

```bash
cd backend
source venv/bin/activate  # Activate virtual env if not active

# Run the seed script
python -m app.data.seed_template_schemas

# Expected output:
# Seeding schemas to mongodb://localhost:27017/autolist_ai...
# Inserted: amazon_shirt_v1
# Inserted: amazon_kurta_v1
# Saved JSON: .../amazon_shirt_v1.json
# Saved JSON: .../amazon_kurta_v1.json
```

### Step 4: Verify Seeding

```bash
mongosh autolist_ai --eval "db.template_schemas.find().pretty()"
```

---

## Environment Configuration

### Backend `.env` File

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | JWT signing key (min 32 chars) | Yes | - |
| `MONGODB_URI` | MongoDB connection string | Yes | `mongodb://localhost:27017` |
| `MONGODB_DB_NAME` | Database name | Yes | `autolist_ai` |
| `ANTHROPIC_API_KEY` | Claude API key for AI mapping | No | - |
| `ENCRYPTION_KEY` | Fernet key for token encryption | No | - |
| `DEBUG` | Enable debug mode | No | `True` |

### Frontend `.env` File

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `VITE_API_URL` | Backend API URL | No | `http://localhost:8000` |

---

## Running the Application

### Option 1: Run Separately (Recommended for Development)

Open **3 terminal windows**:

**Terminal 1 - MongoDB:**
```bash
mongod
# Or if using brew/systemctl, it's already running as a service
```

**Terminal 2 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### Option 2: Using Docker Compose (Coming Soon)

```bash
docker-compose up -d
```

### Accessing the Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |

---

## Testing

### Run Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_normalizer.py -v

# Run specific test
pytest tests/test_mapping.py::TestMapSingleField::test_exact_key_mapping -v
```

### Expected Test Output

```
======================== test session starts ========================
collected 25 items

tests/test_mapping.py ........                                 [ 32%]
tests/test_mapping_worker.py .....                             [ 52%]
tests/test_normalizer.py .......                               [ 80%]
tests/test_template_writer.py .....                            [100%]

======================== 25 passed in 2.34s =========================
```

### Run Frontend Linting

```bash
cd frontend
npm run lint
```

---

## Usage Walkthrough

### Step 1: Login

1. Open http://localhost:5173
2. Click **"Try Demo Account"** to login with demo credentials
   - Or register a new account

### Step 2: Connect Shopify Store (Optional)

1. Navigate to **Connect** page
2. Enter your Shopify store domain: `mystore.myshopify.com`
3. Enter your Admin API access token
4. Click **Connect Store**
5. Click **Sync Products**

> **Note:** Without real Shopify credentials, the app uses mock/sample products.

### Step 3: View Products

1. Navigate to **Products** page
2. View synced products (2 sample products if using mock data)
3. Select products by clicking checkboxes
4. Choose a template (e.g., "AMAZON - shirt")

### Step 4: Map Products

1. Click **"Map N Products"** button
2. View the Mapping Preview page
3. Review confidence badges:
   - 🟢 Green = High confidence (≥80%)
   - 🟡 Yellow = Medium confidence (50-79%)
   - 🔴 Red = Low confidence (<50%)
4. Click ✏️ to edit any field
5. Click **"Approve All Suggested"** to accept AI suggestions

### Step 5: Download Export

1. Click **"Save & Download"**
2. Navigate to **Download** page
3. Select completed jobs
4. Click **Download** to get XLSX file
5. Open in Excel to verify columns are correct

### Step 6: View Dashboard

1. Navigate to **Dashboard**
2. View statistics:
   - Total products synced
   - Mapping jobs by status
   - Auto-fill rate
   - Recent activity

---

## Troubleshooting

### Common Issues

#### 1. MongoDB Connection Error

```
pymongo.errors.ServerSelectionTimeoutError: localhost:27017
```

**Solution:**
```bash
# Check if MongoDB is running
pgrep mongod

# Start MongoDB
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod
# Windows: net start MongoDB
```

#### 2. Python Module Not Found

```
ModuleNotFoundError: No module named 'app'
```

**Solution:**
```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. Frontend Build Errors

```
npm ERR! Could not resolve dependency
```

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 4. Port Already in Use

```
Address already in use: 8000
```

**Solution:**
```bash
# Find process using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8001
```

#### 5. CORS Errors in Browser

```
Access to fetch has been blocked by CORS policy
```

**Solution:**
- Ensure frontend is running on http://localhost:5173
- Check backend CORS settings in `app/main.py`
- Clear browser cache and refresh

#### 6. JWT Token Expired

```
401 Unauthorized: Token has expired
```

**Solution:**
- Login again to get a new token
- Clear localStorage: `localStorage.removeItem('access_token')`

### Getting Help

1. Check the [Integration Checklist](backend/tests/INTEGRATION_CHECKLIST.md)
2. Review API docs at http://localhost:8000/docs
3. Check console logs in browser DevTools
4. Check backend logs in terminal

---

## Project Structure

```
AUTOLIST_AI_NEW_MVP/
├── backend/
│   ├── app/
│   │   ├── api/              # API routers
│   │   │   └── shopify.py
│   │   ├── data/             # Data files and seeds
│   │   │   ├── template_schemas/
│   │   │   └── seed_template_schemas.py
│   │   ├── models/           # Pydantic & MongoDB models
│   │   ├── services/         # Business logic
│   │   │   ├── mapping_service.py
│   │   │   ├── validator_service.py
│   │   │   └── template_writer.py
│   │   ├── tools/            # CLI tools
│   │   │   └── template_ingest.py
│   │   ├── workers/          # Background workers
│   │   │   ├── normalizer.py
│   │   │   └── mapping_worker.py
│   │   ├── auth.py           # Authentication
│   │   ├── config.py         # Configuration
│   │   ├── dependencies.py   # FastAPI dependencies
│   │   ├── main.py           # App entry point
│   │   └── models.py         # Shared Pydantic models
│   ├── tests/                # Test files
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   ├── styles/           # CSS/Tailwind
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── index.html
│
└── SETUP_GUIDE.md            # This file
```

---

## Next Steps

After completing Phase 1 setup:

1. **Add Real Shopify Credentials** - Connect to an actual Shopify store
2. **Configure Claude API** - Enable AI-assisted mapping with Anthropic API key
3. **Ingest Custom Templates** - Use `template_ingest.py` for your marketplace templates
4. **Run Load Tests** - Verify performance with 20 concurrent users
5. **Deploy to Production** - Use Docker, configure production MongoDB

---

## Support

For issues or questions:
- Check [INTEGRATION_CHECKLIST.md](backend/tests/INTEGRATION_CHECKLIST.md)
- Review API documentation at `/docs`
- Check backend/frontend console logs

---

*AutoList AI - Intelligent Product Mapping for E-commerce*
