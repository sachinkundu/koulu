#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Koulu Development Server
# Starts backend + frontend dev servers.
# Run ./setup.sh first if this is a fresh clone.
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

echo ""
echo "=========================================="
echo "  Koulu Development Server"
echo "  Project: ${COMPOSE_PROJECT_NAME}"
echo "=========================================="
echo ""

# ============================================
# Quick sanity checks
# ============================================

# Check .env exists
if [ ! -f .env ]; then
    error ".env not found. Run ./setup.sh first."
fi

# Check Docker daemon is running
if ! docker info &> /dev/null; then
    error "Docker daemon is not running. Please start Docker and try again."
fi

# Detect Docker Compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    error "Docker Compose not found. Run ./setup.sh first."
fi

# Ensure containers are up
if ! $COMPOSE_CMD exec -T postgres pg_isready -U koulu &> /dev/null; then
    info "Docker containers not running. Starting them..."
    $COMPOSE_CMD up -d --remove-orphans

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
else
    success "Docker containers already running"
fi

echo ""

# ============================================
# Start Services
# ============================================
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
