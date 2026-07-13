# 📰 Telegram Media Bot Implementation Guide

**Status:** ✅ **COMPLETE**  
**Date:** July 13, 2026  
**Channel:** @UnitgroupAI

---

## Quick Start

### Commands

```bash
/news_fetch          # Fetch fresh news from RSS feeds → create drafts
/draft_list          # List all drafts (waiting_approval, approved, rejected)
/draft_preview <id>  # Preview specific draft
```

### Configuration

All settings in `data/media_sources.yaml`:

```yaml
moderation:
  require_approval: true      # ✅ Always required
  dry_run_mode: true          # ✅ Always enabled
  allow_auto_publish: false   # ✅ Never auto-publish
```

---

## Architecture

### Components

| Component | File | Purpose |
|-----------|------|---------|
| **News Fetcher** | `app/industry_news_rewriter.py` | Fetch RSS feeds, filter, score, rewrite |
| **Bot Integration** | `app/media_bot_integration.py` | Admin approval workflow, draft management |
| **Config** | `data/media_sources.yaml` | RSS feeds, filters, processing rules |
| **Skill** | `skills/news_rewrite_for_telegram_skill.md` | Rewrite rules, validation, product mapping |
| **Agent** | `.claude/agents/industry-news-rewriter.md` | Agent definition & workflow |
| **Documentation** | `docs/INDUSTRY_NEWS_SOURCES_AND_REWRITE_PIPELINE.md` | Complete architecture |

### Data Flow

```
/news_fetch Command
    ↓
Fetch from RSS Feeds (10 feeds, 5 categories)
    ↓
Filter by Keywords (include/exclude)
    ↓
Score Relevance (min 0.6)
    ↓
Select Top 3
    ↓
Map to Products (UNITPLAST/UNITFURNITURE/UNITMETALL)
    ↓
Rewrite for Telegram (emoji hooks, CTAs, translations)
    ↓
Validate (brand names, content safety)
    ↓
Create Draft JSON (data/post_drafts/)
    ↓
Send Preview to Admin
    ↓
Admin Reviews [Approve] [Reject] [Edit]
    ↓
If Approved:
  - DRY-RUN preview sent
  - Admin confirms: "Publish Live"
  - [FUTURE] Publish to @UnitgroupAI
    ↓
Log to logs/telegram_posts.jsonl
```

---

## Admin Workflow

### Step 1: Fetch News

Admin runs:
```
/news_fetch
```

**Bot Response:**
```
🔄 Fetching industry news...
✅ Created 3 news drafts

📄 draft_news_20240713_100000_001
📄 draft_news_20240713_100005_002
📄 draft_news_20240713_100010_003

Use /draft_preview <id> to review
```

### Step 2: Preview Draft

Admin runs:
```
/draft_preview draft_news_20240713_100000_001
```

**Bot Sends:**

```
🔍 DRAFT PREVIEW

📰 draft_news_20240713_100000_001

Source: IndustryWeek
Product: UNITFURNITURE
Score: 0.85
Date: 2024-07-13

---

🪑 UNITFURNITURE: мебель быстрее с Smart Manufacturing

UNITFURNITURE считает автоматически:
✅ Материал (ЛДСП, МДФ, массив)
✅ Обработку и отделку
✅ Фурнитуру
✅ Сборку и доставку

Коммерческое предложение за 30 сек!

👉 Откроить Mini App
📰 Источник: Furniture Today (2024-07-13)

---

Status: waiting_approval
Dry-Run Mode: ✅ ON
Require Approval: ✅ YES

Validation:
- Brand Names: ✅ PASS
- Content Safety: ✅ PASS
- Format: ✅ PASS

[✅ Approve] [❌ Reject]
[📝 Edit in App] [🔗 View Source]
```

### Step 3: Approve Draft

Admin clicks: **✅ Approve**

**What Happens:**
1. Draft status → `approved`
2. Logged with admin_id + timestamp
3. Bot confirms: "✅ Draft approved!"
4. Message updated: "✅ **APPROVED** by admin"

### Step 4: Dry-Run Preview (Future)

When fully integrated with publish system:
1. Bot sends dry-run preview to admin's private chat
2. Shows exactly how post will look in @UnitgroupAI
3. Admin reviews and confirms: "Publish Live"
4. [SYSTEM] Posts to @UnitgroupAI
5. Message ID logged to `logs/telegram_posts.jsonl`

---

## Safety Guarantees

### Design Principles

✅ **NO Auto-Publish**
- Every post requires explicit admin approval
- Guaranteed by architecture (no auto-publish code paths)

✅ **Dry-Run Mode Always On**
- Posts first shown to admin in dry-run
- Never automatically published to channel

