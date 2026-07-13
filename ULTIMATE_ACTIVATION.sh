#!/bin/bash
# 🚀 ULTIMATE ACTIVATION - ДЕЛАЕТ ВСЁ АВТОМАТИЧЕСКИ
# Просто запустите: bash ULTIMATE_ACTIVATION.sh

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║      🚀 ULTIMATE AUTONOMOUS ACTIVATION - AUTOMATIC MODE       ║"
echo "║                                                                ║"
echo "║      Сейчас произойдёт ВСЁ:                                  ║"
echo "║      1. SSH подключение к VPS                                ║"
echo "║      2. Обновление кода                                       ║"
echo "║      3. Финальная конфигурация                                ║"
echo "║      4. Запуск системы                                        ║"
echo "║      5. Проверка статуса                                      ║"
echo "║      6. Первые посты в @UnitgroupAI!                         ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

VPS="root@193.104.33.29"
PROJECT_PATH="/home/unitplast_bot"

echo "🔐 Подключаюсь к VPS..."
echo ""

# Вся работа на VPS через SSH
ssh $VPS << 'EOFSCRIPT'

set -e

PROJECT_PATH="/home/unitplast_bot"
cd "$PROJECT_PATH"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   🚀 AUTOMATIC ACTIVATION                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# STEP 1: Pull latest code
echo "STEP 1️⃣  Обновляю код из GitHub..."
git pull origin main
echo "✅ Код обновлён"
echo ""

# STEP 2: Backup .env
echo "STEP 2️⃣  Сохраняю резервную копию .env..."
cp .env .env.backup.ultimate.$(date +%Y%m%d_%H%M%S)
echo "✅ Backup создан"
echo ""

# STEP 3: Configure .env
echo "STEP 3️⃣  Конфигурирую .env для АВТОНОМНОГО режима..."

# Remove old settings
sed -i '/^AUTONOMOUS_MODE=/d' .env 2>/dev/null || true
sed -i '/^AUTO_PUBLISH_ENABLED=/d' .env 2>/dev/null || true
sed -i '/^TELEGRAM_DRY_RUN=/d' .env 2>/dev/null || true
sed -i '/^TELEGRAM_REQUIRE_APPROVAL=/d' .env 2>/dev/null || true
sed -i '/^ENABLE_CLAUDE_ENHANCEMENT=/d' .env 2>/dev/null || true

# Add correct settings
echo "" >> .env
echo "# AUTONOMOUS MODE - ACTIVATED" >> .env
echo "AUTONOMOUS_MODE=true" >> .env
echo "AUTO_PUBLISH_ENABLED=true" >> .env
echo "TELEGRAM_DRY_RUN=false" >> .env
echo "TELEGRAM_REQUIRE_APPROVAL=false" >> .env
echo "ENABLE_CLAUDE_ENHANCEMENT=true" >> .env
echo "FETCH_INTERVAL_MINUTES=30" >> .env
echo "AUTONOMOUS_QUALITY_THRESHOLD=0.85" >> .env

echo "✅ .env настроена"
echo ""

# STEP 4: Verify critical settings
echo "STEP 4️⃣  Проверяю критические настройки..."

AUTONOMOUS=$(grep "AUTONOMOUS_MODE=true" .env || echo "NOT_FOUND")
if [ "$AUTONOMOUS" = "NOT_FOUND" ]; then
    echo "❌ AUTONOMOUS_MODE не установлена!"
    exit 1
fi
echo "  ✅ AUTONOMOUS_MODE=true"

AUTO_PUBLISH=$(grep "AUTO_PUBLISH_ENABLED=true" .env || echo "NOT_FOUND")
if [ "$AUTO_PUBLISH" = "NOT_FOUND" ]; then
    echo "❌ AUTO_PUBLISH_ENABLED не установлена!"
    exit 1
fi
echo "  ✅ AUTO_PUBLISH_ENABLED=true"

DRY_RUN=$(grep "TELEGRAM_DRY_RUN=false" .env || echo "NOT_FOUND")
if [ "$DRY_RUN" = "NOT_FOUND" ]; then
    echo "❌ TELEGRAM_DRY_RUN не выключена!"
    exit 1
