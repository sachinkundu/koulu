#!/usr/bin/env bash
#
# project-env.sh — Single source of truth for per-project isolation.
#
# Computes and exports:
#   COMPOSE_PROJECT_NAME   — derived from folder basename
#   KOULU_VOLUME_PREFIX    — prefix for Docker container/volume/network names
#   KOULU_WORKTREE_BRANCH  — current git branch (for display)
#   KOULU_PG_PORT          — PostgreSQL host port
#   KOULU_REDIS_PORT       — Redis host port
#   KOULU_MAIL_SMTP_PORT   — MailHog SMTP host port
#   KOULU_MAIL_WEB_PORT    — MailHog Web UI host port
#   KOULU_BACKEND_PORT     — Backend API server port
#   KOULU_FRONTEND_PORT    — Frontend dev server port
#
# Usage:
#   source scripts/project-env.sh
#
# Every script that touches Docker should source this file first.
# Worktree-safe: each worktree directory gets unique names and ports.

# Resolve the project root (parent of the scripts/ directory)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Project name = folder basename, lowercased, non-alphanumeric stripped
COMPOSE_PROJECT_NAME="$(basename "$PROJECT_ROOT" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')"
export COMPOSE_PROJECT_NAME

# Volume prefix for Docker container/volume/network names — derived from project name
# so each worktree gets its own containers (koulu_postgres, koululeaderboards_postgres, etc.)
export KOULU_VOLUME_PREFIX="${KOULU_VOLUME_PREFIX:-${COMPOSE_PROJECT_NAME}}"

# Current git branch (for display in banners)
export KOULU_WORKTREE_BRANCH="$(git -C "$PROJECT_ROOT" branch --show-current 2>/dev/null || echo 'unknown')"

# Port offset: MUST be set explicitly in .env — no implicit fallback.
# Each worktree/checkout sets PORT_OFFSET in .env to avoid collisions.
# Run ./setup.sh to generate .env with a PORT_OFFSET if you don't have one.
if [ -f "${PROJECT_ROOT}/.env" ] && grep -q '^PORT_OFFSET=' "${PROJECT_ROOT}/.env" 2>/dev/null; then
    PORT_OFFSET=$(grep '^PORT_OFFSET=' "${PROJECT_ROOT}/.env" | cut -d= -f2)
else
    echo ""
    echo -e "\033[0;31m══════════════════════════════════════════════════════════════\033[0m"
    echo -e "\033[0;31m  ERROR: PORT_OFFSET not set in ${PROJECT_ROOT}/.env\033[0m"
    echo -e "\033[0;31m══════════════════════════════════════════════════════════════\033[0m"
    echo ""
    echo "  Every worktree/checkout needs an explicit PORT_OFFSET in .env"
    echo "  to avoid port collisions between environments."
    echo ""
    echo "  Fix: add a line like this to ${PROJECT_ROOT}/.env:"
    echo ""
    echo "    PORT_OFFSET=100"
    echo ""
    echo "  Or run ./setup.sh to generate .env automatically."
    echo ""
    return 1 2>/dev/null || exit 1
fi
export PORT_OFFSET

# Compute per-project host ports (infrastructure)
export KOULU_PG_PORT=${KOULU_PG_PORT:-$(( 5432 + PORT_OFFSET ))}
export KOULU_REDIS_PORT=${KOULU_REDIS_PORT:-$(( 6379 + PORT_OFFSET ))}
export KOULU_MAIL_SMTP_PORT=${KOULU_MAIL_SMTP_PORT:-$(( 1025 + PORT_OFFSET ))}
export KOULU_MAIL_WEB_PORT=${KOULU_MAIL_WEB_PORT:-$(( 8025 + PORT_OFFSET ))}

# Compute per-project application server ports
export KOULU_BACKEND_PORT=${KOULU_BACKEND_PORT:-$(( 8000 + PORT_OFFSET ))}
export KOULU_FRONTEND_PORT=${KOULU_FRONTEND_PORT:-$(( 5173 + PORT_OFFSET ))}

# E2E uses separate ports (+100) so it can run alongside dev servers
export KOULU_E2E_BACKEND_PORT=${KOULU_E2E_BACKEND_PORT:-$(( KOULU_BACKEND_PORT + 100 ))}
export KOULU_E2E_FRONTEND_PORT=${KOULU_E2E_FRONTEND_PORT:-$(( KOULU_FRONTEND_PORT + 100 ))}

# ---------------------------------------------------------------------------
# print_worktree_banner — Display project identity in script headers
# Usage: print_worktree_banner
# ---------------------------------------------------------------------------
print_worktree_banner() {
    local BLUE='\033[0;34m'
    local GREEN='\033[0;32m'
    local YELLOW='\033[1;33m'
    local CYAN='\033[0;36m'
    local NC='\033[0m'
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${GREEN}Project:${NC}  ${COMPOSE_PROJECT_NAME}"
    echo -e "${CYAN}║${NC}  ${GREEN}Branch:${NC}   ${KOULU_WORKTREE_BRANCH}"
    echo -e "${CYAN}║${NC}  ${GREEN}Path:${NC}     ${PROJECT_ROOT}"
    echo -e "${CYAN}║${NC}  ${YELLOW}Ports:${NC}    PG=${KOULU_PG_PORT} Redis=${KOULU_REDIS_PORT} BE=${KOULU_BACKEND_PORT} FE=${KOULU_FRONTEND_PORT}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""
}
