# 📰 Industry News Sources & Rewrite Pipeline for @UnitgroupAI

**Date:** July 13, 2024  
**Channel:** @UnitgroupAI  
**Status:** ✅ **ARCHITECTURE & CONFIG COMPLETE**

---

## Executive Summary

Industry news automation pipeline for @UnitgroupAI channel:

1. **Fetch** news from RSS feeds (manufacturing, plastics, furniture, metal, automation)
2. **Filter** by relevance (keywords, industry focus)
3. **Rewrite** for Telegram format (emoji hook, CTA, UNITGROUP context)
4. **Adapt** to UNITPLAST/UNITFURNITURE/UNITMETALL
5. **Validate** brand names and content safety
6. **Preview** to admin in Telegram
7. **DRY-RUN** mode (no auto-publish)
8. **Log** complete audit trail

**Key Guarantee:** NO auto-publishing. Admin approval required always.

---

## Architecture

### Components Created

| File | Purpose | Status |
|------|---------|--------|
| `data/media_sources.yaml` | RSS feed config & filtering rules | ✅ Created |
| `skills/news_rewrite_for_telegram_skill.md` | Rewrite rules & validation | ✅ Created |
| `.claude/agents/industry-news-rewriter.md` | Agent definition & workflow | ✅ Created |
| `data/post_drafts/example_unitfurniture_news_draft.json` | Draft JSON example | ✅ Created |
| `docs/INDUSTRY_NEWS_SOURCES_AND_REWRITE_PIPELINE.md` | Complete documentation | ✅ Created |

### Data Flow

```
RSS Feeds (media_sources.yaml)
    ↓
Fetch Latest News
    ↓
Filter by Keywords (include/exclude)
    ↓
Score Relevance (0-1.0)
    ↓
Select Top 3 per Day
    ↓
Map to Products (UNITPLAST/UNITFURNITURE/UNITMETALL)
    ↓
Rewrite for Telegram
    ↓
Create Draft JSON
    ↓
Validate Brand Names
    ↓
Check Content Safety
    ↓
Send Preview to Admin
    ↓
Wait for Approval
    ↓
DRY-RUN Preview
    ↓
Admin Confirms: "Publish Live"
    ↓
[FUTURE] Publish to @UnitgroupAI
    ↓
Log to telegram_posts.jsonl
```

---

## Configuration

### RSS Feeds (data/media_sources.yaml)

**5 categories configured:**

1. **Manufacturing**
   - IndustryWeek
   - Manufacturing Tomorrow

2. **Plastics & Polymers**
   - PlasticsToday
   - Plastics Technology Online

3. **Furniture & Design**
   - Furniture Today
   - Décor Magazine

4. **Metal & Fabrication**
   - The Fabricator
   - Sheet Metal Magazine

5. **Automation & AI**
   - Robotics Business Review
   - AI Weekly

### Filter Rules

**Include keywords:**
```
automation, cost reduction, production efficiency,
order management, pricing, manufacturing, 
calculation, AI, delivery time, supply chain
```

**Exclude keywords:**
```
politics, weather, sports, entertainment,
fake, test
```

**Constraints:**
- Min 50 words
- Max 5000 words
- Min relevance score: 0.6

### Processing Rules

```yaml
language: en → ru (translate to Russian)
rewrite_style: telegram (emoji hooks, CTAs)
include_source: true (always show source)
include_date: true (always show publish date)
max_posts_per_day: 3
scheduling: 9am, 12pm, 5pm UTC
min_hours_between_posts: 4
```

### Moderation

```yaml
require_approval: true          # Always
require_content_review: true    # Always
dry_run_mode: true              # Always (no publish)
allow_auto_publish: false       # Never (guaranteed)
```

---

## Rewrite Rules

### Rule 1: Emoji Hook

**Before:** "Smart manufacturing increases efficiency"

**After:** "🤖 Интеллектуальное производство повышает эффективность"

### Rule 2: UNITGROUP Context

**Before:** "AI helps with calculations"

**After:** "UNITGROUP делает это за 30 сек:
- Автоматический расчёт
- Точная коммерческое предложение
- PDF готов для клиента"

### Rule 3: Product Mapping

**Before:** "Manufacturing automation"

**After:** "🪑 Для UNITFURNITURE:
✅ Расчёт материала
✅ Обработка + отделка
✅ Фурнитура
✅ Итоговая цена"

### Rule 4: CTA

**Before:** "Read full article..."

**After:** "👉 Откроить Mini App
Рассчитай свой заказ за 30 сек"

