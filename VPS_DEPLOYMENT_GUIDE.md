# 🚀 VPS DEPLOYMENT GUIDE - TELEGRAM MEDIA BOT

**Target VPS:** 193.104.33.29  
**Date:** July 13, 2026  
**Status:** Ready to Deploy

---

## ⚡ Quick Deploy (5 minutes)

### Option 1: Automated Script (Recommended)

```bash
# SSH to VPS
ssh root@193.104.33.29

# Navigate to project
cd /home/unitplast_bot

# Pull latest code
git pull origin main

# Run automated deployment script
bash DEPLOY_TELEGRAM_MEDIA_BOT.sh
```

### Option 2: Manual Steps

```bash
# 1. SSH to VPS
ssh root@193.104.33.29

# 2. Navigate to project directory
cd /home/unitplast_bot

# 3. Pull latest changes
git pull origin main

# 4. Install/upgrade dependencies
pip3 install -r requirements.txt --upgrade

# 5. Verify configuration
cat .env | grep TELEGRAM

# 6. Run tests
python3 -m pytest test_industry_news_rewriter.py test_media_bot_integration.py -v

# 7. Restart bot service
sudo systemctl restart unitplast-bot

# 8. Verify running
ps aux | grep telegram_final_bot
```

---

## 📋 PRE-DEPLOYMENT CHECKLIST

Before deploying, verify:

- ✅ Latest code committed and pushed to GitHub
- ✅ Git status clean: `git status`
- ✅ .env file exists with production values
- ✅ TELEGRAM_BOT_TOKEN set correctly
- ✅ TELEGRAM_CHANNEL_USERNAME = @UnitgroupAI
- ✅ Database migrations (if any) applied
- ✅ No hardcoded secrets in code
- ✅ All tests pass locally

```bash
# Verify locally before pushing
git status
python3 -m pytest test_*.py -v
grep -r "TELEGRAM_BOT_TOKEN" app/ | grep -v config.py
```

---

## 🔐 SECURITY CHECKLIST

Verify security before deployment:

```bash
# 1. Check no hardcoded tokens
grep -r "^[0-9]\+:AA" . --include="*.py"
grep -r "TELEGRAM_BOT_TOKEN" . --exclude-dir=.git --include="*.py" | grep -v config.py | grep -v test | grep -v ".env"

# 2. Verify .env is in .gitignore
grep "^.env" .gitignore

# 3. Verify no old brand names
grep -r "UNIFURNITURE\|UNIMETALL" app/ --include="*.py"

# 4. Check .env exists on VPS
ssh root@193.104.33.29 "test -f /home/unitplast_bot/.env && echo '✅ .env exists' || echo '❌ .env missing'"
```

---

## 📥 WHAT GETS DEPLOYED

**New/Updated Files:**
```
data/media_sources.yaml                              (18 RSS sources)
skills/news_rewrite_for_telegram_skill.md           (updated with scoring)
.claude/agents/industry-news-rewriter.md            (10-step workflow)
app/industry_news_rewriter.py                       (NewsRewriter class)
app/media_bot_integration.py                        (Admin workflow)
test_industry_news_rewriter.py                      (14 tests)
test_media_bot_integration.py                       (11 tests)
requirements.txt                                    (feedparser, PyYAML added)
.env.example                                        (updated with TELEGRAM_MEDIA_BOT_*)
docs/INDUSTRY_NEWS_SOURCES_AND_REWRITE_PIPELINE.md (architecture)
TELEGRAM_MEDIA_BOT_IMPLEMENTATION.md               (implementation guide)
TELEGRAM_MEDIA_BOT_FINAL_CHECKLIST.md              (checklist)
DEPLOY_TELEGRAM_MEDIA_BOT.sh                       (this deployment script)
VPS_DEPLOYMENT_GUIDE.md                            (this guide)
```

---

## 🔄 DEPLOYMENT WORKFLOW

```
Local Machine
  ↓
git pull origin main (latest)
  ↓
python3 -m pytest (verify tests pass)
  ↓
git push origin main (push to GitHub)
  ↓
VPS (193.104.33.29)
  ↓
git pull origin main (get latest code)
  ↓
pip3 install -r requirements.txt (install deps)
  ↓
Run DEPLOY_TELEGRAM_MEDIA_BOT.sh (automated checks)
  ↓
sudo systemctl restart unitplast-bot (restart service)
  ↓
Verify running (ps aux | grep telegram)
  ↓
Check logs (tail -f logs/telegram_posts.jsonl)
```

---

## 📊 WHAT HAPPENS AFTER DEPLOYMENT

### Telegram Bot Commands Available

```
/draft_list              → List all drafts by status
/news_fetch              → Fetch latest news, create drafts
/draft_preview <id>      → Preview specific draft
[✅ Approve] button      → Approve draft for publication
[❌ Reject] button       → Reject draft
```

### Automated Processes

- **RSS Feed Fetching** (on command: /news_fetch)
  - Fetches from 18 sources
  - Filters by keywords
  - Scores relevance (min 0.6)
  - Creates JSON drafts

- **Admin Approval Workflow**
  - Draft → Preview → Admin Review → Approve/Reject → Dry-Run → Publish

- **Logging**
  - All events logged to `logs/telegram_posts.jsonl`
  - Format: JSONL (one JSON per line)
  - Events: fetch, filter, score, rewrite, validate, approve, publish

