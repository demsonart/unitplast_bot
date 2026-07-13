# Skill: News Rewrite for Telegram / UNITGROUP AI

## Purpose

Безопасный рерайт отраслевых новостей для информационного Telegram-канала @UnitgroupAI.

Канал — это источник информации о производстве, машинах, технологиях и бизнес-идеях,
не продажный питч. 

**Правила:**
- ✅ Переписывать, не копировать (не дословно)
- ✅ Мягкие, информационные CTA только
- ✅ Сохранять ссылку на источник всегда
- ✅ Писать на русском
- ✅ Добавлять практический вывод для производителей
- ✅ Не выдумывать клиентов, цифры или факты
- ✅ Не копировать картинки без разрешения
- ❌ НИКОГДА не использовать hard CTA (Mini App, КП, расчеты, демо)
- ❌ Публиковать ТОЛЬКО после approval в DRY_RUN режиме

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
  "text": "🪑 AI контролирует качество мебели\n\nНовое исследование показывает...",
  "cta": "Какие технологии вас интересуют?",
  "draft_id": "draft_news_20240713_001",
  "source_url": "https://...",
  "status": "draft",
  "require_approval": true
}
```

## Rewrite Rules

### Rule 1: Hook (Emoji + Headline)

**Before:**
"New automation technology reduces costs"

**After:**
"🤖 Автоматизация снижает затраты на производство"

### Rule 2: Explain Context (Why It Matters)

**Before:**
"AI helps with manufacturing efficiency"

**After:**
"Новые технологии помогают производителям:
- Ускорить процесс
- Снизить затраты
- Улучшить качество"

### Rule 3: Adapt to Audience (Manufacturing Focus)

**Before:**
"Manufacturing costs decreased"

**After:**
"📊 Для производства это означает:
- Меньше брака
- Быстрее сроки
- Стабильнее качество"

### Rule 4: Add Soft CTA (Engagement)

**Before:**
"Read more at..."

**After:**
"→ Какие технологии вас интересуют?
Напишите в комментариях"

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

## Content Safety & CTA Checks

```
❌ FORBIDDEN:
- Fake statistics
- Unverified claims
- Competitor names
- Political content
- Spam
- Hard CTA (sales pitch)

✅ ALLOWED:
- Real industry news
- Factual rewrites
- Educational content
- Honest examples
- Source attribution
- Soft CTA (engagement)

❌ FORBIDDEN CTA LIST:
- Открыть Mini App
- Получить КП
- Рассчитать заказ
- Получить демо
- Попробовать калькулятор
- Запросить КП
- Оставить заявку на расчёт
- Узнать стоимость
- Зарегистрируйся в app
- Используй наш сервис

✅ ALLOWED SOFT CTA:
- Подписаться на @UnitgroupAI
- Сохранить идею
- Написать, какую тему разобрать
- Выбрать тему следующего поста
- Оставить мнение в комментариях
- Написать, какой станок разобрать
- Написать, какая ниша интересна
- Поделиться советом
- Дать рекомендацию
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
    "soft_cta": "Какие технологии вас интересуют?",
    "category": "news|ideas|machinery|materials|trends"
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
    "soft_cta_present": true,
    "no_hard_cta": true,
    "source_attributed": true,
    "category_valid": true
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

## Adaptation by Category

### Категория 1: Новости производства

**Original news:**
"Plastic injection molding sees 25% efficiency gain with AI"

**Rewritten:**
"🎯 Пластиковое литьё: +25% эффективности с AI

Новое исследование показывает что автоматизация:
- Ускорила процесс на четверть
- Снизила брак на 15%
- Сократила трудозатраты

Это важно для всех, кто работает с литьём.

→ Какие технологии вы хотите разобрать?

📰 Источник: Manufacturing News"

### Категория 2: Бизнес-идеи

**Original news:**
"Smart manufacturing reduces furniture production time"

**Rewritten:**
"💡 Ниша: модульная офисная мебель

Компании все больше переходят на удалённую работу,
и спрос на качественную модульную мебель растёт.

Это может быть вашей нишей если:
- Можете инвестировать 1-2 млн
- Готовы работать с корпоративными клиентами
- Владеете ЧПУ или готовы купить

→ Какие ниши вас интересуют?

📰 Источник: Industry Analysis"

### Категория 3: Станки и оборудование

**Original news:**
"Metal fabrication AI improves quote accuracy"

**Rewritten:**
"🔧 Выбираем фрезерный станок для мебели

Новые станки 2026 года могут:
- Обрабатывать сложные формы
- Работать 24/7 без перерывов
- Снижать отходы на 20%

Цена вопроса: 2-5 млн за качественный станок.

→ Какой станок вы хотите разобрать?

📰 Источник: Equipment Review"

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

## Post Structure (Информационный формат)

1. 🔥 Хук с emoji + заголовок (5-10 слов)
2. 📝 Суть (2-3 предложения что произошло)
3. 💡 Практический вывод (почему это важно для производства)
4. ⭐ Действие (что можно сделать на основе этого)
5. → Мягкий CTA (вопрос к аудитории)
6. 📰 Источник (название + URL)
7. 🏭 Категория (новости / идеи / станки / технологии / тренды)

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