### Rule 5: Source Attribution

**Before:** (no source)

**After:** "📰 Источник: Furniture Today (July 13, 2024)"

---

## Draft JSON Structure

**Example:** `data/post_drafts/example_unitfurniture_news_draft.json`

```json
{
  "id": "draft_news_20240713_unitfurniture_001",
  "channel": "@UnitgroupAI",
  "status": "draft",
  "type": "text",
  
  "source": {
    "url": "...",
    "title": "Original news",
    "source_name": "Furniture Today",
    "published_date": "2024-07-13"
  },
  
  "content": {
    "emoji_hook": "🪑",
    "headline": "...",
    "body": "...",
    "full_text": "...",
    "cta_text": "👉 Откроить Mini App",
    "cta_url": "https://unitgroup.tech/app/"
  },
  
  "metadata": {
    "brand_module": "UNITFURNITURE",
    "category": "automation",
    "keywords": [...],
    "relevance_score": 0.94,
    "word_count": 92,
    "language_original": "en",
    "language_current": "ru"
  },
  
  "validation": {
    "brand_names_check": { "passed": true },
    "safety_check": { "passed": true },
    "format_check": { "passed": true }
  },
  
  "approval_workflow": {
    "dry_run_mode": true,
    "require_approval": true,
    "allow_auto_publish": false,
    "status": "waiting_approval",
    "approved_by": null,
    "approved_at": null
  }
}
```

---

## Validation Checks

### Brand Names (Automatic)

```
✅ UNITPLAST (not UniPlast)
✅ UNITFURNITURE (not UNIFURNITURE)
✅ UNITMETALL (not UNIMETALL)
✅ UNITGROUP (not UniGroup)
```

**If error found:** 🚫 BLOCK draft, alert admin

### Content Safety (Automatic)

```
❌ Fake clients (blocked)
❌ Fake metrics (blocked)
❌ Unverified claims (blocked)
❌ Political/controversial (blocked)
❌ Spam (blocked)

✅ Real industry news (allowed)
✅ Factual rewrites (allowed)
✅ Honest examples (allowed)
✅ Source attribution (required)
```

### Format Checks (Automatic)

```
✅ Has emoji hook
✅ Has clear CTA
✅ 50-200 words (or valid length)
✅ Source attributed
✅ Date included
✅ UNITGROUP context added
```

---

## Example Rewrites

### UNITPLAST Example

**Original:**
"Plastic injection molding sees 25% efficiency gain with AI"

**Rewritten:**
"🎯 Пластиковое литьё: +25% эффективности с AI

UNITPLAST автоматически рассчитывает:
- Материал и вес
- Цикл литья  
- Стоимость партии
- Сроки доставки

Результат КП за 30 сек вместо часов.

👉 Откроить калькулятор
Источник: IndustryWeek (July 13)"

### UNITFURNITURE Example

**Original:**
"Smart manufacturing reduces furniture production time"

**Rewritten:**
"🪑 Мебель быстрее: Smart Manufacturing

UNITFURNITURE считает автоматически:
- Материал (ЛДСП, МДФ, массив)
- Обработку и отделку
- Фурнитуру
- Сборку и доставку

Коммерческое предложение готово за 30 сек!

👉 Попробовать прямо сейчас
Источник: Furniture Today (July 13)"

### UNITMETALL Example

**Original:**
"Metal fabrication AI improves quote accuracy"

**Rewritten:**
"🔧 Металл точнее: AI расчёты

UNITMETALL автоматически определяет:
- Тип и профиль металла
- Резка, гибка, сварка
- Покрытие и покраска
- Итоговая стоимость

Точная коммерческое предложение за 30 сек.

👉 Рассчитать заказ
Источник: The Fabricator (July 13)"

---

## Approval Workflow

### Step 1: Create Draft

Agent creates JSON draft in `data/post_drafts/`

### Step 2: Preview to Admin

Send to admin's private Telegram chat:
- Full post text
- Formatted with emoji, CTA
- [Approve] [Reject] [Edit] buttons

### Step 3: Admin Reviews

Admin sees:
- How it looks in channel
- Source attribution
- Brand module (UNITPLAST/UNITFURNITURE/UNITMETALL)
- Validation status

### Step 4: Admin Approves

Admin taps [Approve] button

### Step 5: Dry-Run

Bot sends dry-run preview:
- "Here's what will post to @UnitgroupAI"
- Admin reviews appearance

### Step 6: Publish Confirmation

Admin taps [Publish Live]

