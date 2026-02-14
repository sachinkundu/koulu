#!/usr/bin/env bash
# =============================================================================
# deploy-railway.sh — Provision a Railway environment from zero to working
#
# Usage:
#   ./scripts/deploy-railway.sh                          # production (default)
#   ./scripts/deploy-railway.sh --environment staging    # staging
#   ./scripts/deploy-railway.sh --dry-run                # show what would happen
#   ./scripts/deploy-railway.sh --skip-deploy            # set up vars only
#   ./scripts/deploy-railway.sh --help
#
# Prerequisites:
#   - Railway CLI installed (https://docs.railway.com/guides/cli)
#   - Logged in: railway login
#   - Project linked: railway link
# =============================================================================

set -euo pipefail

# ─── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ─── Defaults ────────────────────────────────────────────────────────────────
ENVIRONMENT="production"
DRY_RUN=false
SKIP_DEPLOY=false
HEALTH_CHECK_TIMEOUT=120  # seconds
HEALTH_CHECK_INTERVAL=5   # seconds

# ─── Parse Arguments ────────────────────────────────────────────────────────
usage() {
    cat <<EOF
${BOLD}Railway Deployment Script${NC}

Provisions a complete Railway environment from zero to working.

${BOLD}Usage:${NC}
  $0 [options]

${BOLD}Options:${NC}
  --environment, -e <name>   Environment name (default: production)
  --dry-run                  Show what would happen without making changes
  --skip-deploy              Set up services and vars only, don't deploy
  --timeout <seconds>        Health check timeout (default: 120)
  --help, -h                 Show this help message

${BOLD}Examples:${NC}
  $0                                    # Deploy to production
  $0 --environment staging              # Create & deploy staging
  $0 --dry-run                          # Preview changes
  $0 --environment staging --skip-deploy # Set up staging without deploying

${BOLD}Prerequisites:${NC}
  1. Railway CLI:  npm install -g @railway/cli
  2. Login:        railway login
  3. Link project: railway link
  4. (Optional) Resend API key for email sending
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --environment|-e) ENVIRONMENT="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        --skip-deploy) SKIP_DEPLOY=true; shift ;;
        --timeout) HEALTH_CHECK_TIMEOUT="$2"; shift 2 ;;
        --help|-h) usage ;;
        *) echo -e "${RED}Unknown option: $1${NC}"; usage ;;
    esac
done

# ─── Helpers ─────────────────────────────────────────────────────────────────
log_step() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}"; }
log_ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
log_skip() { echo -e "  ${YELLOW}⊘${NC} $1 (already exists)"; }
log_set()  { echo -e "  ${CYAN}→${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
log_err()  { echo -e "  ${RED}✗${NC} $1"; }

run_cmd() {
    if $DRY_RUN; then
        echo -e "  ${YELLOW}[dry-run]${NC} $*"
    else
        "$@"
    fi
}

generate_secret() {
    openssl rand -base64 48 | tr -d '\n/+=' | head -c 64
}

# ─── Service/Environment Flags ──────────────────────────────────────────────
# Build the --environment flag used for multi-env commands
ENV_FLAG="--environment $ENVIRONMENT"

railway_var_set() {
    # Set a Railway variable, optionally skipping deploys
    local key="$1"
    local value="$2"
    local skip_deploy="${3:-true}"

    if $DRY_RUN; then
        # Mask secrets in dry-run output
        local display_value="$value"
        if [[ "$key" == *SECRET* || "$key" == *PASSWORD* || "$key" == *API_KEY* ]]; then
            display_value="${value:0:8}...(masked)"
        fi
        echo -e "  ${YELLOW}[dry-run]${NC} railway variable set $key=$display_value"
    else
        local flags=""
        if [[ "$skip_deploy" == "true" ]]; then
            flags="--skip-deploys"
        fi
        railway variable set "${key}=${value}" $ENV_FLAG $flags 2>/dev/null
    fi
}

railway_var_get() {
    # Get a single Railway variable, returns empty string if not set
    railway variables --json $ENV_FLAG 2>/dev/null \
        | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('$1',''))" 2>/dev/null || echo ""
}

service_exists() {
    # Check if a service with the given name exists in the project
    local name="$1"
    railway service status 2>&1 | grep -qi "$name"
}

# =============================================================================
# STEP 1: Preflight Checks
# =============================================================================
log_step "Step 1/6: Preflight Checks"

# Railway CLI
if ! command -v railway &>/dev/null; then
    log_err "Railway CLI not found. Install: npm install -g @railway/cli"
    exit 1
fi
log_ok "Railway CLI found ($(railway --version 2>/dev/null || echo 'unknown'))"

# Logged in
if ! railway whoami &>/dev/null; then
    log_err "Not logged in. Run: railway login"
    exit 1
fi
log_ok "Logged in as $(railway whoami 2>/dev/null)"

# Project linked
if ! railway status &>/dev/null; then
    log_err "No project linked. Run: railway link"
    exit 1
