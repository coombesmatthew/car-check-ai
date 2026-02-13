#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🚀 Setting up Car Check AI..."

# Check prerequisites
command -v node >/dev/null 2>&1 || { echo -e "${RED}❌ Node.js required${NC}"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}❌ Python 3 required${NC}"; exit 1; }

# Environment files
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env with your API keys${NC}"
fi

# Frontend setup
echo "📦 Installing frontend dependencies..."
cd frontend && npm install && cd ..

# Backend setup
echo "🐍 Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Database setup
if command -v docker >/dev/null 2>&1; then
    echo "🐘 Starting database..."
    docker-compose up -d postgres redis
    sleep 5
    echo -e "${GREEN}✅ Database ready${NC}"
fi

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Run 'make dev' to start"
echo "3. Visit http://localhost:3000"
