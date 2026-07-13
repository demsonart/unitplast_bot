# 🚀 ПОЛНАЯ СИСТЕМА @UnitgroupAI С КАРТИНКАМИ
## Инструкция по использованию

**Версия:** 2.0 — С интеграцией изображений  
**Дата:** July 14, 2026  
**Статус:** ✅ ГОТОВО К РАЗВЕРТЫВАНИЮ

---

## 📋 ЧТО БЫЛО СДЕЛАНО?

### ✅ Решены все проблемы

| Проблема | Решение |
|----------|---------|
| Картинок нет в постах | Парсинг из RSS + AI-генерация как fallback |
| Перегруз эмодзи | Оптимизация: только для разделения/подчеркивания |
| Источники вместо хештегов | Убрано, добавлены 7-10 русских хештегов |
| HTML теги и спецсимволы | Убрано, только чистый текст |
| Посты слишком сухие | Расширены до 2000-2400 слов с примерами |

### ✅ Готовые компоненты

```
unitplast_bot/
├── docs/
│   ├── FINAL_5_POSTS_OPTIMIZED.md          ← 5 постов готовых к публикации
│   ├── POSTS_WITH_IMAGES_AND_PROMPTS.md    ← С AI-промптами
│   ├── COMPLETE_SYSTEM_README.md           ← ЭТА ИНСТРУКЦИЯ
│   └── UNITGROUPAI_MEDIA_STRATEGY_2026.md  ← Стратегия
│
├── scripts/
│   ├── media_integration.py                ← Парсинг картинок + AI-генерация
│   ├── telegram_publisher.py               ← Публикация в Telegram
│   ├── full_deployment.py                  ← Полный процесс (4 шага)
│   └── (другие)
│
├── data/
│   ├── posts_prepared.json                 ← Подготовленные посты
│   ├── posts_with_images.json              ← С картинками
│   ├── media_cache/                        ← Кэш изображений
│   ├── publication_results.json            ← Результаты публикации
│   └── (другие)
│
└── logs/
    └── deployment.log                       ← Логи развертывания
```

---

## 🎯 КАК ИСПОЛЬЗОВАТЬ СИСТЕМУ?

### Вариант 1: ЗАПУСТИТЬ ВСЕ СРАЗУ (Рекомендуется)

```bash
# 1. Установить зависимости
pip install feedparser requests openai

# 2. Настроить .env файл
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvWXYZ
TELEGRAM_CHANNEL_ID=-1001234567890
TELEGRAM_ADMIN_ID=123456789
DRY_RUN=true
REQUIRE_APPROVAL=true
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx  # Опционально, для AI-генерации
EOF

# 3. Запустить полный процесс
python3 scripts/full_deployment.py
```

**Что произойдет:**
1. ✅ Подготовка контента (5 постов)
2. ✅ Интеграция медиа (парсинг картинок + AI-генерация)
3. ✅ Оптимизация эмодзи
4. ✅ Отправка превью админу (если REQUIRE_APPROVAL=true)
5. ⏳ Ожидание одобрения админа
6. 🚀 Публикация в @UnitgroupAI (после одобрения)

---

### Вариант 2: ЗАПУСТИТЬ ОТДЕЛЬНЫЕ ШАГИ

#### Шаг 1: Интеграция картинок
```bash
python3 scripts/media_integration.py
```

**Результат:** `data/posts_with_images.json`  
**Время:** 2-5 минут (зависит от источников)

**Что происходит:**
- Парсит RSS-фиды источников (IndustryWeek, Statista и т.д.)
- Скачивает изображения в `data/media_cache/`
- Если изображение не найдено — генерирует через DALL-E (если есть API ключ)
- Сохраняет пути к картинкам в JSON

#### Шаг 2: Публикация в Telegram
```bash
python3 scripts/telegram_publisher.py
```

**Результат:** `data/publication_results.json`  
**Режим:** DRY_RUN=true и REQUIRE_APPROVAL=true (безопасно)

**Что происходит:**
- Загружает посты с картинками
- Отправляет превью админу
- Ждет одобрения перед публикацией
- Логирует каждый шаг

---

## ⚙️ КОНФИГУРАЦИЯ

### Обязательные переменные в .env:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvWXYZ
TELEGRAM_CHANNEL_ID=-1001234567890           # ID канала @UnitgroupAI
TELEGRAM_ADMIN_ID=123456789                  # ID админа для одобрения

# Безопасность
DRY_RUN=true                  # true = посты НЕ публикуются
REQUIRE_APPROVAL=true         # true = нужно одобрение админа
```

### Опциональные переменные:

```bash
# Для AI-генерации картинок
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Для отладки
LOG_LEVEL=INFO
DEBUG=false
```

---

## 📸 КАК РАБОТАЕТ ПАРСИНГ КАРТИНОК?

### Primary: Парсинг из источников (Экономит токены!)

```
RSS-фид источника (напр. IndustryWeek)
       ↓
Поиск записей по ключевым словам
       ↓
Извлечение image URL из <media_content>
       ↓
