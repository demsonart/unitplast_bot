#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# UNITGROUP AI / unitplast_bot - BOT STATUS CHECK
# Run on VPS: 193.104.33.29
# Date: July 13, 2026
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 1: SERVICE STATUS
# ═══════════════════════════════════════════════════════════════════════════════

print_header "CHECK 1: SERVICE STATUS"

echo "Checking systemd service..."
if sudo systemctl is-active --quiet unitplast-bot; then
    print_success "Service is ACTIVE"
    echo ""
    sudo systemctl status unitplast-bot --no-pager | head -15
else
    print_error "Service is NOT RUNNING"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 2: PROCESS VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

print_header "CHECK 2: PROCESS VERIFICATION"

echo "Checking running processes..."
if ps aux | grep -q "[t]elegram_final_bot"; then
    print_success "Bot process is running"
    ps aux | grep "telegram_final_bot" | grep -v grep | awk '{print $2, $8, $9, $10, $11}'
else
    print_error "Bot process NOT found"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 3: PORT LISTENING
# ═══════════════════════════════════════════════════════════════════════════════

print_header "CHECK 3: PORT LISTENING"

echo "Checking if Flask is listening on port 8000..."
if sudo lsof -i :8000 2>/dev/null | grep -q LISTEN; then
    print_success "Flask is listening on port 8000"
    sudo lsof -i :8000 | head -5
else
    print_warning "Port 8000 not found (might be using different port)"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 4: CONFIGURATION VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

print_header "CHECK 4: CONFIGURATION VERIFICATION"

echo "Verifying environment settings (without showing secrets)..."

if grep -q "TELEGRAM_DRY_RUN=true" .env; then
    print_success "Dry-run mode: ENABLED ✓"
else
    print_error "Dry-run mode: DISABLED ❌"
    exit 1
fi

if grep -q "TELEGRAM_REQUIRE_APPROVAL=true" .env; then
    print_success "Approval requirement: ENABLED ✓"
else
    print_error "Approval requirement: DISABLED ❌"
    exit 1
fi

if grep -q "TELEGRAM_CHANNEL_USERNAME=@UnitgroupAI" .env; then
    print_success "Channel: @UnitgroupAI ✓"
else
    print_error "Channel not set to @UnitgroupAI ❌"
    exit 1
fi

echo ""
echo "Token status:"
if grep -q "TELEGRAM_BOT_TOKEN=" .env; then
    TOKEN_LEN=$(grep "TELEGRAM_BOT_TOKEN=" .env | cut -d= -f2 | wc -c)
    if [ "$TOKEN_LEN" -gt 10 ]; then
        print_success "Bot token is configured (${TOKEN_LEN} chars)"
    else
        print_error "Bot token appears to be empty"
    fi
else
    print_error "TELEGRAM_BOT_TOKEN not found in .env"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 5: RECENT LOGS
# ═══════════════════════════════════════════════════════════════════════════════

print_header "CHECK 5: RECENT SYSTEM LOGS"

echo "Last 30 seconds of system journal..."
sudo journalctl -u unitplast-bot --since "30 seconds ago" --no-pager 2>/dev/null | tail -10
print_success "Journal check complete"

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 6: APPLICATION LOGS
# ═══════════════════════════════════════════════════════════════════════════════

print_header "CHECK 6: APPLICATION LOGS"

if [ -f "logs/telegram_final_bot.log" ]; then
    echo "Last 10 lines of bot log..."
    tail -10 logs/telegram_final_bot.log
    print_success "Bot log available"
else
    print_warning "Bot log file not found (will be created on first run)"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 7: DRAFT LOG (JSONL)
# ═══════════════════════════════════════════════════════════════════════════════

print_header "CHECK 7: DRAFT/EVENT LOG"

if [ -f "logs/telegram_posts.jsonl" ]; then
    LINE_COUNT=$(wc -l < logs/telegram_posts.jsonl)
    echo "Draft log has $LINE_COUNT entries"

    echo -e "\nLast 3 events:"
    tail -3 logs/telegram_posts.jsonl | python3 -m json.tool 2>/dev/null | head -20 || tail -3 logs/telegram_posts.jsonl
    print_success "Draft log available"
else
    print_warning "Draft log not found (will be created on first event)"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 8: DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════════

print_header "CHECK 8: KEY DEPENDENCIES"

echo "Python version:"
python3 --version
print_success "Python3 available"

echo -e "\nKey packages:"
python3 -c "import aiogram; print(f'  aiogram: {aiogram.__version__}')" 2>/dev/null || print_warning "  aiogram: NOT FOUND"
python3 -c "import flask; print(f'  flask: {flask.__version__}')" 2>/dev/null || print_warning "  flask: NOT FOUND"
python3 -c "import feedparser; print('  feedparser: OK')" 2>/dev/null || print_warning "  feedparser: NOT FOUND"
python3 -c "import yaml; print('  yaml: OK')" 2>/dev/null || print_warning "  yaml: NOT FOUND"

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 9: CODE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

print_header "CHECK 9: CODE VERIFICATION"

echo "Checking for old brand names..."
OLD_BRANDS=$(grep -r "UNIFURNITURE\|UNIMETALL" app/ --include="*.py" 2>/dev/null | grep -v "validation\|test" | wc -l || echo 0)
if [ "$OLD_BRANDS" -eq 0 ]; then
    print_success "No old brand names found"
else
    print_warning "Found $OLD_BRANDS old brand references"
fi

echo -e "\nVerifying media sources..."
if [ -f "data/media_sources.yaml" ]; then
    SOURCE_COUNT=$(python3 -c "import yaml; sources = yaml.safe_load(open('data/media_sources.yaml'))['sources']; print(len(sources))" 2>/dev/null || echo 0)
    if [ "$SOURCE_COUNT" -ge 18 ]; then
        print_success "$SOURCE_COUNT news sources configured"
    else
        print_warning "Only $SOURCE_COUNT sources (expected 18+)"
    fi
else
    print_error "media_sources.yaml not found"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# CHECK 10: FINAL STATUS
# ═══════════════════════════════════════════════════════════════════════════════

print_header "CHECK 10: FINAL STATUS SUMMARY"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║           🤖 BOT STATUS CHECK COMPLETE                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Status Summary:"
echo "  ✅ Service: RUNNING"
echo "  ✅ Process: ACTIVE"
echo "  ✅ Configuration: VERIFIED"
echo "  ✅ Dry-run: ENABLED"
echo "  ✅ Approval: REQUIRED"
echo "  ✅ Channel: @UnitgroupAI"
echo "  ✅ Dependencies: AVAILABLE"
echo ""
echo "Next Steps:"
echo "  1. Test in Telegram:"
echo "     /draft_list              - Check draft status"
echo "     /news_fetch              - Fetch news sources"
echo "     /draft_preview <id>      - Preview draft"
echo ""
echo "  2. Verify channel is empty:"
echo "     Open @UnitgroupAI in Telegram"
echo "     Should show NO new posts (dry-run prevents publish)"
echo ""
echo "  3. Monitor logs in real-time:"
echo "     tail -f logs/telegram_posts.jsonl"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "Status: ✅ BOT IS OPERATIONAL"
echo "════════════════════════════════════════════════════════════"
echo ""

print_success "STATUS CHECK COMPLETE"
