#!/usr/bin/env bash
#
# verify-phase-complete.sh
#
# Helper script to verify that a phase is complete and ready to mark done.
# Enforces the "Zero Tolerance Policy" for test failures.
#
# Usage: ./scripts/verify-phase-complete.sh [phase-name]
#
# Exit codes:
#   0 - All checks passed, phase is complete
#   1 - One or more checks failed, phase is NOT complete
#

set -e

PHASE_NAME="${1:-current phase}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "=========================================="
echo "Phase Completion Verification: $PHASE_NAME"
echo "=========================================="
echo ""

# Track overall success
ALL_PASSED=true

# Check 1: Infrastructure running
echo "✓ Checking infrastructure..."
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Infrastructure is running${NC}"
else
    echo -e "${RED}✗ Infrastructure is NOT running${NC}"
    echo "  Run: docker-compose up -d"
    ALL_PASSED=false
fi
echo ""

# Check 2: Test database exists
echo "✓ Checking test database..."
if docker exec koulu-postgres psql -U koulu -c "\l" 2>/dev/null | grep -q "koulu_test"; then
    echo -e "${GREEN}✓ Test database exists${NC}"
else
    echo -e "${RED}✗ Test database does NOT exist${NC}"
    echo "  Run: docker exec koulu-postgres psql -U koulu -d postgres -c \"CREATE DATABASE koulu_test OWNER koulu;\""
    ALL_PASSED=false
fi
echo ""

# Check 3: BDD tests - MUST show 0 failed
echo "✓ Running BDD tests (CRITICAL: must show '0 failed')..."
cd "$PROJECT_DIR"

# Capture pytest output
PYTEST_OUTPUT=$(pytest tests/features/ --tb=short 2>&1) || true
echo "$PYTEST_OUTPUT"

# Check for "failed" in output
if echo "$PYTEST_OUTPUT" | grep -q " 0 failed"; then
    echo -e "${GREEN}✓ BDD tests: 0 failed (PASS)${NC}"
elif echo "$PYTEST_OUTPUT" | grep -q " [1-9][0-9]* failed"; then
    # Extract failed count
    FAILED_COUNT=$(echo "$PYTEST_OUTPUT" | grep -oP '\d+ failed' | grep -oP '^\d+' | head -1)
    echo -e "${RED}✗ BDD tests: $FAILED_COUNT failed (FAIL)${NC}"
    echo ""
    echo -e "${RED}⛔ CRITICAL FAILURE ⛔${NC}"
    echo "  pytest output shows '$FAILED_COUNT failed'"
    echo "  This means the phase is NOT complete."
    echo ""
    echo "  You MUST either:"
    echo "    1. Fix the failing tests by implementing missing code"
    echo "    2. Add @pytest.mark.skip(reason=\"Phase X: condition\") to tests for future phases"
    echo ""
    echo "  NEVER mark work complete with failing tests."
    echo "  'These are Phase 2-4 scenarios' is NOT an excuse."
    echo ""
    ALL_PASSED=false
else
    # Couldn't determine failed count - treat as failure
    echo -e "${YELLOW}⚠ Could not determine test status from output${NC}"
    ALL_PASSED=false
fi

# Check for warnings
if echo "$PYTEST_OUTPUT" | grep -q " 0 warnings"; then
    echo -e "${GREEN}✓ BDD tests: 0 warnings (PASS)${NC}"
else
    WARNING_COUNT=$(echo "$PYTEST_OUTPUT" | grep -oP '\d+ warnings' | grep -oP '^\d+' | head -1)
    if [ -n "$WARNING_COUNT" ]; then
        echo -e "${RED}✗ BDD tests: $WARNING_COUNT warnings (FAIL)${NC}"
        echo "  Fix warnings at source, don't suppress them"
        ALL_PASSED=false
    fi
fi
echo ""

# Check 4: Coverage
echo "✓ Running Python verification (coverage must be ≥80%)..."
if ./scripts/verify.sh 2>&1 | tee /tmp/verify-output.txt; then
    # Check coverage from output
    COVERAGE=$(grep "TOTAL" /tmp/verify-output.txt | awk '{print $NF}' | sed 's/%//')
    if [ -n "$COVERAGE" ]; then
        if [ "${COVERAGE%.*}" -ge 80 ]; then
            echo -e "${GREEN}✓ Coverage: ${COVERAGE}% (≥80%, PASS)${NC}"
        else
            echo -e "${RED}✗ Coverage: ${COVERAGE}% (<80%, FAIL)${NC}"
            echo "  Add unit tests for untested domain logic"
            ALL_PASSED=false
        fi
    else
        echo -e "${GREEN}✓ Verification scripts passed${NC}"
    fi
else
    echo -e "${RED}✗ Verification scripts failed${NC}"
    ALL_PASSED=false
fi
echo ""

# Final verdict
echo "=========================================="
if [ "$ALL_PASSED" = true ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    echo ""
    echo "Phase '$PHASE_NAME' is complete and ready to mark done."
    echo "You may proceed with:"
    echo "  - Marking task complete"
    echo "  - Creating git commit"
    echo "  - Pushing to remote"
    echo ""
    exit 0
else
    echo -e "${RED}✗ CHECKS FAILED${NC}"
    echo ""
    echo "Phase '$PHASE_NAME' is NOT complete."
    echo ""
    echo "⛔ DO NOT:"
    echo "  - Mark task complete"
    echo "  - Create git commit"
    echo "  - Push to remote"
    echo ""
    echo "✓ INSTEAD:"
    echo "  - Fix the failing checks listed above"
    echo "  - Re-run this script to verify"
    echo "  - Only proceed when all checks pass"
    echo ""
    exit 1
fi
