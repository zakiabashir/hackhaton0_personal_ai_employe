#!/bin/bash
#
# setup_odoo_cloud.sh - Deploy Odoo Community on Cloud VM
# For Platinum Tier - Cloud + Local Executive
#

set -e

echo "=========================================="
echo "Odoo Cloud Deployment - Platinum Tier"
echo "=========================================="
echo ""

# Configuration
ODOO_VERSION=${1:-19.0}
ODOO_USER="odoo"
ODOO_HOME="/opt/odoo"
ODOO_CONFIG="/etc/odoo/odoo.conf"
DB_USER="odoo"
DB_PASS=$(openssl rand -base64 32)
ADMIN_PASS=$(openssl rand -base64 16)

echo "[1/10] Installing PostgreSQL..."
sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

echo "[2/10] Creating Odoo database user..."
sudo -u postgres createuser --createdb --pwprompt "$DB_USER" << EOF
$DB_PASS
$DB_PASS
EOF

echo "[3/10] Installing Python dependencies..."
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libtiff5-dev \
    libjpeg8-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    libpq-dev

echo "[4/10] Installing wkhtmltopdf..."
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo apt-get install -f -y

echo "[5/10] Creating Odoo user..."
sudo useradd -m -d $ODOO_HOME -s /bin/bash $ODOO_USER

echo "[6/10] Cloning Odoo $ODOO_VERSION..."
sudo -u $ODOO_USER git clone --depth 1 --branch $ODOO_VERSION https://github.com/odoo/odoo.git $ODOO_HOME/odoo

echo "[7/10] Installing Python requirements..."
sudo -u $ODOO_USER pip3 install -r $ODOO_HOME/odoo/requirements.txt

echo "[8/10] Creating Odoo configuration..."
sudo mkdir -p /etc/odoo
sudo mkdir -p /var/log/odoo

sudo tee $ODOO_CONFIG > /dev/null << EOF
[options]
admin_passwd = $ADMIN_PASS
db_host = localhost
db_port = 5432
db_user = $DB_USER
db_password = $DB_PASS
dbfilter = .*
addons_path = $ODOO_HOME/odoo/addons,$ODOO_HOME/odoo
logfile = /var/log/odoo/odoo.log
log_level = info
http_port = 8069
proxy_mode = True
EOF

sudo chown $ODOO_USER:$ODOO_USER /etc/odoo/odoo.conf
sudo chown $ODOO_USER:$ODOO_USER /var/log/odoo

echo "[9/10] Creating systemd service..."
sudo tee /etc/systemd/system/odoo.service > /dev/null << EOF
[Unit]
Description=Odoo Open Source ERP
After=network.target postgresql.service

[Service]
Type=simple
User=$ODOO_USER
Group=$ODOO_USER
ExecStart=/usr/bin/python3 $ODOO_HOME/odoo/odoo-bin -c $ODOO_CONFIG
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable odoo

echo "[10/10] Starting Odoo..."
sudo systemctl start odoo
sleep 5

if systemctl is-active --quiet odoo; then
    echo ""
    echo "=========================================="
    echo "Odoo deployed successfully!"
    echo "=========================================="
    echo ""
    echo "URL: http://<your-vm-ip>:8069"
    echo "Admin password: $ADMIN_PASS"
    echo ""
    echo "IMPORTANT: Save these credentials!"
    echo "Admin password: $ADMIN_PASS"
    echo "Database password: $DB_PASS"
    echo ""
    echo "Next steps:"
    echo "1. Setup HTTPS with Nginx"
    echo "2. Configure backups"
    echo "3. Connect MCP server"
    echo ""
else
    echo "Error: Odoo failed to start. Check logs:"
    sudo journalctl -u odoo -n 50
fi
