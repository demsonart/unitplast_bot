# 📊 AUTONOMOUS NEWS SYSTEM - LIVE DASHBOARD
## Real-time monitoring guide for @UnitgroupAI automation

**Status:** 🟢 ACTIVE  
**System:** Autonomous News Enhancement Agent  
**Channel:** @UnitgroupAI  
**Bot:** @Media_Unitgroup_bot  
**Frequency:** Every 30 minutes  

---

## 🎯 WHAT'S HAPPENING RIGHT NOW

### Phase 1: Initial Activation (First 30 minutes)
```
⏱️ 0:00 - Service restarted
✅ Agent initialized
🔍 First news fetch starting...
🧹 Filtering and scoring articles
🤖 AI enhancement in progress
📊 Quality calculation
```

### Phase 2: First Posts (30-60 minutes)
```
🚀 Auto-publishing high-quality articles (0.85+)
⚠️ Sending previews for 0.75-0.85 scores
❌ Rejecting low-quality (< 0.65)
📝 Logging all actions
```

### Phase 3: Continuous Operation (Every 30 min)
```
🔄 Fetch → Filter → Score → Publish
🤖 Claude enhancement applied
✅ 5-15 posts per day
📈 Quality improving over time
```

---

## 📱 WATCH IN REAL-TIME

### Open Telegram

```
Search: @UnitgroupAI
Pin the channel
Watch for new posts appearing!
```

**Expected first posts in:** 5-30 minutes

**Expected posts per hour:** 2-3 posts

**Expected posts per day:** 5-15 posts

---

## 💻 MONITOR ON VPS

### Command 1: Watch Autonomous Logs (Real-time)
```bash
ssh root@193.104.33.29
cd /home/unitplast_bot
tail -f logs/autonomous_news.jsonl
```

**You'll see:**
```json
{"timestamp": "2026-07-13T12:30:00Z", "event": "auto_published", "score": 0.87, "product": "UNITFURNITURE", "post": "Manufacturing innovation..."}
{"timestamp": "2026-07-13T13:00:00Z", "event": "auto_published", "score": 0.91, "product": "UNITMETALL", "post": "Metal fabrication trends..."}
```

### Command 2: Watch System Logs
```bash
sudo journalctl -u unitplast-bot -f
```

**You'll see:**
```
🤖 AUTONOMOUS MODE ACTIVATED
🔄 AUTONOMOUS ITERATION 1
🔍 AUTONOMOUS: Fetched 150 articles
🧹 AUTONOMOUS: Filtered to 25 candidates
✅ AUTO-PUBLISHED: Score 0.87
```

### Command 3: Check Quality Statistics
```bash
cat logs/autonomous_news.jsonl | python3 -c "
import json, sys
logs = [json.loads(l) for l in sys.stdin]
published = [l for l in logs if l.get('event') == 'auto_published']
scores = [l.get('score', 0) for l in published]
print(f'Total published: {len(published)}')
print(f'Avg score: {sum(scores)/len(scores):.2f}' if scores else 'N/A')
print(f'Min: {min(scores):.2f}, Max: {max(scores):.2f}' if scores else 'N/A')
"
```

---

## 🎯 QUALITY TRACKING

### Score Breakdown

```
Score < 0.65  → ❌ REJECTED (not published)
Score 0.65-0.75 → ⚠️ MANUAL REVIEW (admin check)
Score 0.75-0.85 → 👤 PREVIEW (1-hour admin window)
Score ≥ 0.85  → ✅ AUTO-PUBLISHED (immediate)
```

### Expected Quality Progression

**Day 1:**
- Avg score: 0.75
- Auto-published: 30%
- Rejection rate: 20%

**Day 2-3:**
- Avg score: 0.78
- Auto-published: 45%
- Rejection rate: 15%

**Day 4-7:**
- Avg score: 0.80+
- Auto-published: 65%
- Rejection rate: 10%

**Week 2+:**
- Avg score: 0.82+
- Auto-published: 80%
- Rejection rate: 5%

---

## 📊 METRIC COMMANDS

### Posts per day
```bash
grep "auto_published" logs/autonomous_news.jsonl | wc -l
```

### Products distribution
```bash
grep "auto_published" logs/autonomous_news.jsonl | \
  jq '.product' | sort | uniq -c | sort -rn
```

### Rejection reasons
```bash
grep "rejected" logs/autonomous_news.jsonl | \
  jq '.details' | sort | uniq -c
```

### Avg quality score
```bash
grep "auto_published" logs/autonomous_news.jsonl | \
  jq '.score' | awk '{sum+=$1; count++} END {print "Avg:", sum/count}'
```

---

## 🎮 ADMIN CONTROLS

### If You Get a Preview (Score 0.75-0.85)

Admin receives in Telegram:
```
⚠️ NEWS PREVIEW (Score: 0.78)
[Full post content]
Quality: Good
[✅ Approve Now] [❌ Reject]
Auto-publishes in: 60 min
```

**Actions:**
- `✅ /approve_now` - Publish immediately
- `❌ /reject` - Block forever
- Wait 1 hour - Auto-publishes

### Stop Autonomous Mode (Emergency)

```bash
ssh root@193.104.33.29
cd /home/unitplast_bot
vim .env
# Change: AUTONOMOUS_MODE=false
sudo systemctl restart unitplast-bot
```

### Adjust Quality Threshold

```bash
vim .env
# Lower threshold = more posts (0.80)
# Higher threshold = better quality (0.88)
AUTONOMOUS_QUALITY_THRESHOLD=0.85
sudo systemctl restart unitplast-bot
```

