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
echo "Ports:   E2E Backend=${KOULU_E2E_BACKEND_PORT} E2E Frontend=${KOULU_E2E_FRONTEND_PORT}"
echo "         Dev Backend=${KOULU_BACKEND_PORT} Dev Frontend=${KOULU_FRONTEND_PORT}"
echo ""

PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
E2E_DIR="${PROJECT_ROOT}/tests/e2e"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"
POSTGRES_CONTAINER="${KOULU_VOLUME_PREFIX:-koulu}_postgres"
REDIS_CONTAINER="${KOULU_VOLUME_PREFIX:-koulu}_redis"
E2E_DB_NAME="koulu_e2e"
E2E_BACKEND_PID=""
E2E_FRONTEND_PID=""

# Cleanup function — kills E2E backend and frontend on exit (success or failure)
cleanup() {
    if [ -n "$E2E_FRONTEND_PID" ] && kill -0 "$E2E_FRONTEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}Stopping E2E frontend (PID ${E2E_FRONTEND_PID})...${NC}"
        kill "$E2E_FRONTEND_PID" 2>/dev/null || true
        wait "$E2E_FRONTEND_PID" 2>/dev/null || true
    fi
    if [ -n "$E2E_BACKEND_PID" ] && kill -0 "$E2E_BACKEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}Stopping E2E backend (PID ${E2E_BACKEND_PID})...${NC}"
        kill "$E2E_BACKEND_PID" 2>/dev/null || true
        wait "$E2E_BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$E2E_FRONTEND_PID" ] || [ -n "$E2E_BACKEND_PID" ]; then
        echo -e "${GREEN}E2E servers stopped${NC}"
    fi
}
trap cleanup EXIT

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

# ============================================================================
# Step 1: Check Docker infrastructure services
# ============================================================================
echo -e "${YELLOW}Step 1: Checking Docker Services${NC}"
echo "-----------------------------------"

ALL_OK=true
check_compose_service "postgres" || ALL_OK=false
check_compose_service "redis" || ALL_OK=false
check_compose_service "mailhog" || ALL_OK=false

echo ""

if [ "$ALL_OK" = false ]; then
    echo -e "${RED}Docker services not running!${NC}"
    echo "  Fix: docker compose up -d"
    exit 1
fi

# ============================================================================
# Step 2: Drop and recreate E2E database (clean slate with fresh seed data)
# ============================================================================
echo -e "${YELLOW}Step 2: Recreating E2E Database (${E2E_DB_NAME})${NC}"
echo "-----------------------------------"

# Terminate existing connections and drop the database
docker exec "${POSTGRES_CONTAINER}" psql -U koulu -d postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '${E2E_DB_NAME}' AND pid <> pg_backend_pid();
" > /dev/null 2>&1 || true

echo -n "Dropping database ${E2E_DB_NAME}... "
docker exec "${POSTGRES_CONTAINER}" psql -U koulu -d postgres -c "DROP DATABASE IF EXISTS ${E2E_DB_NAME};" > /dev/null 2>&1
echo -e "${GREEN}Done${NC}"

echo -n "Creating database ${E2E_DB_NAME}... "
docker exec "${POSTGRES_CONTAINER}" psql -U koulu -d postgres -c "CREATE DATABASE ${E2E_DB_NAME} OWNER koulu;" > /dev/null 2>&1
echo -e "${GREEN}Created${NC}"

# ============================================================================
# Step 3: Run migrations on E2E database (includes seed data)
# ============================================================================
echo -e "${YELLOW}Step 3: Running Migrations on E2E Database${NC}"
echo "-----------------------------------"

E2E_DATABASE_URL="postgresql+asyncpg://koulu:koulu_dev_password@localhost:${KOULU_PG_PORT}/${E2E_DB_NAME}"

echo "Running alembic upgrade head..."
cd "${PROJECT_ROOT}" && DATABASE_URL="${E2E_DATABASE_URL}" python -m alembic upgrade head
echo -e "${GREEN}Migrations complete (includes seed data)${NC}"
echo ""

