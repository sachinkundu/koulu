#!/usr/bin/env bash
# =============================================================================
# install-prereqs.sh — Detect and offer to install missing prerequisites
#
# Checks for: Docker, Python 3.11+, Node.js 18+, virtual environment
# Supports: Ubuntu/Debian (apt), Fedora (dnf), macOS (brew)
# Safe: prompts before every install, idempotent
# =============================================================================

# Colors (reuse from caller or define our own)
RED="${RED:-\033[0;31m}"
GREEN="${GREEN:-\033[0;32m}"
YELLOW="${YELLOW:-\033[1;33m}"
BLUE="${BLUE:-\033[0;34m}"
NC="${NC:-\033[0m}"

_info()    { echo -e "${BLUE}[PREREQ]${NC} $1"; }
_success() { echo -e "${GREEN}[PREREQ]${NC} $1"; }
_warn()    { echo -e "${YELLOW}[PREREQ]${NC} $1"; }
_error()   { echo -e "${RED}[PREREQ]${NC} $1"; }

# ---------------------------------------------------------------------------
# Load version managers if installed (they may not be in PATH yet)
# ---------------------------------------------------------------------------

# Load pyenv if present
if [ -d "$HOME/.pyenv" ] && ! command -v pyenv &>/dev/null; then
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)" 2>/dev/null || true
fi

# Load nvm if present
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    . "$NVM_DIR/nvm.sh"
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Compare versions: returns 0 if $1 >= $2
_version_gte() {
    [ "$(printf '%s\n' "$2" "$1" | sort -V | head -n1)" = "$2" ]
}

# Prompt user with [Y/n]. Returns 0 for yes, 1 for no.
_confirm() {
    local prompt="$1"
    read -p "$(echo -e "${YELLOW}[PREREQ]${NC} ${prompt} [Y/n] ")" -n 1 -r
    echo ""
    [[ ! $REPLY =~ ^[Nn]$ ]]
}

# Detect OS and package manager
_detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        if command -v brew &>/dev/null; then
            PKG_MGR="brew"
        else
            PKG_MGR="none"
        fi
    elif [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$ID" in
            ubuntu|debian|pop|linuxmint)
                OS="debian"
                PKG_MGR="apt"
                ;;
            fedora|rhel|centos|rocky|alma)
                OS="fedora"
                PKG_MGR="dnf"
                ;;
            arch|manjaro)
                OS="arch"
                PKG_MGR="pacman"
                ;;
            *)
                OS="linux"
                PKG_MGR="unknown"
                ;;
        esac
    else
        OS="unknown"
        PKG_MGR="unknown"
    fi
}

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------
_install_docker() {
    if command -v docker &>/dev/null; then
        _success "Docker is already installed"
        return 0
    fi

    _warn "Docker is not installed."

    if ! _confirm "Install Docker?"; then
        _warn "Skipping Docker installation."
        return 1
    fi

    case "$OS" in
        macos)
            if [ "$PKG_MGR" = "brew" ]; then
                _info "Installing Docker via Homebrew cask..."
                brew install --cask docker
                _warn "Please launch Docker Desktop from Applications to start the daemon."
            else
                _error "Homebrew not found. Please install Docker Desktop manually: https://docs.docker.com/desktop/install/mac-install/"
                return 1
            fi
            ;;
        debian|fedora|arch)
            _info "Installing Docker via official install script (get.docker.com)..."
            curl -fsSL https://get.docker.com | sudo sh
            sudo usermod -aG docker "$USER"
            _warn "Added $USER to the docker group. You may need to log out and back in for this to take effect."
            sudo systemctl enable --now docker
            ;;
        *)
            _error "Unsupported OS for automatic Docker install. Please install manually: https://docs.docker.com/get-docker/"
            return 1
            ;;
    esac

    if command -v docker &>/dev/null; then
        _success "Docker installed successfully"
    else
        _error "Docker installation may require a new shell session to take effect."
        return 1
    fi
}

