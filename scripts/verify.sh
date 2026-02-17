#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

# =============================================================================
# Phase 1: Static checks + frontend in parallel
# =============================================================================
# ruff check, ruff format, mypy, and frontend verification are all independent.
# Run them concurrently, collect exit codes, fail fast if any fail.

echo "🔍 Running static checks and frontend in parallel..."

TMPDIR_VERIFY=$(mktemp -d)
trap 'rm -rf "${TMPDIR_VERIFY}"' EXIT

# --- Background: ruff check ---
(
  echo "1️⃣  Linting (ruff)..."
  if ruff check . > "${TMPDIR_VERIFY}/ruff_check.log" 2>&1; then
    echo "  ✅ ruff check passed"
  else
    echo "  ❌ ruff check failed"
    cat "${TMPDIR_VERIFY}/ruff_check.log"
    exit 1
  fi
) &
PID_RUFF_CHECK=$!

# --- Background: ruff format ---
(
  echo "2️⃣  Formatting (ruff)..."
  if ruff format --check . > "${TMPDIR_VERIFY}/ruff_format.log" 2>&1; then
    echo "  ✅ ruff format passed"
  else
    echo "  ❌ ruff format failed"
    cat "${TMPDIR_VERIFY}/ruff_format.log"
    exit 1
  fi
) &
PID_RUFF_FORMAT=$!

# --- Background: mypy ---
(
  echo "3️⃣  Type Checking (mypy)..."
  if mypy . > "${TMPDIR_VERIFY}/mypy.log" 2>&1; then
    echo "  ✅ mypy passed"
  else
    echo "  ❌ mypy failed"
    cat "${TMPDIR_VERIFY}/mypy.log"
    exit 1
  fi
) &
PID_MYPY=$!

# --- Background: frontend ---
PID_FRONTEND=""
if [ -d "${PROJECT_ROOT}/frontend" ]; then
  (
    echo "4️⃣  Frontend Verification..."
    if "${SCRIPT_DIR}/verify-frontend.sh" > "${TMPDIR_VERIFY}/frontend.log" 2>&1; then
      echo "  ✅ frontend passed"
    else
      echo "  ❌ frontend failed"
      cat "${TMPDIR_VERIFY}/frontend.log"
      exit 1
    fi
  ) &
  PID_FRONTEND=$!
else
  echo "⚠️  No frontend/ directory found, skipping frontend verification."
fi

# --- Wait for all parallel jobs ---
FAILED=0

wait "${PID_RUFF_CHECK}" || FAILED=1
wait "${PID_RUFF_FORMAT}" || FAILED=1
wait "${PID_MYPY}" || FAILED=1
if [ -n "${PID_FRONTEND}" ]; then
  wait "${PID_FRONTEND}" || FAILED=1
fi

if [ "${FAILED}" -ne 0 ]; then
  echo ""
  echo "❌ Static checks or frontend failed. See output above."
  exit 1
fi

echo ""
echo "✅ Static checks + frontend passed!"

# =============================================================================
# Phase 2: Tests with coverage (must run after static checks pass)
# =============================================================================

echo ""
echo "5️⃣  Running Tests with Coverage..."
"${SCRIPT_DIR}/test.sh" --all --ignore=tests/features/identity/ --cov=src --cov-fail-under=80

echo ""
echo "✅ All Checks Passed (backend + frontend)!"
