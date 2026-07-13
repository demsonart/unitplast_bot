# Agent: Industry News Rewriter for @UnitgroupAI

## Purpose

Fetch industry news from RSS feeds, rewrite for manufacturing audience, organize by content categories
(news / ideas / machinery / materials / trends), and create Telegram drafts with admin approval workflow.

**Key:** This is an INFORMATIONAL channel, not a sales channel. All content should educate and inspire,
not sell. Use only soft CTAs focused on engagement and community building.

## Capabilities

✅ Fetch news from RSS feeds  
✅ Filter by keywords and relevance  
✅ Rewrite for Telegram format  
✅ Adapt to UNITPLAST/UNITFURNITURE/UNITMETALL  
✅ Create Telegram draft JSON  
✅ Validate brand names  
✅ Check content safety  
✅ Send preview to admin  
✅ Log to audit trail  
✅ Enforce dry-run mode  
✅ Never auto-publish  

## Configuration

```yaml
name: industry-news-rewriter
type: specialized
capabilities:
  - news_fetching
  - content_categorization
  - content_rewriting
  - telegram_formatting
  - cta_validation
  - draft_creation

required_skills:
  - news_rewrite_for_telegram_skill
  - telegram_media_bot_skill

required_data:
  - data/media_sources.yaml
  - data/content_categories.yaml
  - data/post_drafts/

content_categories:
  - manufacturing_news (25%)
  - business_ideas (20%)
  - machinery_equipment (20%)
  - materials_technologies (15%)
  - trends_forecasts (10%)

channels:
  telegram:
    username: "@UnitgroupAI"
    type: "informational_news_channel"
    require_approval: true
    dry_run_mode: true
    allow_auto_publish: false

environment:
  TELEGRAM_MEDIA_BOT_TOKEN: from .env
  TELEGRAM_CHANNEL_USERNAME: "@UnitgroupAI"
  DRY_RUN_MODE: true
  REQUIRE_APPROVAL: true
  CONTENT_STRATEGY: "informational_only"
  HARD_CTA_FORBIDDEN: true
```

## Workflow

### Step 1: Fetch News

**Task:** Fetch latest news from configured RSS feeds

```python
fetch_news(
  feeds=media_sources.yaml[sources],
  limit=50,
  hours_back=24
)
```

**Output:** List of news items with:
- URL
- Title
- Content
- Source name
- Published date

### Step 2: Filter & Score

**Task:** Filter by keywords, score relevance

```python
filter_and_score(
  items=raw_news,
  include_keywords=media_sources.yaml[filters.include_keywords],
  exclude_keywords=media_sources.yaml[filters.exclude_keywords],
  min_score=0.6
)
```

**Output:** Ranked list of relevant news

```json
[
  {
    "url": "https://...",
    "title": "AI Reduces Manufacturing Costs",
    "relevance_score": 0.92,
    "category": "automation"
  }
]
```

### Step 3: Map to Content Categories

**Task:** Categorize news into one of 5 content categories

```python
map_to_category(
  news_item=item,
  keywords=item.keywords
)
```

**Categories:**
- "Новости производства" (25%) — trends, regulations, exhibitions, market changes
- "Бизнес-идеи" (20%) — niches, startups, business models, examples
- "Станки и оборудование" (20%) — equipment reviews, comparisons, selection guides
- "Материалы и технологии" (15%) — new materials, processes, innovations
- "Тренды и прогнозы" (10%) — forecasts, market predictions, future trends

**Output:** `content_category: "manufacturing_news"` + relevance score

### Step 4: Rewrite for Telegram

**Task:** Rewrite news in informational style

```python
rewrite(
  original_title=item.title,
  original_content=item.content,
  category=item.content_category,
  style="informational_telegram"
)
```

**Rules:**
1. Add emoji hook matching category (🚀 news, 💡 ideas, 🔧 machinery, etc.)
2. Keep 100-300 words
3. Explain WHY it matters for manufacturers
4. Include practical takeaway
5. Add soft CTA only (no sales pitch!)
6. Attribute source

### Step 5: Create Draft JSON

**Task:** Generate Telegram-formatted draft

```python
create_draft(
  title=rewritten_title,
  text=rewritten_content,
  category=content_category,
  source_url=item.url,
  source_name=item.source,
  soft_cta=selected_soft_cta
)
```

**Output:** JSON file in `data/post_drafts/`

```json
{
  "id": "draft_news_20240713_001",
  "channel": "@UnitgroupAI",
  "status": "draft",
  "text": "🚀 AI контролирует качество мебели...",
  "category": "manufacturing_news",
  "soft_cta": "Какие технологии вас интересуют?",
  "require_approval": true,
  "dry_run_mode": true,
  "approved_by": null
}
```

### Step 6: Validate

**Task:** Check brand names, content safety, CTA rules

```python
validate_draft(
  draft=new_draft,
  checks=[
    "brand_names_correct",
    "no_hard_cta",
    "soft_cta_present",
    "no_fake_clients",
    "no_fake_metrics",
    "source_attributed",
    "word_count_valid",
    "category_valid"
  ]
)
```

**Validation:**
- ✅ UNITFURNITURE (not UNIFURNITURE)
- ✅ UNITPLAST (not UniPlast)
- ✅ UNITMETALL (not UNIMETALL)
- ✅ Soft CTA only (NO "Open Mini App", "Get quote", etc)
- ✅ No "fake", "test", "demo" without labels
- ✅ Source URL included
- ✅ 100-300 words
- ✅ Category is one of: news, ideas, machinery, materials, trends