# ============================================================================
# Step 5: Flush Redis (clear rate limits)
# ============================================================================
echo -e "${YELLOW}Step 5: Clearing Redis (rate limits)${NC}"
echo "-----------------------------------"
if docker exec "${REDIS_CONTAINER}" redis-cli FLUSHALL > /dev/null 2>&1; then
    echo -e "${GREEN}Redis flushed${NC}"
else
    echo -e "${RED}Failed to flush Redis${NC}"
    exit 1
fi
echo ""

# ============================================================================
# Step 6: Setup Node environment
# ============================================================================
echo -e "${YELLOW}Step 6: Setting up Node.js${NC}"
echo "-----------------------------------"
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

# ============================================================================
# Step 7: Start E2E backend on separate port
# ============================================================================
echo -e "${YELLOW}Step 7: Starting E2E Backend (port ${KOULU_E2E_BACKEND_PORT})${NC}"
echo "-----------------------------------"

# Kill any stale E2E backend process (DB was just recreated, old connections are invalid)
STALE_PID=$(lsof -ti :${KOULU_E2E_BACKEND_PORT} 2>/dev/null || true)
if [ -n "$STALE_PID" ]; then
    echo -e "${YELLOW}Killing stale process on port ${KOULU_E2E_BACKEND_PORT} (PID ${STALE_PID})${NC}"
    kill $STALE_PID 2>/dev/null || true
    sleep 1
    # Force kill if still alive
    kill -9 $STALE_PID 2>/dev/null || true
    sleep 1
fi

E2E_BACKEND_LOG="${PROJECT_ROOT}/tests/e2e/e2e-backend.log"
DATABASE_URL="${E2E_DATABASE_URL}" \
    SMTP_HOST="localhost" \
    SMTP_PORT="${KOULU_MAIL_SMTP_PORT}" \
    REDIS_URL="redis://localhost:${KOULU_REDIS_PORT}/0" \
    FRONTEND_URL="http://localhost:${KOULU_E2E_FRONTEND_PORT}" \
    DB_POOL_SIZE="10" \
    DB_MAX_OVERFLOW="20" \
    uvicorn src.main:app \
    --host 0.0.0.0 \
    --port "${KOULU_E2E_BACKEND_PORT}" \
    > "${E2E_BACKEND_LOG}" 2>&1 &
E2E_BACKEND_PID=$!
echo "E2E backend PID: ${E2E_BACKEND_PID}"
echo "Log: ${E2E_BACKEND_LOG}"

# Wait for backend to become healthy
echo -n "Waiting for health check"
for i in $(seq 1 30); do
    if curl -sf "http://localhost:${KOULU_E2E_BACKEND_PORT}/health" > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}E2E backend ready${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ "$i" -eq 30 ]; then
        echo ""
        echo -e "${RED}E2E backend failed to start within 30s${NC}"
        echo "Check log: ${E2E_BACKEND_LOG}"
        exit 1
    fi
done
echo ""

# ============================================================================
# Step 8: Start E2E frontend on separate port (points at E2E backend)
# ============================================================================
echo -e "${YELLOW}Step 8: Starting E2E Frontend (port ${KOULU_E2E_FRONTEND_PORT})${NC}"
echo "-----------------------------------"

# Kill any stale E2E frontend process
STALE_FE_PID=$(lsof -ti :${KOULU_E2E_FRONTEND_PORT} 2>/dev/null || true)
if [ -n "$STALE_FE_PID" ]; then
    echo -e "${YELLOW}Killing stale process on port ${KOULU_E2E_FRONTEND_PORT} (PID ${STALE_FE_PID})${NC}"
    kill $STALE_FE_PID 2>/dev/null || true
    sleep 1
    kill -9 $STALE_FE_PID 2>/dev/null || true
    sleep 1
fi