Скачивание и кэширование локально
       ↓
✅ Картинка найдена!
```

**Преимущества:**
- Экономит токены (не нужна AI-генерация)
- Реальные фотографии (качество выше)
- Быстрее

**Источники, из которых парсим:**
- IndustryWeek
- PlasticsToday
- Statista
- Manufacturing.net
- Google Images (HTML парсинг)

### Fallback: AI-генерация (Если парсинг не дал результата)

```
Изображение не найдено в источнике
       ↓
Использование AI-промпта из поста
       ↓
Вызов DALL-E API (требует OPENAI_API_KEY)
       ↓
Генерация новой картинки (1-2 минуты)
       ↓
Кэширование локально
       ↓
✅ Картинка сгенерирована!
```

**Примеры AI-промптов:**

Post #1 (AI Quality Control):
```
"Industrial factory conveyor line with AI computer vision system. 
Red laser inspection lines scanning wooden furniture parts. 
Close-up of AI camera detecting defects in wood surfaces. 
Quality control monitoring screen showing 95% accuracy..."
```

Post #5 (Price Forecast):
```
"Financial chart showing rising price trend. Red upward arrow 
line graph from July 2026 to December 2026. Y-axis shows prices 
in rubles 95-130..."
```

---

## 🛡️ БЕЗОПАСНОСТЬ И КОНТРОЛЬ

### DRY_RUN=true (Рекомендуется для тестирования)

Что происходит:
```
✅ Посты подготавливаются
✅ Картинки парсятся/генерируются
✅ Превью отправляется админу (для просмотра)
❌ ПОСТОВ НЕ ОТПРАВЛЯЕТСЯ В КАНАЛ
❌ Реальная публикация не происходит
```

Включить реальную публикацию:
```bash
# В .env
DRY_RUN=false

# ⚠️  ВНИМАНИЕ! Только после тестирования!
```

### REQUIRE_APPROVAL=true (Обязательно)

Что происходит:
```
📋 Превью поста → Админу в личку
⏳ Админ видит как выглядит пост
👁️  Админ может одобрить или отклонить
❌ Пост НЕ публикуется автоматически
✅ Только после явного одобрения
```

Одобрение от админа:
```
В Telegram личке админа:
[ПРЕВЬЮ ПОСТА]
[Approve] [Reject] кнопки

Админ нажимает [Approve] → пост готов
Админ нажимает [Reject] → пост удаляется
```

---

## 📊 ПРИМЕРЫ РЕЗУЛЬТАТОВ

### После запуска full_deployment.py:

**Логи процесса:**
```
2026-07-14 14:30:00 🚀 ЗАПУСК ПОЛНОГО ПРОЦЕССА
2026-07-14 14:30:05 🎬 ШАГ 1: ПОДГОТОВКА КОНТЕНТА
2026-07-14 14:30:10 ✅ Подготовлено постов: 5
2026-07-14 14:30:15 🎬 ШАГ 2: ИНТЕГРАЦИЯ МЕДИА
2026-07-14 14:30:20 📡 Парсим RSS: https://www.industryweek.com/feed
2026-07-14 14:30:45 ✅ Найдена картинка: https://...image.jpg
2026-07-14 14:31:00 📦 Картинка сохранена: data/media_cache/post_001.jpg
2026-07-14 14:31:30 🎬 ШАГ 3: ОПТИМИЗАЦИЯ ЭМОДЗИ
2026-07-14 14:31:35 ✅ Оптимизировано 5 постов
2026-07-14 14:31:45 🎬 ШАГ 4: ПУБЛИКАЦИЯ В TELEGRAM
2026-07-14 14:32:00 📨 Превью отправлено админу
2026-07-14 14:32:05 ✅ ВЕСЬ ПРОЦЕСС ЗАВЕРШЕН УСПЕШНО!
```

**Файл результатов:**
```json
[
  {
    "title": "🔧 AI КОНТРОЛИРУЕТ КАЧЕСТВО МЕБЕЛИ",
    "status": "pending_approval",
    "has_image": true,
    "image_path": "data/media_cache/post_001.jpg",
    "dry_run": true
  },
  ...
]
```

---

## 🔍 ПРОВЕРКА СТАТУСА

### Проверить что посты подготовлены:
```bash
ls -la data/posts_*.json
# Должны быть файлы:
# - posts_prepared.json
# - posts_with_images.json
```

### Проверить что картинки загружены:
```bash
ls -la data/media_cache/
# Должны быть файлы:
# - post_001.jpg
# - post_002.jpg
# - post_003.jpg
# - post_004.jpg
# - post_005.jpg
```

### Проверить логи:
```bash
tail -100 logs/deployment.log
# Должны видеть весь процесс deployment
```

### Проверить что Telegram Bot работает:
```bash
# Отправить тестовое сообщение
curl -X POST https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage \
  -d chat_id=${TELEGRAM_ADMIN_ID} \
  -d text="Test from deployment"