---

## 🧪 POST-DEPLOYMENT VERIFICATION

After deployment, verify everything works:

```bash
# 1. Check bot is running
ssh root@193.104.33.29
ps aux | grep telegram_final_bot
# Should show: python3 -m app.telegram_final_bot

# 2. Check logs
tail -f /home/unitplast_bot/logs/telegram_posts.jsonl

# 3. Test bot commands in Telegram
# Send: /draft_list
# Expected: Bot shows draft summary

# 4. Verify no errors
grep -i error /home/unitplast_bot/logs/telegram_*.log | tail -5

# 5. Check RSS fetching
# Send: /news_fetch
# Expected: Bot fetches news, creates 1-3 drafts

# 6. Verify approvals workflow
# /draft_preview <id>
# Should show [✅ Approve] [❌ Reject] buttons
```

---

## ⚠️ TROUBLESHOOTING

### Bot not responding to commands

```bash
# Check if service is running
sudo systemctl status unitplast-bot

# Restart if needed
sudo systemctl restart unitplast-bot

# Check logs for errors
tail -100 /home/unitplast_bot/logs/telegram_final_bot.log
```

### No drafts being created

```bash
# Verify RSS sources are accessible
python3 -c "
import yaml
from app.industry_news_rewriter import NewsRewriter
rewriter = NewsRewriter()
news = rewriter.fetch_news(limit=5)
print(f'Fetched {len(news)} items')
"

# Check network connectivity
curl https://www.industryweek.com/feed -I

# Verify media_sources.yaml syntax
python3 -c "import yaml; yaml.safe_load(open('data/media_sources.yaml'))"
```

### Token/authentication errors

```bash
# Verify .env has correct token
grep TELEGRAM_BOT_TOKEN .env

# Verify token format (should be: 123456789:ABCdefGHIjklmnOPQRstuvWXYZ...)
# Token must start with digits followed by :AA...

# Test connection
python3 -c "
from aiogram import Bot
from app.config import TELEGRAM_BOT_TOKEN
bot = Bot(token=TELEGRAM_BOT_TOKEN)
print('✅ Bot token valid' if TELEGRAM_BOT_TOKEN else '❌ Token missing')
"
```

### Memory/performance issues

```bash
# Check memory usage
top -p $(pgrep -f telegram_final_bot)

# If high memory, restart service
sudo systemctl restart unitplast-bot

# Check disk space
df -h /home/unitplast_bot

# Archive old logs if needed
gzip /home/unitplast_bot/logs/*.log
```

---

## 📝 ROLLBACK PLAN

If deployment has issues:

```bash
# 1. Check git status
git status

# 2. View recent commits
git log --oneline -10

# 3. Rollback to previous commit if needed
git revert HEAD
# OR
git reset --hard <previous-commit-hash>

# 4. Reinstall dependencies
pip3 install -r requirements.txt

# 5. Restart service
sudo systemctl restart unitplast-bot
```

---

## 📚 DOCUMENTATION

**Post-Deployment, read:**

1. **TELEGRAM_MEDIA_BOT_IMPLEMENTATION.md**
   - Complete implementation guide
   - Admin workflow details
   - Commands reference

2. **docs/INDUSTRY_NEWS_SOURCES_AND_REWRITE_PIPELINE.md**
   - Architecture overview
   - All 18 sources described
   - Scoring examples
   - Approval workflow details

3. **TELEGRAM_MEDIA_BOT_FINAL_CHECKLIST.md**
   - Definition of Done verification
   - Safety guarantees
   - Risk assessment

---

## 🎯 SUCCESS CRITERIA

Deployment is successful when:

- ✅ Bot service running
- ✅ `/draft_list` returns "No drafts yet"
- ✅ `/news_fetch` creates 1-3 drafts
- ✅ `/draft_preview <id>` shows preview with buttons
- ✅ [✅ Approve] button works
- ✅ Logs record all events
- ✅ No errors in logs

---

## 🚨 EMERGENCY CONTACTS

If deployment fails:

1. **Check logs first**
   ```bash
   tail -100 /home/unitplast_bot/logs/telegram_*.log
   ```

2. **Verify configuration**
   ```bash
   cat .env | grep -E "TELEGRAM|DATABASE"
   ```

3. **Restart service**
   ```bash
   sudo systemctl restart unitplast-bot
   sudo systemctl status unitplast-bot
   ```

4. **Rollback if needed**
   ```bash
   git log --oneline -5
   git reset --hard <previous-commit>
   sudo systemctl restart unitplast-bot
   ```

---

## 📅 DEPLOYMENT LOG

| Date | Action | Status | Notes |
|------|--------|--------|-------|
| 2026-07-13 | Code Complete | ✅ | All 18 sources configured |
| 2026-07-13 | Tests Pass | ✅ | 25+ tests passing |
| 2026-07-13 | Git Push | ✅ | Code in GitHub |
| 2026-07-13 | Deploy Script | ✅ | DEPLOY_TELEGRAM_MEDIA_BOT.sh ready |
| 2026-07-13 | VPS Deploy | ⏳ | Ready to run |

---

**Last Updated:** 2026-07-13  
**Status:** 🟢 READY FOR DEPLOYMENT  
**Next:** Run deployment script on VPS

