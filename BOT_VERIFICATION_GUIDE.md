# 🤖 BOT VERIFICATION GUIDE
## UNITGROUP AI / unitplast_bot

**Date:** July 13, 2026  
**Status:** Ready for verification  
**Mode:** DRY-RUN ACTIVE

---

## 🔍 QUICK VERIFICATION (5 minutes)

### Step 1: Check Service Status (On VPS)

```bash
# SSH to VPS
ssh root@193.104.33.29

# Navigate to project
cd /home/unitplast_bot

# Run status check
bash VPS_BOT_STATUS_CHECK.sh
```

**Expected Output:**
```
✅ Service: RUNNING
✅ Process: ACTIVE
✅ Configuration: VERIFIED
✅ Dry-run: ENABLED
✅ Approval: REQUIRED
✅ Channel: @UnitgroupAI
```

---

## 📱 TELEGRAM BOT VERIFICATION

### Step 1: Test Bot Commands (Private Chat)

Send these commands to the bot in Telegram:

#### Command 1: Check Draft Status
```
/draft_list
```

**Expected Response:**
```
📋 Total Drafts: 0
or
📋 No drafts yet
```

#### Command 2: Fetch News
```
/news_fetch
```

**Expected Response (after 5-30 seconds):**
```
🔄 Fetching industry news...
✅ Created 3 news drafts

Drafts:
  1. draft_news_xxx_001
  2. draft_news_xxx_002
  3. draft_news_xxx_003

Use /draft_preview <id> to review drafts
```

#### Command 3: Preview Draft
```
/draft_preview draft_news_xxx_001
```

**Expected Response:**
```
🔍 DRAFT PREVIEW

📰 draft_news_xxx_001

🏭 Industry News
Source: INDUSTRY_SITE
Product: UNITFURNITURE
Score: 0.87

[Full draft content with emoji, headline, body, CTA, source]

[✅ Approve] [❌ Reject]
[📝 Edit] [🔗 View Source]
```

#### Command 4: Test Approval Workflow
```
Click [✅ Approve] button
```

**Expected Response:**
```
✅ Draft approved for dry-run preview

Content preview:
[Shows how post will look]

In dry-run mode: Post is NOT published
Ready to transition to production
```

---

## ✅ CHANNEL VERIFICATION

### Step 1: Check @UnitgroupAI Channel

Open Telegram → Search: @UnitgroupAI

**Expected Status:**
```
❌ NO new posts from bot
(Dry-run mode prevents publishing)
```

### Step 2: What Should NOT Be There

✅ **Correct (Nothing should be published):**
- ❌ No posts from bot
- ❌ No news articles
- ❌ No industry updates

**If you see posts:**
- 🚨 **CRITICAL** - Dry-run mode is not working
- 🚨 Stop bot immediately
- 🚨 Check .env for `TELEGRAM_DRY_RUN=true`

---

## 📊 LOG VERIFICATION

### Check Bot Activity Logs

```bash
# On VPS

# 1. View last 20 entries
tail -20 logs/telegram_posts.jsonl

# 2. Pretty-print as JSON
tail -10 logs/telegram_posts.jsonl | python3 -m json.tool

# 3. Watch in real-time
tail -f logs/telegram_posts.jsonl

# 4. Check system logs
sudo journalctl -u unitplast-bot -n 50 --no-pager
```

**Expected Log Entries:**
```json
{
  "timestamp": "2026-07-13T12:00:00",
  "event": "news_fetched",
  "source_count": 3,
  "drafts_created": 3,
  "status": "success"
}

{
  "timestamp": "2026-07-13T12:05:00",
  "event": "draft_preview_requested",
  "draft_id": "draft_news_xxx_001",
  "admin_id": 123456,
  "status": "shown"
}

{
  "timestamp": "2026-07-13T12:06:00",
  "event": "draft_approved",
  "draft_id": "draft_news_xxx_001",
  "admin_id": 123456,
  "mode": "dry_run",
  "published": false
}
```

---

## 🔐 SECURITY VERIFICATION

### Dry-Run Mode Check

```bash
# On VPS
grep "TELEGRAM_DRY_RUN" .env
# Must show: TELEGRAM_DRY_RUN=true
```

**Expected:**
```
TELEGRAM_DRY_RUN=true ✅
```

### Approval Requirement Check

```bash
# On VPS
grep "TELEGRAM_REQUIRE_APPROVAL" .env
# Must show: TELEGRAM_REQUIRE_APPROVAL=true
```

**Expected:**
```
TELEGRAM_REQUIRE_APPROVAL=true ✅
```

### Channel Configuration Check

```bash
# On VPS
grep "TELEGRAM_CHANNEL_USERNAME" .env
# Must show: TELEGRAM_CHANNEL_USERNAME=@UnitgroupAI
```

**Expected:**
```
TELEGRAM_CHANNEL_USERNAME=@UnitgroupAI ✅
```

---

## 📋 VERIFICATION CHECKLIST

### Service Level ✅

- [ ] Service running: `systemctl status unitplast-bot`
- [ ] Process active: `ps aux | grep telegram_final_bot`
- [ ] Port listening: `sudo lsof -i :8000`
- [ ] Configuration verified: All security settings enabled
- [ ] Dependencies installed: aiogram, flask, feedparser, yaml
- [ ] Code correct: No old brand names, media sources configured

### Telegram Bot Level ✅

- [ ] Bot responds to `/draft_list`
- [ ] Bot responds to `/news_fetch` (creates 1-3 drafts)
- [ ] Bot responds to `/draft_preview <id>`
- [ ] Preview shows `[✅ Approve]` button
- [ ] Approve button works (changes status)
- [ ] Logs update with each action