Bot asks final confirmation:
"Are you sure? This will post to @UnitgroupAI now."

### Step 7: [FUTURE] Publish

Bot publishes to @UnitgroupAI

Logs message ID to `logs/telegram_posts.jsonl`

---

## Logging & Audit Trail

**File:** `logs/telegram_posts.jsonl`

**Format:** One JSON object per line

```json
{"timestamp": "2024-07-13T10:00:00Z", "event": "draft_created", "draft_id": "draft_news_001", "brand_module": "UNITFURNITURE", "source": "Furniture Today"}
{"timestamp": "2024-07-13T10:00:30Z", "event": "validation_passed", "draft_id": "draft_news_001", "checks": ["brand", "safety", "format"]}
{"timestamp": "2024-07-13T10:01:00Z", "event": "preview_sent", "draft_id": "draft_news_001", "admin_id": 123456}
{"timestamp": "2024-07-13T10:05:00Z", "event": "draft_approved", "draft_id": "draft_news_001", "admin_id": 123456}
{"timestamp": "2024-07-13T10:10:00Z", "event": "dry_run_preview", "draft_id": "draft_news_001", "preview_msg_id": 999}
```

---

## Safety Guarantees

```
✅ NO auto-publish (ever, by design)
✅ Dry-run mode always on (no publish without approval)
✅ Admin approval required (no exceptions)
✅ Brand validation automatic (blocks wrong names)
✅ Content safety checks (blocks fake/spam)
✅ Source always attributed (no anonymous posts)
✅ Complete audit log (full history)
✅ Token never exposed (never in logs)
✅ Never commits .env (protected)
```

---

## Implementation Status

| Phase | Status | Details |
|-------|--------|---------|
| **Architecture** | ✅ Complete | Config files, skill, agent defined |
| **Configuration** | ✅ Complete | data/media_sources.yaml |
| **Skill Definition** | ✅ Complete | skills/news_rewrite_for_telegram_skill.md |
| **Agent Definition** | ✅ Complete | .claude/agents/industry-news-rewriter.md |
| **Example Draft** | ✅ Complete | data/post_drafts/example_unitfurniture_news_draft.json |
| **Code Implementation** | ⏳ TODO | Implement industry_news_rewriter.py |
| **Testing** | ⏳ TODO | Test fetch, filter, rewrite, validation |
| **Deployment** | ⏳ TODO | Deploy to VPS |

---

## Next Steps

### Immediate (Next Sprint)

1. Implement `industry_news_rewriter.py` module
   - Fetch from RSS feeds
   - Filter and score
   - Map to products
   - Rewrite
   - Create draft JSON
   - Validate
   - Send preview

2. Implement logging to `telegram_posts.jsonl`

3. Create admin commands:
   - `/draft_list`
   - `/draft_preview <id>`
   - `/draft_approve <id>`
   - `/draft_reject <id>`

### Testing

4. Test fetch from real RSS feeds
5. Test filtering and scoring
6. Test rewriting and adaptation
7. Test validation (brand, safety)
8. Test draft creation
9. Test preview sending
10. Test dry-run mode
11. Test logging

### Deployment

12. Deploy `industry_news_rewriter.py` to VPS
13. Configure cron jobs for daily fetch (9am, 12pm, 5pm UTC)
14. Monitor logs and admin approvals
15. Track publishing history

---

## Files Summary

| File | Lines | Purpose |
|------|-------|---------|
| data/media_sources.yaml | 87 | RSS feeds, filters, config |
| skills/news_rewrite_for_telegram_skill.md | 386 | Rewrite rules, validation |
| .claude/agents/industry-news-rewriter.md | 327 | Agent workflow, steps |
| data/post_drafts/example_unitfurniture_news_draft.json | 132 | Example draft JSON |
| docs/INDUSTRY_NEWS_SOURCES_AND_REWRITE_PIPELINE.md | This file | Complete documentation |

**Total:** 932 lines of configuration + documentation

---

## Security Checklist

- ✅ No TELEGRAM_BOT_TOKEN in config files
- ✅ No .env file committed
- ✅ No auto-publish (guaranteed by design)
- ✅ Approval always required
- ✅ Dry-run mode always on
- ✅ Content validated before draft
- ✅ Brand names checked automatically
- ✅ Fake metrics blocked
- ✅ Source always attributed
- ✅ Complete audit trail

---

**Status: ✅ READY FOR IMPLEMENTATION**

Architecture, configuration, and documentation complete.  
Awaiting code implementation in next sprint.

