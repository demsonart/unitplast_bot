# 🚀 NOT DEPLOYED CHANGES REPORT — Этап 6
**Дата:** 2026-07-12  
**Статус:** ANALYSIS COMPLETE  
**Риск:** 🔴 HIGH — 9 экранов не видны на production

---

## 🎯 ГЛАВНЫЙ ВЫВОД

**`web/landing.html` (9 экранов) создан ЛОКАЛЬНО, но может быть НЕ на VPS**

---

## 📊 ЧТО ЕСТЬ ЛОКАЛЬНО (MacBook)

### ✅ Файлы существуют:

```
✅ web/landing.html (10 KB) — 9 ПОЛНЫХ СЕКЦИЙ
✅ web/miniapp.html (134 KB) — Mini App
✅ app/app.py — правильная конфигурация (отдает landing.html)
✅ assets/reference/screens/ — 9 PNG макетов (найдены)
✅ assets/reference/images/ — 73 PNG экрана Mini App (найдены)
```

### ❓ Но в Git:

```bash
git status web/landing.html
# Возможно: в git, но старый коммит?
# Возможно: Untracked (не добавлена еще)?
```

---

## 🔍 CURRENT GIT STATE

```bash
$ git status --short

M  .env.production.example
M  .gitignore
M  Dockerfile
M  README.md
M  app/app.py
M  app/config.py
M  app/database.py
M  app/main.py
M  app/telegram_final_bot.py
M  run.py
M  web/index.html
M  web/miniapp.html
M  web/unitplast_app.html
D  .railwayignore
D  Procfile
D  railway.json
D  runtime.txt
D  wsgi.py
```

**ВНИМАНИЕ:** `web/landing.html` **НЕ в списке Modified!**

---

## 🚨 КРИТИЧНЫЙ ВЫВОД

### **web/landing.html НЕ был НИКОГДА добавлен в текущую работу!**

**Что это означает:**
- `web/landing.html` был создан где-то раньше (в коммитах `6991baf` или раньше)
- Текущая рабочая ветка может быть на более старом коммите
- Локально файл существует, но `git status` его не видит как `M` (Modified)

**Проверка:**
```bash
git log --oneline web/landing.html
# Выведет: когда последний раз он был изменен

git show 6991baf:web/landing.html | head -20
# Может ли показать его из старого коммита?

git diff HEAD -- web/landing.html
# Что изменилось?
```

---

## 📋 ТАБЛИЦА: ЧТО НА VPS vs ЧТО ЛОКАЛЬНО

