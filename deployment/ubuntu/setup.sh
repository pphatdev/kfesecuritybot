#!/bin/bash
# Detected Bot - Ubuntu Setup Script
# Run this script with sudo (e.g., sudo ./setup.sh)

set -e

PROJECT_DIR="/var/www/pphat/pphat.me"

echo "======================================"
echo "Starting Ubuntu Deployment Setup..."
echo "======================================"

# 1. Update and install dependencies
echo "Updating apt packages..."
apt-get update

echo "Installing Python 3, pip, and venv..."
apt-get install -y python3 python3-pip python3-venv nginx curl

echo "Installing Node.js (20.x)..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# 2. Setup Python Bot
echo "Setting up Python virtual environment..."
cd $PROJECT_DIR
python3 -m venv .venv

echo "Installing Python dependencies..."
$PROJECT_DIR/.venv/bin/pip install -r requirements.txt

# 3. Setup Nuxt Dashboard
echo "Building Nuxt Dashboard..."
cd $PROJECT_DIR/dashboard
npm install
npm run build

# 4. Configure Systemd Services
echo "Configuring Systemd Services..."
cd $PROJECT_DIR

# Copy service files to systemd
cp deployment/ubuntu/bot.service /etc/systemd/system/
cp deployment/ubuntu/dashboard.service /etc/systemd/system/

# Reload systemd and enable services
systemctl daemon-reload
systemctl enable bot.service
systemctl enable dashboard.service

# Start the services
systemctl restart bot.service
systemctl restart dashboard.service

# 5. Configure Nginx
echo "Configuring Nginx Reverse Proxy..."
cp deployment/ubuntu/nginx.conf /etc/nginx/sites-available/detected-bot
ln -sf /etc/nginx/sites-available/detected-bot /etc/nginx/sites-enabled/

# Remove default nginx site if exists
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
fi

# Restart Nginx
systemctl restart nginx

echo "======================================"
echo "Deployment Setup Complete! 🚀"
echo "- Bot is running in the background."
echo "- Dashboard is available on port 80."
echo "Check bot logs: sudo journalctl -u bot.service -f"
echo "Check dashboard logs: sudo journalctl -u dashboard.service -f"
echo "======================================"
