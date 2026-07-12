#!/bin/bash
# FINAL LANDING DEPLOY
# Copy this entire script, SSH to VPS, paste and run

cd /var/www/unitplast_bot

echo "1. Pull latest code..."
git pull origin main

echo ""
echo "2. Stop service..."
sudo systemctl stop unitplast.service

echo ""
echo "3. Clear any caches..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null

echo ""
echo "4. Start service..."
sudo systemctl start unitplast.service

echo ""
echo "5. Wait for startup..."
sleep 3

echo ""
echo "6. Check health..."
curl -s http://127.0.0.1:5000/health | head -20

echo ""
echo "7. Verify landing has contacts..."
curl -s http://127.0.0.1:5000/ | grep -i "главный телефон\|+7 916" && echo "✅ CONTACTS FOUND" || echo "❌ CONTACTS NOT FOUND"

echo ""
echo "✅ DONE - Check browser: https://unitgroup.tech/"
