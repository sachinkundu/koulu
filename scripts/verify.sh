#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

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
"${SCRIPT_DIR}/test.sh" --all --ignore=tests/features/identity/ --cov=src --cov-fail-under=80

echo ""
echo "✅ All Checks Passed!"
