#!/bin/bash

###############################################################################
# Test Deployment Script - Run this locally before deploying to EC2
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Social Searcher - Pre-Deployment Test${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check Docker
echo -e "${YELLOW}Checking Docker...${NC}"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker installed${NC}"
    docker --version
else
    echo -e "${RED}✗ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

# Check Docker Compose
echo -e "${YELLOW}Checking Docker Compose...${NC}"
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
    docker-compose --version
else
    echo -e "${RED}✗ Docker Compose not found. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check .env files
echo -e "${YELLOW}Checking environment files...${NC}"
if [ -f ".env" ] && [ -f "backend/.env" ] && [ -f "frontend/.env" ]; then
    echo -e "${GREEN}✓ Environment files found${NC}"
else
    echo -e "${RED}✗ Missing environment files. Please copy .env.example files.${NC}"
    exit 1
fi

# Check for API keys
echo -e "${YELLOW}Checking API keys...${NC}"
if grep -q "your_claude_api_key_here" backend/.env; then
    echo -e "${RED}✗ Please update ANTHROPIC_API_KEY in backend/.env${NC}"
    exit 1
else
    echo -e "${GREEN}✓ API keys configured${NC}"
fi

# Build containers
echo -e "${YELLOW}Building Docker containers...${NC}"
docker-compose -f docker-compose.dev.yml build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Containers built successfully${NC}"
else
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi

# Start services
echo -e "${YELLOW}Starting services...${NC}"
docker-compose -f docker-compose.dev.yml up -d

echo "Waiting for services to start..."
sleep 15

# Check backend health
echo -e "${YELLOW}Testing backend...${NC}"
if curl -f http://localhost:8000/health &> /dev/null; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    docker-compose -f docker-compose.dev.yml logs backend
    exit 1
fi

# Check frontend
echo -e "${YELLOW}Testing frontend...${NC}"
if curl -f http://localhost:5173 &> /dev/null; then
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
else
    echo -e "${RED}✗ Frontend check failed${NC}"
    docker-compose -f docker-compose.dev.yml logs frontend
    exit 1
fi

# Check database
echo -e "${YELLOW}Testing database...${NC}"
if docker exec socialsearcher_dev_db pg_isready -U devuser &> /dev/null; then
    echo -e "${GREEN}✓ Database is healthy${NC}"
else
    echo -e "${RED}✗ Database check failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All tests passed! ✓${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Application is running at:"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.dev.yml logs -f"
echo ""
echo "To stop:"
echo "  docker-compose -f docker-compose.dev.yml down"
echo ""
echo -e "${GREEN}You're ready to deploy to AWS EC2!${NC}"
