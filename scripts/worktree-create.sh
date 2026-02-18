#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# worktree-create.sh — Create a new git worktree with full isolated environment
#
# Usage:
#   ./scripts/worktree-create.sh <epic-name> [branch-name]
#
# Examples:
#   ./scripts/worktree-create.sh leaderboards feature/leaderboard-views
#   ./scripts/worktree-create.sh calendar feature/calendar-events
#   ./scripts/worktree-create.sh messaging   # auto-creates branch feature/messaging
#
# What it does:
#   1. Creates git branch (if it doesn't exist)
#   2. Creates worktree at ../koulu-<epic-name>
#   3. Runs setup.sh in the new worktree (Docker, deps, migrations, .env)
#   4. Prints connection info (ports, URLs)
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

# Parse arguments
EPIC_NAME="${1:-}"
BRANCH_NAME="${2:-epic/${EPIC_NAME}}"

if [ -z "$EPIC_NAME" ]; then
    echo -e "${RED}Usage: $0 <epic-name> [branch-name]${NC}"
    echo ""
    echo "Examples:"
    echo "  $0 leaderboards                           # branch defaults to epic/leaderboards"
    echo "  $0 calendar epic/calendar-events"
    echo "  $0 messaging feature/direct-messaging     # override with any branch name"
    exit 1
fi

WORKTREE_DIR="$(dirname "$MAIN_ROOT")/koulu-${EPIC_NAME}"

echo ""
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Creating Worktree: koulu-${EPIC_NAME}${NC}"
echo -e "${CYAN}  Branch: ${BRANCH_NAME}${NC}"
echo -e "${CYAN}  Path:   ${WORKTREE_DIR}${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo ""

# Check worktree doesn't already exist
if [ -d "$WORKTREE_DIR" ]; then
    echo -e "${RED}Error: Directory already exists: ${WORKTREE_DIR}${NC}"
    echo "  To remove it: ./scripts/worktree-teardown.sh ${EPIC_NAME}"
    exit 1
fi

# Create branch if it doesn't exist
cd "$MAIN_ROOT"
if git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}" 2>/dev/null; then
    echo -e "${GREEN}Branch '${BRANCH_NAME}' already exists${NC}"
else
    echo -e "${BLUE}Creating branch '${BRANCH_NAME}'...${NC}"
    git branch "$BRANCH_NAME"
    echo -e "${GREEN}Branch created${NC}"
fi

# Create the worktree
echo -e "${BLUE}Creating worktree at ${WORKTREE_DIR}...${NC}"
git worktree add "$WORKTREE_DIR" "$BRANCH_NAME"
echo -e "${GREEN}Worktree created${NC}"
echo ""

# Run setup in the new worktree
echo -e "${BLUE}Running setup in new worktree...${NC}"
echo -e "${YELLOW}(This will start Docker containers, install deps, run migrations)${NC}"
echo ""
cd "$WORKTREE_DIR"
./setup.sh

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Worktree ready!${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════${NC}"
echo ""
echo "  cd ${WORKTREE_DIR}"
echo "  ./start.sh          # Start dev servers"
echo "  ./scripts/verify.sh # Run all checks"
echo ""