# ---------------------------------------------------------------------------
# Python 3.11+ via pyenv
# ---------------------------------------------------------------------------
_install_python() {
    local required_version="3.11"

    # Check if python3 exists and meets version requirement
    if command -v python3 &>/dev/null; then
        local current_version
        current_version=$(python3 --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1)
        if _version_gte "$current_version" "$required_version"; then
            _success "Python $current_version is already installed (>= $required_version)"
            return 0
        fi
        _warn "Python $current_version found but $required_version+ is required."
    else
        _warn "Python 3 is not installed."
    fi

    if ! _confirm "Install Python $required_version+ via pyenv?"; then
        _warn "Skipping Python installation."
        return 1
    fi

    # Install pyenv if missing
    if ! command -v pyenv &>/dev/null; then
        _info "Installing pyenv..."

        # Install build dependencies first
        case "$OS" in
            debian)
                _info "Installing Python build dependencies..."
                sudo apt-get update -qq
                sudo apt-get install -y -qq make build-essential libssl-dev zlib1g-dev \
                    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
                    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
                    libffi-dev liblzma-dev git
                ;;
            fedora)
                _info "Installing Python build dependencies..."
                sudo dnf install -y gcc make zlib-devel bzip2 bzip2-devel \
                    readline-devel sqlite sqlite-devel openssl-devel tk-devel \
                    libffi-devel xz-devel git
                ;;
            macos)
                if [ "$PKG_MGR" = "brew" ]; then
                    brew install openssl readline sqlite3 xz zlib tcl-tk git
                fi
                ;;
        esac

        curl -fsSL https://pyenv.run | bash

        # Configure shell for pyenv
        export PYENV_ROOT="$HOME/.pyenv"
        export PATH="$PYENV_ROOT/bin:$PATH"
        eval "$(pyenv init -)"

        # Add to shell profile if not already there
        local shell_profile=""
        if [ -f "$HOME/.bashrc" ]; then
            shell_profile="$HOME/.bashrc"
        elif [ -f "$HOME/.zshrc" ]; then
            shell_profile="$HOME/.zshrc"
        fi

        if [ -n "$shell_profile" ] && ! grep -q 'pyenv init' "$shell_profile" 2>/dev/null; then
            _info "Adding pyenv to $shell_profile..."
            {
                echo ''
                echo '# pyenv'
                echo 'export PYENV_ROOT="$HOME/.pyenv"'
                echo 'export PATH="$PYENV_ROOT/bin:$PATH"'
                echo 'eval "$(pyenv init -)"'
            } >> "$shell_profile"
        fi
    else
        _success "pyenv is already installed"
        eval "$(pyenv init -)" 2>/dev/null || true
    fi

    # Find latest Python 3.11.x or 3.12.x
    _info "Finding latest Python >= $required_version..."
    local latest_python
    latest_python=$(pyenv install --list 2>/dev/null | tr -d ' ' | grep -E '^3\.(11|12|13)\.[0-9]+$' | tail -1)

    if [ -z "$latest_python" ]; then
        _error "Could not find a Python >= $required_version in pyenv. Try: pyenv install --list"
        return 1
    fi

    _info "Installing Python $latest_python via pyenv (this may take a few minutes)..."
    pyenv install -s "$latest_python"
    pyenv global "$latest_python"

    # Verify
    if command -v python3 &>/dev/null; then
        local new_version
        new_version=$(python3 --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1)
        _success "Python $new_version installed via pyenv"
    else
        _error "Python installation completed but python3 not found in PATH. Try opening a new shell."
        return 1
    fi
}

# ---------------------------------------------------------------------------
# Node.js 18+ via nvm
# ---------------------------------------------------------------------------
_install_node() {
    local required_version="18.0"

    # Check if node exists and meets version requirement
    if command -v node &>/dev/null; then
        local current_version
        current_version=$(node --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1)
        if _version_gte "$current_version" "$required_version"; then
            _success "Node.js $current_version is already installed (>= 18)"
            return 0
        fi
        _warn "Node.js $current_version found but 18+ is required."
    else
        _warn "Node.js is not installed."
    fi

    if ! _confirm "Install Node.js 18+ via nvm?"; then
        _warn "Skipping Node.js installation."
        return 1
    fi

    # Install nvm if missing
    export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
    if [ ! -d "$NVM_DIR" ] || ! command -v nvm &>/dev/null; then
        _info "Installing nvm (Node Version Manager)..."
        curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

        # Load nvm into current shell
        export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
        [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    else
        _success "nvm is already installed"
        [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    fi

    # Install latest LTS
    _info "Installing latest Node.js LTS via nvm..."
    nvm install --lts
    nvm use --lts

    # Verify
    if command -v node &>/dev/null; then
        local new_version
        new_version=$(node --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1)
        _success "Node.js $new_version installed via nvm"
    else
        _error "Node.js installation completed but node not found in PATH. Try opening a new shell."
        return 1
    fi
}

# ---------------------------------------------------------------------------
# Virtual environment
# ---------------------------------------------------------------------------
_setup_venv() {
    if [ -n "${VIRTUAL_ENV:-}" ]; then
        _success "Virtual environment is active: $VIRTUAL_ENV"
        return 0
    fi

    # Check if a venv directory already exists (use project root, not scripts/)
    local project_root="${SCRIPT_DIR:-$(pwd)}"
    # If SCRIPT_DIR points to scripts/, go up one level
    if [[ "$project_root" == */scripts ]]; then
        project_root="$(dirname "$project_root")"
    fi
    local venv_dir="${project_root}/venv"
    if [ -d "$venv_dir" ]; then
        _warn "Virtual environment found at $venv_dir but not activated."
        if _confirm "Activate existing virtual environment?"; then
            # shellcheck disable=SC1091
            source "$venv_dir/bin/activate"
            _success "Activated virtual environment: $venv_dir"
            return 0
        fi
        return 0
    fi

    _warn "No virtual environment detected."
    if _confirm "Create a virtual environment at ./venv?"; then
        python3 -m venv "$venv_dir"
        # shellcheck disable=SC1091
        source "$venv_dir/bin/activate"
        _success "Created and activated virtual environment: $venv_dir"
    else
        _warn "Skipping virtual environment setup."
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
_install_prereqs_main() {
    echo ""
    _info "Checking and installing prerequisites..."
    echo ""

    _detect_os
    _info "Detected OS: $OS (package manager: $PKG_MGR)"
    echo ""

    _install_docker
    echo ""

    _install_python
    echo ""

    _install_node
    echo ""

    _setup_venv
    echo ""

    _info "Prerequisite check complete."
    echo ""
}

# Run if sourced or executed directly
_install_prereqs_main
