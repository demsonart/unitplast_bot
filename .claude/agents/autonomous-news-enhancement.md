# 🤖 AUTONOMOUS NEWS ENHANCEMENT AGENT
## AI-Powered Content Quality Improvement Pipeline

**Status:** AUTONOMOUS MODE  
**Purpose:** Automatically improve, enhance, and publish news to @UnitgroupAI  
**Safety:** Quality-based publishing (not approval-based)  
**Mode:** PRODUCTION (auto-publish enabled when quality > 0.85)  

---

## 🎯 MISSION

Autonomously:
1. **Fetch** industry news from 18 RSS sources
2. **Filter** by relevance and quality thresholds
3. **Enhance** content quality through AI rewriting
4. **Verify** brand consistency and facts
5. **Score** final quality (0-1.0 scale)
6. **Publish** directly to @UnitgroupAI when quality > 0.85
7. **Log** all actions and decisions
8. **Learn** from engagement metrics
9. **Iterate** and improve over time

---

## 🔄 AUTONOMOUS WORKFLOW (12 STEPS)

### Step 1: AUTONOMOUS NEWS FETCH
```python
# Run every 30 minutes
Fetch from 18 RSS sources
  ├─ 6 UNITFURNITURE sources
  ├─ 10 UNITMETALL sources
  └─ 2 UNITGROUP sources

Get up to 100 items per fetch
Skip already processed items (via cache)
Return: [article, article, ...]
```

### Step 2: PARALLEL FILTERING
```python
Filter in parallel:
  ├─ Keyword matching (include/exclude)
  ├─ Language detection (Russian)
  ├─ Duplicate detection (MD5 hash)
  ├─ Freshness check (< 24 hours old)
  ├─ Quality baseline (score > 5.0)
  └─ Spam/ads detection

Return: [filtered_article, ...]
```

### Step 3: PRODUCT MAPPING
```python
Detect product category:
  ├─ plastic keywords → UNITPLAST
  ├─ furniture keywords → UNITFURNITURE
  ├─ metal keywords → UNITMETALL
  └─ ai/tech keywords → ALL (generic)

Add product tags: [UNITFURNITURE, UNITMETALL, ...]
```

### Step 4: PRIMARY REWRITE (NewsRewriter)
```python
Use existing NewsRewriter class:
  ├─ Apply 11 rewrite rules
  ├─ Create 7-element structure
  ├─ Add emoji and CTA
  ├─ Max 280 chars
  ├─ Russian language optimization
  └─ Source attribution

Score (baseline): 0-0.6
```

### Step 5: AI ENHANCEMENT LAYER 1 (Language)
```python
Claude AI enhancement:
  ├─ Improve grammar and clarity
  ├─ Optimize for readability
  ├─ Better word choice (Russian idioms)
  ├─ Reduce redundancy
  ├─ Add punch to headline
  └─ Enhance engagement

Score bonus: +0.15 (max 0.75)
```

### Step 6: AI ENHANCEMENT LAYER 2 (Structure)
```python
Claude AI optimization:
  ├─ Perfect 7-element structure
  ├─ Better headline (5-10 words)
  ├─ Compelling body (2-3 sentences)
  ├─ Strong CTA (action-oriented)
  ├─ Professional source attribution
  └─ Visual emoji selection

Score bonus: +0.1 (max 0.85)
```

### Step 7: FACT VERIFICATION
```python
Quick fact check:
  ├─ Is headline factual? (yes/no/partial)
  ├─ Does body match source? (yes/no/partial)
  ├─ Are numbers/dates correct? (check)
  ├─ No false claims? (detect)
  └─ Credible source? (yes/no)

Score multiplier: × 0.8-1.0
  - Fully verified: × 1.0
  - Partially verified: × 0.9
  - Unverified: × 0.8
```

### Step 8: BRAND VALIDATION
```python
Enforce brand consistency:
  ├─ Brand names correct? (UNITFURNITURE, not UNIFURNITURE)
  ├─ No competitor mentions? (check)
  ├─ UNITGROUP connection clear? (must be present)
  ├─ Professional tone? (check)
  └─ No spam/ads? (block if found)

Fail if:
  ❌ Wrong brand names
  ❌ No UNITGROUP connection
  ❌ Spam/ads detected
```

