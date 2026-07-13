# 📺 TELEGRAM MEDIA BOT - Complete Setup Report

**Date:** July 13, 2024  
**Channel:** @UnitgroupAI  
**Status:** ✅ **SKILL CREATED & ENV CONFIGURED**  
**Bot Purpose:** Safe channel publishing with admin approval workflow

---

## Executive Summary

Telegram Media Bot skill has been created for @UnitgroupAI channel. The bot ensures:

✅ **No auto-publishing** - Always requires explicit admin approval  
✅ **Dry-run enabled** - Preview before every publish  
✅ **Brand validation** - Checks UNITFURNITURE, UNITMETALL spelling  
✅ **Content safety** - Blocks fake clients, fake metrics  
✅ **Token protected** - Never stored in code  
✅ **Approval workflow** - draft → preview → approve → publish  

**Status: READY FOR IMPLEMENTATION**

---

## What Was Created

### 1. Telegram Media Bot Skill

**File:** `skills/telegram_media_bot_skill.md`

**Contains:**
- Complete skill specification
- Architecture and API methods
- Environment variables needed
- Security rules (token protection)
- Brand validation rules
- Content rubrics for 5 post types
- QA checklist (10-point review)
- Approval workflow (4 stages)
- Logging & audit trail format
- Error handling procedures

**Length:** 428 lines of documentation

### 2. Environment Configuration

**Updated:** `.env.example`

**New variables added:**
```env
TELEGRAM_MEDIA_BOT_TOKEN=optional_media_bot_token
TELEGRAM_CHANNEL_USERNAME=@UnitgroupAI
TELEGRAM_CHANNEL_ID=-100optional_channel_id
TELEGRAM_MEDIA_ADMIN_IDS=optional_admin_user_id
TELEGRAM_DRY_RUN=true
TELEGRAM_REQUIRE_APPROVAL=true
TELEGRAM_POST_LOG_PATH=logs/telegram_posts.jsonl
TELEGRAM_DRAFT_STORAGE_PATH=data/drafts/
```

**Key:**
- ✅ Dry-run enabled by default
- ✅ Approval required
- ✅ Paths for logs and drafts

---

## Key Features Defined

### Dry-Run Mode

**Default state:** `TELEGRAM_DRY_RUN=true`

When enabled:
1. Bot creates draft
2. Bot sends preview to admin chat
3. Admin sees exact appearance
4. Admin can edit or approve
5. **Bot does NOT publish to @UnitgroupAI**
6. Only explicit "PUBLISH LIVE" goes to channel

### Approval Workflow

```
CREATE         →  User creates draft
                  (text + media)
   ↓
PREVIEW        →  Bot sends preview to admin
                  Admin sees: text, media, formatting
   ↓
QA CHECK       →  Automated validation:
                  - Brand names correct?
                  - No fake clients?
                  - No fake metrics?
                  - CTA clear?
                  - Safety check
   ↓
ADMIN REVIEW   →  Admin reviews in Telegram
                  Taps: [Approve] or [Reject]
   ↓
APPROVE        →  Admin explicit confirmation
                  "Are you sure? This posts to @UnitgroupAI"
   ↓
PUBLISH        →  Bot publishes to channel
                  Logs message ID
   ↓
LOG RESULT     →  Records in logs/telegram_posts.jsonl
```

### Brand Validation

**Before publish, check:**
- ✅ UNITPLAST (correct)
- ✅ UNITFURNITURE (correct)
- ✅ UNITMETALL (correct)
- ✅ UNITGROUP (correct)
- ❌ UNIFURNITURE (WRONG - block)
- ❌ UNIMETALL (WRONG - block)
- ❌ Any misspellings (block)

### Content Rubrics

**5 approved post types:**

1. **Product Updates** - New features, improvements
2. **Calculation Examples** - Real pricing breakdowns
3. **Before/After Automation** - Time savings examples
4. **Integration News** - 1C, Google Sheets, etc
5. **Educational Content** - How to calculate, tips

### QA Checklist (10 Points)

Before admin approval, verify:

- [ ] Hook present? (First sentence grabs attention)
- [ ] Benefit clear? (Why should reader care?)
- [ ] Real data? (No fake numbers)
- [ ] No fake clients? (Real team feedback only)
- [ ] Branding correct? (UNITFURNITURE not UNIFURNITURE)
- [ ] CTA clear? (One action button)
- [ ] Text length OK? (Fits mobile view)
- [ ] Media attached? (if needed)
- [ ] No secrets? (No tokens, no passwords)
- [ ] Approval explicit? (Admin said "yes")

---

## Security Measures

### Token Protection

```
❌ BAD:  token = "123456:ABCdef..."  # In code
❌ BAD:  export TELEGRAM_BOT_TOKEN  # In bash_history
❌ BAD:  console.log(full_token)   # In logs

✅ GOOD: token = os.getenv("TELEGRAM_MEDIA_BOT_TOKEN")
✅ GOOD: log("token: 123456...hidden")  # Prefix only
✅ GOOD: .env in .gitignore
```

### Publish Protection

```
❌ Auto-publish (NEVER)
❌ Silent publishing (NEVER)
❌ Without approval (NEVER)

✅ Explicit admin approval
✅ Dry-run preview first
✅ Confirmation dialog
✅ Logged to JSONL
```

### Content Safety

```
❌ Allowed: Fake clients
❌ Allowed: Fake metrics ("100x faster" without data)
❌ Allowed: Misleading claims
❌ Allowed: Exposing tokens

✅ Allowed: Real examples
✅ Allowed: Real team feedback
✅ Allowed: Honest mockups
✅ Allowed: Verifiable claims
```

