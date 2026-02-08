# Scripts

This directory contains utility scripts for managing the Koulu development environment.

## test.sh

**Multi-agent safe test runner** with automatic test database setup.

### Features

- ✅ **Multi-agent isolation**: Each agent gets their own test database (e.g., `koulu_test_agent1`, `koulu_test_agent2`)
- ✅ **Idempotent**: Checks if test database exists before creating
- ✅ **Flexible**: Run all tests, unit tests only, or integration tests only
- ✅ **Pass-through**: All extra arguments are passed to pytest

### Usage

```bash
# Run all tests (default)
./scripts/test.sh

# Run only unit tests
./scripts/test.sh --unit

# Run only integration tests (BDD)
./scripts/test.sh --integration

# Pass additional pytest arguments
./scripts/test.sh --integration -v              # Verbose output
./scripts/test.sh --unit -k test_user           # Run tests matching pattern
./scripts/test.sh --integration -x              # Stop on first failure
./scripts/test.sh --unit --pdb                  # Drop into debugger on failure

# Combine options
./scripts/test.sh --integration -v --tb=short --ignore=tests/features/identity/
```

### How It Works

1. **Reads project isolation variables** from `project-env.sh`
2. **Creates project-specific test database** (e.g., `koulu_test_cckoulu`)
3. **Exports `KOULU_TEST_DB_NAME`** for `conftest.py` to use
4. **Runs pytest** with specified scope (unit/integration/all)

### Multi-Agent Safety

Each Claude Code agent running on the same machine gets:
- Unique database ports (computed from project path hash)
- Unique test database name (includes project identifier)
- Isolated Docker Compose services

This means multiple agents can run tests simultaneously without conflicts.

### Examples

```bash
# Quick smoke test of integration tests
./scripts/test.sh --integration -x

# Run unit tests with coverage report
./scripts/test.sh --unit --cov=src --cov-report=term-missing

# Run specific test file
./scripts/test.sh tests/unit/identity/domain/test_user.py

# Run tests matching a pattern
./scripts/test.sh -k "test_user and test_verify"
```

## Other Scripts

### start.sh

Development environment setup script. Automatically:
- Checks prerequisites (Python, Node.js, Docker)
- Creates `.env` files with project-specific ports
- Starts Docker containers
- Installs dependencies
- Runs migrations

```bash
./start.sh
```

### verify.sh

Backend verification script. Runs:
- Ruff linting
- MyPy type checking
- Pytest unit tests
- Coverage check (requires ≥80%)

```bash
./scripts/verify.sh
```

### verify-frontend.sh

Frontend verification script. Runs:
- ESLint linting
- TypeScript type checking
- Vitest tests (if present)
- Vite build

```bash
./scripts/verify-frontend.sh
```

### project-env.sh

**Source this file to get project-specific environment variables.**

Computes unique ports based on project path hash to avoid conflicts between agents.

```bash
source scripts/project-env.sh
echo "My PostgreSQL port: $KOULU_PG_PORT"
echo "My project name: $COMPOSE_PROJECT_NAME"
```
