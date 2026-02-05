#!/bin/bash
set -e

# Change to frontend directory
cd "$(dirname "$0")/../frontend"

echo "🔍 Running Frontend Verification..."

# Check Node version (Vite 5 requires Node 18+)
NODE_VERSION=$(node -v | cut -d'.' -f1 | sed 's/v//')
if [ "$NODE_VERSION" -lt 18 ]; then
  echo ""
  echo "⚠️  WARNING: Node version $(node -v) detected. Vite 5 requires Node 18+."
  echo "   Build step will be skipped. Please upgrade Node for full verification."
  echo ""
  SKIP_BUILD=true
fi

echo ""
echo "1️⃣  Linting..."
npm run lint

echo ""
echo "2️⃣  Type Checking..."
npm run typecheck

echo ""
echo "3️⃣  Running Tests..."
# Check if there are any test files before running tests
if find src -name "*.test.ts*" -o -name "*.spec.ts*" 2>/dev/null | grep -q .; then
  if [ "$NODE_VERSION" -ge 18 ]; then
    npm run test -- --run
  else
    echo "Skipping tests due to Node version < 18..."
  fi
else
  echo "No test files found, skipping..."
fi

echo ""
echo "4️⃣  Building..."
if [ "$SKIP_BUILD" = true ]; then
  echo "Skipping build due to Node version < 18..."
else
  npm run build
fi

echo ""
echo "✅ Frontend Verification Complete!"
if [ "$SKIP_BUILD" = true ]; then
  echo "   Note: Build was skipped. Upgrade to Node 18+ for full verification."
fi
