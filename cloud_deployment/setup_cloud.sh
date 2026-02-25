#!/bin/bash
#
# setup_cloud.sh - Initial setup script for Oracle Cloud VM
# Run this on the newly created VM
#

set -e

echo "=========================================="
echo "AI Employee - Cloud VM Setup"
echo "=========================================="
echo ""

# Update system
echo "[1/8] Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python 3.13
echo "[2/8] Installing Python 3.13..."
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update -y
sudo apt-get install -y python3.13 python3.13-venv python3.13-dev python3-pip

# Install Node.js 24 LTS
echo "[3/8] Installing Node.js 24 LTS..."
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Git
echo "[4/8] Installing Git..."
sudo apt-get install -y git

# Install additional dependencies
echo "[5/8] Installing additional dependencies..."
sudo apt-get install -y \
    build-essential \
    wget \
    curl \
    vim \
    htop \
    tmux \
    ufw \
    nginx \
    certbot \
    python3.13-venv \
    python3-dev

# Create AI Employee directory
echo "[6/8] Creating AI Employee directory..."
mkdir -p ~/ai-employee
cd ~/ai-employee

# Create Python virtual environment
echo "[7/8] Creating Python virtual environment..."
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Install Python dependencies
pip install \
    watchdog \
    google-api-python-client \
    google-auth-oauthlib \
    playwright \
    requests \
    aiohttp \
    python-dotenv

# Install Playwright browsers
playwright install chromium

# Create log directory
mkdir -p ~/ai-employee/logs

# Setup firewall
echo "[8/8] Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Setup Git sync: bash setup_git_sync.sh"
echo "2. Deploy cloud agent: bash deploy_cloud_agent.sh"
echo "3. Start services: bash start_services.sh"
echo ""
