# 🚀 VS CODE TO VPS - DEPLOYMENT INSTRUCTIONS
## Execute on VPS: 193.104.33.29

**Date:** July 13, 2026  
**Bot:** @Media_Unitgroup_bot  
**Channel:** @UnitgroupAI  
**Mode:** DRY-RUN ACTIVE (Safe)  

---

## ⚡ QUICK START - 3 COMMANDS

Copy and paste these commands into terminal:

```bash
ssh root@193.104.33.29 && cd /home/unitplast_bot && bash VPS_DEPLOYMENT_PLAYBOOK.sh
```

Or execute step-by-step:

```bash
# 1. SSH to VPS
ssh root@193.104.33.29

# 2. Navigate to project
cd /home/unitplast_bot

# 3. Run deployment
bash VPS_DEPLOYMENT_PLAYBOOK.sh
```

---

## 📋 FULL DEPLOYMENT SEQUENCE

### STEP 1: SSH Connection

```bash
ssh root@193.104.33.29
```

**Expected output:**
```
Welcome to Ubuntu 22.04.1 LTS
...
root@vps-193-104-33-29:~#
```

### STEP 2: Verify Project Directory

```bash
cd /home/unitplast_bot
pwd
```

**Expected:**
```
/home/unitplast_bot
```

### STEP 3: Check Git Status

```bash
git status
```

**Expected:**
```
On branch main
nothing to commit, working tree clean
```

### STEP 4: Verify Latest Commit

```bash
git log --oneline -1
```

**Expected:**
```
bc12389 docs: Deployment start guide - ready to execute on VPS
```

### STEP 5: Pull Latest Code (Safety Check)

```bash
git pull origin main
```

**Expected:**
```
Already up to date.
```

### STEP 6: Verify Configuration Settings

```bash
grep -E "TELEGRAM_DRY_RUN|TELEGRAM_REQUIRE_APPROVAL|TELEGRAM_CHANNEL_USERNAME" .env
```

**Expected output (without showing full token):**
```
TELEGRAM_DRY_RUN=true
TELEGRAM_REQUIRE_APPROVAL=true
TELEGRAM_CHANNEL_USERNAME=@UnitgroupAI
```

**Safety check - show token is configured but hide value:**
```bash
grep "TELEGRAM_MEDIA_BOT_TOKEN" .env | sed 's/=.*/=***HIDDEN***/'
```

**Expected:**
```
TELEGRAM_MEDIA_BOT_TOKEN=***HIDDEN***
```

### STEP 7: Make Scripts Executable

```bash
chmod +x VPS_DEPLOYMENT_PLAYBOOK.sh
chmod +x VPS_BOT_STATUS_CHECK.sh
```

### STEP 8: Run Deployment Playbook

```bash
bash VPS_DEPLOYMENT_PLAYBOOK.sh
```

**This will execute 8 phases:**
- Phase 0: Pre-deployment verification
- Phase 1: Update code from GitHub
- Phase 2: Verify environment settings
- Phase 3: Install dependencies
- Phase 4: Verify code quality
- Phase 5: Run tests (25+)
- Phase 6: Start/restart systemd service
- Phase 7: Security verification
- Phase 8: Final status report

**Expected final output:**
```
╔═══════════════════════════════════════════════════════════╗
║        🎉 DEPLOYMENT COMPLETE - STATUS REPORT            ║
╚═══════════════════════════════════════════════════════════╝

Deployment Summary:
  ✅ Code: Updated from GitHub
  ✅ Tests: Passed
  ✅ Service: Running
  ✅ Dry-run: ENABLED
  ✅ Approval: REQUIRED
  ✅ Channel: @UnitgroupAI

Status: ✅ PRODUCTION READY - DRY-RUN MODE ACTIVE
```

---

## ✅ POST-DEPLOYMENT VERIFICATION

### Check 1: Service Status

```bash
sudo systemctl status unitplast-bot --no-pager
```

**Expected:**
```
● unitplast-bot.service - Loaded | Active (running)
```

### Check 2: View System Logs

```bash
sudo journalctl -u unitplast-bot -n 100 --no-pager
```

**Expected:** Clean logs, no critical errors

### Check 3: List Running Processes

```bash
ps aux | grep telegram_final_bot | grep -v grep
```

**Expected:** One process line showing bot is running

---

## 📱 TEST BOT IN TELEGRAM (After Deployment)

### Test 1: Check Bot Status

Open Telegram → @Media_Unitgroup_bot (private chat)

Send:
```
/draft_list
```

**Expected response:**
```
📋 Total Drafts: 0
or
📋 No drafts yet
```

### Test 2: Fetch News

Send:
```
/news_fetch
```

**Expected response (after 5-30 seconds):**
```
🔄 Fetching industry news...
✅ Created 3 news drafts

Drafts:
  1. draft_news_xxx_001
  2. draft_news_xxx_002
  3. draft_news_xxx_003

Use /draft_preview <id> to review drafts
```

### Test 3: Preview Draft

Send:
```
/draft_preview draft_news_xxx_001
```

**Expected response:**
```
🔍 DRAFT PREVIEW

📰 draft_news_xxx_001

[Full draft with headline, body, CTA, source attribution]

[✅ Approve] [❌ Reject]
[📝 Edit] [🔗 View Source]
```

### Test 4: Approve Draft

Click the `[✅ Approve]` button

**Expected:**
```
✅ Draft approved for dry-run preview

[Shows how post will look]

Note: In dry-run mode, post is NOT published to @UnitgroupAI
```

