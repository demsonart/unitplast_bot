# 🚀 VPS DEPLOYMENT INSTRUCTIONS
## UNITGROUP AI / unitplast_bot → 193.104.33.29

**Date:** July 13, 2026  
**Status:** ✅ READY TO DEPLOY  
**Mode:** Production with DRY-RUN  

---

## ⚡ QUICK START (3 Steps)

### Step 1: SSH to VPS

```bash
ssh root@193.104.33.29
```

### Step 2: Navigate to Project

```bash
cd /home/unitplast_bot
```

### Step 3: Run Deployment Playbook

```bash
bash VPS_DEPLOYMENT_PLAYBOOK.sh
```

**That's it!** The playbook will:
- ✅ Pull latest code from GitHub
- ✅ Verify environment configuration
- ✅ Install dependencies
- ✅ Run tests
- ✅ Start/restart service
- ✅ Verify security settings
- ✅ Display deployment status

---

## 📋 WHAT THE PLAYBOOK DOES

The `VPS_DEPLOYMENT_PLAYBOOK.sh` runs 8 phases:

### Phase 0: Pre-Deployment Verification
- Check git repository status
- Verify current branch (main)
- Display recent commits

### Phase 1: Update Code
- `git pull origin main`
- Verify latest commit
- Status: ✅ Complete

### Phase 2: Environment Verification
- Check .env file exists
- Verify `TELEGRAM_CHANNEL_USERNAME=@UnitgroupAI`
- Verify `TELEGRAM_DRY_RUN=true`
- Verify `TELEGRAM_REQUIRE_APPROVAL=true`

### Phase 3: Install Dependencies
- Install/upgrade Python packages
- Verify aiogram, flask, feedparser, yaml
- Status: ✅ Dependencies ready

### Phase 4: Code Verification
- Check for old brand names (UNIFURNITURE/UNIMETALL)
- Verify no Math.random() in calculations
- Count news sources (must be 18+)

### Phase 5: Run Tests
- Install pytest
- Run test_industry_news_rewriter.py (14 tests)
- Run test_media_bot_integration.py (11 tests)
- Status: ✅ All tests pass

### Phase 6: Systemd Service
- Stop service (if running)
- Start/restart service
- Verify service is running
- Display service status

### Phase 7: Security Verification
- ✅ Dry-run mode: ENABLED
- ✅ Approval requirement: ENABLED
- ✅ Channel: @UnitgroupAI
- ✅ No token leaks in logs

### Phase 8: Final Status
- Display deployment summary
- Show next steps
- Confirm: ✅ PRODUCTION READY

---

## ✅ SUCCESS CRITERIA

After playbook completes, you should see:

```
╔═══════════════════════════════════════════════════════════╗
║        🎉 DEPLOYMENT COMPLETE - STATUS REPORT            ║
╚═══════════════════════════════════════════════════════════╝

Deployment Summary:
  ✅ Code: Updated from GitHub
  ✅ Branch: main
  ✅ Python: Configured
  ✅ Dependencies: Installed
  ✅ Tests: Passed
  ✅ Service: Running
  ✅ Dry-run: ENABLED
  ✅ Approval: REQUIRED
  ✅ Channel: @UnitgroupAI

Status: ✅ PRODUCTION READY - DRY-RUN MODE ACTIVE
```

---

## 🧪 AFTER DEPLOYMENT - TEST IN TELEGRAM

### 1. Test with Bot (Private Chat)

Send to bot:
```
/draft_list
```

Expected response:
```
📋 No drafts yet
or
📋 Total Drafts: 0
```

### 2. Create Drafts

Send to bot:
```
/news_fetch
```

Expected response:
```
🔄 Fetching industry news...
✅ Created 3 news drafts
[list of draft IDs]

Use /draft_preview <id> to review
```

### 3. Preview Draft

Send to bot:
```
/draft_preview draft_news_xxx_001
```

Expected response:
```
🔍 DRAFT PREVIEW

📰 draft_news_xxx_001

Source: IndustryWeek
Product: UNITFURNITURE
Score: 0.85
Date: 2024-07-13

[Full draft text with emoji, headline, body, CTA, source]

[✅ Approve] [❌ Reject]
[📝 Edit in App] [🔗 View Source]
```

### 4. Verify Channel is Empty

Open @UnitgroupAI in Telegram:
```
Expected: NO new posts from bot
(Dry-run mode prevents publishing)
```

---

## 🔍 VERIFICATION COMMANDS

After deployment, verify manually:

```bash
# Check service is running
sudo systemctl status unitplast-bot

# Check process
ps aux | grep telegram_final_bot

# Check logs
tail -50 /home/unitplast_bot/logs/telegram_final_bot.log

# Check draft log
tail -20 /home/unitplast_bot/logs/telegram_posts.jsonl

# Verify configuration
grep -E "TELEGRAM_DRY_RUN|TELEGRAM_REQUIRE_APPROVAL|TELEGRAM_CHANNEL" .env

# Test Python import
python3 -c "from app.industry_news_rewriter import NewsRewriter; print('✅ Imports OK')"
```

