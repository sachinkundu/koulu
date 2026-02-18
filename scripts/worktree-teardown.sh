#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# worktree-teardown.sh — Remove a worktree and its Docker resources
#
# Usage:
#   ./scripts/worktree-teardown.sh <epic-name>
#
# Examples:
#   ./scripts/worktree-teardown.sh leaderboards
#   ./scripts/worktree-teardown.sh calendar
#
# What it does:
#   1. Stops Docker containers for the worktree
#   2. Removes Docker volumes (database data, redis data)
#   3. Removes the git worktree
#   4. Optionally deletes the branch
# =============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

EPIC_NAME="${1:-}"

if [ -z "$EPIC_NAME" ]; then
    echo -e "${RED}Usage: $0 <epic-name>${NC}"
    echo ""
    echo "Examples:"
    echo "  $0 leaderboards"
    echo "  $0 calendar"
    echo ""
    echo "Current worktrees:"
    git -C "$MAIN_ROOT" worktree list
    exit 1
fi

WORKTREE_DIR="$(dirname "$MAIN_ROOT")/koulu-${EPIC_NAME}"

echo ""
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Tearing Down Worktree: koulu-${EPIC_NAME}${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo ""

# Verify worktree exists
if [ ! -d "$WORKTREE_DIR" ]; then
    echo -e "${RED}Error: Worktree directory not found: ${WORKTREE_DIR}${NC}"
    echo ""
    echo "Current worktrees:"
    git -C "$MAIN_ROOT" worktree list
    exit 1
fi

# Get the branch name before we remove the worktree
BRANCH_NAME="$(git -C "$WORKTREE_DIR" branch --show-current 2>/dev/null || echo '')"

# Step 1: Stop Docker containers and remove volumes
echo -e "${BLUE}Stopping Docker containers...${NC}"
cd "$WORKTREE_DIR"
if docker compose ps --quiet 2>/dev/null | grep -q .; then
    docker compose down -v --remove-orphans
    echo -e "${GREEN}Containers and volumes removed${NC}"
else
    echo -e "${YELLOW}No running containers found${NC}"
fi
echo ""

# Step 2: Remove the worktree
echo -e "${BLUE}Removing git worktree...${NC}"
cd "$MAIN_ROOT"
git worktree remove "$WORKTREE_DIR" --force 2>/dev/null || {
    echo -e "${YELLOW}Force removing worktree directory...${NC}"
    rm -rf "$WORKTREE_DIR"
    git worktree prune
}
echo -e "${GREEN}Worktree removed${NC}"
echo ""

# Step 3: Optionally delete the branch
if [ -n "$BRANCH_NAME" ] && [ "$BRANCH_NAME" != "main" ] && [ "$BRANCH_NAME" != "master" ]; then
    echo -e "${YELLOW}Branch '${BRANCH_NAME}' still exists.${NC}"
    read -p "Delete branch '${BRANCH_NAME}'? [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if git branch -d "$BRANCH_NAME" 2>/dev/null; then
            echo -e "${GREEN}Branch deleted${NC}"
        else
            echo -e "${YELLOW}Branch not fully merged. Force delete? [y/N]${NC}"
            read -p "" -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git branch -D "$BRANCH_NAME"
                echo -e "${GREEN}Branch force deleted${NC}"
            else
                echo -e "${YELLOW}Branch kept${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}Branch kept${NC}"
    fi
fi

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Teardown complete: koulu-${EPIC_NAME}${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════${NC}"
echo ""

# Show remaining worktrees
echo "Remaining worktrees:"
git worktree list
echo ""