# Должно прийти в личку админу
```

---

## ⚠️ ЧАСТЫЕ ОШИБКИ И РЕШЕНИЯ

### Ошибка: "TELEGRAM_BOT_TOKEN не установлен"
```bash
# Решение: добавить в .env
echo "TELEGRAM_BOT_TOKEN=ххх" >> .env
source .env
```

### Ошибка: "Картинок не найдено в RSS"
```
Это нормально! Система перейдет на AI-генерацию.
Требуется OPENAI_API_KEY в .env
```

### Ошибка: "feedparser не установлен"
```bash
pip install feedparser
```

### Ошибка: "Превью не отправился админу"
```bash
# Проверить TELEGRAM_ADMIN_ID
echo $TELEGRAM_ADMIN_ID
# Должно быть число, например: 123456789
```

---

## 🎯 ПОЛНЫЙ ПРОЦЕСС ПОШАГОВО

### День 1: Подготовка

```bash
# 1. Настроить .env с токенами
# 2. Установить зависимости
pip install feedparser requests

# 3. Запустить интеграцию картинок
python3 scripts/media_integration.py

# 4. Проверить результаты
ls data/posts_with_images.json
ls data/media_cache/
```

### День 2: Тестирование

```bash
# 1. Запустить publisher в DRY_RUN режиме
export DRY_RUN=true
export REQUIRE_APPROVAL=true
python3 scripts/telegram_publisher.py

# 2. Проверить превью в Telegram администратора
# (должно прийти сообщение с превью первого поста)

# 3. Проверить логи
tail logs/deployment.log
```

### День 3: Одобрение

```
Администратор в Telegram:
[Видит превью поста]
[Нажимает Approve] ← ОДИН РАЗ НА ПОСТ

После одобрения:
✅ Пост готов к публикации
```

### День 4: Публикация (после одобрения всех постов)

```bash
# 1. Перейти в production режим
export DRY_RUN=false

# 2. Запустить publisher
python3 scripts/telegram_publisher.py

# 3. Посты начнут публиковаться в @UnitgroupAI
# 4. Проверить канал
```

---

## 📱 ПРИМЕРЫ ПОСТОВ В КАНАЛЕ

После публикации в @UnitgroupAI посты будут выглядеть так:

```
[ИЗОБРАЖЕНИЕ: Промышленная камера AI]

🔧 AI КОНТРОЛИРУЕТ КАЧЕСТВО МЕБЕЛИ

На европейских мебельных фабриках произошла революция...

📊 Результаты фабрик:

95-99% точность (люди ошибаются в 10% случаев)
Скорость: 5000+ деталей в день...

[И так далее...]

Вы уже думали о контроле качества? Какой брак у вас сейчас?

#мебель #производство #AI #автоматизация #качество
```

---

## 🔧 ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ

### Архитектура системы:

```
┌─────────────────────────────────────────┐
│  FULL_DEPLOYMENT.py                     │
│  (Master Script)                        │
└────────────┬────────────────────────────┘
             │
    ┌────────┴─────────┬─────────────┬────────────┐
    │                  │             │            │
    ▼                  ▼             ▼            ▼
┌─────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ Prepare     │ │Media         │ │Optimize  │ │Publish to    │
│ Content     │ │Integration   │ │Emojis   │ │Telegram      │
│             │ │              │ │          │ │              │
│ CSV → JSON  │ │ RSS Parse    │ │ Regex   │ │ sendPhoto    │
│             │ │ AI Generate  │ │ Filter  │ │ sendMessage  │
│             │ │ Cache Images │ │         │ │              │
└─────────────┘ └──────────────┘ └──────────┘ └──────────────┘
    │               │                │             │
    └───────────────┴────────────────┴─────────────┘
                        │
                        ▼
            ┌────────────────────────┐
            │  data/*.json files     │
            │  media_cache/images    │
            │  logs/deployment.log   │
            └────────────────────────┘
```

### Зависимости:

```
- Python 3.8+
- feedparser (RSS парсинг)
- requests (HTTP запросы)
- openai (опционально, для AI-генерации)
```

### Файлы конфигурации:

```
.env                    ← Переменные окружения
data/media_sources.yaml ← Источники RSS
data/content_categories.yaml ← Категории контента
```

---

## ✅ ИТОГОВЫЙ ЧЕКЛИСТ

Перед публикацией:

- [ ] Установлены все зависимости (`pip install ...`)
- [ ] Настроен .env с токенами
- [ ] Запущен `full_deployment.py`
- [ ] Картинки загружены в `data/media_cache/`
- [ ] Превью отправлены админу
- [ ] Админ одобрил все посты
- [ ] DRY_RUN=false (для реальной публикации)
- [ ] Логи проверены (нет ошибок)
- [ ] Посты появились в @UnitgroupAI

---

## 🚀 ГОТОВО К ЗАПУСКУ!

```bash
# ФИНАЛЬНАЯ КОМАНДА:
python3 scripts/full_deployment.py
```

**Все системы: GO!** 🎉

---

**Версия документа:** 2.0  
**Последнее обновление:** July 14, 2026  
**Автор:** Claude Code  
**Статус:** ✅ PRODUCTION READY
