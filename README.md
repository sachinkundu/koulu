# Koulu

A community platform with feed, classroom, calendar, members, and leaderboards.

## Development

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker and Docker Compose

### Setup

1. Start infrastructure services:
   ```bash
   docker-compose up -d
   ```

2. Install Python dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

4. Install frontend dependencies:
   ```bash
   cd frontend && npm install
   ```

### Running

- Backend: `uvicorn src.main:app --reload`
- Frontend: `cd frontend && npm run dev`

### Testing

- Backend: `./scripts/verify.sh`
- Frontend: `./scripts/verify-frontend.sh`