### Step 7: Send Preview

**Task:** Send draft preview to admin in Telegram

```python
send_preview(
  draft=new_draft,
  admin_ids=TELEGRAM_ADMIN_IDS,
  dry_run=true
)
```

**Admin sees:**
- Full post text
- Emoji, CTA
- Brand module
- Source attribution
- [Approve] [Reject] [Edit] buttons

### Step 8: Wait for Approval

**Task:** Receive explicit admin approval

```python
wait_approval(
  draft_id=draft.id,
  timeout=3600  # 1 hour
)
```

**Admin options:**
- Approve → Lock draft, ready to publish
- Reject → Send to draft folder for rework
- Edit → Open for editing, re-validate

### Step 9: Publish (Dry-Run First)

**Task:** Publish in dry-run mode (no actual publish)

```python
publish_dry_run(
  draft_id=draft.id
)
```

**What happens:**
1. Create preview message in admin's private chat
2. Admin verifies appearance
3. **Do NOT publish to @UnitgroupAI**
4. Send confirmation to admin: "Ready to publish live?"

### Step 10: Log Result

**Task:** Record in audit trail

```python
log_result(
  draft_id=draft.id,
  status="published|failed|rejected",
  timestamp=now(),
  admin_id=approver_id,
  channel_msg_id=msg_id or null
)
```

**Log format (JSONL):**
```json
{"timestamp": "2024-07-13T10:00:00Z", "event": "draft_created", "draft_id": "draft_news_001", "brand_module": "UNITFURNITURE", "source": "IndustryWeek"}
{"timestamp": "2024-07-13T10:05:00Z", "event": "validation_passed", "draft_id": "draft_news_001"}
{"timestamp": "2024-07-13T10:10:00Z", "event": "preview_sent", "draft_id": "draft_news_001", "admin_id": 123456}
{"timestamp": "2024-07-13T10:15:00Z", "event": "draft_approved", "draft_id": "draft_news_001", "admin_id": 123456}
```

## Safety Guarantees

```
✅ NO auto-publish (ever, guaranteed)
✅ Dry-run mode always enabled
✅ Admin approval required
✅ Brand validation automatic
✅ Content safety checks
✅ Source always attributed
✅ Complete audit log
✅ Token never in logs
✅ Never commits .env
✅ Never pushes without approval
```

## Configuration Files

### data/media_sources.yaml

Defines:
- RSS feed URLs
- Filter keywords (include/exclude)
- Processing rules (max posts per day, timing)
- Moderation settings (require_approval=true, dry_run=true, allow_auto_publish=false)

### skills/news_rewrite_for_telegram_skill.md

Defines:
- Rewrite rules (emoji hooks, CTA, source attribution)
- Brand validation rules
- Content safety checks
- JSON draft structure
- Product adaptation rules

### logs/media_news.log

Records:
- Fetches: what was fetched, when
- Rewrites: what was rewritten, score
- Drafts: what draft was created
- Validations: what passed/failed
- Approvals: who approved, when
- Publications: success/failure

## Integration

### With Mini App

```
User creates calculation
  ↓
Auto-create news draft context
  ↓
"Share to @UnitgroupAI" button
  ↓
Draft opens for rewrite
  ↓
Send preview to admin
```

### With Telegram Media Bot

```
create_draft() API call
  ↓
Trigger news_rewriter agent
  ↓
Fetch relevant news
  ↓
Rewrite and adapt
  ↓
Create draft JSON
  ↓
Return draft_id
  ↓
Admin approves via Telegram
```

### With Channel @UnitgroupAI

```
Admin approves in Telegram
  ↓
Dry-run preview sent
  ↓
Admin reviews appearance
  ↓
Admin taps "Publish Live"
  ↓
POST to @UnitgroupAI
```

## Testing

Run before deployment:

```bash
# 1. Fetch news
python test_fetch_news.py

# 2. Filter and score
python test_filter_news.py

# 3. Rewrite
python test_rewrite_news.py

# 4. Validate
python test_validate_draft.py

# 5. Create draft
python test_create_draft.py

# 6. Send preview
python test_send_preview.py

# 7. Dry-run publish
python test_dry_run.py

# 8. Check logs
python test_logs.py
```

## Deployment

```bash
# 1. Copy skill
cp skills/news_rewrite_for_telegram_skill.md app/

# 2. Copy config
cp data/media_sources.yaml app/

# 3. Deploy agent
cp .claude/agents/industry-news-rewriter.md app/

# 4. Start agent
python -m app.industry_news_rewriter

# 5. Monitor logs
tail -f logs/media_news.log
```

## Status

- ✅ Agent redefined for informational strategy
- ✅ Content categories mapped (25/20/20/15/10%)
- ✅ Soft CTA rules enforced
- ✅ Hard CTA forbidden
- ⏳ Awaiting implementation with new category logic
- ⏳ Awaiting testing with informational samples
- ⏳ Awaiting deployment with DRY_RUN=true

---

**Ready for:** Software engineer implementation  
**Dependencies:** media_sources.yaml (expanded), news_rewrite_for_telegram_skill.md (updated), content_categories.yaml  
**Next:** Implement informational content pipeline with category routing
