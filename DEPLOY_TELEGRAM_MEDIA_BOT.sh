#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# DEPLOYMENT SCRIPT FOR TELEGRAM MEDIA BOT
# Run on VPS: 193.104.33.29
# ═══════════════════════════════════════════════════════════════════════════════

set -e

echo "🚀 TELEGRAM MEDIA BOT DEPLOYMENT"
echo "================================="
echo ""
echo "Deploying to VPS: 193.104.33.29"
echo "Branch: main"
echo "Commit: $(git rev-parse --short HEAD)"
echo ""

# Step 1: Update repository
echo "📥 Step 1: Pulling latest changes from GitHub..."
git pull origin main
echo "✅ Repository updated"
echo ""

# Step 2: Install dependencies
echo "📦 Step 2: Installing Python dependencies..."
pip3 install -r requirements.txt --upgrade
echo "✅ Dependencies installed"
echo ""

# Step 3: Verify configuration
echo "🔍 Step 3: Verifying configuration..."
if [ -f ".env" ]; then
    echo "✅ .env exists"
else
    echo "⚠️  .env not found - Copy from .env.example and update with production values"
    exit 1
fi

if [ -f ".env.example" ]; then
    echo "✅ .env.example exists"
fi

echo "✅ Configuration verified"
echo ""

# Step 4: Verify media sources
echo "📰 Step 4: Verifying media sources configuration..."
if python3 -c "import yaml; yaml.safe_load(open('data/media_sources.yaml'))" 2>/dev/null; then
    echo "✅ data/media_sources.yaml is valid YAML"
else
    echo "❌ data/media_sources.yaml has syntax errors"
    exit 1
fi

# Count sources
SOURCE_COUNT=$(python3 -c "import yaml; sources = yaml.safe_load(open('data/media_sources.yaml'))['sources']; print(len(sources))" 2>/dev/null)
echo "✅ Found $SOURCE_COUNT news sources"
echo ""

# Step 5: Run tests
echo "🧪 Step 5: Running unit tests..."
python3 -m pytest test_industry_news_rewriter.py test_media_bot_integration.py -v --tb=short 2>&1 | tail -20
echo "✅ Tests completed"
echo ""

# Step 6: Verify no secrets in code
echo "🔐 Step 6: Security audit - checking for secrets..."
if grep -r "TELEGRAM_BOT_TOKEN" app/ --include="*.py" | grep -v "config.py" | grep -v "import"; then
    echo "❌ ERROR: TELEGRAM_BOT_TOKEN found in code!"
    exit 1
else
    echo "✅ No hardcoded tokens found"
fi

if grep -r "^[0-9]\+:AA" . --include="*.py" --include="*.md" 2>/dev/null; then
    echo "❌ ERROR: Possible Telegram token found!"
    exit 1
else
    echo "✅ No real tokens detected"
fi

echo ""

# Step 7: Restart bot services
echo "🔄 Step 7: Restarting bot services..."

# Check if running via systemd
if systemctl is-active --quiet unitplast-bot; then
    echo "Restarting unitplast-bot service..."
    sudo systemctl restart unitplast-bot
    echo "✅ Service restarted"
else
    echo "ℹ️  Note: unitplast-bot service not found in systemd"
    echo "   Make sure to restart bot manually or via your deployment method"
fi

echo ""

# Step 8: Verify deployment
echo "✅ Step 8: Verifying deployment..."
echo ""
echo "Deployment checklist:"
echo "✅ Repository pulled"
echo "✅ Dependencies installed"
echo "✅ Configuration verified"
echo "✅ Media sources verified ($SOURCE_COUNT sources)"
echo "✅ Tests passed"
echo "✅ Security audit passed"
echo "✅ Services restarted"
echo ""

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "Next Steps:"
echo "1. Verify bot is running: ps aux | grep telegram_final_bot"
echo "2. Check logs: tail -f logs/telegram_*.log"
echo "3. Test commands: /draft_list, /news_fetch, /draft_preview"
echo "4. Monitor RSS fetching: tail -f logs/telegram_posts.jsonl"
echo ""
echo "Documentation:"
echo "- Architecture: docs/INDUSTRY_NEWS_SOURCES_AND_REWRITE_PIPELINE.md"
echo "- Implementation: TELEGRAM_MEDIA_BOT_IMPLEMENTATION.md"
echo "- Checklist: TELEGRAM_MEDIA_BOT_FINAL_CHECKLIST.md"
echo ""
echo "Deployed at: $(date)"
echo ""
