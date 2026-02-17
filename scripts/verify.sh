#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

# =============================================================================
# Backend Verification
# =============================================================================

echo "🔍 Running Backend Verification..."

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
echo "✅ Backend Verification Passed!"

# =============================================================================
# Frontend Verification
# =============================================================================

if [ -d "${PROJECT_ROOT}/frontend" ]; then
  echo ""
  echo "🔍 Running Frontend Verification..."
  "${SCRIPT_DIR}/verify-frontend.sh"
else
  echo ""
  echo "⚠️  No frontend/ directory found, skipping frontend verification."
fi

echo ""
echo "✅ All Checks Passed (backend + frontend)!"