fi
PROJECT_INFO=$(railway status 2>/dev/null)
log_ok "Project linked: $(echo "$PROJECT_INFO" | head -1)"

# openssl for secret generation
if ! command -v openssl &>/dev/null; then
    log_err "openssl not found. Required for generating secrets."
    exit 1
fi
log_ok "openssl available"

echo -e "\n  ${BOLD}Environment:${NC} $ENVIRONMENT"
if $DRY_RUN; then
    echo -e "  ${BOLD}Mode:${NC} ${YELLOW}DRY RUN (no changes will be made)${NC}"
fi

# =============================================================================
# STEP 2: Environment Setup
# =============================================================================
log_step "Step 2/6: Environment Setup"

# Check if the target environment exists, create if needed
CURRENT_ENV=$(railway status 2>/dev/null | grep -i "environment" | head -1 | awk '{print $NF}')

if [[ "$CURRENT_ENV" == "$ENVIRONMENT" ]]; then
    log_ok "Already on environment: $ENVIRONMENT"
else
    # Try to link to the environment
    if run_cmd railway environment link "$ENVIRONMENT" 2>/dev/null; then
        log_ok "Linked to environment: $ENVIRONMENT"
    else
        echo -e "  Environment '${ENVIRONMENT}' not found. Creating..."
        run_cmd railway environment new "$ENVIRONMENT" 2>/dev/null
        run_cmd railway environment link "$ENVIRONMENT" 2>/dev/null
        log_ok "Created and linked environment: $ENVIRONMENT"
    fi
fi

# =============================================================================
# STEP 3: Provision Database & Redis
# =============================================================================
log_step "Step 3/6: Provision Services (PostgreSQL + Redis)"

# Check existing variables to see if services are already provisioned
EXISTING_DB_URL=$(railway_var_get "DATABASE_URL")
EXISTING_REDIS_URL=$(railway_var_get "REDIS_URL")

if [[ -n "$EXISTING_DB_URL" ]]; then
    log_skip "PostgreSQL (DATABASE_URL already set)"
else
    echo -e "  Adding PostgreSQL..."
    run_cmd railway add --database postgres
    log_ok "PostgreSQL added"
    echo -e "  ${CYAN}ℹ${NC}  Railway auto-injects DATABASE_URL into your service"
fi

if [[ -n "$EXISTING_REDIS_URL" ]]; then
    log_skip "Redis (REDIS_URL already set)"
else
    echo -e "  Adding Redis..."
    run_cmd railway add --database redis
    log_ok "Redis added"
    echo -e "  ${CYAN}ℹ${NC}  Railway auto-injects REDIS_URL into your service"
fi

# =============================================================================
# STEP 4: Set Environment Variables
# =============================================================================
log_step "Step 4/6: Environment Variables"

# Link back to the main service (not the DB/Redis services)
if ! $DRY_RUN; then
    railway service link koulu 2>/dev/null || true
fi

# ── Application ──
echo -e "\n  ${BOLD}Application:${NC}"
railway_var_set "APP_ENV" "$ENVIRONMENT"
log_set "APP_ENV=$ENVIRONMENT"

railway_var_set "APP_DEBUG" "false"
log_set "APP_DEBUG=false"

EXISTING_APP_SECRET=$(railway_var_get "APP_SECRET_KEY")
if [[ -n "$EXISTING_APP_SECRET" && "$EXISTING_APP_SECRET" != "your-super-secret"* ]]; then
    log_skip "APP_SECRET_KEY (already set)"
else
    NEW_SECRET=$(generate_secret)
    railway_var_set "APP_SECRET_KEY" "$NEW_SECRET"
    log_set "APP_SECRET_KEY=(auto-generated, 64 chars)"
fi

# ── JWT ──
echo -e "\n  ${BOLD}JWT:${NC}"
EXISTING_JWT_SECRET=$(railway_var_get "JWT_SECRET_KEY")
if [[ -n "$EXISTING_JWT_SECRET" && "$EXISTING_JWT_SECRET" != "your-jwt-secret"* ]]; then
    log_skip "JWT_SECRET_KEY (already set)"
else
    NEW_JWT_SECRET=$(generate_secret)
    railway_var_set "JWT_SECRET_KEY" "$NEW_JWT_SECRET"
    log_set "JWT_SECRET_KEY=(auto-generated, 64 chars)"
fi

railway_var_set "JWT_ALGORITHM" "HS256"
log_set "JWT_ALGORITHM=HS256"

railway_var_set "JWT_ACCESS_TOKEN_EXPIRE_MINUTES" "30"
log_set "JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30"

railway_var_set "JWT_REFRESH_TOKEN_EXPIRE_DAYS" "7"
log_set "JWT_REFRESH_TOKEN_EXPIRE_DAYS=7"

railway_var_set "JWT_REFRESH_TOKEN_REMEMBER_ME_DAYS" "30"
log_set "JWT_REFRESH_TOKEN_REMEMBER_ME_DAYS=30"