---

## 🔍 TROUBLESHOOTING

### No posts appearing?

```bash
# Check service status
sudo systemctl status unitplast-bot

# Check for errors
sudo journalctl -u unitplast-bot -n 50 --no-pager | grep -i error

# Check if autonomous mode is ON
grep AUTONOMOUS_MODE .env

# Manual restart
sudo systemctl restart unitplast-bot
```

### Posts but low quality?

```bash
# Check score distribution
grep "auto_published" logs/autonomous_news.jsonl | jq '.score'

# Lower threshold temporarily
sed -i 's/AUTONOMOUS_QUALITY_THRESHOLD=.*/AUTONOMOUS_QUALITY_THRESHOLD=0.80/' .env
sudo systemctl restart unitplast-bot
```

### Too many posts?

```bash
# Increase fetch interval
sed -i 's/FETCH_INTERVAL_MINUTES=.*/FETCH_INTERVAL_MINUTES=60/' .env
sudo systemctl restart unitplast-bot
```

---

## 📈 EXPECTED PROGRESSION

### Hour 1
```
⏱️ 00:00 - Activation
⏱️ 00:30 - First fetch
⏱️ 01:00 - First posts appearing! 🎉
```

### Day 1
```
📊 Posts: 5-8
📈 Avg quality: 0.75
🤖 System learning
```

### Day 2-3
```
📊 Posts: 8-12 per day
📈 Avg quality: 0.78
🤖 Optimization phase
```

### Day 4+
```
📊 Posts: 12-15 per day
📈 Avg quality: 0.82+
🤖 Peak performance
📚 Continuous learning
```

---

## 🎯 SUCCESS INDICATORS

✅ **Check these to confirm system working:**

- [ ] New posts appearing in @UnitgroupAI
- [ ] Posts appearing every 30 minutes
- [ ] Quality improving daily
- [ ] No critical errors in logs
- [ ] Avg score >= 0.75
- [ ] Auto-published posts >= 30%

---

## 📊 LIVE METRICS (Update commands)

### Get Current Stats
```bash
echo "=== AUTONOMOUS SYSTEM STATUS ==="
echo ""
echo "Last 10 published posts:"
tail -10 logs/autonomous_news.jsonl | grep "auto_published" | jq '{score, product}'
echo ""
echo "Total published today:"
grep "auto_published" logs/autonomous_news.jsonl | wc -l
echo ""
echo "Avg quality score:"
grep "auto_published" logs/autonomous_news.jsonl | jq '.score' | \
  awk '{sum+=$1; count++} END {printf "%.2f\n", sum/count}'
```

---

## 🎉 LIVE DASHBOARD

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║            🟢 AUTONOMOUS SYSTEM - LIVE ACTIVE                 ║
║                                                                ║
║  Channel: @UnitgroupAI                                        ║
║  Bot: @Media_Unitgroup_bot                                    ║
║  VPS: 193.104.33.29                                           ║
║  Status: 🟢 RUNNING                                           ║
║                                                                ║
║  System Metrics:                                              ║
║  ✅ Autonomous Mode: ON                                       ║
║  ✅ Auto-publish: ENABLED                                     ║
║  ✅ Claude Enhancement: ENABLED                               ║
║  ✅ Quality Threshold: 0.85                                   ║
║  ✅ Fetch Interval: 30 minutes                                ║
║                                                                ║
║  Activity:                                                    ║
║  📊 Posts published today: N                                  ║
║  📈 Avg quality score: 0.XX                                   ║
║  🔄 Next fetch in: ~30 min                                    ║
║                                                                ║
║  Channel Status:                                              ║
║  📱 @UnitgroupAI: ACTIVE                                      ║
║  📋 New posts: Appearing automatically                        ║
║  ⭐ Quality: Professional AI-enhanced                         ║
║                                                                ║
║  Next Steps:                                                  ║
║  1. Open @UnitgroupAI in Telegram                            ║
║  2. Watch new posts appearing                                 ║
║  3. Monitor logs: tail -f logs/autonomous_news.jsonl         ║
║  4. Track quality improvements daily                          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 📞 QUICK REFERENCE

### Monitor Real-Time
```bash
tail -f logs/autonomous_news.jsonl
```

### Check Service
```bash
sudo systemctl status unitplast-bot
```

### View Errors
```bash
sudo journalctl -u unitplast-bot -n 100 --no-pager | grep -i error
```

### Get Full Status
```bash
cat > status.sh << 'EOF'
#!/bin/bash
echo "=== SERVICE STATUS ==="
sudo systemctl status unitplast-bot --no-pager | head -5
echo ""
echo "=== RECENT POSTS ==="
tail -5 logs/autonomous_news.jsonl | jq '{score, event, product}'
echo ""
echo "=== TODAY'S COUNT ==="
grep "auto_published" logs/autonomous_news.jsonl | wc -l
EOF
chmod +x status.sh
./status.sh
```

---

## 🚀 STATUS

```
🟢 SYSTEM ACTIVE
📱 CHANNEL LIVE
🤖 AUTONOMOUS MODE ON
📈 POSTS FLOWING
✅ MISSION ACCOMPLISHED
```

---

**Activated:** July 13, 2026  
**Status:** 🟢 LIVE AND AUTONOMOUS  

🎉 **Welcome to the future of automated news distribution!**

**Open @UnitgroupAI now and watch it fill with quality content!**
