#!/bin/bash
# Диагностика что происходит на VPS

echo "=== 1. Проверяем статус сервиса ==="
sudo systemctl status unitplast.service --no-pager | head -20

echo ""
echo "=== 2. Последние ошибки в логе ==="
sudo journalctl -u unitplast.service -n 20 --no-pager

echo ""
echo "=== 3. Какой файл подаётся? ==="
ls -lh /var/www/unitplast_bot/web/landing.html
tail -50 /var/www/unitplast_bot/web/landing.html | grep -i "IBM\|#FFFFFF\|material\|plastic" || echo "❌ Старый файл"

echo ""
echo "=== 4. Git статус ==="
cd /var/www/unitplast_bot
git log --oneline -3

echo ""
echo "=== 5. Прямой тест что подаётся ==="
curl -s http://127.0.0.1:5000/ | head -50 | grep -i "IBM\|#FFFFFF\|background.*white" && echo "✅ НОВЫЙ ФАЙЛ" || echo "❌ СТАРЫЙ ФАЙЛ"

echo ""
echo "=== 6. Проверяем процесс Python ==="
ps aux | grep python | grep -v grep | head -3

echo ""
echo "=== 7. Попробуем рестарт ==="
sudo systemctl restart unitplast.service
sleep 2
curl -s http://127.0.0.1:5000/ | head -30
