# Stage 1: Build React SPA
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend + built frontend
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY --from=frontend-build /app/frontend/dist ./static/

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