✅ **Admin Approval Required**
- Every draft waits for admin decision
- Admin can approve, reject, or edit

✅ **Brand Validation Automatic**
- Enforces: UNITFURNITURE (not UNIFURNITURE)
- Enforces: UNITMETALL (not UNIMETALL)
- Enforces: UNITPLAST (correct)
- Enforces: UNITGROUP (correct)

✅ **Content Safety Checks**
- Blocks: Fake metrics, unverified claims
- Blocks: Political/controversial content
- Blocks: Spam
- Requires: Source attribution

✅ **Complete Audit Trail**
- Every event logged (fetch, filter, score, rewrite, validate, approve, publish)
- Admin tracked (admin_id, timestamp)
- Changes tracked (reason for rejection, etc.)

### Configuration Locks

```yaml
data/media_sources.yaml:
  moderation:
    require_approval: true      # Hardcoded to true
    dry_run_mode: true          # Hardcoded to true
    allow_auto_publish: false   # Hardcoded to false
```

No environment variable can override these.

### Draft Safety

Every draft has:
```json
{
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

No publish can happen without:
1. `status` → `approved`
2. `approved_by` set to admin_id
3. Manual admin confirmation

---

## RSS Feed Sources

### 5 Categories, 10 Feeds

| Category | Feeds |
|----------|-------|
| **Manufacturing** | IndustryWeek, Manufacturing Tomorrow |
| **Plastics** | PlasticsToday, Plastics Technology Online |
| **Furniture** | Furniture Today, Décor Magazine |
| **Metal** | The Fabricator, Sheet Metal Magazine |
| **Automation** | Robotics Business Review, AI Weekly |

### Filter Rules

**Include Keywords:**
- automation, cost reduction, production efficiency
- order management, pricing, manufacturing
- calculation, AI, delivery time, supply chain

**Exclude Keywords:**
- politics, weather, sports, entertainment
- fake, test

**Constraints:**
- Min 50 words, max 5000 words
- Min relevance score: 0.6

---

## Rewrite Rules

### Rule 1: Emoji Hook

```
Before: "Smart manufacturing increases efficiency"
After: "🤖 Интеллектуальное производство повышает эффективность"
```

### Rule 2: Product Context

```
Before: "Manufacturing news"
After: "UNITFURNITURE считает автоматически:
- Материал (ЛДСП, МДФ, массив)
- Обработка и отделка
- Фурнитура
- Сборка и доставка"
```

### Rule 3: CTA

```
Before: "Read more..."
After: "👉 Откроить Mini App
Рассчитай свой заказ за 30 сек"
```

### Rule 4: Source Attribution

```
After: "📰 Источник: Furniture Today (July 13)"
```

---

## Logging

### Log File

**Location:** `logs/telegram_posts.jsonl`

**Format:** One JSON object per line

```json
{"timestamp": "2024-07-13T10:00:00Z", "event": "draft_created", "draft_id": "draft_news_001", "brand_module": "UNITFURNITURE", "source": "Furniture Today"}
{"timestamp": "2024-07-13T10:00:30Z", "event": "validation_passed", "draft_id": "draft_news_001", "checks": ["brand", "safety", "format"]}
{"timestamp": "2024-07-13T10:01:00Z", "event": "preview_sent", "draft_id": "draft_news_001", "admin_id": 123456}
{"timestamp": "2024-07-13T10:05:00Z", "event": "draft_approved", "draft_id": "draft_news_001", "admin_id": 123456}
{"timestamp": "2024-07-13T10:10:00Z", "event": "dry_run_preview", "draft_id": "draft_news_001"}
{"timestamp": "2024-07-13T10:15:00Z", "event": "published", "draft_id": "draft_news_001", "channel_message_id": 999}
```

**Events:**
- `news_fetched` - News item fetched from RSS
- `validation_completed` - Brand/safety validation done
- `draft_created` - Draft JSON saved
- `draft_approved` - Admin approved
- `draft_rejected` - Admin rejected
- `dry_run_preview` - Dry-run shown to admin
- `published` - Posted to @UnitgroupAI (future)

---

## File Structure

```
unitplast_bot/
├── app/
│   ├── industry_news_rewriter.py      # NewsRewriter class (fetch, filter, score, rewrite, validate, create drafts)
│   └── media_bot_integration.py        # MediaBotIntegration class (admin workflow, approvals, callbacks)
├── data/
│   ├── media_sources.yaml             # RSS feed config (10 feeds, filters, processing)
│   └── post_drafts/                   # Draft JSON files
│       ├── draft_news_20240713_001.json
│       └── draft_news_20240713_002.json
├── skills/
│   └── news_rewrite_for_telegram_skill.md  # Rewrite rules, validation rules, examples
├── .claude/agents/
│   └── industry-news-rewriter.md      # Agent definition & 10-step workflow
├── docs/
│   └── INDUSTRY_NEWS_SOURCES_AND_REWRITE_PIPELINE.md  # 500-line complete architecture
├── logs/
│   └── telegram_posts.jsonl           # Audit trail (JSONL format)
├── requirements.txt                   # feedparser, PyYAML
├── test_industry_news_rewriter.py     # 14 test cases for NewsRewriter
└── test_media_bot_integration.py      # 11 test cases for integration
```

---

## Testing

### Run All Tests

```bash
# News rewriter tests
python3 -m pytest test_industry_news_rewriter.py -v

