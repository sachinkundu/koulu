#!/usr/bin/env bash
set -e

# Deployability Check: Verifies features have UI components

FEATURE=$1
if [ -z "$FEATURE" ]; then
    echo "Usage: ./scripts/check-deployability.sh <feature-name>"
    exit 1
fi

echo "🔍 Checking deployability for: $FEATURE"

# Check backend exists
if [ ! -d "src/$FEATURE" ]; then
    echo "❌ Backend not found: src/$FEATURE"
    exit 1
fi
echo "✅ Backend found: src/$FEATURE"

# Check API endpoints exist
API_FILES=$(find "src/$FEATURE/interface/api" -name "*_controller.py" 2>/dev/null | wc -l)
if [ "$API_FILES" -eq 0 ]; then
    echo "❌ No API controllers found in src/$FEATURE/interface/api"
    exit 1
fi
echo "✅ API endpoints found: $API_FILES controllers"

# Check frontend exists
FRONTEND_DIR="frontend/src/features/$FEATURE"
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "⚠️  WARNING: No frontend found at $FRONTEND_DIR"
    echo ""
    echo "📋 Analysis:"
    echo "   ✅ Backend implemented"
    echo "   ❌ Frontend missing"
    echo ""
    echo "🛠️  This feature is NOT deployable (no user-facing UI)"
    echo ""
    echo "Next steps:"
    echo "1. If backend-only is intentional (background job, internal API):"
    echo "   - Document in docs/features/$FEATURE/*-phases.md why no UI needed"
    echo "   - Add 'Why No UI?' section to phase summary"
    echo ""
    echo "2. If UI should exist:"
    echo "   - Implement components in $FRONTEND_DIR"
    echo "   - Add routes to frontend/src/pages/"
    echo "   - Write E2E tests in tests/e2e/specs/$FEATURE/"
    echo "   - Re-run this script to verify"
    exit 1
fi

COMPONENT_FILES=$(find "$FRONTEND_DIR" -name "*.tsx" 2>/dev/null | wc -l)
if [ "$COMPONENT_FILES" -eq 0 ]; then
    echo "❌ Frontend directory exists but no .tsx components found"
    exit 1
fi
echo "✅ Frontend found: $COMPONENT_FILES components"

# Check E2E tests exist
E2E_DIR="tests/e2e/specs/$FEATURE"
if [ ! -d "$E2E_DIR" ]; then
    echo "⚠️  WARNING: No E2E tests found at $E2E_DIR"
    echo "   Frontend exists but no browser automation tests"
    echo "   Create tests with: /write-e2e-tests $FEATURE"
    # Don't fail - E2E tests can be added after feature works
fi

echo ""
echo "✅ Feature is DEPLOYABLE:"
echo "   ✅ Backend: $API_FILES controllers"
echo "   ✅ Frontend: $COMPONENT_FILES components"
echo "   ✅ Users can interact with this feature"
echo ""
echo "🚀 Ready for deployment"
