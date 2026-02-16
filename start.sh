#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Source per-project isolation variables
# ============================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/scripts/project-env.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Check if a command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        error "$1 is not installed. $2"
    fi
}

# Compare versions (returns 0 if $1 >= $2)
version_gte() {
    [ "$(printf '%s\n' "$2" "$1" | sort -V | head -n1)" = "$2" ]
}

# Extract major.minor version
get_version() {
    echo "$1" | grep -oE '[0-9]+\.[0-9]+' | head -1
}

echo ""
echo "=========================================="
echo "  Koulu Development Environment Setup"
echo "  Project: ${COMPOSE_PROJECT_NAME}"
echo "=========================================="
echo ""

# ============================================
# STEP 0: Install Missing Prerequisites
# ============================================
source "${SCRIPT_DIR}/scripts/install-prereqs.sh"

# ============================================
# STEP 1: Check Prerequisites
# ============================================
info "Checking prerequisites..."

# Check Python
check_command python3 "Please install Python 3.11+ from https://www.python.org/downloads/"
PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
if ! version_gte "$PYTHON_VERSION" "3.11"; then
    error "Python 3.11+ required, found $PYTHON_VERSION. Please upgrade Python."
fi
success "Python $PYTHON_VERSION"

# Check pip
check_command pip3 "Please install pip: python3 -m ensurepip --upgrade"
success "pip installed"

# Check Node.js
check_command node "Please install Node.js 18+ from https://nodejs.org/"
NODE_VERSION=$(node --version | grep -oE '[0-9]+\.[0-9]+')
if ! version_gte "$NODE_VERSION" "18.0"; then
    error "Node.js 18+ required, found $NODE_VERSION. Please upgrade Node.js."
fi
success "Node.js $NODE_VERSION"

# Check npm
check_command npm "Please install npm (comes with Node.js)"
success "npm installed"

# Check Docker
check_command docker "Please install Docker from https://docs.docker.com/get-docker/"
success "Docker installed"

# Check Docker Compose (v2 style)
if docker compose version &> /dev/null; then
    success "Docker Compose (v2) installed"
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    success "Docker Compose (v1) installed"
    COMPOSE_CMD="docker-compose"
else
    error "Docker Compose not found. Please install Docker Compose."
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    error "Docker daemon is not running. Please start Docker and try again."
fi
success "Docker daemon is running"

echo ""

# ============================================
# STEP 2: Setup Environment Files
# ============================================
info "Setting up environment files..."

# Generate .env with computed ports
if [ -f .env.example ]; then
    if [ ! -f .env ]; then
        cp .env.example .env
        success "Created .env from .env.example"
    else
        success ".env already exists"
    fi

    # Patch port-dependent values in .env to match computed ports
    sed -i "s|^KOULU_PG_PORT=.*|KOULU_PG_PORT=${KOULU_PG_PORT}|" .env
    sed -i "s|^KOULU_REDIS_PORT=.*|KOULU_REDIS_PORT=${KOULU_REDIS_PORT}|" .env
    sed -i "s|^KOULU_MAIL_SMTP_PORT=.*|KOULU_MAIL_SMTP_PORT=${KOULU_MAIL_SMTP_PORT}|" .env
    sed -i "s|^KOULU_MAIL_WEB_PORT=.*|KOULU_MAIL_WEB_PORT=${KOULU_MAIL_WEB_PORT}|" .env
    sed -i "s|^DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://koulu:koulu_dev_password@localhost:${KOULU_PG_PORT}/koulu|" .env
    sed -i "s|^REDIS_URL=.*|REDIS_URL=redis://localhost:${KOULU_REDIS_PORT}/0|" .env
    sed -i "s|^MAIL_PORT=.*|MAIL_PORT=${KOULU_MAIL_SMTP_PORT}|" .env
    sed -i "s|^FRONTEND_URL=.*|FRONTEND_URL=http://localhost:${KOULU_FRONTEND_PORT}|" .env
    success "Patched .env with computed ports (PG:${KOULU_PG_PORT} Redis:${KOULU_REDIS_PORT} Mail:${KOULU_MAIL_SMTP_PORT}/${KOULU_MAIL_WEB_PORT} Frontend:${KOULU_FRONTEND_PORT})"
else
    error ".env.example not found. Cannot create .env file."
fi

