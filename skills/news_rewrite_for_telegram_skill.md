# Skill: News Rewrite for Telegram / UNITGROUP AI

## Purpose

Безопасный рерайт отраслевых новостей для Telegram-канала @UnitgroupAI.

Не копировать текст источника. Не переводить дословно. Не брать больше 25 слов прямой цитаты.
Сохранять ссылку на источник. Писать на русском. Добавлять производственный вывод.
Связывать новость с UNITGROUP AI. Не выдумывать клиентов или метрики.
Не копировать картинки без разрешения. Публиковать только после approval.

## Key Capabilities

1. **Fetch News** - Pull from RSS feeds (data/media_sources.yaml)
2. **Filter** - Include/exclude by keywords, relevance scoring
3. **Rewrite** - Adapt industry news to UNITGROUP value proposition
4. **Adapt to Products** - Map news to UNITPLAST/UNITFURNITURE/UNITMETALL use cases
5. **Create Draft** - Generate Telegram-formatted post draft
6. **Preview** - Show to admin before publish
7. **Validate** - Check brand names, no fake content
8. **Log** - Track all rewrites and publications

## Workflow

```
Fetch News Feed
    ↓
Filter by Keywords
    ↓
Relevance Score
    ↓
Rewrite for Telegram
    ↓
Adapt to UNITGROUP Context
    ↓
Create Draft JSON
    ↓
Brand Validation
    ↓
Preview in Admin Chat
    ↓
Admin Approves
    ↓
DRY-RUN (No publish)
    ↓
Log Result
```

## Input: Raw Industry News

**Example:**
```
Title: "New AI-Powered Automation Reduces Manufacturing Costs by 40%"
Source: "IndustryWeek"
URL: "https://..."
Content: "A new study shows that AI automation in manufacturing..."
Date: "2024-07-13"
```

## Output: Telegram Draft

**Example:**
```json
{
  "type": "text_with_photo",
  "brand_module": "UNITFURNITURE",
  "text": "🤖 AI снижает стоимость производства на 40%\n\nИсточник: IndustryWeek\n\nНовое исследование...",
  "cta": "Откроить Mini App",
  "draft_id": "draft_news_20240713_001",
  "source_url": "https://...",
  "status": "draft",
  "require_approval": true
}
```

## Rewrite Rules

### Rule 1: Hook (Emoji + Number/Benefit)

**Before:**
"New automation technology reduces costs"

**After:**
"🤖 Сокращение затрат на производство"

### Rule 2: Explain Why (UNITGROUP Context)

**Before:**
"AI helps with calculation"

**After:**
"Как UNITGROUP делает это за 30 секунд:
- Умное ценообразование
- Автоматический расчёт сроков
- Экспорт в PDF"

### Rule 3: Adapt to Product (UNITPLAST/UNITFURNITURE/UNITMETALL)

**Before:**
"Manufacturing costs decreased"

**After:**
"📊 Для UNITFURNITURE это означает:
- Точный расчёт фурнитуры
- Минимум отходов
- Быстрая коммерческое предложение"

### Rule 4: Add CTA (Clear Action)

**Before:**
"Read more at..."

**After:**
"👉 Откроить Mini App калькулятора
Рассчитай свой заказ за 30 сек"

### Rule 5: Keep Source

**Before:**
"From an article..."

**After:**
"📰 Источник: IndustryWeek (July 13)"

## Brand Validation (Mandatory)

Before creating draft, verify:

```
✅ UNITPLAST (not UNITPLAST)
✅ UNITFURNITURE (not UNIFURNITURE)
✅ UNITMETALL (not UNIMETALL)
✅ UNITGROUP (not UniGroup)
✅ Mini App (not mini-app, MiniApp)
```

If any wrong:
- 🚫 BLOCK draft
- 📝 Log error
- ⚠️ Alert admin

## Content Safety Checks

```
❌ FORBIDDEN:
- Fake statistics
- Unverified claims
- Competitor names
- Political content
- Spam

✅ ALLOWED:
- Real industry news
- Factual rewrites
- Educational content
- Honest examples
- Source attribution
```

## JSON Draft Structure

```json
{
  "id": "draft_news_20240713_001",
  "channel": "@UnitgroupAI",
  "status": "draft",
  "type": "text|photo|video|media_group",
  
  "source": {
    "url": "https://...",
    "title": "Original news title",
    "source_name": "IndustryWeek",
    "published_date": "2024-07-13",
    "fetched_at": "2024-07-13T10:00:00Z"
  },
  
  "content": {
    "text": "Telegram-formatted post text",
    "emoji_hook": "🤖",
    "cta_button_text": "Откроить Mini App",
    "cta_link": "https://unitgroup.tech/app/"
  },
  
  "metadata": {
    "brand_module": "UNITFURNITURE|UNITPLAST|UNITMETALL",
    "category": "automation|pricing|efficiency|design",
    "keywords": ["ai", "cost", "efficiency"],
    "relevance_score": 0.85,
    "word_count": 120
  },
  
  "validation": {
    "brand_check_passed": true,
    "safety_check_passed": true,
    "word_count_valid": true,
    "cta_present": true,
    "source_attributed": true
  },
  
  "approval": {
    "dry_run_mode": true,
    "require_approval": true,
    "approved_by": null,
    "approved_at": null
  },
  
  "history": {
    "created_at": "2024-07-13T10:00:00Z",
    "created_by": "news_rewriter",
    "rewrite_version": 1,
    "preview_sent_at": null,
    "published_at": null,
    "errors": []
  }
}
```