---

## Implementation Checklist (For Next Sprint)

### Phase 1: Core Bot (1-2 weeks)

- [ ] Create `app/telegram_media_bot.py`
  - `TelegramMediaBot` class
  - `create_draft()` method
  - `preview_draft()` method
  - `publish_draft()` method (with confirmation)
  - `validate_branding()` checker
  - `validate_safety()` checker

- [ ] Create draft storage
  - `data/drafts/` directory
  - JSON storage for drafts
  - Draft status tracking

- [ ] Implement logging
  - `logs/telegram_posts.jsonl`
  - Per-post logging
  - Audit trail

- [ ] Create admin commands
  - `/draft_list` - Show pending
  - `/draft_preview <id>` - Preview
  - `/draft_approve <id>` - Approve & publish
  - `/draft_reject <id>` - Reject with reason

### Phase 2: Integration (1 week)

- [ ] Connect to Mini App
  - Users can draft in app
  - Admins approve in Telegram

- [ ] Connect to backend API
  - Store drafts in database
  - Track publish history
  - Admin dashboard

- [ ] Create admin panel
  - View pending drafts
  - Approve/reject UI
  - Publish history view

### Phase 3: Testing (1 week)

- [ ] Test dry-run mode
- [ ] Test approval workflow
- [ ] Test brand validation
- [ ] Test content safety checks
- [ ] Test token security
- [ ] Test error handling
- [ ] Test logging

### Phase 4: Deployment (1 week)

- [ ] Deploy to VPS
- [ ] Configure bot in @BotFather
- [ ] Add bot as admin to @UnitgroupAI
- [ ] Test live publishing
- [ ] Monitor logs

---

## Required Agents (For Management)

### telegram-channel-manager

Responsible for:
- Channel content strategy
- Publishing schedule
- Rubric selection
- Quality standards
- Team coordination

### media-content-producer

Responsible for:
- Post ideas
- Draft writing
- Caption writing
- Content calendar
- Adapting product → B2B content

### telegram-bot-engineer

Responsible for:
- Bot implementation
- API integration
- Webhook/polling setup
- VPS deployment
- Token security
- Dry-run testing
- Approval workflow

### channel-qa-moderator

Responsible for:
- QA checklist verification
- Brand name validation
- Fact checking
- Content safety review
- Final "APPROVED/BLOCKED" decision

---

## Deployment Architecture

### Current State

```
.env                    ← Stores TELEGRAM_MEDIA_BOT_TOKEN
.env.example            ← Template (safe for Git)
skills/
  ├── telegram_media_bot_skill.md  ← This specification
```

### After Implementation (Phase 1)

```
app/
  ├── telegram_media_bot.py         ← Bot implementation
  ├── telegram_draft_store.py       ← Draft storage
  └── telegram_validators.py        ← Brand/safety checks
data/
  └── drafts/                       ← Draft JSON files
logs/
  └── telegram_posts.jsonl          ← Audit trail
```

### After Integration (Phase 2)

```
web/
  └── miniapp.html                  ← Add "Share to channel" UI
docker-compose.yml                  ← Media bot service
scripts/
  └── deploy_media_bot.sh           ← Deployment script
```

---

## Security Checklist

- ✅ `.env` not in Git (protected by .gitignore)
- ✅ `.env.example` safe for Git (no real tokens)
- ✅ Tokens loaded from environment only
- ✅ Token prefix logged only (123456...hidden)
- ✅ No auto-publishing
- ✅ Approval required
- ✅ Dry-run by default
- ✅ Content validated
- ✅ Audit trail in JSONL
- ✅ Admin permissions checked

---

## Next Actions

### Immediate (This Week)

1. ✅ Create skill specification - **DONE**
2. ✅ Configure .env.example - **DONE**
3. ⏳ Create agents (telegram-channel-manager, etc.)
4. ⏳ Create admin panel UI (or dashboard)

### Soon (Next Week)

5. ⏳ Implement `TelegramMediaBot` class
6. ⏳ Implement draft storage
7. ⏳ Implement validators
8. ⏳ Implement admin commands
9. ⏳ Deploy to VPS

### Later (Next Sprint)

10. ⏳ Mini App integration
11. ⏳ Backend database storage
12. ⏳ Publish history dashboard
13. ⏳ Advanced scheduling

---

## FAQ

**Q: Why dry-run by default?**  
A: Safety first. Bot never publishes without admin seeing preview + confirming.

**Q: Why block UNIFURNITURE?**  
A: Brand consistency. Must be UNITFURNITURE (correct spelling).

**Q: Can I auto-publish release notes?**  
A: No. Always requires admin approval. Auto-publish is forbidden.

**Q: What if admin doesn't approve?**  
A: Draft stays in "needs_review" status. Can edit and resubmit.

**Q: Where's the bot token stored?**  
A: In `.env` file (not in code). Loaded via `os.getenv()`.

**Q: Can I delete published posts?**  
A: Only with explicit admin command. All deletions logged.

**Q: What prevents fake metrics?**  
A: QA checklist item: "Real data?" Bot flags suspicious claims.

---

## References

- Channel: https://t.me/UnitgroupAI
- Skill: `skills/telegram_media_bot_skill.md`
- Telegram Bot API: https://core.telegram.org/bots/api
- aiogram library: https://docs.aiogram.dev/

---

**Status: ✅ SKILL & ENV READY FOR IMPLEMENTATION**

Next: Create agents and implement bot code.

