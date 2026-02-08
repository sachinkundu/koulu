# Multi-Project Development Workflow

**TLDR:** Just run `./start.sh` in any project folder. Ports are auto-assigned based on folder path hash.

---

## 🎯 How It Works

The project uses **hash-based port isolation** to allow multiple project instances to run simultaneously without conflicts.

### Automatic Port Assignment

```bash
# Each unique folder path gets deterministic ports
/home/user/code/KOULU/cc_koulu       → Offset 67 → Ports: 5499, 6446, 1092, 8092
/home/user/code/KOULU/koulu          → Offset 74 → Ports: 5506, 6453, 1099, 8099
/home/user/code/KOULU/purekoulu      → Offset 58 → Ports: 5490, 6437, 1083, 8083
```

**Formula:** Port = Base Port + (path hash % 100)
- PostgreSQL:  5432 + offset
- Redis:       6379 + offset
- MailHog SMTP: 1025 + offset
- MailHog Web:  8025 + offset

---

## 🚀 Quick Start

### Run Single Project

```bash
cd /home/user/code/KOULU/cc_koulu
./start.sh  # That's it!
```

**What `start.sh` does automatically:**
1. ✅ Computes ports from folder path (via `scripts/project-env.sh`)
2. ✅ Creates/patches `.env` with correct ports
3. ✅ Starts Docker containers (postgres, redis, mailhog)
4. ✅ Installs Python dependencies
5. ✅ Runs database migrations
6. ✅ Installs frontend dependencies
7. ✅ Optionally starts backend + frontend

### Run Multiple Projects Simultaneously

**Terminal 1: Project A**
```bash
cd /home/user/code/KOULU/cc_koulu
./start.sh
```

**Terminal 2: Project B**
```bash
cd /home/user/code/KOULU/koulu
./start.sh
```

**Terminal 3: Project C**
```bash
cd /home/user/code/KOULU/my-feature-branch-copy
./start.sh
```

All three run simultaneously on different ports!

---

## 📋 Port Offset Calculation

The system uses `scripts/project-env.sh`:

```bash
# Compute port offset from absolute path hash
PROJECT_ROOT="/home/user/code/KOULU/cc_koulu"
PORT_OFFSET=$(echo -n "$PROJECT_ROOT" | cksum | awk '{print $1 % 100}')

# Export environment variables
export KOULU_PG_PORT=$((5432 + PORT_OFFSET))
export KOULU_REDIS_PORT=$((6379 + PORT_OFFSET))
export KOULU_MAIL_SMTP_PORT=$((1025 + PORT_OFFSET))
export KOULU_MAIL_WEB_PORT=$((8025 + PORT_OFFSET))
export COMPOSE_PROJECT_NAME="cckoulu"  # From folder basename
```

**Key features:**
- ✅ Deterministic (same path = same ports always)
- ✅ Collision-resistant (hash distributes 0-99)
- ✅ Works with ANY folder name (no naming convention required)
- ✅ Automatic (no manual configuration)

---

## 🔍 Check Current Configuration

```bash
# Source the environment to see your ports
source scripts/project-env.sh

echo "Project: $COMPOSE_PROJECT_NAME"
echo "PostgreSQL: $KOULU_PG_PORT"
echo "Redis: $KOULU_REDIS_PORT"
echo "MailHog: $KOULU_MAIL_SMTP_PORT / $KOULU_MAIL_WEB_PORT"
```

---

## 🐳 Docker Container Names

Each project gets unique container names:

```bash
# Project: cckoulu
cckoulu-postgres-1   # PostgreSQL
cckoulu-redis-1      # Redis
cckoulu-mailhog-1    # MailHog

# Project: koulu
koulu-postgres-1
koulu-redis-1
koulu-mailhog-1
```

Pattern: `{compose_project_name}-{service}-{instance}`

---

## 🗄️ Volume Isolation

**Current Setup:** Shared volume names (⚠️ projects share data)

```yaml
volumes:
  koulu_postgres_data:  # Shared across all projects
  koulu_redis_data:     # Shared across all projects
```

**To Enable Per-Project Volumes:**

Update `docker-compose.yml`:

```yaml
volumes:
  postgres_data:
    name: ${COMPOSE_PROJECT_NAME}_postgres_data  # cckoulu_postgres_data
  redis_data:
    name: ${COMPOSE_PROJECT_NAME}_redis_data     # cckoulu_redis_data
```

This gives each project its own database.

---

## 🔄 Multi-Developer Workflow

### Developer 1: Feature A

```bash
# Clone main to dedicated folder
cd ~/code/KOULU
git clone <repo> feature-user-auth
cd feature-user-auth

# Start infrastructure (auto-detects ports)
./start.sh

# Create branch
git checkout -b feature/user-auth

# Work on feature
# ... code changes ...

# Test locally
pytest tests/

# Commit and push
git add .
git commit -m "feat: add user auth"
git push origin feature/user-auth
```

### Developer 2: Feature B

