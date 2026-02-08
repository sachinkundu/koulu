#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Source per-project isolation variables
# ============================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/project-env.sh"

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

# ============================================
# Parse Command Line Arguments
# ============================================
TEST_TYPE="all"  # Default: run all tests
PYTEST_ARGS=()

show_usage() {
    echo "Usage: $0 [OPTIONS] [PYTEST_ARGS...]"
    echo ""
    echo "Options:"
    echo "  --unit          Run only unit tests (tests/unit/)"
    echo "  --integration   Run only integration tests (tests/features/)"
    echo "  --all           Run all tests (default)"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Run all tests"
    echo "  $0 --unit                    # Run only unit tests"
    echo "  $0 --integration             # Run only integration tests"
    echo "  $0 --integration -v          # Run integration tests with verbose output"
    echo "  $0 --unit -k test_user       # Run unit tests matching 'test_user'"
    echo ""
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            TEST_TYPE="unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            shift
            ;;
        --all)
            TEST_TYPE="all"
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            # Pass through to pytest
            PYTEST_ARGS+=("$1")
            shift
            ;;
    esac
done

# ============================================
# Setup Test Database
# ============================================
info "Setting up test database for project: ${COMPOSE_PROJECT_NAME}"

# Compute test database name using project name for isolation
# Replace hyphens with underscores for PostgreSQL compatibility
PROJECT_SAFE_NAME=$(echo "${COMPOSE_PROJECT_NAME}" | tr '-' '_')
TEST_DB_NAME="koulu_test_${PROJECT_SAFE_NAME}"

# Export for conftest.py to use
export KOULU_TEST_DB_NAME="${TEST_DB_NAME}"

# Check if Docker is running
if ! docker info &> /dev/null; then
    error "Docker daemon is not running. Please start Docker and try again."
fi

# Detect compose command
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    error "Docker Compose not found. Please install Docker Compose."
fi

# Check if postgres container is running for this project
if ! $COMPOSE_CMD ps postgres --status running &> /dev/null; then
    warn "PostgreSQL container is not running for project ${COMPOSE_PROJECT_NAME}"
    info "Starting containers..."
    $COMPOSE_CMD up -d postgres

    # Wait for PostgreSQL to be ready
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
fi

success "PostgreSQL is running"

# Check if test database exists
DB_EXISTS=$($COMPOSE_CMD exec -T postgres psql -U koulu -tAc "SELECT 1 FROM pg_database WHERE datname='${TEST_DB_NAME}'" 2>/dev/null || echo "")

if [ -z "$DB_EXISTS" ]; then
    info "Creating test database: ${TEST_DB_NAME}"
    $COMPOSE_CMD exec -T postgres psql -U koulu -c "CREATE DATABASE ${TEST_DB_NAME};" > /dev/null
    success "Test database created: ${TEST_DB_NAME}"
else
    success "Test database exists: ${TEST_DB_NAME}"
fi

echo ""

# ============================================
# Run Tests
# ============================================
info "Running ${TEST_TYPE} tests for project: ${COMPOSE_PROJECT_NAME}"
echo ""

cd "${PROJECT_ROOT}"

case $TEST_TYPE in
    unit)
        info "Test scope: Unit tests only (tests/unit/)"
        pytest tests/unit/ "${PYTEST_ARGS[@]}"
        ;;
    integration)
        info "Test scope: Integration tests only (tests/features/)"
        pytest tests/features/ "${PYTEST_ARGS[@]}"
        ;;
    all)
        info "Test scope: All tests"
        pytest tests/ "${PYTEST_ARGS[@]}"
        ;;
esac

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    success "Tests passed!"
else
    error "Tests failed with exit code ${TEST_EXIT_CODE}"
fi

exit $TEST_EXIT_CODE