# Integration tests
python3 -m pytest test_media_bot_integration.py -v

# All tests
python3 -m pytest test_*.py -v
```

### Test Coverage

- ✅ RSS fetching
- ✅ Keyword filtering
- ✅ Relevance scoring
- ✅ Product mapping
- ✅ Brand name validation
- ✅ Content safety checks
- ✅ Telegram rewriting
- ✅ Draft creation
- ✅ Draft persistence
- ✅ Admin approval workflow
- ✅ Rejection tracking
- ✅ Audit logging

---

## Integration with telegram_final_bot.py

To integrate into the main bot:

```python
from .media_bot_integration import (
    MediaBotIntegration,
    cmd_draft_list,
    cmd_news_fetch,
    cmd_draft_preview,
    handle_draft_callback
)

class TelegramFinalBot:
    def _setup_handlers(self):
        # ... existing handlers ...
        
        # Media bot commands
        self.dp.message.register(self.cmd_news_fetch, Command("news_fetch"))
        self.dp.message.register(self.cmd_draft_list, Command("draft_list"))
        self.dp.message.register(self.cmd_draft_preview, Command("draft_preview"))
        
        # Callbacks
        self.dp.callback_query.register(self.handle_draft_callback)
    
    async def cmd_news_fetch(self, message: types.Message):
        await cmd_news_fetch(message, self.media_integration)
    
    async def cmd_draft_list(self, message: types.Message):
        await cmd_draft_list(message, self.media_integration)
    
    # ... etc ...
```

---

## Next Steps

### Immediate (This Sprint)

1. ✅ Architecture & configuration complete
2. ✅ NewsRewriter module implemented
3. ✅ MediaBotIntegration module implemented
4. ✅ Tests created and passing (25+ test cases)
5. ⏳ **Integrate handlers into telegram_final_bot.py**
6. ⏳ **Deploy to VPS**
7. ⏳ **Monitor and iterate**

### Testing Phase

- Test fetch from real RSS feeds
- Test filtering and scoring accuracy
- Test rewriting quality and brand consistency
- Test admin approval workflow
- Test dry-run mode
- Test audit logging completeness

### Monitoring

- Watch `logs/telegram_posts.jsonl` for all events
- Verify no unwanted publishes to @UnitgroupAI
- Track admin approval rate
- Monitor content quality
- Review rejection reasons

---

## Security Checklist

- ✅ No TELEGRAM_BOT_TOKEN in config files
- ✅ No .env file committed
- ✅ No auto-publish code paths exist
- ✅ Approval always required (by design)
- ✅ Dry-run mode always on
- ✅ Content validated before draft
- ✅ Brand names checked automatically
- ✅ Fake metrics blocked
- ✅ Source always attributed
- ✅ Complete audit trail
- ✅ Token never exposed

---

## Implementation Status

| Phase | Status | Details |
|-------|--------|---------|
| **Architecture** | ✅ Complete | Config, skill, agent |
| **Configuration** | ✅ Complete | RSS feeds, filters, rules |
| **Core Implementation** | ✅ Complete | NewsRewriter, MediaBotIntegration |
| **Testing** | ✅ Complete | 25+ test cases, all passing |
| **Bot Integration** | ⏳ TODO | Add handlers to telegram_final_bot.py |
| **Deployment** | ⏳ TODO | Deploy to VPS |
| **Monitoring** | ⏳ TODO | Watch logs, verify no auto-publish |

---

**Status: ✅ IMPLEMENTATION COMPLETE, READY FOR DEPLOYMENT**

Architecture, configuration, modules, tests, and documentation complete.  
Awaiting integration with main telegram_final_bot.py and deployment to VPS.

---

**Questions? Check:**
- `docs/INDUSTRY_NEWS_SOURCES_AND_REWRITE_PIPELINE.md` - Architecture
- `data/media_sources.yaml` - Configuration
- `test_industry_news_rewriter.py` - Examples
- `test_media_bot_integration.py` - Integration examples
