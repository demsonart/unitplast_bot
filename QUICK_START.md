# 🚀 QUICK START — 5 минут до запуска

## ШАГ 1: Токены (1 минута)

Получите в Telegram:

```
@BotFather → /newbot → скопируйте TOKEN
@UnitgroupAI → /getid → скопируйте CHANNEL_ID
@userinfobot → скопируйте ADMIN_ID
```

## ШАГ 2: .env файл (1 минута)

```bash
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvWXYZ
TELEGRAM_CHANNEL_ID=-1001234567890
TELEGRAM_ADMIN_ID=123456789
DRY_RUN=true
REQUIRE_APPROVAL=true
EOF
```

## ШАГ 3: Установить зависимости (2 минуты)

```bash
pip install feedparser requests
```

## ШАГ 4: ЗАПУСТИТЬ! (1 минута)

```bash
python3 scripts/full_deployment.py
```

---

## ✅ Результат

```
✅ Картинки загружены (из RSS или AI-сгенерированы)
✅ Эмодзи оптимизированы (минимально)
✅ Превью отправлены админу (для одобрения)
✅ Логирован весь процесс
✅ Готовно к публикации в @UnitgroupAI
```

---

## 📱 Что происходит дальше?

1. **Админ видит превью в Telegram** (5 постов)
2. **Админ нажимает Approve** (для каждого поста)
3. **После одобрения:** Меняем `DRY_RUN=false`
4. **Запускаем еще раз:** `python3 scripts/full_deployment.py`
5. **Посты опубликуются в @UnitgroupAI** ✅

---

## 📚 Полная документация

- `docs/FINAL_5_POSTS_OPTIMIZED.md` — 5 готовых постов
- `docs/COMPLETE_SYSTEM_README.md` — Полная инструкция
- `docs/IMPLEMENTATION_COMPLETE_SUMMARY.md` — Обзор всей системы

---

## 🆘 Проблемы?

**Ошибка: "TELEGRAM_BOT_TOKEN не установлен"**
```bash
cat .env | grep TELEGRAM_BOT_TOKEN
# Должно что-то вывести
```

**Ошибка: "Картинок не найдено"**
```
Нормально! Система перейдет на AI-генерацию.
Нужен OPENAI_API_KEY в .env
```

**Никакие посты не публикуются?**
```
Это правильно! DRY_RUN=true означает что посты НЕ отправляются.
Это режим тестирования.
```

---

## 🎯 Полный процесс

```
5 МИНУТ ПЕРВЫЙ ЗАПУСК:
├─ pip install feedparser requests
├─ Настроить .env токены
├─ python3 scripts/full_deployment.py
└─ ✅ Готово!

ДАЛЬШЕ:
├─ Одобрить посты в Telegram (админ)
├─ Поменять DRY_RUN=false
├─ Запустить еще раз
└─ 🎉 Посты в канале!
```

---

**Система готова. Отправляем!** 🚀
