#!/bin/bash

# Script to update all ports in Car Check AI project
# This avoids conflicts with other running projects

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔧 Updating ports to avoid conflicts...${NC}\n"

# New port configuration
FRONTEND_PORT=3001
BACKEND_PORT=8001
POSTGRES_PORT=5433
REDIS_PORT=6380

echo -e "${YELLOW}New port configuration:${NC}"
echo "  Frontend:   3000 → ${FRONTEND_PORT}"
echo "  Backend:    8000 → ${BACKEND_PORT}"
echo "  PostgreSQL: 5432 → ${POSTGRES_PORT}"
echo "  Redis:      6379 → ${REDIS_PORT}"
echo ""

# Backup original files
echo -e "${BLUE}📦 Creating backups...${NC}"
cp docker-compose.yml docker-compose.yml.backup
cp .env .env.backup
echo -e "${GREEN}✅ Backups created (.backup files)${NC}\n"

# Update docker-compose.yml
echo -e "${BLUE}🐳 Updating docker-compose.yml...${NC}"

# Frontend port
sed -i.tmp "s/\"3000:3000\"/\"${FRONTEND_PORT}:3000\"/" docker-compose.yml

# Backend port
sed -i.tmp "s/\"8000:8000\"/\"${BACKEND_PORT}:8000\"/" docker-compose.yml

# PostgreSQL port
sed -i.tmp "s/\"5432:5432\"/\"${POSTGRES_PORT}:5432\"/" docker-compose.yml

# Redis port
sed -i.tmp "s/\"6379:6379\"/\"${REDIS_PORT}:6379\"/" docker-compose.yml

rm -f docker-compose.yml.tmp

echo -e "${GREEN}✅ docker-compose.yml updated${NC}\n"

# Update .env file
echo -e "${BLUE}⚙️  Updating .env file...${NC}"

# Database URL
sed -i.tmp "s|postgresql://carcheck:password@localhost:5432/carcheck|postgresql://carcheck:password@localhost:${POSTGRES_PORT}/carcheck|" .env

# Redis URL
sed -i.tmp "s|redis://localhost:6379|redis://localhost:${REDIS_PORT}|" .env

# API URL (if exists)
sed -i.tmp "s|http://localhost:8000|http://localhost:${BACKEND_PORT}|" .env

rm -f .env.tmp

echo -e "${GREEN}✅ .env updated${NC}\n"

# Update frontend .env.local
echo -e "${BLUE}⚛️  Updating frontend environment...${NC}"

cat > frontend/.env.local << EOF
# Frontend environment variables
NEXT_PUBLIC_API_URL=http://localhost:${BACKEND_PORT}
NEXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key_here
NEXT_PUBLIC_SITE_URL=http://localhost:${FRONTEND_PORT}
EOF

echo -e "${GREEN}✅ frontend/.env.local created${NC}\n"

# Update Makefile help text (optional)
if [ -f "Makefile" ]; then
    echo -e "${BLUE}📝 Updating Makefile comments...${NC}"
    # This is optional - just updates any hardcoded port references in comments
    sed -i.tmp "s/localhost:3000/localhost:${FRONTEND_PORT}/g" Makefile
    sed -i.tmp "s/localhost:8000/localhost:${BACKEND_PORT}/g" Makefile
    rm -f Makefile.tmp
    echo -e "${GREEN}✅ Makefile updated${NC}\n"
fi

# Update README if it has hardcoded ports
if [ -f "README.md" ]; then
    echo -e "${BLUE}📖 Updating README.md...${NC}"
    sed -i.tmp "s/localhost:3000/localhost:${FRONTEND_PORT}/g" README.md
    sed -i.tmp "s/localhost:8000/localhost:${BACKEND_PORT}/g" README.md
    rm -f README.md.tmp
    echo -e "${GREEN}✅ README.md updated${NC}\n"
fi

# Show summary
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Port configuration updated successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Access your application at:${NC}"
echo "  Frontend:    http://localhost:${FRONTEND_PORT}"
echo "  Backend API: http://localhost:${BACKEND_PORT}"
echo "  API Docs:    http://localhost:${BACKEND_PORT}/docs"
echo ""
echo -e "${YELLOW}Database connections:${NC}"
echo "  PostgreSQL:  localhost:${POSTGRES_PORT}"
echo "  Redis:       localhost:${REDIS_PORT}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review the changes in .env"
echo "2. Add your API keys to .env"
echo "3. Stop any running containers: ${BLUE}docker-compose down${NC}"
echo "4. Start with new ports: ${BLUE}docker-compose up -d${NC}"
echo ""
echo -e "${YELLOW}To revert changes:${NC}"
echo "  mv docker-compose.yml.backup docker-compose.yml"
echo "  mv .env.backup .env"
echo ""
