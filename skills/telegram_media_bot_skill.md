# Skill: Telegram Media Bot for UNITGROUP AI

## Purpose

Управление медиа-контентом и публикациями в Telegram-канале @UnitgroupAI с требованием явного подтверждения перед публикацией.

## Channel

- **Username:** @UnitgroupAI
- **Public URL:** https://t.me/UnitgroupAI
- **Type:** Public channel
- **Purpose:** Product updates, feature announcements, educational content about manufacturing AI

## Core Capabilities

1. ✅ Create Telegram post drafts (text + media)
2. ✅ Prepare media captions and formatting
3. ✅ Publish text posts to channel
4. ✅ Publish single photo posts
5. ✅ Publish video posts
6. ✅ Publish media groups / albums
7. ✅ Dry-run mode (preview without publishing)
8. ✅ Admin approval workflow (draft → preview → approve → publish)
9. ✅ Store draft history
10. ✅ Validate brand names before publish
11. ✅ Check content safety
12. ✅ Protect and log Telegram bot token securely
13. ✅ Require explicit admin approval before any publish action

## Required Bot API Methods

- `getMe` — Bot identity
- `sendMessage` — Send text messages
- `sendPhoto` — Publish photo posts
- `sendVideo` — Publish video posts
- `sendAnimation` — Publish GIFs
- `sendDocument` — Publish documents
- `sendMediaGroup` — Publish photo/video albums
- `editMessageText` — Edit draft previews
- `deleteMessage` — Remove draft previews after publish
- `getChatMember` — Verify admin permissions
- `pinChatMessage` — Pin important announcements

## Required Environment Variables

```env
# Telegram Media Bot
TELEGRAM_MEDIA_BOT_TOKEN=<bot_token_from_@BotFather>
TELEGRAM_CHANNEL_USERNAME=@UnitgroupAI
TELEGRAM_CHANNEL_ID=-100<numeric_id>
TELEGRAM_ADMIN_IDS=<comma_separated_user_ids>

# Bot Behavior
TELEGRAM_DRY_RUN=true                    # Enabled by default
TELEGRAM_REQUIRE_APPROVAL=true           # Always require approval
TELEGRAM_POST_LOG_PATH=logs/telegram_posts.jsonl
TELEGRAM_DRAFT_STORAGE_PATH=data/drafts/
```

## Security Rules

- ✅ **Never commit .env or store bot token in code**
- ✅ **Always load token from environment variable**
- ✅ **Never hardcode bot token in source files**
- ✅ **Never publish without explicit approval**
- ✅ **Never delete channel messages without explicit approval**
- ✅ **Never expose admin IDs publicly**
- ✅ **Log only token prefix (first 10 chars) + ...hidden**
- ✅ **Always support dry-run mode**
- ✅ **Always validate admin permissions**
- ✅ **Never auto-publish**

## Brand Rules

### Correct Brand Names

```txt
✅ UNITPLAST
✅ UNITFURNITURE
✅ UNITMETALL
✅ UNITGROUP
✅ UNITGROUP AI
```

### Incorrect Names (FORBIDDEN)

```txt
❌ UNIFURNITURE
❌ UNIMETALL
❌ Unifurniture
❌ Unimetall
❌ UniFurniture
❌ UniMetall
❌ UniGroup
```

### Brand Validation

Before publishing, check:
- No UNIFURNITURE (should be UNITFURNITURE)
- No UNIMETALL (should be UNITMETALL)
- Product names spelled correctly
- No typos in UNITGROUP, UNITPLAST, UNITFURNITURE, UNITMETALL

## Content Rules

### ✅ Allowed Content

- Product updates and new features
- Mini App progress and releases
- Calculator improvements
- AI production automation examples
- Real UNITPLAST calculations
- Real UNITFURNITURE calculations
- Real UNITMETALL calculations
- Telegram bot updates
- Real project progress
- Educational content about manufacturing
- Integration announcements (1C, Google Sheets, etc)
- Video tutorials (10-30 seconds)
- Before/after automation examples
- Honest mockups and prototypes

### ❌ Forbidden Content

