#!/bin/bash
#
# deploy_cloud_agent.sh - Deploy and start Cloud Agent on Oracle Cloud VM
#

set -e

echo "=========================================="
echo "Cloud Agent Deployment"
echo "=========================================="
echo ""

# Configuration
AGENT_DIR="$HOME/ai-employee"
VAULT_DIR="$AGENT_DIR/vault"
REPO_URL="${1:-https://github.com/zakiabashir/hackhaton0_personal_ai_employe.git}"

# Create directories
echo "[1/6] Setting up directories..."
mkdir -p "$VAULT_DIR"
mkdir -p "$AGENT_DIR/logs"
cd "$AGENT_DIR"

# Clone or update repository
echo "[2/6] Cloning repository..."
if [ -d "$AGENT_DIR/hackhaton0_personal_ai_employe" ]; then
    cd "$AGENT_DIR/hackhaton0_personal_ai_employe"
    git pull
else
    git clone "$REPO_URL" "$AGENT_DIR/hackhaton0_personal_ai_employe"
fi

# Setup Python virtual environment
echo "[3/6] Setting up Python environment..."
if [ ! -d "$AGENT_DIR/venv" ]; then
    python3 -m venv "$AGENT_DIR/venv"
fi

source "$AGENT_DIR/venv/bin/activate"
pip install --upgrade pip

# Install Python dependencies
echo "[4/6] Installing Python dependencies..."
pip install \
    watchdog \
    google-api-python-client \
    google-auth-oauthlib \
    playwright \
    requests \
    aiohttp \
    python-dotenv \
    psutil

# Copy cloud agent to working directory
echo "[5/6] Setting up Cloud Agent..."
cp "$AGENT_DIR/hackhaton0_personal_ai_employe/orchestrator/cloud_agent.py" "$AGENT_DIR/"
cp "$AGENT_DIR/hackhaton0_personal_ai_employe/vault_sync/sync.py" "$AGENT_DIR/"
cp "$AGENT_DIR/hackhaton0_personal_ai_employe/vault_sync/claim_by_move.py" "$AGENT_DIR/"

# Create environment file
cat > "$AGENT_DIR/.env" << 'EOF'
# Cloud Agent Configuration
CLOUD_VAULT_PATH=$HOME/ai-employee/vault/AI_Employee_Vault
VAULT_SYNC_INTERVAL=60
HEALTH_CHECK_INTERVAL=300
LOG_LEVEL=INFO
EOF

# Create systemd service
echo "[6/6] Creating systemd service..."
sudo tee /etc/systemd/system/ai-employee-cloud.service > /dev/null << EOF
[Unit]
Description=AI Employee Cloud Agent
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$AGENT_DIR
Environment="PATH=$AGENT_DIR/venv/bin"
EnvironmentFile=$AGENT_DIR/.env
ExecStart=$AGENT_DIR/venv/bin/python $AGENT_DIR/cloud_agent.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ai-employee-cloud.service

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "To start the Cloud Agent:"
echo "  sudo systemctl start ai-employee-cloud"
echo ""
echo "To check status:"
echo "  sudo systemctl status ai-employee-cloud"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u ai-employee-cloud -f"
echo ""
echo "To stop:"
echo "  sudo systemctl stop ai-employee-cloud"
echo ""