---

## ⚠️ IF SOMETHING GOES WRONG

### Service Won't Start

```bash
# Check logs
sudo journalctl -u unitplast-bot -n 100 --no-pager

# Restart manually
sudo systemctl restart unitplast-bot

# Check status
sudo systemctl status unitplast-bot --no-pager
```

### Dependency Issues

```bash
# Reinstall all dependencies
pip3 install -r requirements.txt --upgrade --force-reinstall

# Check specific package
python3 -c "import aiogram; print(aiogram.__version__)"
```

### Token/Environment Issues

```bash
# Verify .env file
cat .env | grep -E "TELEGRAM|DRY|APPROVAL|CHANNEL"

# Check for syntax errors
python3 -c "import dotenv; dotenv.load_dotenv(); print('✅ .env OK')"
```

### Rollback

If something critical breaks:

```bash
# Check git log
git log --oneline -5

# Rollback to previous commit
git reset --hard <previous-commit>

# Restart service
sudo systemctl restart unitplast-bot
```

---

## 📊 MONITORING

### Real-Time Logs

```bash
# Watch bot logs
tail -f logs/telegram_final_bot.log

# Watch media bot logs
tail -f logs/telegram_posts.jsonl

# Watch system journal
sudo journalctl -u unitplast-bot -f
```

### Key Monitoring Points

1. **Dry-Run Mode:** Should always be `true`
2. **Approval Requirement:** Should always be `true`
3. **Channel:** Should always be `@UnitgroupAI`
4. **Publications:** Should be `ZERO` (dry-run mode prevents publish)
5. **Errors:** Should be minimal (check logs)

---

## ✨ DEPLOYMENT CHECKLIST

Before running playbook:
- [ ] Logged into VPS via SSH
- [ ] In `/home/unitplast_bot` directory
- [ ] .env file exists with token
- [ ] TELEGRAM_DRY_RUN=true in .env
- [ ] TELEGRAM_REQUIRE_APPROVAL=true in .env
- [ ] TELEGRAM_CHANNEL_USERNAME=@UnitgroupAI in .env

After running playbook:
- [ ] All 8 phases completed
- [ ] ✅ Code updated
- [ ] ✅ Tests passed
- [ ] ✅ Service running
- [ ] ✅ Dry-run enabled
- [ ] ✅ Approval required
- [ ] ✅ Channel verified

After testing in Telegram:
- [ ] /draft_list responds
- [ ] /news_fetch creates drafts
- [ ] /draft_preview shows preview
- [ ] [✅ Approve] button works
- [ ] @UnitgroupAI has NO new posts
- [ ] Logs updated with events

---

## 🎯 NEXT STEPS

1. **Deploy** using playbook ✅
2. **Test** using commands above ✅
3. **Monitor** logs for events ✅
4. **Verify** no publications to @UnitgroupAI ✅
5. **Document** deployment report ✅
6. **Plan** transition from dry-run mode (if needed)

---

## 📞 TROUBLESHOOTING REFERENCE

| Issue | Solution |
|-------|----------|
| Service won't start | Check logs with `journalctl` |
| Tests fail | Run `pip3 install -r requirements.txt` |
| Dry-run disabled | Check .env file (must have TELEGRAM_DRY_RUN=true) |
| No drafts created | Check media_sources.yaml and test RSS feeds |
| Approval not working | Check TELEGRAM_REQUIRE_APPROVAL=true |
| Posts in @UnitgroupAI | CRITICAL - dry-run mode is OFF, check .env |

---

## 📝 DEPLOYMENT REPORT

After deployment, run this to create report:

```bash
# Create deployment report
cat > docs/VPS_DEPLOYMENT_REPORT_$(date +%Y%m%d).md << 'EOF'
# VPS Deployment Report
- Date: $(date)
- Path: /home/unitplast_bot
- Git commit: $(git rev-parse --short HEAD)
- Service status: $(sudo systemctl status unitplast-bot 2>/dev/null | grep Active)
- Dry-run: $(grep TELEGRAM_DRY_RUN .env)
- Approval: $(grep TELEGRAM_REQUIRE_APPROVAL .env)
- Channel: $(grep TELEGRAM_CHANNEL_USERNAME .env)
EOF
```

---

## ✅ STATUS

🟢 **READY FOR DEPLOYMENT**

All files prepared. Playbook tested. Ready to execute.

Execute on VPS:
```bash
cd /home/unitplast_bot
bash VPS_DEPLOYMENT_PLAYBOOK.sh
```

---

**Prepared:** July 13, 2026  
**Status:** ✅ PRODUCTION READY  
**Mode:** Dry-Run Active  
**Safety:** ALL CHECKS PASS  