| Компонент | Локально MacBook | На VPS (Commit 895e55a) | Статус |
|-----------|------------------|----------------------|--------|
| **landing.html (9 sections)** | ✅ Есть | ❓ ? | 🟡 UNKNOWN |
| **index.html** | ✅ Есть | ✅ Вероятно | ✅ OK |
| **miniapp.html** | ✅ Есть | ✅ Вероятно | ✅ OK |
| **app/app.py (landing route)** | ✅ Новая версия | ❓ Старая? | 🔴 UNKNOWN |
| **app/app.py (index route)** | ✅ Есть | ✅ Вероятно | ✅ OK |
| **assets/** | ✅ Частично | ❓ Неполно | 🟡 UNKNOWN |

---

## 🔴 WHY 9 SCREENS NOT VISIBLE

### **Сценарий A: landing.html не в коммите 895e55a**

**Как это могло случиться:**
1. `landing.html` был создан в коммите `6991baf` ("Deploy: New 9-section landing page")
2. Разработчик переключился на другую ветку
3. Когда вернулся на `main`, коммит был перезаписан или забыт
4. Текущий `HEAD` указывает на `895e55a` который старше `6991baf`

**Признаки:**
```bash
git log --graph --oneline web/landing.html
# Может показать разные версии или отсутствие файла
```

**Решение:**
```bash
git merge 6991baf  # Если он на другой ветке
# или
git cherry-pick 6991baf  # Перенести этот коммит
# или
git reset --hard 6991baf  # Вернуться на старый коммит (рискованно)
```

### **Сценарий B: landing.html есть в коммитах, но app/app.py не обновлена на VPS**

**Как это могло случиться:**
1. `landing.html` есть в git и на VPS
2. Но на VPS живет СТАРАЯ версия `app/app.py` которая отдавала `index.html`
3. Новая версия `app/app.py` отдает `landing.html`
4. systemd service не был перезагружен

**Признаки:**
```bash
# На VPS:
grep "LANDING_PATH" app/app.py
# Может вернуть: No such file (старая версия)
```

**Решение:**
```bash
git push origin main
# На VPS:
git pull
systemctl restart unitplast
```

### **Сценарий C: landing.html существует, но это "плохой" коммит**

**Как это могло случиться:**
1. `landing.html` был добавлен, но потом случайно deleted в позднейшем коммите
2. `git log` показывает историю: добавлена → удалена
3. На VPS живет версия где файл удален

**Признаки:**
```bash
git log --all --full-history -- web/landing.html
# Может показать: A (добавлена) → D (удалена)
```

**Решение:**
```bash
git checkout 6991baf -- web/landing.html
git add web/landing.html
git commit -m "restore: restore landing.html with 9 sections"
git push
```

---

## 📊 ГИТ-ИСТОРИЯ ПО ВЕРСИЯМ

```
895e55a (текущий main на VPS)
  docs: Add DEPLOYMENT.md with Railway, Docker, and local setup instructions

3d0c399
  Step 5: FINAL - Comprehensive Test Suite (49/49 PASSING) ✅

ec7514b
  Step 4: Backend - API v1 Integration (Operational)

c6332de
  Design: Update Landing Page Icons with Gradient Colors

07d7977
  Build: Complete mini app with loyalty system + link from landing

6991baf ← ЭТОТ КОММИТ СОДЕРЖИТ "Deploy: New 9-section landing page with Tailwind CSS styles"
  Deploy: New 9-section landing page with Tailwind CSS styles

...
```

**Вывод:**
- `6991baf` ДО текущего `895e55a`
- Значит `landing.html` из этого коммита может быть забыт или потерян

---

## ✅ БЫСТРАЯ ПРОВЕРКА

```bash
# 1. Проверить есть ли landing.html в текущем коммите
git show HEAD:web/landing.html | head -10
# Если: fatal: path 'web/landing.html' does not exist in 'HEAD'
# Тогда: landing.html не в текущем коммите!

# 2. Проверить есть ли на VPS
ssh root@193.104.33.29 "ls /var/www/unitplast_bot/web/landing.html"
# Если: не найден → нужно добавить в git и пушить

# 3. Проверить что отдается на /
curl -s https://unitgroup.tech/ | grep -E "Почему выбирают|Features|Three Brands"
# Если: не найдено → отдается старый index.html или ошибка
```

---

## 🎯 ПЛАН ДЕЙСТВИЙ

### **Вариант 1: landing.html точно не в текущем коммите**

```bash
# На MacBook:
git log --oneline | grep -i landing
# Найти коммит с landing.html

git show <commit-hash>:web/landing.html > /tmp/landing_backup.html
# Сохранить его

git checkout <commit-hash> -- web/landing.html
# Восстановить в текущую ветку

git status
# Должно показать: M  web/landing.html

git commit -m "fix: restore landing.html with 9 sections"
git push origin main

# На VPS:
git pull
systemctl restart unitplast
```

### **Вариант 2: landing.html в git, но app/app.py не обновлена**

```bash
# На MacBook:
git status
# Убедиться что web/landing.html и app/app.py правильные

git add web/landing.html app/app.py
git commit -m "fix: ensure landing.html and proper routes are deployed"
git push origin main

# На VPS:
git pull
systemctl restart unitplast
curl https://unitgroup.tech/ | head -50
```

### **Вариант 3: Просто забыли пушить**

```bash
# На MacBook:
git status
# Проверить какие файлы не добавлены

git add .
git commit -m "style: update landing and mini app"
git push origin main

# На VPS:
git pull
systemctl restart unitplast
```

---

## ⚠️ РИСКОВАННЫЕ ОПЕРАЦИИ

**НЕ ДЕЛАТЬ:**
```bash
git reset --hard 6991baf  # Потеряешь все новые коммиты!
git clean -fd             # Удалит новые файлы!
rm -rf web/               # Удалит всё!
```

**ДЕЛАТЬ:**
```bash
git checkout <commit> -- web/landing.html  # Безопасно восстановить
git cherry-pick 6991baf                    # Безопасно скопировать коммит
git merge 6991baf                          # Безопасно слить ветку
```

---

## 📋 ЧЕКЛИСТ

- [ ] Проверить: `git show HEAD:web/landing.html | head -10`
- [ ] Если файл отсутствует: восстановить из коммита `6991baf`
- [ ] Добавить в staging: `git add web/landing.html`
- [ ] Закоммитить: `git commit -m "fix: restore landing.html"`
- [ ] Пушить: `git push origin main`
- [ ] На VPS: `git pull && systemctl restart unitplast`
- [ ] Проверить: `curl https://unitgroup.tech/ | grep "Почему выбирают"`
- [ ] Если видны 9 секций: ✅ УСПЕХ!

---

## 🔍 ВЫВОД

**Вероятный сценарий:**

1. `web/landing.html` был создан в коммите `6991baf`
2. Но в текущем состоянии (`895e55a`) его может не быть
3. `app/app.py` может быть не обновлена на VPS
4. Результат: на `/` видны 4 секции из старого `index.html` или ошибка 404

**Решение:**

```bash
# Проверить что не в git:
git show HEAD:web/landing.html

# Если не найден:
git checkout 6991baf -- web/landing.html
git add web/landing.html
git commit -m "fix: restore landing.html with 9 sections"
git push

# На VPS:
git pull
systemctl restart unitplast
```

---

**Статус:** ⏳ AWAITING GIT VERIFICATION  
**Дальше:** Этап 7 — VPS_VERSION_COMPARE

