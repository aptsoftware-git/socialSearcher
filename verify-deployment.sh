#!/bin/bash

###############################################################################
# Post-Deployment Verification Script
# Run this after deployment to verify everything is working correctly
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

DOMAIN="tigerosint.aptsoftware.in"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Post-Deployment Verification${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Test 1: Backend Health
echo -e "${YELLOW}Test 1: Checking backend health...${NC}"
if curl -f https://$DOMAIN/api/health &> /dev/null; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    exit 1
fi

# Test 2: API Documentation
echo -e "${YELLOW}Test 2: Checking API documentation...${NC}"
if curl -f https://$DOMAIN/api/docs &> /dev/null; then
    echo -e "${GREEN}✓ API documentation accessible${NC}"
else
    echo -e "${RED}✗ API documentation not accessible${NC}"
    exit 1
fi

# Test 3: Frontend
echo -e "${YELLOW}Test 3: Checking frontend...${NC}"
if curl -f https://$DOMAIN &> /dev/null; then
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
else
    echo -e "${RED}✗ Frontend not accessible${NC}"
    exit 1
fi

# Test 4: SSL Certificate
echo -e "${YELLOW}Test 4: Checking SSL certificate...${NC}"
SSL_INFO=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ SSL certificate is valid${NC}"
    echo "$SSL_INFO"
else
    echo -e "${RED}✗ SSL certificate check failed${NC}"
fi

# Test 5: Response Time
echo -e "${YELLOW}Test 5: Checking response time...${NC}"
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' https://$DOMAIN/api/health)
echo -e "${GREEN}Response time: ${RESPONSE_TIME}s${NC}"

if (( $(echo "$RESPONSE_TIME < 2.0" | bc -l) )); then
    echo -e "${GREEN}✓ Response time is good${NC}"
else
    echo -e "${YELLOW}⚠ Response time is slow (>2s)${NC}"
fi

# Test 6: Security Headers
echo -e "${YELLOW}Test 6: Checking security headers...${NC}"
HEADERS=$(curl -s -I https://$DOMAIN)

if echo "$HEADERS" | grep -q "Strict-Transport-Security"; then
    echo -e "${GREEN}✓ HSTS header present${NC}"
else
    echo -e "${YELLOW}⚠ HSTS header missing${NC}"
fi

if echo "$HEADERS" | grep -q "X-Content-Type-Options"; then
    echo -e "${GREEN}✓ X-Content-Type-Options header present${NC}"
else
    echo -e "${YELLOW}⚠ X-Content-Type-Options header missing${NC}"
fi

# Test 7: Database Connectivity
echo -e "${YELLOW}Test 7: Checking database connectivity...${NC}"
if docker exec socialSearcher_db pg_isready -U dbuser &> /dev/null; then
    echo -e "${GREEN}✓ Database is accessible${NC}"
else
    echo -e "${RED}✗ Database connection failed${NC}"
fi

# Test 8: Container Status
echo -e "${YELLOW}Test 8: Checking container status...${NC}"
CONTAINERS=$(docker-compose ps | grep -c "Up")
if [ "$CONTAINERS" -ge 4 ]; then
    echo -e "${GREEN}✓ All containers are running${NC}"
    docker-compose ps
else
    echo -e "${RED}✗ Some containers are not running${NC}"
    docker-compose ps
fi

# Test 9: Disk Space
echo -e "${YELLOW}Test 9: Checking disk space...${NC}"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo -e "${GREEN}✓ Disk space is sufficient (${DISK_USAGE}% used)${NC}"
else
    echo -e "${YELLOW}⚠ Disk space is running low (${DISK_USAGE}% used)${NC}"
fi

# Test 10: Memory Usage
echo -e "${YELLOW}Test 10: Checking memory usage...${NC}"
MEM_USAGE=$(free | awk 'NR==2 {printf "%.0f", $3*100/$2}')
if [ "$MEM_USAGE" -lt 90 ]; then
    echo -e "${GREEN}✓ Memory usage is normal (${MEM_USAGE}% used)${NC}"
else
    echo -e "${YELLOW}⚠ Memory usage is high (${MEM_USAGE}% used)${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Verification Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Application URLs:"
echo "  Frontend:    https://$DOMAIN"
echo "  API Docs:    https://$DOMAIN/api/docs"
echo "  Health:      https://$DOMAIN/api/health"
echo ""
echo "Next Steps:"
echo "  1. Change default admin password"
echo "  2. Test user registration"
echo "  3. Test search functionality"
echo "  4. Setup monitoring alerts"
echo "  5. Configure daily backups"
echo ""