if [ -f frontend/.env.example ]; then
    if [ ! -f frontend/.env ]; then
        cp frontend/.env.example frontend/.env
        success "Created frontend/.env from frontend/.env.example"
    else
        success "frontend/.env already exists"
    fi

    # Patch frontend .env with correct backend API URL and project name
    sed -i "s|^VITE_API_URL=.*|VITE_API_URL=http://localhost:${KOULU_BACKEND_PORT}/api/v1|" frontend/.env

    # Add or update project name for UI display
    if grep -q "^VITE_PROJECT_NAME=" frontend/.env 2>/dev/null; then
        sed -i "s|^VITE_PROJECT_NAME=.*|VITE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}|" frontend/.env
    else
        echo "VITE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}" >> frontend/.env
    fi

    success "Patched frontend/.env with backend URL (http://localhost:${KOULU_BACKEND_PORT}/api/v1) and project name (${COMPOSE_PROJECT_NAME})"
else
    warn "frontend/.env.example not found. Skipping frontend .env setup."
fi

echo ""

# ============================================
# STEP 3: Start Docker Containers
# ============================================
info "Starting Docker containers (project: ${COMPOSE_PROJECT_NAME})..."

# Remove any stale containers with our names (e.g., left over from E2E tests or a different compose project).
# Data is preserved in named volumes — only the container instances are removed.
VOLUME_PREFIX="${KOULU_VOLUME_PREFIX:-koulu}"
for svc in postgres redis mailhog; do
    cname="${VOLUME_PREFIX}_${svc}"
    if docker container inspect "$cname" &>/dev/null 2>&1; then
        warn "Removing stale container: $cname"
        docker rm -f "$cname" 2>/dev/null || true
    fi
done

$COMPOSE_CMD up -d --remove-orphans
success "Containers started"

# Wait for PostgreSQL to be healthy
info "Waiting for PostgreSQL to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0
until $COMPOSE_CMD exec -T postgres pg_isready -U koulu &> /dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        error "PostgreSQL failed to start after $MAX_RETRIES attempts"
    fi
    sleep 1
done
success "PostgreSQL is ready"

# Wait for Redis to be healthy
info "Waiting for Redis to be ready..."
RETRY_COUNT=0
until $COMPOSE_CMD exec -T redis redis-cli ping &> /dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        error "Redis failed to start after $MAX_RETRIES attempts"
    fi
    sleep 1
done
success "Redis is ready"

success "All containers are running"
echo ""

# ============================================
# STEP 4: Install Python Dependencies
# ============================================
info "Installing Python dependencies..."

# Check if we're in a virtual environment
if [ -z "${VIRTUAL_ENV:-}" ]; then
    warn "No virtual environment detected. Consider using one:"
    warn "  python3 -m venv venv && source venv/bin/activate"
fi

pip3 install -e ".[dev]" --quiet
success "Python dependencies installed"
echo ""

# ============================================
# STEP 5: Run Database Migrations
# ============================================
info "Running database migrations..."

if command -v alembic &> /dev/null; then
    alembic upgrade head
    success "Database migrations complete"
else
    # Try with python -m
    python3 -m alembic upgrade head
    success "Database migrations complete"
fi
echo ""

# ============================================
# STEP 5b: Seed Database (optional)
# ============================================
if [ -f scripts/seed_db.py ]; then
    read -p "$(echo -e "${YELLOW}[INFO]${NC} Seed database with sample data? [y/N] ")" -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "Seeding database..."
        python3 scripts/seed_db.py
        success "Database seeded"
    else
        info "Skipping database seeding"
    fi
    echo ""
fi

# ============================================
# STEP 6: Install Frontend Dependencies
# ============================================
info "Installing frontend dependencies..."

cd frontend
npm install --silent
cd ..
success "Frontend dependencies installed"
echo ""

