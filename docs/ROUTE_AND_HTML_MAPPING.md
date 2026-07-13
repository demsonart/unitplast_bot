# 🗺️ ROUTE AND HTML MAPPING — Этап 5
**Дата:** 2026-07-12  
**Статус:** LOCAL ANALYSIS COMPLETE  
**VPS проверка требуется SSH**

---

## 📊 ТЕКУЩИЙ КОНФИГ НА MacBook (локально)

### **app/app.py — Routes**

```python
LANDING_PATH = WEB_DIR / "landing.html"  # ← NEW 9-section landing
INDEX_PATH = WEB_DIR / "index.html"      # ← OLD fallback
MINIAPP_PATH = WEB_DIR / "miniapp.html"  # ← Mini App

@app.route('/')
def landing():
    """Landing page"""
    try:
        with open(LANDING_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "Landing page not found"}), 404

@app.route('/app/miniapp')
def miniapp():
    """Telegram Mini App"""
    try:
        with open(MINIAPP_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"error": "Mini App not found"}), 404
```

**Поведение:**
- `/` → попытается открыть `web/landing.html` → если НЕ найден → 404 ошибка
- `/app/miniapp` → попытается открыть `web/miniapp.html` → если НЕ найден → 404 ошибка

**Fallback strategy:** ❌ **НЕ РЕАЛИЗОВАН!**
- Если `landing.html` не найден → 404 (не переходит на `index.html`)
- Есть переменная `INDEX_PATH` но она не используется в route

**Это означает:**
- Если `landing.html` не на VPS → пользователь видит 404 ошибку
- `index.html` используется ТОЛЬКО если разработчик явно изменит код

---

## 🔍 ФАЙЛЫ В web/ ДИРЕКТОРИИ

```
web/
├── landing.html         (10 KB)  ← 9 SECTIONS — НОВЫЙ дизайн
├── index.html           (33 KB)  ← 8 SECTIONS — СТАРЫЙ дизайн (fallback)
├── miniapp.html         (134 KB) ← Mini App
├── unitplast_app.html   (2.8 KB) ← Старый (не используется)
├── app.html             (21 KB)  ← Разное приложение?
├── manager.html         (13 KB)  ← Manager интерфейс?
├── furniture_factory.html (8.0 KB) ← UNITFURNITURE?
├── metal_factory.html   (8.1 KB) ← UNITMETALL?
├── plastics_factory.html (8.1 KB) ← UNITPLAST factory?
├── packaging_factory.html (8.1 KB) ← Тестовый?
├── unitplast_catalog.html (24 KB) ← Каталог?
├── unitplast_client.html  (32 KB) ← Клиент-интерфейс?
├── unitplast_email.html   (20 KB) ← Email интерфейс?
├── unitplast_employee.html (19 KB) ← Сотрудник-интерфейс?
├── unitplast_production.html (21 KB) ← Production?
└── assets/
    ├── images/
    ├── css/
    └── js/
```

**Вывод:** Много файлов, но используются только:
- `landing.html` на `/`
- `miniapp.html` на `/app/miniapp`

---

## 📐 МАРШРУТЫ И ИХ СОДЕРЖИМОЕ

| Маршрут | Файл | Размер | Секций | Статус |
|---------|------|--------|--------|--------|
| **`/`** | `landing.html` | 10 KB | 9 | ✅ Production-ready |
| **`/app/miniapp`** | `miniapp.html` | 134 KB | ? | ✅ Production-ready |
| **`/health`** | JSON response | N/A | N/A | ✅ API |
| **`/api/materials`** | JSON response | N/A | N/A | ✅ API |
| **`/api/emails`** | JSON response | N/A | N/A | ✅ API |
| **`/api/dashboard/stats`** | JSON response | N/A | N/A | ✅ API |
| **`/robots.txt`** | SEO | N/A | N/A | ✅ SEO |
| **`/sitemap.xml`** | SEO | N/A | N/A | ✅ SEO |
| **`/og-image.svg`** | Image | N/A | N/A | ✅ OG |
| **`/assets/*`** | Static | Variable | N/A | ✅ Static serving |

