#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# UNITPLAST BOT - VPS Setup Script
# This script automates the VPS deployment setup
# Usage: sudo bash deploy/setup.sh
# ═══════════════════════════════════════════════════════════════════════════════

set -e

DOMAIN="unitgroup.tech"
APP_DIR="/var/www/unitplast_bot"
APP_USER="unitplast"
PYTHON_VERSION="python3"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  UNITPLAST BOT - VPS Setup                                   ║"
echo "║  Domain: $DOMAIN                                            ║"
echo "║  Application: $APP_DIR                                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

echo ""
echo "📦 Step 1: Update System"
apt-get update
apt-get upgrade -y

echo ""
echo "📦 Step 2: Install Dependencies"
apt-get install -y \
    git \
    python3 \
    python3-venv \
    python3-dev \
    build-essential \
    nginx \
    certbot \
    python3-certbot-nginx \
    curl \
    wget \
    htop

echo ""
echo "👤 Step 3: Create Application User"
if id "$APP_USER" &>/dev/null; then
    echo "   User $APP_USER already exists"
else
    useradd -m -s /bin/bash $APP_USER
    usermod -aG sudo $APP_USER
    echo "   ✅ User $APP_USER created"
fi

echo ""
echo "📁 Step 4: Setup Application Directory"
if [ -d "$APP_DIR" ]; then
    echo "   Directory $APP_DIR already exists"
    cd "$APP_DIR"
    echo "   Pulling latest code..."
    sudo -u $APP_USER git pull origin main 2>/dev/null || true
else
    echo "   Cloning repository..."
    mkdir -p /var/www
    cd /var/www
    git clone https://github.com/demsonart/unitplast_bot.git unitplast_bot
    cd $APP_DIR
fi

chown -R $APP_USER:$APP_USER $APP_DIR
echo "   ✅ Application directory setup complete"

echo ""
echo "🐍 Step 5: Create Python Virtual Environment"
if [ ! -d "$APP_DIR/venv" ]; then
    sudo -u $APP_USER $PYTHON_VERSION -m venv $APP_DIR/venv
    sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip
    sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r requirements.txt
    sudo -u $APP_USER $APP_DIR/venv/bin/pip install gunicorn
    echo "   ✅ Virtual environment created"
else
    echo "   Virtual environment already exists"
    sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip
    sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r requirements.txt
    echo "   ✅ Dependencies updated"
fi

echo ""
echo "📁 Step 6: Create Log and Data Directories"
mkdir -p /var/www/unitplast_bot/data /var/log/unitplast
chown -R $APP_USER:$APP_USER /var/www/unitplast_bot/data /var/log/unitplast
echo "   ✅ Directories created"

echo ""
echo "⚙️  Step 7: Setup systemd Service"
cp $APP_DIR/deploy/unitplast.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable unitplast
echo "   ✅ Service file installed and enabled"

echo ""
echo "🌐 Step 8: Setup Nginx"
cp $APP_DIR/deploy/unitgroup.tech.conf /etc/nginx/sites-available/
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/unitgroup.tech.conf /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
echo "   ✅ Nginx configured"

echo ""
echo "📝 Step 9: Create .env.production File"
if [ ! -f "$APP_DIR/.env.production" ]; then
    echo "   ⚠️  Please configure .env.production manually:"
    echo "       cp $APP_DIR/.env.production.example $APP_DIR/.env.production"
    echo "       nano $APP_DIR/.env.production"
    echo ""
    echo "   Required values:"
    echo "       - TELEGRAM_BOT_TOKEN"
    echo "       - TELEGRAM_GROUP_ID"
    echo "       - DATABASE_PATH=/app/data/unitplast.db"
else
    echo "   ✅ .env.production already exists"
fi

echo ""
echo "🔒 Step 10: Configure SSL (Optional)"
echo "   To setup SSL, run:"
echo "   sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ VPS Setup Complete!                                       ║"
echo "║                                                                ║"
echo "║  Next steps:                                                   ║"
echo "║  1. Configure .env.production:                                ║"
echo "║     nano $APP_DIR/.env.production                             ║"
echo "║  2. Setup SSL:                                                 ║"
echo "║     sudo certbot --nginx -d $DOMAIN                           ║"
echo "║  3. Start the application:                                     ║"
echo "║     sudo systemctl start unitplast                            ║"
echo "║  4. Check status:                                              ║"
echo "║     sudo systemctl status unitplast                           ║"
echo "║  5. View logs:                                                 ║"
echo "║     sudo journalctl -u unitplast -f                           ║"
echo "║                                                                ║"
echo "║  Test the application:                                         ║"
echo "║  https://$DOMAIN/health                                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