- **Fake clients** (No made-up company names)
- **Fake metrics** (No invented statistics)
- **Fake testimonials** (Use real team feedback only)
- **Misleading guarantees** ("100% faster" without data)
- **Secret tokens or passwords**
- **Private user data or personal information**
- **Spam or repetitive content**
- **Auto-posting without approval**
- **Political or controversial content**
- **Promotional content for competitors**
- **Unverified claims about product capabilities**

## Content Rubrics for @UnitgroupAI

### 1. Product Updates

```txt
🎯 Title: [Feature Name]
📝 Body:
  1. What changed?
  2. Why does it matter?
  3. How to use?
  4. CTA
```

### 2. Calculation Examples

```txt
📊 Title: Как рассчитывается [UNITPLAST/UNITFURNITURE/UNITMETALL]?
📝 Body:
  1. Материал → [X ₽/м²]
  2. Обработка → [Y ₽]
  3. Сборка → [Z ₽]
  4. КП → [TOTAL ₽]
  5. CTA: Расчёт за 30 сек
```

### 3. Before/After Automation

```txt
⏱️ Title: До и после автоматизации
📝 Body:
  ❌ Было: X часов на КП
  ✅ Стало: 30 секунд
  Как? [Объяснение]
```

### 4. Integration News

```txt
🔗 Title: Интеграция с [System]
📝 Body:
  Что? [Description]
  Зачем? [Use case]
  Как? [Quick start]
  CTA: Попробовать
```

### 5. Educational Content

```txt
🎓 Title: Как считать [Product Type]?
📝 Body:
  1. Входные данные
  2. Формула / процесс
  3. Пример
  4. Результат
```

## Post Structure Template

```txt
[HOOK - 1 sentence that grabs attention]

[BODY - 3-4 sentences explaining problem/solution]

[EXAMPLE - Real calculation or before/after]

[CTA - One clear action]
  Button: Открыть Mini App / Получить демо / Написать вопрос
```

## Approval Workflow

### Draft Creation

```python
draft = {
    "id": "draft_123",
    "channel": "@UnitgroupAI",
    "status": "draft",
    "type": "text|photo|video|media_group",
    "brand_module": "UNITPLAST|UNITFURNITURE|UNITMETALL|UNITGROUP",
    "text": "...",
    "media": [...],
    "cta": "...",
    "created_at": "2024-07-13T10:00:00Z",
    "created_by": "user_123",
    "approved_by": null,
    "approved_at": null,
    "published_at": null,
    "telegram_message_ids": [],
    "errors": []
}
```

### Draft Statuses

```txt
draft          → Just created, under editing
needs_review   → Ready for admin review
approved       → Admin approved, ready to publish
published      → Successfully published to channel
failed         → Publishing failed (see errors)
blocked        → Content blocked by QA
archived       → Old draft, hidden from list
```

### Approval Process

1. **CREATE:** User creates draft in mini app or admin panel
2. **PREVIEW:** Bot sends preview message in private chat
3. **VALIDATE:** QA checks branding, content, safety
4. **REVIEW:** Admin reviews in Telegram
5. **APPROVE:** Admin taps "Approve" button
6. **PUBLISH:** Bot publishes to @UnitgroupAI
7. **LOG:** Record publish result

### Admin Commands

```txt
/draft_preview <id>     → Show draft preview
/draft_approve <id>     → Approve and publish
/draft_reject <id>      → Reject with comment
/draft_list             → Show pending drafts
/draft_archive <id>     → Hide old draft
/channel_stats          → Show publish stats
```

## QA Checklist (Before Approval)

Before admin approves ANY post, check:

- [ ] **Hook Present?** First sentence grabs attention
- [ ] **Benefit Clear?** Reader knows why they should care
- [ ] **Real Data?** No fake numbers, no invented metrics
- [ ] **No Fake Clients?** Real team feedback only
- [ ] **Branding Correct?**
  - ✅ UNITPLAST, UNITFURNITURE, UNITMETALL
  - ❌ No UNIFURNITURE, UNIMETALL
