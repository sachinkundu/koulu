# E2E Tests - Quick Start

## TL;DR - Run All Tests

```bash
./scripts/run-e2e-tests.sh
```

That's it! The script automatically:
- ✅ Checks all prerequisites (Docker, backend, frontend)
- ✅ Flushes Redis (clears rate limits)
- ✅ Sets up Node.js 20
- ✅ Runs all Playwright tests

---

## Common Usage

### Run all tests
```bash
./scripts/run-e2e-tests.sh
```

### Run specific test file
```bash
./scripts/run-e2e-tests.sh specs/identity/login.spec.ts
```

### Run tests matching a pattern
```bash
./scripts/run-e2e-tests.sh --grep "login"
```

### Debug mode (step through test)
```bash
./scripts/run-e2e-tests.sh --debug specs/identity/login.spec.ts
```

### UI mode (interactive)
```bash
./scripts/run-e2e-tests.sh --ui
```

### Headed mode (see browser)
```bash
./scripts/run-e2e-tests.sh --headed
```

---

## Manual Steps (if you prefer)

### 1. Start services

```bash
# Start Docker containers
docker compose up -d

# Start backend (in separate terminal)
cd backend
uvicorn src.main:app --host 0.0.0.0 --port 8000

# Start frontend (in separate terminal)
cd frontend
npm run dev
```

### 2. Run tests

```bash
# Flush Redis (clear rate limits)
docker exec koulu-redis redis-cli FLUSHALL

# Setup Node.js
source "$HOME/.config/nvm/nvm.sh"
nvm use 20

# Run tests
cd tests/e2e
npx playwright test
```

---

## Debugging Failed Tests

### View HTML report
```bash
cd tests/e2e
npx playwright show-report
```

### View trace for failed test
```bash
cd tests/e2e
npx playwright show-trace test-results/.../trace.zip
```

### Debug specific test
```bash
cd tests/e2e
npx playwright test specs/identity/login.spec.ts --debug
```

---

## Prerequisites (one-time setup)

### Install Playwright
```bash
cd tests/e2e
npm install
npx playwright install chromium
```

### Install Node.js 20
```bash
# Using nvm (recommended)
nvm install 20
nvm use 20
```

---

## Troubleshooting

### "Connection refused" errors
**Problem:** Backend or frontend not running

**Fix:**
```bash
# Check backend
curl http://localhost:8000/health

# Check frontend
curl http://localhost:5173

# If not running, start them (see "Start services" above)
```

### "Rate limit exceeded" errors
**Problem:** Redis has cached rate limit data

**Fix:**
```bash
docker exec koulu-redis redis-cli FLUSHALL
```

### "Browser not found" errors
**Problem:** Playwright browsers not installed

**Fix:**
```bash
cd tests/e2e
npx playwright install chromium
```

### "Node version" errors
**Problem:** Wrong Node.js version

**Fix:**
```bash
source "$HOME/.config/nvm/nvm.sh"
nvm use 20
```

---

## CI/CD

In CI, the script automatically detects CI environment and:
- Uses 2 workers (instead of 4)
- Enables retries (2 attempts)

```bash
# CI usage (same command!)
./scripts/run-e2e-tests.sh
```

---

## Related Files

- `scripts/run-e2e-tests.sh` - Main test runner script
- `playwright.config.ts` - Playwright configuration
- `specs/` - Test files
- `fixtures/` - Page objects and helpers
- `.claude/skills/e2e-test.md` - Detailed E2E testing guide
