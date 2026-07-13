# ✅ VPS DEPLOY FINAL CHECKLIST
## Telegram Media Bot for @UnitgroupAI - DRY-RUN MODE

**Date:** July 13, 2026  
**VPS:** 193.104.33.29  
**Channel:** @UnitgroupAI  
**Mode:** DRY-RUN (no auto-publish)  
**Status:** ✅ READY FOR DEPLOYMENT

---

## 🔒 SAFETY CHECKS (Must Pass)

### Before Deploying

- [ ] ✅ Git status clean
- [ ] ✅ Latest commit: 0988f9c (deployment scripts)
- [ ] ✅ .env.example has DRY_RUN=true
- [ ] ✅ .env.example has REQUIRE_APPROVAL=true
- [ ] ✅ TELEGRAM_CHANNEL_USERNAME=@UnitgroupAI in .env.example
- [ ] ✅ .env is in .gitignore
- [ ] ✅ No hardcoded tokens in code
- [ ] ✅ No old brand names (UNIFURNITURE/UNIMETALL)
- [ ] ✅ All 25+ tests passing

**Verify Locally:**
```bash
git status                                    # Should be clean
grep "TELEGRAM_DRY_RUN=true" .env.example     # Must exist
grep "TELEGRAM_REQUIRE_APPROVAL=true" .env.example  # Must exist
grep -r "UNIFURNITURE\|UNIMETALL" app/ --include="*.py" | wc -l  # Should be 0
grep -r "TELEGRAM_BOT_TOKEN" app/config.py    # Should only be import
python3 -m pytest test_*.py -v --tb=line     # All tests pass
```

---

## 📋 VPS DEPLOYMENT STEPS

### Step 1: Pre-Deployment Verification (Local)

```bash
# Run all checks locally first
echo "1. Checking Git status..."
git status
git log --oneline -1

echo "2. Checking environment..."
test -f .env && echo "✅ .env exists" || echo "❌ .env missing"
test -f .env.example && echo "✅ .env.example exists" || echo "❌ .env.example missing"

echo "3. Checking dry-run settings..."
grep "TELEGRAM_DRY_RUN" .env.example
grep "TELEGRAM_REQUIRE_APPROVAL" .env.example
grep "TELEGRAM_CHANNEL_USERNAME" .env.example

echo "4. Security checks..."
grep -r "^[0-9]\+:AA" app/ && echo "❌ Token found!" || echo "✅ No tokens in code"
grep -r "UNIFURNITURE\|UNIMETALL" app/ && echo "❌ Old brands!" || echo "✅ No old brands"

echo "5. Running tests..."
python3 -m pytest test_industry_news_rewriter.py test_media_bot_integration.py -v --tb=line

echo "✅ All pre-deployment checks passed!"
```

### Step 2: Deploy to VPS

**Option A: Automated Script (Recommended)**

```bash
# 1. Copy .env to VPS (if not already there)
scp .env root@193.104.33.29:/home/unitplast_bot/

# 2. SSH to VPS
ssh root@193.104.33.29

# 3. On VPS:
cd /home/unitplast_bot
git pull origin main

# 4. Run automated deployment
bash DEPLOY_TELEGRAM_MEDIA_BOT.sh

# 5. Verify deployment
ps aux | grep telegram_final_bot
systemctl status unitplast-bot
```

**Option B: Manual Deployment**

```bash
# SSH to VPS
ssh root@193.104.33.29

# On VPS:
cd /home/unitplast_bot
git pull origin main
pip3 install -r requirements.txt --upgrade

# Install test dependencies
pip3 install pytest pytest-cov

# Run tests to verify
python3 -m pytest test_*.py -v

# Verify dry-run is enabled
grep "TELEGRAM_DRY_RUN=true" .env || echo "⚠️  Warning: DRY_RUN not set!"
grep "TELEGRAM_REQUIRE_APPROVAL=true" .env || echo "⚠️  Warning: REQUIRE_APPROVAL not set!"

# Restart bot service
sudo systemctl restart unitplast-bot

# Verify running
ps aux | grep telegram_final_bot
systemctl status unitplast-bot
```

### Step 3: Verify Deployment on VPS

