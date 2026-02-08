#!/usr/bin/env bash
set -e

# Source per-project isolation variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/project-env.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}   Koulu E2E Test Runner${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo "Project: ${COMPOSE_PROJECT_NAME}"
echo "Ports:   Backend=${KOULU_BACKEND_PORT} Frontend=${KOULU_FRONTEND_PORT}"
echo ""

PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
E2E_DIR="${PROJECT_ROOT}/tests/e2e"

# Function to check if a service is running
check_service() {
    local name=$1
    local url=$2
    local check_cmd=$3

    echo -n "Checking ${name}... "
    if eval "${check_cmd}" > /dev/null 2>&1; then
        echo -e "${GREEN}Running${NC}"
        return 0
    else
        echo -e "${RED}Not running${NC}"
        return 1
    fi
}

# Function to check docker compose service
check_compose_service() {
    local service=$1
    echo -n "Checking ${service}... "
    if docker compose ps --status running --format '{{.Service}}' 2>/dev/null | grep -q "^${service}$"; then
        echo -e "${GREEN}Running${NC}"
        return 0
    else
        echo -e "${RED}Not running${NC}"
        return 1
    fi
}

echo -e "${YELLOW}Step 1: Checking Prerequisites${NC}"
echo "-----------------------------------"

# Check docker compose services
ALL_OK=true
check_compose_service "postgres" || ALL_OK=false
check_compose_service "redis" || ALL_OK=false
check_compose_service "mailhog" || ALL_OK=false

# Check backend
check_service "Backend API (port ${KOULU_BACKEND_PORT})" "http://localhost:${KOULU_BACKEND_PORT}/health" "curl -sf http://localhost:${KOULU_BACKEND_PORT}/health" || ALL_OK=false

# Check frontend
check_service "Frontend (port ${KOULU_FRONTEND_PORT})" "http://localhost:${KOULU_FRONTEND_PORT}" "curl -sf http://localhost:${KOULU_FRONTEND_PORT}" || ALL_OK=false

echo ""

if [ "$ALL_OK" = false ]; then
    echo -e "${RED}Prerequisites not met!${NC}"
    echo ""
    echo "To fix:"
    echo "  1. Start Docker containers: docker compose up -d"
    echo "  2. Start backend: uvicorn src.main:app --host 0.0.0.0 --port ${KOULU_BACKEND_PORT}"
    echo "  3. Start frontend: cd frontend && npm run dev -- --port ${KOULU_FRONTEND_PORT}"
    echo ""
    echo "Project: ${COMPOSE_PROJECT_NAME}"
    echo "Ports: Backend=${KOULU_BACKEND_PORT} Frontend=${KOULU_FRONTEND_PORT}"
    echo ""
    exit 1
fi

echo -e "${GREEN}All prerequisites met${NC}"
echo ""

# Step 2: Flush Redis (clear rate limits)
echo -e "${YELLOW}Step 2: Clearing Redis (rate limits)${NC}"
echo "-----------------------------------"
if docker compose exec -T redis redis-cli FLUSHALL > /dev/null 2>&1; then
    echo -e "${GREEN}Redis flushed${NC}"
else
    echo -e "${RED}Failed to flush Redis${NC}"
    exit 1
fi
echo ""

# Step 3: Setup Node environment
echo -e "${YELLOW}Step 3: Setting up Node.js${NC}"
echo "-----------------------------------"
# Source nvm
if [ -f "$HOME/.config/nvm/nvm.sh" ]; then
    source "$HOME/.config/nvm/nvm.sh"
    nvm use 20 > /dev/null 2>&1
    echo -e "${GREEN}Using Node $(node --version)${NC}"
elif command -v node > /dev/null 2>&1; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 20 ]; then
        echo -e "${GREEN}Using Node $(node --version)${NC}"
    else
        echo -e "${RED}Node 20+ required (found $(node --version))${NC}"
        exit 1
    fi
else
    echo -e "${RED}Node.js not found${NC}"
    exit 1
fi
echo ""

# Step 4: Run Playwright tests
echo -e "${YELLOW}Step 4: Running Playwright Tests${NC}"
echo "-----------------------------------"
cd "${E2E_DIR}"

# Export environment variables for Playwright to use computed ports
export BASE_URL="http://localhost:${KOULU_FRONTEND_PORT}"
export API_URL="http://localhost:${KOULU_BACKEND_PORT}/api/v1"
export MAILHOG_URL="http://localhost:${KOULU_MAIL_WEB_PORT}"
export REDIS_CONTAINER="${KOULU_VOLUME_PREFIX:-koulu}_redis"

echo "Test environment:"
echo "  BASE_URL=${BASE_URL}"
echo "  API_URL=${API_URL}"
echo "  MAILHOG_URL=${MAILHOG_URL}"
echo "  REDIS_CONTAINER=${REDIS_CONTAINER}"
echo ""

# Parse arguments
if [ $# -eq 0 ]; then
    # No arguments - run all tests
    echo "Running all E2E tests..."
    echo ""
    npx playwright test
else
    # Pass arguments to playwright
    echo "Running: npx playwright test $@"
    echo ""
    npx playwright test "$@"
fi

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}   All E2E tests passed!${NC}"
    echo -e "${GREEN}======================================${NC}"
else
    echo -e "${RED}======================================${NC}"
    echo -e "${RED}   E2E tests failed${NC}"
    echo -e "${RED}======================================${NC}"
    echo ""
    echo "To view the HTML report:"
    echo "  cd tests/e2e && npx playwright show-report"
    echo ""
    echo "To debug a specific test:"
    echo "  cd tests/e2e && npx playwright test <test-file> --debug"
fi

exit $EXIT_CODE