## Adaptation by Product

### UNITPLAST Example

**Original news:**
"Plastic injection molding sees 25% efficiency gain with AI"

**Rewritten:**
"🎯 Пластиковое литьё: +25% эффективности с AI

UNITPLAST автоматически рассчитывает:
- Материал и вес
- Цикл литья
- Стоимость партии
- Сроки доставки

Результат КП за 30 сек вместо часов.

👉 Откроить калькулятор"

### UNITFURNITURE Example

**Original news:**
"Smart manufacturing reduces furniture production time"

**Rewritten:**
"🪑 Мебель быстрее: Smart Manufacturing

UNITFURNITURE считает автоматически:
- Материал (ЛДСП, МДФ, массив)
- Обработка и отделка
- Фурнитура
- Сборка и доставка

Коммерческое предложение готово за 30 сек!

👉 Попробовать прямо сейчас"

### UNITMETALL Example

**Original news:**
"Metal fabrication AI improves quote accuracy"

**Rewritten:**
"🔧 Металл точнее: AI расчёты

UNITMETALL автоматически определяет:
- Тип и профиль металла
- Резка, гибка, сварка
- Покрытие и покраска
- Итоговая стоимость

Точная коммерческое предложение за 30 сек.

👉 Рассчитать заказ"

## Integration Points

### With media_sources.yaml

- Fetch from configured feeds
- Apply include/exclude filters
- Score relevance
- Choose top 3 per day

### With Mini App

- Add "Share to channel" button
- Draft auto-created from calculation
- Auto-rewrite with context

### With Telegram Media Bot

- Create draft via /draft_create
- Preview via /draft_preview
- Require admin approval
- Log to telegram_posts.jsonl

## Configuration

```yaml
# In data/media_sources.yaml
processing:
  rewrite_style: "telegram"
  translate_to: "ru"
  max_posts_per_day: 3

moderation:
  require_approval: true
  dry_run_mode: true
  allow_auto_publish: false
```

## Safety Guarantees

```
✅ NO auto-publish (ever)
✅ Dry-run mode always on
✅ Admin approval required
✅ Brand validation automatic
✅ Safety checks before draft
✅ Source always attributed
✅ Logs complete audit trail
✅ Token never exposed
```

## Main Rules (Mandatory)

1. Не копировать текст источника.
2. Не переводить дословно.
3. Не брать больше 25 слов прямой цитаты из одного источника.
4. Сохранять ссылку на источник.
5. Писать на русском.
6. Добавлять производственный вывод.
7. Связывать новость с UNITGROUP AI.
8. Не выдумывать клиентов.
9. Не выдумывать цифры.
10. Не копировать картинки без разрешения.
11. Публиковать только после approval.

## Post Structure

1. Хук (с emoji).
2. Что произошло.
3. Почему это важно производству.
4. Как это связано с UNITPLAST / UNITFURNITURE / UNITMETALL.
5. Что можно автоматизировать.
6. CTA (Call To Action).
7. Источник.

## Scoring Rules

```
+3 — есть станок / технология / производство
+3 — относится к UNITPLAST / UNITFURNITURE / UNITMETALL
+2 — можно объяснить пользу для малого/среднего производства
+2 — есть визуал или можно сделать свой
+1 — свежая новость
-5 — просто реклама без пользы
-5 — нет источника
-5 — нельзя безопасно использовать
-5 — нет связи с производством
-5 — невозможно проверить факт
```

Публиковать можно только если:
- score >= 6
- safety_status = APPROVED
- approval_required = true
- user_approved = true

## Visual Rules

**Allowed:**
- AI-generated image
- Official press image with permission
- Own product mockup
- Own UI screenshot

**Forbidden:**
- Random article image
- Pinterest image
- Instagram image
- Telegram repost image
- Watermark removal
- Fake factory photo

## Post Types

- Новость + вывод
- Новинка станка
- Технология недели
- Ошибка производства
- Как AI считает КП
- До / после автоматизации
- Разбор тренда
- Видео-сценарий
- Карусель
- Дайджест

## Testing Checklist

- [ ] Fetch from RSS works
- [ ] Filter by keywords works
- [ ] Rewrite produces readable text
- [ ] Brand validation catches errors
- [ ] Scoring logic correct
- [ ] Draft JSON valid
- [ ] Preview in admin chat works
- [ ] Dry-run prevents publish
- [ ] Logging complete
- [ ] No token in logs
- [ ] Approval workflow works

---

**Status:** Ready for implementation  
**Dependencies:** data/media_sources.yaml, telegram_final_bot.py  
**Next:** Verify all sources classified, update agent definition