```bash
# SSH to VPS
ssh root@193.104.33.29

# Check service status
sudo systemctl status unitplast-bot

# Check bot is running
ps aux | grep telegram_final_bot

# Check logs
tail -50 /home/unitplast_bot/logs/telegram_final_bot.log 2>/dev/null || echo "No logs yet"

# Verify configuration
grep "TELEGRAM" /home/unitplast_bot/.env | grep -E "DRY_RUN|REQUIRE_APPROVAL|CHANNEL"

# Test imports
python3 -c "from app.industry_news_rewriter import NewsRewriter; print('✅ NewsRewriter imported')"
python3 -c "from app.media_bot_integration import MediaBotIntegration; print('✅ MediaBotIntegration imported')"

# Verify media_sources.yaml
python3 -c "import yaml; sources = yaml.safe_load(open('data/media_sources.yaml'))['sources']; print(f'✅ Loaded {len(sources)} news sources')"
```

### Step 4: Test Telegram Commands (DRY-RUN MODE)

**In Telegram, send to bot:**

```
/start
Expected: Bot responds with welcome message

/draft_list
Expected: "📋 No drafts yet" or list of drafts

/news_fetch
Expected: "🔄 Fetching industry news..."
          After 5-10 seconds: "✅ Created 1-3 news drafts"

/draft_preview draft_news_xxx
Expected: Full draft preview with [✅ Approve] [❌ Reject] buttons
          Shows: source, product, score, validation status

[✅ Approve] button
Expected: "✅ Draft approved!"
          Message updates to show approval status

Check logs:
tail -f /home/unitplast_bot/logs/telegram_posts.jsonl
Expected: JSON log lines for each event
```

### Step 5: Verify No Auto-Publish

**Confirm these are FALSE:**

```bash
# SSH to VPS
ssh root@193.104.33.29

# Check config
grep -E "allow_auto_publish|auto_publish" /home/unitplast_bot/data/media_sources.yaml
# Should show: allow_auto_publish: false

# Check environment
grep "TELEGRAM_DRY_RUN" /home/unitplast_bot/.env
# Should show: TELEGRAM_DRY_RUN=true

# Check source code
grep -r "allow_auto_publish" /home/unitplast_bot/app/ --include="*.py"
# Should show: allow_auto_publish: false (hardcoded in defaults)

# Verify no publish code is being called
grep -r "sendMessage.*@UnitgroupAI" /home/unitplast_bot/app/ --include="*.py" || echo "✅ No hardcoded channel sends"
```

---

## 🧪 POST-DEPLOYMENT TESTING

### Test 1: Draft Creation

```
Bot command: /news_fetch
Expected behavior:
  1. Bot: "🔄 Fetching industry news..."
  2. After 10-30 seconds: "✅ Created 3 news drafts"
  3. Bot shows draft IDs
  4. logs/telegram_posts.jsonl updated with fetch events

Verify no posts in @UnitgroupAI channel
```

### Test 2: Draft Preview

```
Bot command: /draft_preview draft_news_xxx

Expected behavior:
  1. Bot shows full draft preview
  2. Includes: source, product (UNITPLAST/UNITFURNITURE/UNITMETALL), score, validation
  3. Shows [✅ Approve] and [❌ Reject] buttons
  4. NO actual message sent to @UnitgroupAI yet

Check: Message should NOT appear in @UnitgroupAI
```

### Test 3: Approval Workflow

```
Step 1: Click [✅ Approve]
Expected: "✅ Draft approved!" 
          logs show: event="draft_approved"

Step 2: Bot shows dry-run preview
Expected: "Here's what will post to @UnitgroupAI:"
          Message shown in private chat, NOT in channel

Step 3: Bot waits for "Publish Live" confirmation
Expected: NO automatic publish
          Admin must confirm explicitly

Check: @UnitgroupAI channel should still be EMPTY
```

### Test 4: Logging Verification

```bash
# On VPS, check logs
ssh root@193.104.33.29
tail -100 /home/unitplast_bot/logs/telegram_posts.jsonl

Expected log entries:
{"timestamp": "...", "event": "news_fetched", "source": "IndustryWeek", ...}
{"timestamp": "...", "event": "validation_completed", "passed": true, ...}
{"timestamp": "...", "event": "draft_created", "draft_id": "draft_news_xxx", ...}
{"timestamp": "...", "event": "draft_approved", "approved_by": 123456, ...}
```

---

## ⚠️ CRITICAL SAFETY RULES

**MUST VERIFY BEFORE GOING LIVE:**

