#!/bin/bash
# Convenience wrapper for database seeding
# Worktree-safe: sources project-env.sh for correct container targeting.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/project-env.sh"

echo "🌱 Koulu Database Seeding"
echo "========================="
print_worktree_banner

# Check if database is running
if ! docker compose ps --status running --format '{{.Service}}' 2>/dev/null | grep -q "^postgres$"; then
    echo "⚠️  PostgreSQL is not running"
    echo "   Starting database..."
    docker compose up -d postgres
    echo "   Waiting for database to be ready..."
    sleep 3
fi

# Load environment variables
echo "📝 Loading environment variables..."
set -a
source "${PROJECT_ROOT}/.env"
set +a

# Run migrations
echo "🔄 Running migrations..."
cd "${PROJECT_ROOT}"
alembic upgrade head

# Run seed script
echo "🌱 Seeding database..."
python scripts/seed_db.py

echo ""
echo "✨ Done!"
