#!/bin/bash

###############################################################################
# Social Searcher Deployment Script for AWS EC2
# This script handles the complete deployment process
###############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="socialSearcher"
DEPLOY_USER="ubuntu"
DEPLOY_DIR="/home/$DEPLOY_USER/$APP_NAME"
BACKUP_DIR="/home/$DEPLOY_USER/backups"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Installing..."
        install_docker
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Installing..."
        install_docker_compose
    fi
    
    log_info "All prerequisites met!"
}

install_docker() {
    log_info "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    sudo usermod -aG docker $USER
    log_info "Docker installed successfully!"
}

install_docker_compose() {
    log_info "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    log_info "Docker Compose installed successfully!"
}

backup_database() {
    log_info "Creating database backup..."
    mkdir -p $BACKUP_DIR
    BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    if docker ps | grep -q socialSearcher_db; then
        docker exec socialSearcher_db pg_dump -U dbuser socialsearcher > $BACKUP_FILE
        log_info "Database backed up to: $BACKUP_FILE"
    else
        log_warn "Database container not running. Skipping backup."
    fi
}

stop_services() {
    log_info "Stopping existing services..."
    if [ -f "docker-compose.yml" ]; then
        docker-compose down
    fi
}

pull_latest_code() {
    log_info "Pulling latest code from repository..."
    if [ -d ".git" ]; then
        git pull origin claudeV1
    else
        log_warn "Not a git repository. Skipping pull."
    fi
}

build_containers() {
    log_info "Building Docker containers..."
    docker-compose build --no-cache
}

start_services() {
    log_info "Starting services..."
    docker-compose up -d
    
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check service health
    docker-compose ps
}

setup_ssl() {
    log_info "Setting up SSL certificates with Let's Encrypt..."
    
    # Install certbot if not present
    if ! command -v certbot &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y certbot
    fi
    
    # Create directory for certificates
    sudo mkdir -p ./nginx/ssl
    
    # Stop nginx temporarily
    docker-compose stop nginx
    
    # Get certificate
    sudo certbot certonly --standalone \
        --preferred-challenges http \
        -d tigerosint.aptsoftware.in \
        --agree-tos \
        --non-interactive \
        --email admin@aptsoftware.in
    
    # Copy certificates to nginx directory
    sudo cp /etc/letsencrypt/live/tigerosint.aptsoftware.in/fullchain.pem ./nginx/ssl/cert.pem
    sudo cp /etc/letsencrypt/live/tigerosint.aptsoftware.in/privkey.pem ./nginx/ssl/key.pem
    
    # Start nginx
    docker-compose start nginx
    
    log_info "SSL certificates installed!"
}

cleanup() {
    log_info "Cleaning up old containers and images..."
    docker system prune -f
}

check_health() {
    log_info "Checking application health..."
    
    # Wait for services to start
    sleep 15
    
    # Check backend
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "✓ Backend is healthy"
    else
        log_error "✗ Backend health check failed"
    fi
    
    # Check frontend
    if curl -f http://localhost:80 > /dev/null 2>&1; then
        log_info "✓ Frontend is healthy"
    else
        log_error "✗ Frontend health check failed"
    fi
    
    # Check database
    if docker exec socialSearcher_db pg_isready -U dbuser > /dev/null 2>&1; then
        log_info "✓ Database is healthy"
    else
        log_error "✗ Database health check failed"
    fi
}

show_logs() {
    log_info "Showing recent logs..."
    docker-compose logs --tail=50
}

# Main deployment flow
main() {
    log_info "Starting deployment of $APP_NAME..."
    
    # Change to deploy directory
    cd $DEPLOY_DIR || exit 1
    
    # Run deployment steps
    check_prerequisites
    backup_database
    stop_services
    pull_latest_code
    build_containers
    start_services
    cleanup
    check_health
    
    log_info "=========================================="
    log_info "Deployment completed successfully!"
    log_info "=========================================="
    log_info "Application URL: https://tigerosint.aptsoftware.in"
    log_info "API Docs: https://tigerosint.aptsoftware.in/docs"
    log_info ""
    log_info "To view logs: docker-compose logs -f"
    log_info "To restart: docker-compose restart"
    log_info "To stop: docker-compose down"
}

# Handle script arguments
case "${1:-}" in
    ssl)
        setup_ssl
        ;;
    logs)
        show_logs
        ;;
    backup)
        backup_database
        ;;
    *)
        main
        ;;
esac