- [ ] **CTA Clear?** One action button
- [ ] **Text Length OK?** Not too long (fit in mobile view)
- [ ] **Media Attached?** (if text-only, that's OK)
- [ ] **No Secrets?** No tokens, no passwords, no private data
- [ ] **Tone Professional?** Fits brand
- [ ] **Links Work?** (if any)
- [ ] **Safe to Publish?** No controversial content
- [ ] **Approval Explicit?** Admin said "yes"

### QA Verdict

```txt
✅ APPROVED   → Publish immediately
⚠️  NEEDS_EDIT → Return to draft, list issues
🚫 BLOCKED    → Do not publish, explain why
```

## Dry-Run Mode

**Default:** `TELEGRAM_DRY_RUN=true`

When dry-run is enabled:

1. Bot creates draft
2. Bot sends preview to admin chat
3. Admin sees exactly what will publish
4. Admin taps "Approve in Dry-Run" to test
5. **Bot does NOT publish to @UnitgroupAI**
6. Admin can edit and retry
7. Only after explicit "PUBLISH LIVE" does it go to channel

### Dry-Run Endpoint

```python
publish_dry_run(draft_id) → returns preview_message_id
publish_live(draft_id)     → requires admin_id confirmation
```

## Logging & Audit Trail

### Log File Format (JSONL)

```json
{"timestamp": "2024-07-13T10:00:00Z", "event": "draft_created", "draft_id": "draft_123", "created_by": "user_123"}
{"timestamp": "2024-07-13T10:05:00Z", "event": "draft_preview", "draft_id": "draft_123", "preview_msg_id": 999}
{"timestamp": "2024-07-13T10:10:00Z", "event": "qa_check", "draft_id": "draft_123", "verdict": "approved"}
{"timestamp": "2024-07-13T10:15:00Z", "event": "published", "draft_id": "draft_123", "channel_msg_id": 888, "published_by": "admin_123"}
```

### What NOT to Log

- ❌ Full bot token (OK to log prefix only: `token: 123456...hidden`)
- ❌ Admin user IDs (OK to log admin_username)
- ❌ User private data
- ❌ Passwords or secrets

### What to Log

- ✅ Draft creation (who, when)
- ✅ Approval (who, when, verdict)
- ✅ Publishing (channel, message ID)
- ✅ Failures (error message, timestamp)
- ✅ Deletions (who requested, when)

## Publishing Confirmation

**Never** auto-publish. Always require explicit confirmation:

```txt
Admin sees preview → Admin taps [Approve & Publish]
                   → Bot asks: "Are you sure? This will post to @UnitgroupAI"
                   → Admin taps [Yes, Publish Now]
                   → Bot publishes
```

## Error Handling

### Publishing Failures

If publish fails:

```python
error_reasons = [
    "bot_kicked_from_channel",        # Bot not admin in channel
    "message_too_long",               # > 4096 chars
    "invalid_media_url",              # File not found
    "channel_private",                # Not public channel
    "api_rate_limit",                 # Too many requests
    "invalid_media_type",             # Unsupported file
    "network_error",                  # Telegram API down
]

# On error:
# 1. Log the error
# 2. Notify admin in private chat
# 3. Keep draft in "failed" status
# 4. Suggest retry or edit
```

## Integration Points

### With Mini App

- Mini App users can draft posts
- Admins approve in Telegram
- Published content shows in @UnitgroupAI

### With Backend API

- Store drafts in database
- Track publish history
- Admin dashboard shows stats

### With Webhook (Optional Future)

- Receive events from CI/CD
- Auto-create "Release" drafts
- Admin approves before publish

## Success Criteria

A Telegram Media Bot skill is successful when:

- ✅ Drafts can be created and previewed
- ✅ Dry-run mode works by default
- ✅ Admin approval required before any publish
- ✅ No auto-publishing ever happens
- ✅ All brand names correct before publish
- ✅ No fake clients or fake metrics published
- ✅ Bot token never exposed in logs or code
- ✅ Publish failures logged and reported
- ✅ Admin receives preview in private chat
- ✅ Content published exactly as previewed
- ✅ History logged in JSONL file
- ✅ QA checklist prevents bad posts

---

**Version:** 1.0  
**Last Updated:** 2024-07-13  
**Status:** Draft (Awaiting Implementation)
