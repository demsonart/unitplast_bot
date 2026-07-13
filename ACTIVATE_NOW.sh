#!/bin/bash
# 🚀 ACTIVATE AUTONOMOUS MODE - ONE COMMAND
# Execute on VPS: 193.104.33.29

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║         🚀 AUTONOMOUS MODE ACTIVATION IN PROGRESS             ║"
echo "║                                                                ║"
echo "║  @UnitgroupAI channel will start filling with news!           ║"
echo "║  Expected: 5-15 posts per day, AI-enhanced quality            ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verify we're on VPS
if [ ! -d "/home/unitplast_bot" ]; then
    echo "❌ ERROR: /home/unitplast_bot not found"
    echo "   Make sure you're on VPS: 193.104.33.29"
    exit 1
fi

cd /home/unitplast_bot

echo "📍 Working directory: $(pwd)"
echo ""

# Step 1: Backup current .env
echo "Step 1: Backing up current .env..."
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created"
echo ""

# Step 2: Enable autonomous mode
echo "Step 2: Enabling autonomous mode..."
sed -i 's/AUTONOMOUS_MODE=false/AUTONOMOUS_MODE=true/' .env || true
sed -i 's/AUTONOMOUS_MODE=.*/AUTONOMOUS_MODE=true/' .env || echo "AUTONOMOUS_MODE=true" >> .env
echo "✅ AUTONOMOUS_MODE=true"
echo ""

# Step 3: Enable auto-publish
echo "Step 3: Enabling auto-publish..."
sed -i 's/AUTO_PUBLISH_ENABLED=false/AUTO_PUBLISH_ENABLED=true/' .env || true
sed -i 's/AUTO_PUBLISH_ENABLED=.*/AUTO_PUBLISH_ENABLED=true/' .env || echo "AUTO_PUBLISH_ENABLED=true" >> .env
echo "✅ AUTO_PUBLISH_ENABLED=true"
echo ""

# Step 4: Disable dry-run
echo "Step 4: Disabling dry-run mode (REAL PUBLISHING)..."
sed -i 's/TELEGRAM_DRY_RUN=true/TELEGRAM_DRY_RUN=false/' .env
echo "✅ TELEGRAM_DRY_RUN=false"
echo ""

# Step 5: Disable approval requirement
echo "Step 5: Disabling approval requirement (AUTONOMOUS)..."
sed -i 's/TELEGRAM_REQUIRE_APPROVAL=true/TELEGRAM_REQUIRE_APPROVAL=false/' .env
echo "✅ TELEGRAM_REQUIRE_APPROVAL=false"
echo ""

# Step 6: Enable Claude enhancement
echo "Step 6: Enabling Claude AI enhancement..."
sed -i 's/ENABLE_CLAUDE_ENHANCEMENT=false/ENABLE_CLAUDE_ENHANCEMENT=true/' .env || true
sed -i 's/ENABLE_CLAUDE_ENHANCEMENT=.*/ENABLE_CLAUDE_ENHANCEMENT=true/' .env || echo "ENABLE_CLAUDE_ENHANCEMENT=true" >> .env
echo "✅ ENABLE_CLAUDE_ENHANCEMENT=true"
echo ""

# Step 7: Set quality threshold
echo "Step 7: Setting quality threshold..."
sed -i 's/AUTONOMOUS_QUALITY_THRESHOLD=.*/AUTONOMOUS_QUALITY_THRESHOLD=0.85/' .env || echo "AUTONOMOUS_QUALITY_THRESHOLD=0.85" >> .env
echo "✅ AUTONOMOUS_QUALITY_THRESHOLD=0.85"
echo ""

# Step 8: Verify configuration
echo "Step 8: Verifying configuration..."
echo ""
echo "=== AUTONOMOUS MODE SETTINGS ==="
grep -E "AUTONOMOUS|AUTO_PUBLISH|TELEGRAM_DRY_RUN|TELEGRAM_REQUIRE_APPROVAL|ENABLE_CLAUDE" .env || true
echo ""

# Step 9: Restart service
echo "Step 9: Restarting unitplast-bot service..."
sudo systemctl restart unitplast-bot
echo "✅ Service restarted"
echo ""

# Step 10: Wait for startup
echo "Step 10: Waiting for service to start..."
sleep 3
echo "✅ Done"
echo ""

# Step 11: Verify service is running
echo "Step 11: Verifying service status..."
if sudo systemctl is-active --quiet unitplast-bot; then
    echo "✅ Service is RUNNING"
else
    echo "❌ Service failed to start"
    sudo systemctl status unitplast-bot --no-pager
    exit 1
fi
echo ""

# Step 12: Show logs
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   🎉 ACTIVATION COMPLETE                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 REAL-TIME LOG (last 30 lines):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo journalctl -u unitplast-bot -n 30 --no-pager
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   ✅ SYSTEM ACTIVATED                         ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║                                                                ║"
echo "║  🤖 Autonomous News Agent: ACTIVE                             ║"
echo "║  📱 Channel: @UnitgroupAI                                     ║"
echo "║  🤖 Bot: @Media_Unitgroup_bot                                 ║"
echo "║  ⏱️ Frequency: Every 30 minutes                               ║"
echo "║  📊 Quality threshold: 0.85+                                  ║"
echo "║  🚀 Auto-publish: ENABLED                                     ║"
echo "║  🎨 AI Enhancement: Claude-powered                            ║"
echo "║                                                                ║"
echo "║  📈 Expected: 5-15 posts/day to @UnitgroupAI ✅              ║"
echo "║  📍 Quality: Professional AI-enhanced (avg 0.82+)            ║"
echo "║  🔐 Safety: Brand validated + fact checked                    ║"
echo "║                                                                ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  WATCH THE CHANNEL IN REAL-TIME:                             ║"
echo "║  Open Telegram → @UnitgroupAI                                ║"
echo "║  New posts will appear automatically!                         ║"
echo "║                                                                ║"
echo "║  MONITOR LOGS:                                                ║"
echo "║  tail -f logs/autonomous_news.jsonl                           ║"
echo "║                                                                ║"
echo "║  STOP (if needed):                                            ║"
echo "║  vim .env                                                     ║"
echo "║  # Change: AUTONOMOUS_MODE=false                              ║"
echo "║  sudo systemctl restart unitplast-bot                         ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 System is LIVE and AUTONOMOUS!"
echo "⏰ First news fetch in approximately 30 minutes..."
echo "📱 Open @UnitgroupAI and watch the channel fill!"
echo ""