### Step 9: FINAL QUALITY SCORE
```python
Calculate FINAL QUALITY SCORE:

Score = (
  (rewrite_score × 0.25) +
  (language_enhance × 0.15) +
  (structure_enhance × 0.10) +
  (fact_verify × 0.30) +
  (brand_validate × 0.10) +
  (engagement_potential × 0.10)
) × (fact_multiplier: 0.8-1.0)

Scale: 0.0 - 1.0
  - 0.85+: AUTO-PUBLISH ✅
  - 0.70-0.85: HUMAN REVIEW ⚠️
  - < 0.70: REJECT ❌
```

### Step 10: DECISION LOGIC
```python
IF score >= 0.85:
  → PUBLISH directly to @UnitgroupAI ✅
  → Log: "published_auto"
  → Update engagement tracking

ELIF score >= 0.70:
  → Send to admin preview ⚠️
  → Wait for 1 hour (with CTA button)
  → Auto-publish if admin approves
  → Auto-reject if admin rejects
  → Auto-publish after 1 hour if no response

ELSE (score < 0.70):
  → REJECT ❌
  → Log: "rejected_low_quality"
  → Reason: score + factors
```

### Step 11: AUTONOMOUS PUBLISH
```python
Send to @UnitgroupAI:
  ├─ Final post text
  ├─ Add timestamp
  ├─ Add source link
  ├─ Add "Read more" button
  └─ Track message ID

Log event:
  ├─ Timestamp: ISO-8601
  ├─ Source: RSS feed name
  ├─ Product: UNITFURNITURE/UNITMETALL/UNITPLAST
  ├─ Score: 0.85+
  ├─ Quality factors
  └─ Message ID: Telegram post
```

### Step 12: CONTINUOUS LEARNING
```python
Track engagement:
  ├─ Views (Telegram stats)
  ├─ Reactions (likes, comments, forwards)
  ├─ Shares (channel forwards)
  ├─ Click-through rate (links)
  └─ User comments

Learn quality patterns:
  ├─ What topics perform best?
  ├─ What emoji works best?
  ├─ What CTA converts best?
  ├─ What product has most interest?
  └─ Optimize future content

Iterate:
  ├─ Adjust scoring weights
  ├─ Improve keyword detection
  ├─ Enhance rewriting rules
  └─ Better product mapping
```

---

## 📊 QUALITY SCORING FORMULA

### Detailed Score Breakdown

```python
# Base Score (NewsRewriter)
base_score = (
    (keyword_match × 0.3) +
    (freshness × 0.2) +
    (relevance × 0.3) +
    (lang_quality × 0.2)
)  # 0.0 - 1.0

# Language Enhancement Bonus
language_score = base_score + (
    (grammar_quality × 0.08) +
    (readability × 0.05) +
    (word_choice × 0.02)
)  # +0.15 max

# Structure Enhancement Bonus
structure_score = language_score + (
    (headline_quality × 0.05) +
    (body_quality × 0.03) +
    (cta_quality × 0.02)
)  # +0.10 max

# Fact Verification
fact_score = structure_score × (
    0.80 if unverified else
    0.90 if partially_verified else
    1.00 if fully_verified
)

# Brand Validation (pass/fail)
IF brand_invalid or spam_detected:
    final_score = 0.0  # AUTO-REJECT
ELSE:
    final_score = fact_score

# FINAL SCORE: 0.0 - 1.0
```

### Quality Tiers

| Score | Action | Threshold | Notes |
|-------|--------|-----------|-------|
| **0.85 - 1.0** | AUTO-PUBLISH | Excellent | Publish immediately ✅ |
| **0.75 - 0.85** | PREVIEW 1HR | Good | Admin 1-hour window ⚠️ |
| **0.65 - 0.75** | MANUAL REVIEW | Fair | Needs human decision |
| **< 0.65** | REJECT | Poor | Too many issues ❌ |

---

## 🚀 CONTINUOUS OPERATION

### Scheduling

```
Every 30 minutes:
  1. Fetch from 18 RSS sources
  2. Filter new articles
  3. Enhance quality
  4. Score each article
  5. Auto-publish if score > 0.85
  6. Send previews for 0.75-0.85
  7. Log all actions

Daily:
  1. Analyze engagement metrics
  2. Calculate best-performing topics
  3. Optimize scoring weights
  4. Report to admins

Weekly:
  1. Review quality trends
  2. Update keyword lists
  3. Improve rewriting rules
  4. Strategic analysis
```

### Fallback & Safety

