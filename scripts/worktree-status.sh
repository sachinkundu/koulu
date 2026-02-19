#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# worktree-status.sh — Show status of all git worktrees
#
# Usage:
#   ./scripts/worktree-status.sh
#
# Shows: path, branch, ports, Docker container status for each worktree.
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
DIM='\033[2m'
NC='\033[0m'

echo ""
echo -e "${CYAN}══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Koulu Worktree Status${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Table header
printf "  ${BLUE}%-28s %-30s %-22s %-10s${NC}\n" "WORKTREE" "BRANCH" "PORTS (PG/BE/FE)" "DOCKER"
printf "  %-28s %-30s %-22s %-10s\n" "----------------------------" "------------------------------" "----------------------" "----------"

cd "$MAIN_ROOT"

# Iterate through all worktrees
git worktree list --porcelain | while read -r line; do
    case "$line" in
        "worktree "*)
            WT_PATH="${line#worktree }"
            WT_BRANCH=""
            ;;
        "branch "*)
            WT_BRANCH="${line#branch refs/heads/}"
            ;;
        "")
            # End of a worktree entry — print it
            if [ -n "${WT_PATH:-}" ]; then
                WT_NAME="$(basename "$WT_PATH")"

                # Read PORT_OFFSET from worktree's .env (must be explicit)
                if [ -f "${WT_PATH}/.env" ] && grep -q '^PORT_OFFSET=' "${WT_PATH}/.env" 2>/dev/null; then
                    WT_OFFSET=$(grep '^PORT_OFFSET=' "${WT_PATH}/.env" | cut -d= -f2)
                else
                    WT_OFFSET=""
                fi

                if [ -n "$WT_OFFSET" ]; then
                    WT_PG_PORT=$(( 5432 + WT_OFFSET ))
                    WT_BE_PORT=$(( 8000 + WT_OFFSET ))
                    WT_FE_PORT=$(( 5173 + WT_OFFSET ))
                    PORTS="${WT_PG_PORT}/${WT_BE_PORT}/${WT_FE_PORT}"
                    PORTS_COLOR=""
                else
                    PORTS="no PORT_OFFSET"
                    PORTS_COLOR="${RED}"
                fi

                # Check Docker status — derive compose project name
                WT_PROJECT="$(echo "$WT_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')"
                # Check if postgres container exists and is running
                CONTAINER_NAME="${WT_PROJECT}_postgres"
                if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$"; then
                    DOCKER_STATUS="running"
                    DOCKER_COLOR="${GREEN}"
                elif docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$"; then
                    DOCKER_STATUS="stopped"
                    DOCKER_COLOR="${YELLOW}"
                else
                    DOCKER_STATUS="none"
                    DOCKER_COLOR="${DIM}"
                fi

                # Highlight main worktree
                if [ "$WT_PATH" = "$MAIN_ROOT" ]; then
                    WT_NAME_DISPLAY="${WT_NAME} (main)"
                    WT_COLOR="${GREEN}"
                else
                    WT_NAME_DISPLAY="${WT_NAME}"
                    WT_COLOR=""
                fi

                # Print with color wrapping outside %-width so padding is correct
                printf "  ${WT_COLOR}%-28s${NC} %-30s ${PORTS_COLOR}%-22s${NC} ${DOCKER_COLOR}%-10s${NC}\n" \
                    "$WT_NAME_DISPLAY" "${WT_BRANCH:-detached}" "$PORTS" "$DOCKER_STATUS"
            fi
            WT_PATH=""
            WT_BRANCH=""
            ;;
    esac
done

# Handle last entry (git worktree list --porcelain may not end with empty line)
if [ -n "${WT_PATH:-}" ]; then
    WT_NAME="$(basename "$WT_PATH")"
    if [ -f "${WT_PATH}/.env" ] && grep -q '^PORT_OFFSET=' "${WT_PATH}/.env" 2>/dev/null; then
        WT_OFFSET=$(grep '^PORT_OFFSET=' "${WT_PATH}/.env" | cut -d= -f2)
    else
        WT_OFFSET=""
    fi
    if [ -n "$WT_OFFSET" ]; then
        WT_PG_PORT=$(( 5432 + WT_OFFSET ))
        WT_BE_PORT=$(( 8000 + WT_OFFSET ))
        WT_FE_PORT=$(( 5173 + WT_OFFSET ))
        PORTS="${WT_PG_PORT}/${WT_BE_PORT}/${WT_FE_PORT}"
        PORTS_COLOR=""
    else
        PORTS="no PORT_OFFSET"
        PORTS_COLOR="${RED}"
    fi
    WT_PROJECT="$(echo "$WT_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')"
    CONTAINER_NAME="${WT_PROJECT}_postgres"
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$"; then
        DOCKER_STATUS="running"
        DOCKER_COLOR="${GREEN}"
    elif docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^${CONTAINER_NAME}$"; then
        DOCKER_STATUS="stopped"
        DOCKER_COLOR="${YELLOW}"
    else
        DOCKER_STATUS="none"
        DOCKER_COLOR="${DIM}"
    fi
    if [ "$WT_PATH" = "$MAIN_ROOT" ]; then
        WT_NAME_DISPLAY="${WT_NAME} (main)"
        WT_COLOR="${GREEN}"
    else
        WT_NAME_DISPLAY="${WT_NAME}"
        WT_COLOR=""
    fi
    printf "  ${WT_COLOR}%-28s${NC} %-30s ${PORTS_COLOR}%-22s${NC} ${DOCKER_COLOR}%-10s${NC}\n" \
        "$WT_NAME_DISPLAY" "${WT_BRANCH:-detached}" "$PORTS" "$DOCKER_STATUS"
fi

echo ""
echo -e "${DIM}  Ports shown as: PostgreSQL / Backend API / Frontend Dev${NC}"
echo -e "${DIM}  Docker status checks for postgres container existence${NC}"
echo ""
