#!/bin/bash
# Convenience wrapper for database seeding

set -e

echo "🌱 Koulu Database Seeding"
echo "========================="
echo ""

# Check if database is running
if ! docker compose ps postgres | grep -q "running"; then
    echo "⚠️  PostgreSQL is not running"
    echo "   Starting database..."
    docker compose up -d postgres
    echo "   Waiting for database to be ready..."
    sleep 3
fi

# Load environment variables
echo "📝 Loading environment variables..."
set -a
source .env
set +a

# Run migrations
echo "🔄 Running migrations..."
alembic upgrade head

# Run seed script
echo "🌱 Seeding database..."
python scripts/seed_db.py

echo ""
echo "✨ Done!"