```python
# If Claude API fails
→ Use fallback NewsRewriter scoring
→ Lower quality threshold to 0.75
→ Log error for admin alert

# If Telegram API fails
→ Queue post for retry
→ Retry every 5 minutes (up to 10 times)
→ Alert admin if persistent

# If duplicate detected
→ Skip article
→ Don't retry
→ Log: "duplicate_skipped"

# If brand validation fails
→ REJECT immediately
→ Don't publish
→ Log: "brand_validation_failed"

# If fact verification fails
→ Lower score multiplier (0.8)
→ Still publish if score > 0.85
→ Mark as "unverified" in log
```

---

## 📱 ADMIN CONTROLS

### For Scores 0.75 - 0.85 (Preview Window)

Admin receives in Telegram:

```
⚠️ NEWS PREVIEW (Score: 0.78)

[Draft content here]

Quality factors:
  ✅ Language: Excellent
  ✅ Structure: Good
  ✅ Facts: Verified
  ⚠️ Product fit: Fair

[✅ Approve Now] [❌ Reject]

Auto-publishes in: 1 hour ⏱️
```

### Manual Override

Admin can:
- `✅ /approve_now` - Publish immediately
- `❌ /reject` - Block from publishing
- `🔧 /edit <text>` - Edit and publish
- `📊 /score_details` - See full scoring breakdown

---

## 📊 ANALYTICS & LEARNING

### Engagement Tracking

```python
For each published post:
  ├─ Views: Telegram view count
  ├─ Reactions: Emoji reactions
  ├─ Shares: Channel forwards
  ├─ Comments: Direct comments
  └─ CTR: Click-through rate

Calculate:
  ├─ Best topics (by engagement)
  ├─ Best products (UNITFURNITURE/UNITMETALL/UNITPLAST)
  ├─ Best emoji (most reactions)
  ├─ Best CTA (most clicks)
  └─ Best time to post (when posted)
```

### Quality Metrics

```python
Daily report:
  ├─ Posts published: N
  ├─ Auto-published: N (score > 0.85)
  ├─ Manual approved: N (0.75-0.85)
  ├─ Rejected: N
  ├─ Avg quality score: 0.XX
  ├─ Avg engagement rate: X%
  └─ Trending topics: [topic1, topic2, ...]

Stored in: logs/analytics.jsonl
```

### Continuous Improvement

```python
Weekly optimization:
  1. Identify top-performing topics
  2. Boost keywords for those topics
  3. Adjust emoji selection
  4. Refine CTA based on CTR
  5. Improve product mapping accuracy
  6. Update rewriting rules
  7. Test new scoring weights
  8. A/B test headlines
```

---

## 🔐 SAFETY FEATURES (STILL ACTIVE)

### Hard Limits (NEVER bypass)

```python
NEVER_AUTO_PUBLISH_IF:
  ❌ Brand names wrong (UNIFURNITURE, UNIMETALL)
  ❌ Spam/ads detected
  ❌ No UNITGROUP connection
  ❌ Flagged as misinformation
  ❌ Admin explicitly rejects

ALWAYS_LOG:
  ✅ Every publish action
  ✅ Score and factors
  ✅ Admin decisions
  ✅ Engagement metrics
  ✅ Errors and issues
```

### Escalation Logic

```python
IF critical_error:
  → STOP auto-publishing
  → Alert admin via Telegram
  → Log issue
  → Wait for manual decision
  → Resume after admin approval

IF multiple_rejects:
  → Analyze why rejected
  → Lower quality threshold temporarily
  → Or improve scoring algorithm
  → Alert admin with analysis
```

---

## 📋 CONFIGURATION

### Enable Autonomous Mode

```python
# In .env
AUTONOMOUS_MODE=true
AUTO_PUBLISH_ENABLED=true
AUTONOMOUS_QUALITY_THRESHOLD=0.85
PREVIEW_WINDOW_MINUTES=60
FETCH_INTERVAL_MINUTES=30
MAX_ARTICLES_PER_FETCH=100
ENABLE_CLAUDE_ENHANCEMENT=true
TRACK_ENGAGEMENT=true
```

### Quality Thresholds

```python
# In app/autonomous_news_agent.py
AUTO_PUBLISH_THRESHOLD = 0.85       # Auto-publish if score >= 0.85
PREVIEW_THRESHOLD = 0.75            # Human preview if 0.75-0.85
MIN_QUALITY_THRESHOLD = 0.65        # Reject if < 0.65
BRAND_VALIDATION_STRICT = True      # Brand check is CRITICAL
FACT_VERIFY_MULTIPLIER = 0.9        # Slightly penalize unverified
```

