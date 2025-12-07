#!/bin/bash

# AutoList AI - Quick Setup Script
# Usage: ./setup.sh

set -e

echo "=================================================="
echo "       AutoList AI - Phase 1 Setup Script         "
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# =============================================================================
# Check Prerequisites
# =============================================================================
echo "Checking prerequisites..."
echo ""

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_status "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_status "Node.js $NODE_VERSION found"
else
    print_error "Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_status "npm $NPM_VERSION found"
else
    print_error "npm not found. Please install npm"
    exit 1
fi

# Check MongoDB
if command_exists mongod; then
    print_status "MongoDB found"
else
    print_warning "MongoDB not found. Please install and start MongoDB"
fi

echo ""

# =============================================================================
# Backend Setup
# =============================================================================
echo "Setting up Backend..."
echo ""

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
print_status "Python dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env

    # Generate SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i.bak "s/your-super-secret-key-change-in-production-min-32-chars/$SECRET_KEY/" .env

    # Generate ENCRYPTION_KEY
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    sed -i.bak "s/^ENCRYPTION_KEY=$/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env

    rm -f .env.bak
    print_status ".env file created with generated keys"
else
    print_status ".env file already exists"
fi

cd ..

# =============================================================================
# Frontend Setup
# =============================================================================
echo ""
echo "Setting up Frontend..."
echo ""

cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install --silent
print_status "Node.js dependencies installed"

cd ..

# =============================================================================
# Database Setup
# =============================================================================
echo ""
echo "Setting up Database..."
echo ""

# Check if MongoDB is running
if pgrep -x "mongod" > /dev/null; then
    print_status "MongoDB is running"

    # Seed template schemas
    cd backend
    source venv/bin/activate
    echo "Seeding template schemas..."
    python -m app.data.seed_template_schemas 2>/dev/null || print_warning "Could not seed schemas (MongoDB may not be accessible)"
    cd ..
else
    print_warning "MongoDB is not running. Start it with: mongod"
    print_warning "Then run: cd backend && python -m app.data.seed_template_schemas"
fi

# =============================================================================
# Complete
# =============================================================================
echo ""
echo "=================================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "To start the application:"
echo ""
echo "  1. Start MongoDB (if not running):"
echo "     mongod"
echo ""
echo "  2. Start Backend (Terminal 1):"
echo "     cd backend"
echo "     source venv/bin/activate"
echo "     uvicorn app.main:app --reload --port 8000"
echo ""
echo "  3. Start Frontend (Terminal 2):"
echo "     cd frontend"
echo "     npm run dev"
echo ""
echo "  4. Open in browser:"
echo "     http://localhost:5173"
echo ""
echo "  5. Login with demo account or register new user"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "=================================================="
