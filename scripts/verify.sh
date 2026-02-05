#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔍 Running Python Verification..."

echo ""
echo "1️⃣  Linting (ruff)..."
ruff check .

echo ""
echo "2️⃣  Formatting (ruff)..."
ruff format --check .

echo ""
echo "3️⃣  Type Checking (mypy)..."
mypy .

echo ""
echo "4️⃣  Setting up test database..."
"${SCRIPT_DIR}/setup-test-db.sh"

echo ""
echo "5️⃣  Running Tests with Coverage..."
pytest --cov=src --cov-fail-under=80

echo ""
echo "✅ All Checks Passed!"