# ============================================
# DONE
# ============================================
echo "=========================================="
echo -e "${GREEN}  Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Project: ${COMPOSE_PROJECT_NAME}"
echo "Ports:   PG=${KOULU_PG_PORT} Redis=${KOULU_REDIS_PORT} Mail=${KOULU_MAIL_SMTP_PORT}/${KOULU_MAIL_WEB_PORT}"
echo "         Backend=${KOULU_BACKEND_PORT} Frontend=${KOULU_FRONTEND_PORT}"
echo ""
echo "To start the application, run in separate terminals:"
echo ""
echo -e "  ${BLUE}Backend:${NC}"
echo "    uvicorn src.main:app --reload --host 0.0.0.0 --port ${KOULU_BACKEND_PORT}"
echo ""
echo -e "  ${BLUE}Frontend:${NC}"
echo "    cd frontend && npm run dev -- --port ${KOULU_FRONTEND_PORT}"
echo ""
echo "Access points:"
echo "  - Frontend:    http://localhost:${KOULU_FRONTEND_PORT}"
echo "  - Backend API: http://localhost:${KOULU_BACKEND_PORT}"
echo "  - API Docs:    http://localhost:${KOULU_BACKEND_PORT}/docs"
echo "  - MailHog:     http://localhost:${KOULU_MAIL_WEB_PORT}"
echo ""

# ============================================
# STEP 7: Optional - Start Services
# ============================================
read -p "Do you want to start both frontend and backend now? (Y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    info "Starting frontend and backend services..."
    echo ""

    # PIDs for cleanup
    BACKEND_PID=""
    FRONTEND_PID=""

    # Sticky header is 10 lines tall
    HEADER_LINE_COUNT=10

    # Cleanup function — reset scroll region before exiting
    cleanup() {
        echo -en "\033[r"          # reset scroll region
        echo -en "\033[2J\033[H"   # clear screen, cursor to top
        info "Shutting down services..."

        if [ -n "$BACKEND_PID" ]; then
            kill $BACKEND_PID 2>/dev/null || true
            wait $BACKEND_PID 2>/dev/null || true
        fi

        if [ -n "$FRONTEND_PID" ]; then
            kill $FRONTEND_PID 2>/dev/null || true
            wait $FRONTEND_PID 2>/dev/null || true
        fi

        success "Services stopped"
        exit 0
    }

    # Recompute scroll region on terminal resize
    handle_resize() {
        local term_lines
        term_lines=$(tput lines 2>/dev/null || echo 24)
        # Save cursor, update scroll region, restore cursor
        echo -en "\033[s\033[$((HEADER_LINE_COUNT + 1));${term_lines}r\033[u"
    }

    # Trap signals
    trap cleanup SIGINT SIGTERM
    trap handle_resize SIGWINCH

    # Start backend
    (
        while IFS= read -r line; do
            echo -e "${BLUE}[BACKEND]${NC} $line"
        done < <(uvicorn src.main:app --reload --host 0.0.0.0 --port ${KOULU_BACKEND_PORT} 2>&1)
    ) &
    BACKEND_PID=$!

    # Give backend a moment to start
    sleep 2

    # Start frontend
    (
        cd frontend
        while IFS= read -r line; do
            echo -e "${GREEN}[FRONTEND]${NC} $line"
        done < <(npm run dev -- --port ${KOULU_FRONTEND_PORT} 2>&1)
    ) &
    FRONTEND_PID=$!

    # Let services emit initial startup output before taking over the screen
    sleep 3

    # ── Sticky header: URLs pinned at top, logs scroll below ──
    TERM_LINES=$(tput lines 2>/dev/null || echo 24)

    # Clear screen, cursor to row 1
    echo -en "\033[2J\033[H"

    # Print the 10-line header
    echo "══════════════════════════════════════════════════"
    echo -e "  ${GREEN}Koulu Development Environment${NC}"
    echo ""
    echo -e "  Frontend:     ${YELLOW}http://localhost:${KOULU_FRONTEND_PORT}${NC}"
    echo -e "  Backend API:  ${YELLOW}http://localhost:${KOULU_BACKEND_PORT}${NC}"
    echo -e "  API Docs:     ${YELLOW}http://localhost:${KOULU_BACKEND_PORT}/docs${NC}"
    echo -e "  MailHog:      ${YELLOW}http://localhost:${KOULU_MAIL_WEB_PORT}${NC}"
    echo ""
    echo -e "  ${BLUE}Ctrl+C to stop all services${NC}"
    echo "══════════════════════════════════════════════════"

    # Confine scrolling to lines below the header
    echo -en "\033[$((HEADER_LINE_COUNT + 1));${TERM_LINES}r"

    # Move cursor into the scroll region
    echo -en "\033[$((HEADER_LINE_COUNT + 1));1H"

    # Wait for both processes
    wait
fi
