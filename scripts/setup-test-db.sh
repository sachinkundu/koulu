#!/bin/bash
# Setup test database for pytest
# Usage: ./scripts/setup-test-db.sh
#
# This script:
# 1. Checks if PostgreSQL container is running
# 2. Waits for it to be healthy
# 3. Creates koulu_test database if it doesn't exist
#
# For CI: Run this before pytest

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/project-env.sh"

DB_USER="koulu"
TEST_DB="koulu_test"

echo "Setting up test database..."

# Check if the postgres service is running for this compose project
if ! docker compose ps --status running --format '{{.Service}}' 2>/dev/null | grep -q "^postgres$"; then
    echo "PostgreSQL service is not running."
    echo "   Run: docker compose up -d"
    exit 1
fi

# Wait for PostgreSQL to be healthy (max 30 seconds)
echo "Waiting for PostgreSQL to be ready..."
ATTEMPTS=0
MAX_ATTEMPTS=30
until docker compose exec -T postgres pg_isready -U ${DB_USER} > /dev/null 2>&1; do
    ATTEMPTS=$((ATTEMPTS + 1))
    if [ $ATTEMPTS -ge $MAX_ATTEMPTS ]; then
        echo "PostgreSQL did not become ready in time"
        exit 1
    fi
    sleep 1
done
echo "PostgreSQL is ready"

# Check if test database exists
if docker compose exec -T postgres psql -U ${DB_USER} -lqt | cut -d \| -f 1 | grep -qw ${TEST_DB}; then
    echo "Test database '${TEST_DB}' already exists"
else
    echo "Creating test database '${TEST_DB}'..."
    docker compose exec -T postgres psql -U ${DB_USER} -d postgres -c "CREATE DATABASE ${TEST_DB} OWNER ${DB_USER};"
    echo "Test database '${TEST_DB}' created"
fi

echo ""
echo "Test database setup complete!"
echo "   Run tests with: pytest tests/features/"
