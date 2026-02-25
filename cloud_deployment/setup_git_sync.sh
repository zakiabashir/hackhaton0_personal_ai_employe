#!/bin/bash
#
# setup_git_sync.sh - Setup Git-based vault synchronization
#

set -e

echo "=========================================="
echo "Git Vault Sync Setup"
echo "=========================================="
echo ""

# Configuration
REPO_URL="${1:-}"
VAULT_DIR="$HOME/ai-employee/vault"
GIT_EMAIL="${2:-}"
GIT_NAME="${3:-AI Employee Cloud Agent}"

if [ -z "$REPO_URL" ]; then
    echo "Usage: bash setup_git_sync.sh <repo_url> [git_email] [git_name]"
    echo ""
    echo "Create a new GitHub/GitLab repository first, then run this script."
    exit 1
fi

# Configure Git
echo "[1/4] Configuring Git..."
git config --global user.email "$GIT_EMAIL"
git config --global user.name "$GIT_NAME"
git config --global init.defaultBranch main

# Setup SSH keys for GitHub/GitLab
echo "[2/4] Setting up SSH keys..."
if [ ! -f ~/.ssh/id_ed25519 ]; then
    ssh-keygen -t ed25519 -C "ai-employee-cloud" -f ~/.ssh/id_ed25519 -N ""
    echo ""
    echo "SSH key generated. Add this public key to your GitHub/GitLab account:"
    echo ""
    cat ~/.ssh/id_ed25519.pub
    echo ""
    read -p "Press Enter after adding the SSH key..."
fi

# Clone vault repository
echo "[3/4] Cloning vault repository..."
if [ -d "$VAULT_DIR" ]; then
    echo "Vault directory already exists, pulling latest..."
    cd "$VAULT_DIR"
    git pull origin main
else
    git clone "$REPO_URL" "$VAULT_DIR"
fi

# Create .gitignore for security
echo "[4/4] Creating .gitignore for security..."
cat > "$VAULT_DIR/.gitignore" << 'EOF'
# Security - NEVER sync these
.env
*.env
.env.local
.env.production

# WhatsApp sessions
.whatsapp_session/
*.session

# Banking/Payment credentials
*credentials*
*secrets*
*tokens*
banking/
payments/

# SSH keys
*.pem
*.key
id_*

# Local only
.local/
*.local

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Node modules
node_modules/

# Logs (keep local, sync only summaries)
*.log
logs/*.log

# OS files
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
*.swp
*.swo
*~

# But DO sync vault content
!AI_Employee_Vault/
!AI_Employee_Vault/**/*.md
!AI_Employee_Vault/**/*.json
!Updates/
!Signals/
!Plans/
!Needs_Action/
!In_Progress/
EOF

cd "$VAULT_DIR"
git add .gitignore
git commit -m "Add security .gitignore for Platinum Tier" || true

echo ""
echo "=========================================="
echo "Git Sync Setup Complete!"
echo "=========================================="
echo ""
echo "Vault location: $VAULT_DIR"
echo "Repository: $REPO_URL"
echo ""
echo "Test sync with:"
echo "  cd $VAULT_DIR && git pull"
echo ""