### Channel Level ✅

- [ ] @UnitgroupAI channel exists
- [ ] @UnitgroupAI has NO new posts from bot
- [ ] Dry-run mode prevents publishing
- [ ] No accidental publications

### Security Level ✅

- [ ] `TELEGRAM_DRY_RUN=true`
- [ ] `TELEGRAM_REQUIRE_APPROVAL=true`
- [ ] `TELEGRAM_CHANNEL_USERNAME=@UnitgroupAI`
- [ ] No token leaks in logs
- [ ] No hardcoded secrets in code

---

## 🚨 TROUBLESHOOTING

### Issue: Bot doesn't respond to `/draft_list`

**Solution:**
```bash
# 1. Check service status
sudo systemctl status unitplast-bot

# 2. Check logs
sudo journalctl -u unitplast-bot -n 50 --no-pager

# 3. Restart service
sudo systemctl restart unitplast-bot

# 4. Wait 5 seconds
sleep 5

# 5. Try again
# Send /draft_list in Telegram
```

### Issue: `/news_fetch` creates no drafts

**Solution:**
```bash
# 1. Check media_sources.yaml
cat data/media_sources.yaml

# 2. Verify RSS sources are accessible
python3 -c "
import feedparser
feed = feedparser.parse('https://www.industrialweek.com/feed')
print(f'Feed entries: {len(feed.entries)}')
"

# 3. Check for errors
tail -50 logs/telegram_final_bot.log | grep -i error
```

### Issue: Posts are appearing in @UnitgroupAI (CRITICAL!)

**Action Items (IMMEDIATE):**

```bash
# 1. STOP SERVICE NOW
sudo systemctl stop unitplast-bot

# 2. Verify dry-run is enabled
grep "TELEGRAM_DRY_RUN" .env
# MUST show: TELEGRAM_DRY_RUN=true

# 3. If it's false, FIX IT
vim .env
# Change: TELEGRAM_DRY_RUN=false → TELEGRAM_DRY_RUN=true

# 4. Restart service
sudo systemctl restart unitplast-bot

# 5. Delete posts from @UnitgroupAI (via Telegram app)

# 6. Re-verify
bash VPS_BOT_STATUS_CHECK.sh
```

### Issue: Service won't start

**Solution:**
```bash
# 1. Check detailed error
sudo journalctl -u unitplast-bot --no-pager

# 2. Test Python import
python3 -c "from app.industry_news_rewriter import NewsRewriter"

# 3. Reinstall dependencies
pip3 install -r requirements.txt --upgrade --force-reinstall

# 4. Try starting again
sudo systemctl start unitplast-bot

# 5. Check status
sudo systemctl status unitplast-bot
```

---

## 📊 EXPECTED BEHAVIOR

### During Dry-Run Mode

| Action | Expected | What NOT to See |
|--------|----------|-----------------|
| `/draft_list` | Shows 0 or N drafts | Error message |
| `/news_fetch` | Creates 1-3 drafts | No output for >1 min |
| `/draft_preview` | Shows draft + buttons | Blank preview |
| Click `[✅ Approve]` | Draft approved status | Post in channel |
| Check @UnitgroupAI | ❌ NO new posts | ✅ New posts |

### Log Entries Expected

```
Every /draft_list:
  ✅ logged as "draft_list_requested"

Every /news_fetch:
  ✅ logged as "news_fetched"
  ✅ includes draft count

Every /draft_preview:
  ✅ logged as "draft_preview_requested"

Every Approve click:
  ✅ logged as "draft_approved"
  ✅ shows mode="dry_run"
  ✅ shows published=false
```

---

## ✨ VERIFICATION SUMMARY

### Quick Status Check Command

Run this once to verify everything:

```bash
# On VPS
cd /home/unitplast_bot
bash VPS_BOT_STATUS_CHECK.sh
```

### Manual Full Verification (5-10 minutes)

1. Run status check script (5 min)
2. Test bot commands in Telegram (3 min)
3. Verify channel is empty (1 min)
4. Check logs for events (1 min)

**Total Time:** ~10 minutes to full verification

---

## 🎯 SUCCESS CRITERIA - ALL MUST PASS

```
╔═══════════════════════════════════════════════════════════╗
║              BOT VERIFICATION - SUCCESS                  ║
║                                                           ║
║  ✅ Service running and healthy                          ║
║  ✅ Bot responds to all commands                         ║
║  ✅ News drafts are created successfully                 ║
║  ✅ Drafts can be previewed with approval buttons        ║
║  ✅ Approval workflow works                              ║
║  ✅ Dry-run mode prevents channel publishing             ║
║  ✅ No posts in @UnitgroupAI                            ║
║  ✅ Logs track all events                                ║
║  ✅ Configuration verified                               ║
║  ✅ Security settings enabled                            ║
║                                                           ║
║  Status: ✅ BOT OPERATIONAL & SAFE                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 📝 NEXT STEPS

1. **Verify Bot** - Run status check (5 min)
2. **Test Commands** - Try all bot commands (3 min)
3. **Check Channel** - Verify no posts (1 min)
4. **Monitor Logs** - Watch for events (1 min)
5. **Document Results** - Note any issues
6. **Plan Transition** - When ready for production

---

**Verification Guide:** July 13, 2026  
**Status:** Ready to execute  
**Mode:** DRY-RUN ACTIVE  

🤖 Ready to verify bot!