### Test 5: Verify Channel is Empty ⚠️ CRITICAL

Open Telegram → Search: `@UnitgroupAI`

**Expected:**
```
❌ NO new posts from bot
❌ Channel should remain EMPTY
(Dry-run mode prevents publishing)
```

**If you see posts:**
- 🚨 CRITICAL - Dry-run mode is not working
- Stop service immediately: `sudo systemctl stop unitplast-bot`
- Check .env: `grep TELEGRAM_DRY_RUN .env`
- Contact support

---

## 📊 MONITOR LOGS

### Real-time Event Log

```bash
tail -f logs/telegram_posts.jsonl
```

**Expected entries:**
```json
{"timestamp": "2026-07-13T...", "event": "news_fetched", "drafts_created": 3}
{"timestamp": "2026-07-13T...", "event": "draft_preview_requested", "draft_id": "..."}
{"timestamp": "2026-07-13T...", "event": "draft_approved", "mode": "dry_run", "published": false}
```

### System Journal (Real-time)

```bash
sudo journalctl -u unitplast-bot -f
```

### Bot Log File

```bash
tail -f logs/telegram_media_bot.log
```

---

## 🔐 SAFETY VERIFICATION CHECKLIST

After deployment, verify:

- [ ] Service running: `systemctl status unitplast-bot`
- [ ] Bot responds: `/draft_list` works in Telegram
- [ ] News fetching: `/news_fetch` creates drafts
- [ ] Preview works: `/draft_preview <id>` shows draft
- [ ] Dry-run active: `grep TELEGRAM_DRY_RUN .env` shows `true`
- [ ] Approval required: `grep TELEGRAM_REQUIRE_APPROVAL .env` shows `true`
- [ ] Channel correct: `grep TELEGRAM_CHANNEL_USERNAME .env` shows `@UnitgroupAI`
- [ ] **CRITICAL:** @UnitgroupAI has NO posts from bot
- [ ] Logs updated: `telegram_posts.jsonl` has events
- [ ] No errors in system logs

---

## ⚠️ TROUBLESHOOTING

### Service Won't Start

```bash
# Check detailed error
sudo journalctl -u unitplast-bot --no-pager | tail -50

# Try manual start
sudo systemctl start unitplast-bot

# Check status again
sudo systemctl status unitplast-bot
```

### Bot Not Responding

```bash
# Check if process is running
ps aux | grep telegram_final_bot

# Restart service
sudo systemctl restart unitplast-bot

# Wait 5 seconds
sleep 5

# Try bot command again in Telegram
/draft_list
```

### Test Failures

```bash
# Run tests manually
python3 -m pytest test_*.py -v

# Check Python version
python3 --version

# Reinstall dependencies
pip3 install -r requirements.txt --upgrade --force-reinstall
```

### Posts Published (DRY-RUN OFF - CRITICAL)

```bash
# 1. Stop service immediately
sudo systemctl stop unitplast-bot

# 2. Check setting
grep TELEGRAM_DRY_RUN .env

# 3. Fix if needed (must be true)
vim .env
# Edit: TELEGRAM_DRY_RUN=true

# 4. Delete posts from @UnitgroupAI manually via Telegram app

# 5. Restart with correct settings
sudo systemctl restart unitplast-bot

# 6. Verify dry-run is working
bash VPS_BOT_STATUS_CHECK.sh
```

---

## 📋 REFERENCE COMMANDS

```bash
# Service management
sudo systemctl start unitplast-bot
sudo systemctl stop unitplast-bot
sudo systemctl restart unitplast-bot
sudo systemctl status unitplast-bot

# Configuration verification
grep TELEGRAM .env | grep -E "DRY|APPROVAL|CHANNEL|BOT_TOKEN"

# Logs
tail -50 logs/telegram_final_bot.log
tail -20 logs/telegram_posts.jsonl
sudo journalctl -u unitplast-bot -n 100 --no-pager

# Testing
python3 -m pytest test_*.py -v

# System status
ps aux | grep telegram_final_bot
sudo lsof -i :8000
```

---

## ✨ DEPLOYMENT SUMMARY

```
╔════════════════════════════════════════════════════════════════╗
║                  DEPLOYMENT INSTRUCTIONS                      ║
║                                                                ║
║  Quick Deploy (one command):                                  ║
║  ssh root@193.104.33.29 && cd /home/unitplast_bot &&         ║
║  bash VPS_DEPLOYMENT_PLAYBOOK.sh                             ║
║                                                                ║
║  Or Step-by-step:                                             ║
║  1. ssh root@193.104.33.29                                    ║
║  2. cd /home/unitplast_bot                                    ║
║  3. bash VPS_DEPLOYMENT_PLAYBOOK.sh                           ║
║                                                                ║
║  Then Test:                                                    ║
║  - Send /draft_list to @Media_Unitgroup_bot                   ║
║  - Send /news_fetch to @Media_Unitgroup_bot                   ║
║  - Verify @UnitgroupAI shows NO posts                         ║
║                                                                ║
║  Expected: ✅ Service running, bot operational, channel empty ║
║  Time: ~3-5 minutes                                           ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

**Ready to deploy.** Follow these instructions carefully.  
Do NOT modify any settings without explicit authorization.  
Do NOT disable dry-run mode.  
Do NOT publish to @UnitgroupAI without approval.  

🚀 **EXECUTE DEPLOYMENT NOW**