```bash
# Clone main to different folder
cd ~/code/KOULU
git clone <repo> feature-community-feed
cd feature-community-feed

# Start infrastructure (DIFFERENT ports!)
./start.sh

# Create branch
git checkout -b feature/community-feed

# Work independently
# ... code changes ...

# Test locally (separate database)
pytest tests/

# Commit and push
git add .
git commit -m "feat: add community feed"
git push origin feature/community-feed
```

### Sync Changes

```bash
# Developer 1 gets Developer 2's changes
cd ~/code/KOULU/feature-user-auth
git pull origin main
alembic upgrade head

# Developer 2 gets Developer 1's changes
cd ~/code/KOULU/feature-community-feed
git pull origin main
alembic upgrade head
```

---

## 🛠️ Manual Operations

### Start Infrastructure Only

```bash
source scripts/project-env.sh
docker compose up -d
```

### Stop Infrastructure

```bash
source scripts/project-env.sh
docker compose down
```

### Clean Database (Remove Volumes)

```bash
source scripts/project-env.sh
docker compose down -v
```

### Run Migrations

```bash
alembic upgrade head
```

### Access Database

```bash
# Get your project's PostgreSQL port
source scripts/project-env.sh
echo "PostgreSQL port: $KOULU_PG_PORT"

# Connect
psql -h localhost -p $KOULU_PG_PORT -U koulu -d koulu

# Or via Docker
docker compose exec postgres psql -U koulu -d koulu
```

---

## 📊 View All Running Projects

```bash
docker ps --format 'table {{.Names}}\t{{.Ports}}' | grep -E 'NAME|koulu'
```

**Example output:**
```
NAME                  PORTS
cckoulu-postgres-1    0.0.0.0:5499->5432/tcp
cckoulu-redis-1       0.0.0.0:6446->6379/tcp
koulu-postgres-1      0.0.0.0:5506->5432/tcp
koulu-redis-1         0.0.0.0:6453->6379/tcp
```

---

## 🚨 Common Issues

### Port Already in Use

**Problem:** `Error: port 5499 already in use`

**Cause:** Another project instance using same path hash (rare)

**Solution:**
```bash
# Find conflicting project
lsof -i :5499

# Stop it
cd /path/to/other/project
source scripts/project-env.sh
docker compose down

# Or move current project to different path (changes hash)
mv ~/code/KOULU/cc_koulu ~/code/KOULU/cc_koulu2
# New hash = different ports!
```

### Wrong Database Connection

**Problem:** Backend can't connect

**Cause:** `.env` not patched with correct ports

**Solution:**
```bash
# Re-run start.sh to regenerate .env
./start.sh
```

### Shared Data Between Projects

**Problem:** Projects seeing each other's data

**Cause:** Volume names not project-specific

**Solution:** Update `docker-compose.yml` to use `${COMPOSE_PROJECT_NAME}` in volume names (see "Volume Isolation" section above)

---

## 💡 Best Practices

### 1. **One Folder Per Feature**
```bash
~/code/KOULU/
├── main/              # Main development
├── feature-auth/      # Feature branch workspace
├── feature-feed/      # Another feature
└── hotfix-login/      # Hotfix workspace
```

### 2. **Use `start.sh` Always**
- ✅ Do: `./start.sh`
- ❌ Don't: `docker compose up -d` (misses port configuration)

### 3. **Source `project-env.sh` for Manual Operations**
```bash
# Before any docker command
source scripts/project-env.sh
docker compose <command>
```

### 4. **Sync Frequently**
```bash
git pull origin main
alembic upgrade head
```

### 5. **Clean Up Old Projects**
```bash
# List all projects
docker ps -a | grep koulu

# Clean up stopped containers
cd ~/code/KOULU/old-feature
source scripts/project-env.sh
docker compose down -v
```

---

## 🔐 Environment Variables

### Auto-Exported by `project-env.sh`

```bash
COMPOSE_PROJECT_NAME    # From folder basename (e.g., "cckoulu")
KOULU_PG_PORT           # PostgreSQL port (e.g., 5499)
KOULU_REDIS_PORT        # Redis port (e.g., 6446)
KOULU_MAIL_SMTP_PORT    # MailHog SMTP (e.g., 1092)
KOULU_MAIL_WEB_PORT     # MailHog Web UI (e.g., 8092)
```

### Auto-Patched in `.env` by `start.sh`

```bash
DATABASE_URL=postgresql+asyncpg://koulu:koulu_dev_password@localhost:5499/koulu
REDIS_URL=redis://localhost:6446/0
MAIL_PORT=1092
```

---

## 📚 Related Files

- `scripts/project-env.sh` - Port calculation logic
- `start.sh` - Main setup script
- `docker-compose.yml` - Infrastructure definition
- `.env` - Environment configuration (auto-generated)

---

## ✅ Verification Checklist

Before starting work:
- [ ] Run `./start.sh`
- [ ] Check `.env` has correct ports
- [ ] Verify containers running: `docker ps | grep $(basename $PWD | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')`
- [ ] Test database connection: `docker compose exec postgres psql -U koulu -d koulu -c 'SELECT 1;'`
- [ ] Pull latest: `git pull origin main`

---

**Last Updated:** 2026-02-08
**System:** Hash-based port isolation via `scripts/project-env.sh`
**Workflow:** Run `./start.sh` in any project folder