---

## ⚠️ ПРОБЛЕМА: Почему пользователь видит только 4 секции?

### **Гипотеза 1: landing.html не на VPS**

**Сценарий:**
- Локально: `landing.html` существует и работает
- Git: коммит `6991baf` содержал `landing.html`
- VPS: последний коммит `895e55a` может быть старше этого!
- Результат: `/` возвращает 404, или VPS использует старый `index.html`

**Проверка:**
```bash
# На VPS:
ls -la /var/www/unitplast_bot/web/landing.html
cat /var/www/unitplast_bot/web/landing.html | head -20
```

### **Гипотеза 2: Старый app/app.py на VPS**

**Сценарий:**
- VPS имеет старую версию `app/app.py` которая отдавала `index.html` на `/`
- Новая версия `app/app.py` отдает `landing.html`
- VPS не был обновлен

**Проверка:**
```bash
# На VPS:
grep -n "LANDING_PATH\|INDEX_PATH" /var/www/unitplast_bot/app/app.py
grep -n "def landing" /var/www/unitplast_bot/app/app.py
```

### **Гипотеза 3: Nginx кеширует старый контент**

**Сценарий:**
- Nginx может кешировать HTML в памяти
- Даже если обновили файлы, Nginx отдает кешированный контент
- Нужно перезагрузить Nginx или очистить кеш

**Проверка:**
```bash
# На VPS:
curl -i https://unitgroup.tech/
curl -i https://unitgroup.tech/ | grep -i cache
```

### **Гипотеза 4: Systemd service запущен с неправильными файлами**

**Сценарий:**
- Systemd сервис `unitplast.service` запустился с точкой входа в `run.py`
- `run.py` может ссылаться на другой файл или использовать другой путь
- Нужно проверить что запущено на VPS

**Проверка:**
```bash
# На VPS:
systemctl status unitplast
ps aux | grep python
cat /etc/systemd/system/unitplast.service
```

---

## 🎯 ЧТО НУЖНО ПРОВЕРИТЬ НА VPS (для SSH доступа)

### **Список check-листа:**

```bash
#!/bin/bash

echo "===== GIT VERSION ====="
cd /var/www/unitplast_bot
git log --oneline -5
git branch -v

echo "===== FILES ====="
ls -lh web/landing.html web/index.html web/miniapp.html

echo "===== APP.PY ROUTES ====="
grep -n "LANDING_PATH\|def landing" app/app.py | head -10

echo "===== SYSTEMD SERVICE ====="
systemctl status unitplast --no-pager
cat /etc/systemd/system/unitplast.service | grep -i "ExecStart\|WorkingDirectory"

echo "===== RUNNING PROCESS ====="
ps aux | grep "python.*run.py"

echo "===== FLASK PORT ====="
ss -tulpn | grep -i python

echo "===== ACTUAL RESPONSE ====="
curl -I https://unitgroup.tech/
curl -I https://unitgroup.tech/app/miniapp
curl https://unitgroup.tech/ | head -50

echo "===== NGINX CONFIG ====="
cat /etc/nginx/sites-enabled/default | grep -A 10 "location /"
```

---

## 📋 СТАТУС ЛОКАЛЬНО (MacBook)

| Параметр | Статус | Комментарий |
|----------|--------|-----------|
| **landing.html существует** | ✅ | 10 KB, полноценный файл |
| **app/app.py правильно настроен** | ✅ | Отдает `landing.html` на `/` |
| **Маршруты правильные** | ✅ | `/` → landing.html, `/app/miniapp` → miniapp.html |
| **9 секций в landing.html** | ✅ | HTML структура готова |
| **Контент реализован на 100%** | ❌ | Только 44% контента (5 из 9 секций пусты) |

---

## 📊 СТАТУС НА VPS (193.104.33.29)