# ── Email (Resend HTTP API) ──
# Note: Uses Resend's HTTP API (not SMTP). Railway blocks outbound SMTP ports.
echo -e "\n  ${BOLD}Email (Resend HTTP API):${NC}"

EXISTING_RESEND_KEY=$(railway_var_get "RESEND_API_KEY")
if [[ -n "$EXISTING_RESEND_KEY" && "$EXISTING_RESEND_KEY" != "REPLACE_WITH"* ]]; then
    log_skip "RESEND_API_KEY (already set)"
else
    railway_var_set "RESEND_API_KEY" "REPLACE_WITH_RESEND_API_KEY"
    log_warn "RESEND_API_KEY set to placeholder — update with your Resend API key!"
    log_warn "Run: railway variable set RESEND_API_KEY=re_your_key_here"
fi

railway_var_set "MAIL_FROM" "onboarding@resend.dev"
log_set "MAIL_FROM=onboarding@resend.dev"

railway_var_set "MAIL_FROM_NAME" "Koulu"
log_set "MAIL_FROM_NAME=Koulu"

# ── Frontend URL ──
echo -e "\n  ${BOLD}Frontend:${NC}"
# Try to detect the Railway-provided domain
RAILWAY_DOMAIN=$(railway_var_get "RAILWAY_PUBLIC_DOMAIN")
if [[ -n "$RAILWAY_DOMAIN" ]]; then
    FRONTEND_URL="https://${RAILWAY_DOMAIN}"
else
    FRONTEND_URL="https://koulu-${ENVIRONMENT}.up.railway.app"
fi
railway_var_set "FRONTEND_URL" "$FRONTEND_URL"
log_set "FRONTEND_URL=$FRONTEND_URL"

# ── Rate Limiting ──
echo -e "\n  ${BOLD}Rate Limiting:${NC}"
railway_var_set "RATE_LIMIT_ENABLED" "true"
log_set "RATE_LIMIT_ENABLED=true"

# =============================================================================
# STEP 5: Deploy
# =============================================================================
log_step "Step 5/6: Deploy"

if $SKIP_DEPLOY; then
    log_warn "Skipping deploy (--skip-deploy flag)"
elif $DRY_RUN; then
    echo -e "  ${YELLOW}[dry-run]${NC} Would run: railway up"
else
    echo -e "  Deploying from Dockerfile..."
    echo -e "  This builds frontend + backend and runs migrations on startup."
    echo ""
    railway up --detach
    log_ok "Deployment triggered"
fi

# =============================================================================
# STEP 6: Post-Deploy Health Check
# =============================================================================
log_step "Step 6/6: Health Check"

if $SKIP_DEPLOY || $DRY_RUN; then
    log_warn "Skipping health check (no deploy was triggered)"
else
    HEALTH_URL="${FRONTEND_URL}/health"
    echo -e "  Waiting for ${HEALTH_URL} ..."
    echo -e "  Timeout: ${HEALTH_CHECK_TIMEOUT}s (build + deploy takes ~2-4 min)"

    ELAPSED=0
    while [[ $ELAPSED -lt $HEALTH_CHECK_TIMEOUT ]]; do
        HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" 2>/dev/null || echo "000")
        if [[ "$HTTP_STATUS" == "200" ]]; then
            log_ok "Health check passed! (${ELAPSED}s)"
            break
        fi
        echo -e "  ${YELLOW}…${NC} Status: $HTTP_STATUS (${ELAPSED}s elapsed)"
        sleep "$HEALTH_CHECK_INTERVAL"
        ELAPSED=$((ELAPSED + HEALTH_CHECK_INTERVAL))
    done

    if [[ $ELAPSED -ge $HEALTH_CHECK_TIMEOUT ]]; then
        log_warn "Health check timed out after ${HEALTH_CHECK_TIMEOUT}s"
        log_warn "The deployment may still be building. Check:"
        echo -e "    railway logs"
        echo -e "    curl $HEALTH_URL"
    fi
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo -e "${GREEN}━━━ Deployment Summary ━━━${NC}"
echo -e "  ${BOLD}Environment:${NC}  $ENVIRONMENT"
echo -e "  ${BOLD}URL:${NC}          $FRONTEND_URL"
echo -e "  ${BOLD}Health:${NC}       ${FRONTEND_URL}/health"
echo -e "  ${BOLD}API Docs:${NC}     ${FRONTEND_URL}/docs"
echo ""

# Check for placeholder API key
FINAL_RESEND_KEY=$(railway_var_get "RESEND_API_KEY")
if [[ "$FINAL_RESEND_KEY" == "REPLACE_WITH"* ]]; then
    echo -e "  ${YELLOW}⚠ ACTION REQUIRED:${NC} Set your Resend API key:"
    echo -e "    railway variable set RESEND_API_KEY=re_your_key_here"
    echo ""
fi

echo -e "  ${BOLD}Useful commands:${NC}"
echo -e "    railway logs            # View deployment logs"
echo -e "    railway variables       # View all env vars"
echo -e "    railway open            # Open dashboard"
echo -e "    railway connect         # Connect to database shell"
echo ""
