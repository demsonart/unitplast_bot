#!/bin/bash
# 🚨 EMERGENCY DIAGNOSTICS - Найти почему ничего не работает

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         🚨 EMERGENCY SYSTEM DIAGNOSTICS                       ║"
echo "║         Finding why NO POSTS are appearing                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# STEP 1: Service Status
echo "STEP 1: Checking service status..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo systemctl status unitplast-bot --no-pager
echo ""

# STEP 2: Process Check
echo "STEP 2: Checking if process is running..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ps aux | grep -q "[t]elegram_final_bot"; then
    echo "✅ Process IS running"
    ps aux | grep "telegram_final_bot" | grep -v grep
else
    echo "❌ CRITICAL: Process NOT running!"
fi
echo ""

# STEP 3: .env Configuration
echo "STEP 3: Checking .env configuration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Autonomous mode:"
grep "AUTONOMOUS_MODE" .env
echo ""
echo "Auto-publish:"
grep "AUTO_PUBLISH_ENABLED" .env
echo ""
echo "Dry-run:"
grep "TELEGRAM_DRY_RUN" .env
echo ""
echo "Bot token (hidden):"
grep "TELEGRAM_MEDIA_BOT_TOKEN" .env | sed 's/=.*/=***HIDDEN***/'
echo ""

# STEP 4: Recent Errors
echo "STEP 4: Checking for ERRORS in logs..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
errors=$(sudo journalctl -u unitplast-bot -n 200 --no-pager | grep -i "error\|failed\|exception" | head -20)
if [ -z "$errors" ]; then
    echo "✅ No obvious errors found"
else
    echo "❌ FOUND ERRORS:"
    echo "$errors"
fi
echo ""

# STEP 5: Last logs
echo "STEP 5: Last 50 lines of system journal..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo journalctl -u unitplast-bot -n 50 --no-pager
echo ""

# STEP 6: Autonomous logs
echo "STEP 6: Autonomous news logs (if exists)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "logs/autonomous_news.jsonl" ]; then
    echo "✅ Autonomous log file EXISTS"
    echo "Last 10 entries:"
    tail -10 logs/autonomous_news.jsonl
else
    echo "⚠️ Autonomous log file NOT created yet (might be too new)"
fi
echo ""

# STEP 7: File Permissions
echo "STEP 7: Checking file permissions..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ls -la .env | awk '{print $1, $9}'
ls -la VPS_DEPLOYMENT_PLAYBOOK.sh | awk '{print $1, $9}'
ls -la app/autonomous_news_agent.py | awk '{print $1, $9}'
echo ""

# STEP 8: Token validation
echo "STEP 8: Verifying bot token format..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
token=$(grep "TELEGRAM_MEDIA_BOT_TOKEN" .env | cut -d'=' -f2)
if [ -z "$token" ]; then
    echo "❌ NO TOKEN FOUND in .env!"
    echo "   Set: TELEGRAM_MEDIA_BOT_TOKEN=<your_token>"
elif [[ $token =~ ^[0-9]+:AA[A-Za-z0-9_-]+$ ]]; then
    echo "✅ Token format looks valid"
else
    echo "⚠️ Token format might be wrong"
    echo "   Format should be: NUMBER:AASTRING"
fi
echo ""

# STEP 9: Port check
echo "STEP 9: Checking Flask port (8000)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if sudo lsof -i :8000 2>/dev/null | grep -q LISTEN; then
    echo "✅ Port 8000 is listening"
    sudo lsof -i :8000 | grep LISTEN
else
    echo "⚠️ Port 8000 NOT listening (might be normal for bot-only mode)"
fi
echo ""

# STEP 10: Python import test
echo "STEP 10: Testing Python imports..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 -c "
try:
    from app.industry_news_rewriter import NewsRewriter
    print('✅ NewsRewriter import: OK')
except Exception as e:
    print(f'❌ NewsRewriter import failed: {e}')

try:
    from app.autonomous_news_agent import AutonomousNewsAgent
    print('✅ AutonomousNewsAgent import: OK')
except Exception as e:
    print(f'❌ AutonomousNewsAgent import failed: {e}')

try:
    import aiogram
    print(f'✅ aiogram {aiogram.__version__}: OK')
except Exception as e:
    print(f'❌ aiogram import failed: {e}')

try:
    import feedparser
    print('✅ feedparser: OK')
except Exception as e:
    print(f'❌ feedparser import failed: {e}')
" 2>&1
echo ""

# STEP 11: Systemd service file
echo "STEP 11: Checking systemd service file..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "/etc/systemd/system/unitplast-bot.service" ]; then
    echo "✅ Service file EXISTS"
    echo "Contents:"
    cat /etc/systemd/system/unitplast-bot.service | grep -E "ExecStart|User|WorkingDirectory"
else
    echo "❌ Service file NOT found!"
    echo "   Need to create it"
fi
echo ""

# STEP 12: Git status
echo "STEP 12: Checking git status..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git log --oneline -1
git status --short
echo ""

# STEP 13: Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    DIAGNOSTIC SUMMARY                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

if sudo systemctl is-active --quiet unitplast-bot; then
    echo "✅ Service: RUNNING"
else
    echo "❌ Service: NOT RUNNING - THIS IS THE PROBLEM!"
    echo "   Try: sudo systemctl restart unitplast-bot"
fi

if [ -n "$(grep 'AUTONOMOUS_MODE=true' .env)" ]; then
    echo "✅ Autonomous mode: ENABLED"
else
    echo "⚠️ Autonomous mode: DISABLED"
fi

if [ -n "$(grep 'AUTO_PUBLISH_ENABLED=true' .env)" ]; then
    echo "✅ Auto-publish: ENABLED"
else
    echo "⚠️ Auto-publish: DISABLED"
fi

if [ -n "$(grep 'TELEGRAM_DRY_RUN=false' .env)" ]; then
    echo "✅ Dry-run: DISABLED (real publish)"
else
    echo "⚠️ Dry-run: ENABLED (testing mode - no publish!)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "LIKELY ISSUES:"
echo "1. Service not running → systemctl restart unitplast-bot"
echo "2. Dry-run mode ON → Change TELEGRAM_DRY_RUN=false"
echo "3. Auto-publish OFF → Change AUTO_PUBLISH_ENABLED=true"
echo "4. No token → Add TELEGRAM_MEDIA_BOT_TOKEN=..."
echo "5. Autonomous OFF → Change AUTONOMOUS_MODE=true"
echo ""
echo "Try these fixes:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "# Check and fix .env"
echo "grep -E 'AUTONOMOUS|AUTO_PUBLISH|TELEGRAM_DRY_RUN' .env"
echo ""
echo "# If anything is wrong, fix it:"
echo "vim .env"
echo ""
echo "# Then restart:"
echo "sudo systemctl restart unitplast-bot"
echo ""
echo "# Then check logs:"
echo "sudo journalctl -u unitplast-bot -f"
echo ""