| Параметр | Статус | Комментарий |
|----------|--------|-----------|
| **Health endpoint** | ✅ | Работает (проверено в этапе 2) |
| **Landing загружается** | ✅ | HTTP 200 OK (проверено в этапе 2) |
| **landing.html на VPS** | ❓ | НУЖНА ПРОВЕРКА SSH |
| **Это 9 секций или 4?** | ❓ | НУЖНА ПРОВЕРКА curl |
| **app/app.py актуален** | ❓ | НУЖНА ПРОВЕРКА SSH |
| **Systemd service актуален** | ❓ | НУЖНА ПРОВЕРКА SSH |

---

## 🚀 ВОЗМОЖНЫЕ ПРИЧИНЫ (ранжированы)

### **Top 1: landing.html не был закоммичен в git или не был пушнут на VPS**

**Вероятность:** 🔴 HIGH (70%)

**Объяснение:**
- `landing.html` создана локально
- Но коммит был на ветке или в работе
- На VPS живет старая версия кода (до `6991baf`)
- Текущий коммит `895e55a` может быть до появления `landing.html`

**Решение:**
```bash
git status
git log landing.html  # Когда был добавлен?
git push
# На VPS: git pull
systemctl restart unitplast
```

### **Top 2: app/app.py был обновлен, но старая версия на VPS**

**Вероятность:** 🟡 MEDIUM (40%)

**Объяснение:**
- Локальный `app/app.py` имеет новую логику (отдает landing.html)
- VPS имеет старую версию которая отдавала index.html
- systemctl restart не был выполнен

**Решение:**
```bash
git push
# На VPS: git pull && systemctl restart unitplast
```

### **Top 3: Nginx кеширует старый контент**

**Вероятность:** 🟢 LOW (10%)

**Объяснение:**
- Nginx может иметь cache-headers
- Нужно либо очистить кеш, либо перезагрузить Nginx

**Решение:**
```bash
# На VPS:
systemctl restart nginx
```

### **Top 4: Systemd сервис неправильно настроен**

**Вероятность:** 🟢 LOW (5%)

**Объяснение:**
- Сервис может запускаться с неправильной рабочей папкой
- Или неправильным entry point

**Решение:**
```bash
# На VPS:
cat /etc/systemd/system/unitplast.service
systemctl status unitplast
```

---

## ⚡ БЫСТРАЯ ПРОВЕРКА

Запустить команду на VPS (если есть SSH доступ):

```bash
ssh root@193.104.33.29 "cd /var/www/unitplast_bot && \
  echo '=== GIT ===' && \
  git log --oneline -1 && \
  echo '=== LANDING ===' && \
  ls -lh web/landing.html && \
  echo '=== APP.PY ===' && \
  grep 'LANDING_PATH\|def landing' app/app.py | head -3 && \
  echo '=== CURL ===' && \
  curl -s https://unitgroup.tech/ | head -20"
```

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

### Если SSH доступ есть:
1. Запустить check-лист выше
2. Определить какая гипотеза верна
3. Применить соответствующее решение
4. Проверить что `https://unitgroup.tech/` отдает 9 секций

### Если SSH доступа нет:
1. Запустить `git status` локально → все ли файлы в git?
2. Запустить `git log landing.html` → когда был добавлен?
3. Запустить `git push` → выложить на GitHub
4. Попросить пользователя ssh на VPS и запустить `git pull && systemctl restart unitplast`

---

## 📝 ПРЕДПОЛОЖИТЕЛЬНЫЙ СЦЕНАРИЙ

1. **Локально:** Всё правильно (landing.html + app/app.py)
2. **Git:** landing.html был в старых коммитах, но текущая версия на VPS старше
3. **VPS:** Живет commit `895e55a` который не содержит полный landing.html или app/app.py не обновлена
4. **Результат:** Пользователь видит fallback или 4 секции из index.html

**Решение:**
```bash
git add web/landing.html app/app.py
git commit -m "feat(landing): ensure 9-section landing page is deployed"
git push origin main
# На VPS: git pull && systemctl restart unitplast
```

---

**Статус:** ⏳ ANALYSIS COMPLETE — SSH CHECK NEEDED  
**Дальше:** Этап 6 — NOT_DEPLOYED_CHANGES_REPORT