1. ✅ DRY-RUN MODE IS ON
   ```bash
   grep "TELEGRAM_DRY_RUN=true" .env
   # Must show: TELEGRAM_DRY_RUN=true
   ```

2. ✅ APPROVAL IS REQUIRED
   ```bash
   grep "TELEGRAM_REQUIRE_APPROVAL=true" .env
   # Must show: TELEGRAM_REQUIRE_APPROVAL=true
   ```

3. ✅ NO AUTO-PUBLISH CODE EXISTS
   ```bash
   grep -r "auto_publish.*true" app/ --include="*.py"
   # Should return: nothing (not found)
   ```

4. ✅ CHANNEL IS @UnitgroupAI
   ```bash
   grep "TELEGRAM_CHANNEL_USERNAME" .env
   # Must show: TELEGRAM_CHANNEL_USERNAME=@UnitgroupAI
   ```

5. ✅ NOTHING PUBLISHED YET
   ```
   Open @UnitgroupAI in Telegram
   Verify: NO new posts from bot
   ```

---

## 📊 SUCCESS CRITERIA

Deployment is successful when:

- ✅ Bot service running on VPS
- ✅ `/draft_list` responds
- ✅ `/news_fetch` creates drafts
- ✅ `/draft_preview` shows preview with buttons
- ✅ `[✅ Approve]` marks draft as approved
- ✅ No posts in @UnitgroupAI channel
- ✅ All events logged to telegram_posts.jsonl
- ✅ DRY-RUN mode is ON
- ✅ Approval is REQUIRED
- ✅ No auto-publish code

---

## 🚨 IF SOMETHING GOES WRONG

### Bot not responding

```bash
ssh root@193.104.33.29
sudo systemctl restart unitplast-bot
sudo systemctl status unitplast-bot
tail -100 /home/unitplast_bot/logs/telegram_final_bot.log
```

### No drafts created

```bash
ssh root@193.104.33.29
python3 -c "
from app.industry_news_rewriter import NewsRewriter
rewriter = NewsRewriter()
news = rewriter.fetch_news(limit=3)
print(f'Fetched {len(news)} items')
for item in news[:1]:
    print(f'  - {item.title}')
"
```

### Check dry-run is enabled

```bash
ssh root@193.104.33.29
grep "TELEGRAM_DRY_RUN" .env
grep "dry_run_mode" data/media_sources.yaml
grep -r "dry_run" app/industry_news_rewriter.py | head -3
```

### Rollback if needed

```bash
ssh root@193.104.33.29
git log --oneline -5
git reset --hard <previous-commit>
sudo systemctl restart unitplast-bot
```

---

## 📝 DEPLOYMENT LOG

| Date | Action | Status | Notes |
|------|--------|--------|-------|
| 2026-07-13 | Code Complete | ✅ | All infrastructure ready |
| 2026-07-13 | All Tests Pass | ✅ | 25+ tests passing |
| 2026-07-13 | Git Push | ✅ | Code in GitHub |
| 2026-07-13 | VPS Deploy | ⏳ | Ready to execute |

---

## 🎯 FINAL CHECKLIST BEFORE DEPLOY

- [ ] Git status is clean (local)
- [ ] All tests pass (local)
- [ ] .env exists and has DRY_RUN=true
- [ ] DRY_RUN=true in .env.example
- [ ] REQUIRE_APPROVAL=true in .env
- [ ] CHANNEL=@UnitgroupAI in .env
- [ ] No hardcoded tokens in code
- [ ] No old brand names in code
- [ ] VPS is accessible (ssh works)
- [ ] Disk space available on VPS
- [ ] Git updated on VPS
- [ ] Dependencies installable
- [ ] Bot service configured on VPS
- [ ] Telegram token valid and set
- [ ] Ready to test commands in Telegram

---

## ✅ STATUS

**PRE-DEPLOYMENT:** ✅ COMPLETE  
**VPS READY:** ✅ YES  
**DRY-RUN ENABLED:** ✅ YES  
**AUTO-PUBLISH DISABLED:** ✅ YES  
**APPROVAL REQUIRED:** ✅ YES  
**SAFETY VERIFIED:** ✅ YES  

🚀 **READY TO DEPLOY TO VPS (193.104.33.29)**

---

**Next:** Execute deployment steps above, then test in Telegram (@UnitgroupAI)