E2E_FRONTEND_LOG="${PROJECT_ROOT}/tests/e2e/e2e-frontend.log"
(cd "${FRONTEND_DIR}" && \
    VITE_API_URL="http://localhost:${KOULU_E2E_BACKEND_PORT}/api/v1" \
    npx vite --port "${KOULU_E2E_FRONTEND_PORT}" --host \
    > "${E2E_FRONTEND_LOG}" 2>&1) &
E2E_FRONTEND_PID=$!
echo "E2E frontend PID: ${E2E_FRONTEND_PID}"
echo "Log: ${E2E_FRONTEND_LOG}"

# Wait for frontend to become ready
echo -n "Waiting for frontend"
for i in $(seq 1 30); do
    if curl -sf "http://localhost:${KOULU_E2E_FRONTEND_PORT}" > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}E2E frontend ready${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ "$i" -eq 30 ]; then
        echo ""
        echo -e "${RED}E2E frontend failed to start within 30s${NC}"
        echo "Check log: ${E2E_FRONTEND_LOG}"
        exit 1
    fi
done
echo ""

# ============================================================================
# Step 9: Run Playwright tests
# ============================================================================
echo -e "${YELLOW}Step 9: Running Playwright Tests${NC}"
echo "-----------------------------------"
cd "${E2E_DIR}"

# Export environment variables for Playwright — point at E2E servers
export BASE_URL="http://localhost:${KOULU_E2E_FRONTEND_PORT}"
export API_URL="http://localhost:${KOULU_E2E_BACKEND_PORT}/api/v1"
export MAILHOG_URL="http://localhost:${KOULU_MAIL_WEB_PORT}"
export REDIS_CONTAINER="${REDIS_CONTAINER}"
export POSTGRES_CONTAINER="${POSTGRES_CONTAINER}"
export E2E_DB_NAME="${E2E_DB_NAME}"

echo "Test environment:"
echo "  BASE_URL=${BASE_URL}"
echo "  API_URL=${API_URL}"
echo "  MAILHOG_URL=${MAILHOG_URL}"
echo ""

# Retry logic: up to 3 attempts, stop on first success
MAX_ATTEMPTS=3
EXIT_CODE=1

set +e
for ATTEMPT in $(seq 1 $MAX_ATTEMPTS); do
    if [ $ATTEMPT -gt 1 ]; then
        echo ""
        echo -e "${YELLOW}--- Retry $ATTEMPT of $MAX_ATTEMPTS ---${NC}"
        echo ""
    fi

    if [ $# -eq 0 ]; then
        echo "Running all E2E tests..."
        echo ""
        npx playwright test
        EXIT_CODE=$?
    else
        echo "Running: npx playwright test $@"
        echo ""
        npx playwright test "$@"
        EXIT_CODE=$?
    fi

    if [ $EXIT_CODE -eq 0 ]; then
        break
    fi

    if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
        echo ""
        echo -e "${YELLOW}Attempt $ATTEMPT failed — retrying...${NC}"
    fi
done
set -e

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    if [ $ATTEMPT -gt 1 ]; then
        echo -e "${GREEN}======================================${NC}"
        echo -e "${GREEN}   All E2E tests passed! (attempt $ATTEMPT of $MAX_ATTEMPTS)${NC}"
        echo -e "${GREEN}======================================${NC}"
    else
        echo -e "${GREEN}======================================${NC}"
        echo -e "${GREEN}   All E2E tests passed!${NC}"
        echo -e "${GREEN}======================================${NC}"
    fi
else
    echo -e "${RED}======================================${NC}"
    echo -e "${RED}   E2E tests failed after $MAX_ATTEMPTS attempts${NC}"
    echo -e "${RED}======================================${NC}"
    echo ""
    echo "To view the HTML report:"
    echo "  cd tests/e2e && npx playwright show-report"
    echo ""
    echo "To debug a specific test:"
    echo "  cd tests/e2e && npx playwright test <test-file> --debug"
fi

exit $EXIT_CODE
