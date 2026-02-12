#!/usr/bin/env bash
#
# project-env.sh — Single source of truth for per-project isolation.
#
# Computes and exports:
#   COMPOSE_PROJECT_NAME   — derived from folder basename
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

# Resolve the project root (parent of the scripts/ directory)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Project name = folder basename, lowercased, non-alphanumeric stripped
COMPOSE_PROJECT_NAME="$(basename "$PROJECT_ROOT" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')"
export COMPOSE_PROJECT_NAME

# Deterministic port offset from a hash of the absolute path (0–99)
PORT_OFFSET=$(echo -n "$PROJECT_ROOT" | cksum | awk '{print $1 % 100}')

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