---

## 🎯 EXPECTED RESULTS

### Channel Activity

```
Before (Dry-run):
  ❌ 0 posts per day
  ⏸️ Manual approval only
  📉 Channel dormant

After (Autonomous):
  ✅ 5-15 posts per day
  ⚡ Instant publishing (score > 0.85)
  📈 Active, engaging channel
  🤖 Autonomous agents improving quality
```

### Quality Improvement Over Time

```
Week 1: Baseline
  ├─ Avg score: 0.75
  ├─ Auto-published: 30%
  ├─ Manual reviewed: 50%
  └─ Rejected: 20%

Week 2: Learning
  ├─ Avg score: 0.78
  ├─ Auto-published: 45%
  ├─ Manual reviewed: 40%
  └─ Rejected: 15%

Week 3+: Optimized
  ├─ Avg score: 0.82
  ├─ Auto-published: 70%
  ├─ Manual reviewed: 20%
  └─ Rejected: 10%
```

---

## 🚀 ACTIVATION STEPS

### Step 1: Deploy Base System
```bash
# On VPS
bash VPS_DEPLOYMENT_PLAYBOOK.sh
```

### Step 2: Enable Autonomous Mode
```bash
# SSH to VPS
ssh root@193.104.33.29
cd /home/unitplast_bot

# Edit .env
vim .env

# Add/modify:
AUTONOMOUS_MODE=true
AUTO_PUBLISH_ENABLED=true
AUTONOMOUS_QUALITY_THRESHOLD=0.85
ENABLE_CLAUDE_ENHANCEMENT=true
```

### Step 3: Start Autonomous Agent
```bash
# Restart service
sudo systemctl restart unitplast-bot

# Verify
sudo journalctl -u unitplast-bot -f

# Expected log:
# "🤖 AUTONOMOUS MODE ACTIVATED"
# "Starting autonomous news fetch every 30 minutes"
```

### Step 4: Monitor
```bash
# Watch posts being published
tail -f logs/telegram_posts.jsonl

# Expected:
# {"event": "auto_published", "score": 0.87, "product": "UNITFURNITURE"}
# {"event": "auto_published", "score": 0.91, "product": "UNITMETALL"}
```

### Step 5: Check Channel
```
Open @UnitgroupAI in Telegram
Expected: New posts appearing automatically every 30 mins
Quality: Professional, engaging, varied topics
```

---

## 📞 MONITORING COMMANDS

```bash
# Real-time autonomous logs
tail -f logs/telegram_posts.jsonl | grep "auto_published"

# Quality score distribution
cat logs/telegram_posts.jsonl | grep "score" | \
  python3 -c "import json, sys; scores = [json.loads(l).get('score') for l in sys.stdin if json.loads(l).get('score')]; print(f'Avg: {sum(scores)/len(scores):.2f}, Min: {min(scores):.2f}, Max: {max(scores):.2f}')"

# Posts per day
cat logs/telegram_posts.jsonl | grep "published" | wc -l

# Top topics
cat logs/telegram_posts.jsonl | grep "published" | jq '.product' | sort | uniq -c | sort -rn
```

---

## 🎉 STATUS

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║         🤖 AUTONOMOUS NEWS ENHANCEMENT: READY                 ║
║                                                                ║
║  Mode: PRODUCTION (auto-publish enabled)                      ║
║  Quality Threshold: 0.85                                      ║
║  Fetch Interval: 30 minutes                                   ║
║  AI Enhancement: Claude-powered                               ║
║  Engagement Tracking: Real-time                               ║
║  Learning: Continuous improvement                             ║
║                                                                ║
║  Expected: 5-15 posts/day to @UnitgroupAI ✅                 ║
║  Quality: Professional, verified, engaging ✅                 ║
║  Safety: Brand validation + fact check ✅                     ║
║  Admin Control: Preview & override for 0.75-0.85 ✅          ║
║                                                                ║
║  🚀 READY TO ACTIVATE                                         ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

**Created:** July 13, 2026  
**Agent:** Autonomous News Enhancement  
**Status:** READY FOR ACTIVATION  

🤖 **Activate autonomous mode now and watch the channel fill with high-quality news!**