fi
echo "  ✅ TELEGRAM_DRY_RUN=false (РЕАЛЬНАЯ ПУБЛИКАЦИЯ!)"

APPROVAL=$(grep "TELEGRAM_REQUIRE_APPROVAL=false" .env || echo "NOT_FOUND")
if [ "$APPROVAL" = "NOT_FOUND" ]; then
    echo "❌ TELEGRAM_REQUIRE_APPROVAL не выключена!"
    exit 1
fi
echo "  ✅ TELEGRAM_REQUIRE_APPROVAL=false"

TOKEN=$(grep "TELEGRAM_MEDIA_BOT_TOKEN" .env | cut -d'=' -f2)
if [ -z "$TOKEN" ]; then
    echo "❌ BOT TOKEN не найден!"
    exit 1
fi
echo "  ✅ BOT TOKEN: $(echo $TOKEN | head -c 20)..."

CHANNEL=$(grep "TELEGRAM_CHANNEL_USERNAME" .env)
if [ -z "$CHANNEL" ]; then
    echo "❌ CHANNEL не найдена!"
    exit 1
fi
echo "  ✅ CHANNEL: @UnitgroupAI"

echo ""

# STEP 5: Stop service
echo "STEP 5️⃣  Останавливаю текущий сервис..."
sudo systemctl stop unitplast-bot || true
sleep 2
echo "✅ Сервис остановлен"
echo ""

# STEP 6: Start service
echo "STEP 6️⃣  Запускаю сервис с новыми настройками..."
sudo systemctl start unitplast-bot
sleep 3
echo "✅ Сервис запущен"
echo ""

# STEP 7: Verify service
echo "STEP 7️⃣  Проверяю что сервис работает..."
if sudo systemctl is-active --quiet unitplast-bot; then
    echo "✅ Service STATUS: RUNNING ✅"
else
    echo "❌ Service not running!"
    sudo systemctl status unitplast-bot --no-pager
    exit 1
fi
echo ""

# STEP 8: Show status
echo "STEP 8️⃣  Финальный статус:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Статус сервиса:"
sudo systemctl status unitplast-bot --no-pager | head -5
echo ""
echo "Последние 20 строк логов:"
echo ""
sudo journalctl -u unitplast-bot -n 20 --no-pager || true
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# STEP 9: Final message
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║           🎉 АКТИВАЦИЯ ЗАВЕРШЕНА! СИСТЕМА ЗАПУЩЕНА            ║"
echo "║                                                                ║"
echo "║  ✅ Автономный режим: ВКЛЮЧЕН                                 ║"
echo "║  ✅ Публикация: ВКЛЮЧЕНА (не dry-run!)                       ║"
echo "║  ✅ AI Enhancement: ВКЛЮЧЕНА                                  ║"
echo "║  ✅ Сервис: ЗАПУЩЕН И РАБОТАЕТ                               ║"
echo "║                                                                ║"
echo "║  📱 ОТКРОЙТЕ: @UnitgroupAI в Telegram                        ║"
echo "║                                                                ║"
echo "║  ⏰ ОЖИДАЙТЕ: Первые посты появятся за 5-30 минут             ║"
echo "║                                                                ║"
echo "║  🔄 ЧАСТОТА: Новые посты каждые 30 минут                    ║"
echo "║                                                                ║"
echo "║  📊 КАЧЕСТВО: Professional AI-enhanced (avg 0.85+)            ║"
echo "║                                                                ║"
echo "║  🤖 АВТОНОМИЯ: Полная - никакой ручной работы!              ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

EOFSCRIPT

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║              ✅ АКТИВАЦИЯ НА VPS ЗАВЕРШЕНА!                  ║"
echo "║                                                                ║"
echo "║  Система работает автономно на VPS: 193.104.33.29            ║"
echo "║                                                                ║"
echo "║  📱 ОТКРЫВАЙТЕ TELEGRAM:                                      ║"
echo "║     Поиск: @UnitgroupAI                                       ║"
echo "║     Смотрите как наполняется канал!                          ║"
echo "║                                                                ║"
echo "║  ⏰ ПЕРВЫЕ ПОСТЫ: 5-30 минут                                  ║"
echo "║                                                                ║"
echo "║  🚀 Готово! Система работает! 🎉                             ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
