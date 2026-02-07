# Koulu

A community platform with feed, classroom, calendar, members, and leaderboards.

## Development

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker and Docker Compose (v2)

### Quick Start

The easiest way to get everything running:

```bash
./start.sh
```

This will check prerequisites, start Docker containers, install dependencies, run migrations, and set up your `.env` with the correct ports.

### Per-Project Isolation

Each copy of this repo gets its own isolated Docker stack (containers, volumes, networks, ports) so multiple agents or worktrees don't interfere with each other.

How it works:

- `scripts/project-env.sh` computes a deterministic port offset from the project's absolute path
- Docker Compose auto-prefixes container names, volumes, and networks using `COMPOSE_PROJECT_NAME`
- The `.env` file is patched with the correct ports on each `./start.sh` run

To see what ports your copy will use:

```bash
source scripts/project-env.sh
echo "PG=$KOULU_PG_PORT Redis=$KOULU_REDIS_PORT Mail SMTP=$KOULU_MAIL_SMTP_PORT Web=$KOULU_MAIL_WEB_PORT"
```

### Manual Setup

If you prefer to set things up step by step:

1. Source the project environment (sets `COMPOSE_PROJECT_NAME` and port variables):
   ```bash
   source scripts/project-env.sh
   ```

2. Start infrastructure services:
   ```bash
   docker compose up -d
   ```

3. Install Python dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Install frontend dependencies:
   ```bash
   cd frontend && npm install
   ```

### Running

- Backend: `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`
- Frontend: `cd frontend && npm run dev`

### Testing

- Backend: `./scripts/verify.sh`
- Frontend: `./scripts/verify-frontend.sh`
- E2E: `./scripts/run-e2e-tests.sh`

### Stopping

```bash
source scripts/project-env.sh
docker compose down
```

Add `-v` to also remove volumes (database data):

```bash
docker compose down -v
```
