#!/bin/bash
set -e

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
echo "4️⃣  Running Tests with Coverage..."
pytest --cov=src --cov-fail-under=80

echo ""
echo "✅ All Checks Passed!"
