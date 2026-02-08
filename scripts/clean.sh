#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Source per-project isolation variables
# ============================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/project-env.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo ""
echo "=========================================="
echo "  Koulu Environment Cleanup"
echo "  Project: ${COMPOSE_PROJECT_NAME}"
echo "=========================================="
echo ""

# Determine Docker Compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    error "Docker Compose not found. Please install Docker Compose."
    exit 1
fi

info "Stopping and removing containers for project: ${COMPOSE_PROJECT_NAME}..."
$COMPOSE_CMD down -v --remove-orphans
success "Containers, networks, and volumes removed"

# Check for any remaining containers with this project name
REMAINING_CONTAINERS=$($COMPOSE_CMD ps -a --format '{{.Service}}' 2>/dev/null | wc -l)
if [ "$REMAINING_CONTAINERS" -eq 0 ]; then
    success "All containers removed"
else
    warn "Found $REMAINING_CONTAINERS remaining containers"
    $COMPOSE_CMD ps -a
fi

# Check for any remaining volumes with this project name
REMAINING_VOLUMES=$(docker volume ls --filter "name=${COMPOSE_PROJECT_NAME}" --format '{{.Name}}' | wc -l)
if [ "$REMAINING_VOLUMES" -eq 0 ]; then
    success "All volumes removed (PostgreSQL & Redis data cleared)"
else
    warn "Found $REMAINING_VOLUMES remaining volumes:"
    docker volume ls --filter "name=${COMPOSE_PROJECT_NAME}"

    read -p "Do you want to force remove these volumes? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume ls --filter "name=${COMPOSE_PROJECT_NAME}" --format '{{.Name}}' | xargs -r docker volume rm
        success "Volumes force removed"
    fi
fi

# Optional: Remove .env files
echo ""
read -p "Do you want to remove .env files? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f .env ]; then
        rm .env
        success "Removed .env"
    fi
    if [ -f frontend/.env ]; then
        rm frontend/.env
        success "Removed frontend/.env"
    fi
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  Cleanup Complete!${NC}"
echo "=========================================="
echo ""
echo "To set up the environment again, run:"
echo "  ./start.sh"
echo ""
