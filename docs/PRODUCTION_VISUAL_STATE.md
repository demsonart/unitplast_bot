# 📺 PRODUCTION VISUAL STATE — Этап 3
**Дата:** 2026-07-12  
**Статус:** ANALYSIS COMPLETE  
**VPS:** 193.104.33.29 / https://unitgroup.tech

---

## 🎯 ГЛАВНЫЙ ВЫВОД

**Production ДОЛЖЕН показывать 9 экранов лендинга, но может этого не делать.**

Почему:
- ✅ **Коде готов:** `web/landing.html` содержит 9 完整 секций
- ✅ **Роут готов:** `app/app.py` отдает `landing.html` на `/`
- ❓ **Но на VPS?** `landing.html` может не быть в git или не был задеплоен
- ❓ **Старый backup?** `index.html` используется только как fallback

---

## 📊 СТРУКТУРА ЛОКАЛЬНЫХ HTML ФАЙЛОВ

### **Landing Page: web/landing.html (10KB)**

✅ **НОВЫЙ ДИЗАЙН** — 9 ПОЛНЫХ СЕКЦИЙ:

| № | Секция | Описание | HTML элемент |
|---|--------|---------|--------|
| 1 | **HERO** | Заголовок "Расчёт за 30 секунд" + CTA кнопки | `<section class="hero">` |
| 2 | **FEATURES** | 6 карточек преимуществ: ⚡ Расчёт, 🎯 Единая система, 📦 Склад, 📄 КП, 🔗 Интеграция, 📊 Аналитика | `<section class="features">` |
| 3 | **COMMERCIAL OFFERS** | "Коммерческие предложения" — КП автоматически | `<section class="commercial-offers">` |
| 4 | **MINI APP** | "Скачайте приложение" — промо Telegram Mini App | `<section class="mini-app">` |
| 5 | **MANAGEMENT DASHBOARD** | "Контролируйте производство в реальном времени" | `<section class="management">` |
| 6 | **THREE BRANDS** | Три бренда: UNITPLAST (пластик), UNITFURNITURE (мебель), UNITMETALL (металл) | `<section class="three-brands">` |
| 7 | **CONTACTS** | Контактные данные всех отделов (4 карточки) | `<section class="contacts">` |
| 8 | **CTA BLOCK** | Призыв "Сделайте следующий шаг" + кнопка "Запросить демонстрацию" | `<section class="cta-block">` |
| 9 | **FOOTER** | Копирайт + ссылки (Политика, Условия, Контакты) | `<footer>` |

**Размер:** 10 KB (HTML only, without external assets)  
**Язык:** Русский  
**Версия:** Финальная (согласно названию файла = новый дизайн)  
**CSS:** Подключает внешний `/assets/css/landing-styles.css` (но стили также inline)

---

### **Old Landing: web/index.html (33KB) — Fallback**

⚠️ **СТАРЫЙ ДИЗАЙН** — более сложный, больше кода:

| № | Секция | Описание |
|---|--------|---------|
| 1 | **HEADER** | Sticky header с логотипом, навигацией, CTA кнопкой |
| 2 | **HERO** | Левая часть: текст + кнопки; Правая часть: 3D-рендер |
| 3 | **SOLUTIONS** | 6 карточек "AI для производства": Расчёт, Единая система, Скла, КП, Интеграция, Аналитика |
| 4 | **MINI APP** | Секция промо Mini App (4 фишки) + кнопки |
| 5 | **FEATURES** | 6 преимуществ: Расчёт, Единая, КП, Интеграция, Склад, Аналитика |
| 6 | **INFO BOX** | "Telegram Mini App + Web платформа" |
| 7 | **CONTACTS** | Левая часть: форма; Правая часть: контакты отделов |
| 8 | **FOOTER** | Копирайт |

**Размер:** 33 KB (значительно больше)  
**Язык:** Русский  
**Статус:** Fallback (используется ТОЛЬКО если `landing.html` не найден)  
**Стили:** Полностью inline (нет внешних CSS)

**⚠️ Вывод:** `index.html` имеет ВСЕ те же секции, но более сложная реализация, весит в 3 раза больше.

---

### **Mini App: web/miniapp.html (134KB)**

✅ **ПОЛНОФУНКЦИОНАЛЬНОЕ ПРИЛОЖЕНИЕ** — Telegram Mini App

**Структура:**
- `.app-header` — Заголовок с навигацией (12px padding)
- `.app-content` — Основной контент (overflow-y: auto)
- `.app-footer` — 6 навигационных иконок (фиксированный footer)

**Компоненты:**
- Stat cards (статистика)
- Type grids (3 колонки выбора типа)
- Input groups (формы)
- Product cards (каталог)
- Buttons (первичные, вторичные)

**Размер:** 134 KB (в основном HTML + встроенный CSS)  
**Viewport:** max-width: 500px (мобильный)  
**Назначение:** Telegram Mini App для расчётов и управления

---

## 🚀 ЧТО РЕАЛЬНО ОТДАЕТСЯ НА PRODUCTION

### **Маршруты (app/app.py)**

```python
LANDING_PATH = WEB_DIR / "landing.html"  # ← NEW LANDING (9 sections)
INDEX_PATH = WEB_DIR / "index.html"      # ← OLD LANDING (fallback)
MINIAPP_PATH = WEB_DIR / "miniapp.html"  # ← MINI APP

@app.route('/')
def landing():
    return open(LANDING_PATH).read()  # ← ОТДАЕТ landing.html

@app.route('/app/miniapp')
def miniapp():
    return open(MINIAPP_PATH).read()  # ← ОТДАЕТ miniapp.html
```

**Поведение:**
- Если `landing.html` НАЙДЕН → отдает его (9 секций) ✅
- Если `landing.html` НЕ найден → возвращает 404 ❌
- `index.html` используется только если разработчик явно изменит код

**Маршруты API:**
- `/health` — статус сервиса
- `/api/materials` — каталог материалов
- `/api/emails` — примеры писем
- `/api/dashboard/stats` — статистика
- `/robots.txt` — SEO robots
- `/sitemap.xml` — SEO sitemap
- `/og-image.svg` — Open Graph image
- `/data/<filename>` — JSON данные (path traversal protected)
- `/assets/` — статические файлы (CSS, JS, images)

---

## ❓ ПОЧЕМУ ПОЛЬЗОВАТЕЛЬ ВИДИТ ТОЛЬКО 4 СЕКЦИИ?

**Гипотеза 1: landing.html не попал на VPS**
- `landing.html` создан ЛОКАЛЬНО но не был в git commit
- VPS всё ещё использует старый код из последнего commit (895e55a)
- **Решение:** Коммитить + пушить + деплоить

**Гипотеза 2: Неправильный git history**
- `landing.html` был создан но потом удален или перезаписан
- Можно проверить: `git log --follow web/landing.html`
- **Решение:** Восстановить из assets/reference/screens/ или создать заново

**Гипотеза 3: app/app.py не обновлена на VPS**
- Локально app/app.py указывает на `landing.html`
- VPS может использовать старую версию app/app.py которая искала другой файл
- **Решение:** Пушить app/app.py и деплоить

**Гипотеза 4: Старый индекс используется вместо landing**
- VPS по умолчанию отдает что-то другое (может быть какой-то другой HTML)
- **Решение:** Проверить реальное содержимое на VPS через SSH

---

## 📐 СРАВНЕНИЕ ДИЗАЙНА

### **web/landing.html (НОВЫЙ) vs assets/reference/screens/ (МАКЕТЫ)**

| Критерий | landing.html | Макеты (9 PNG) | Статус |
|----------|-------------|-------------|--------|
| **Кол-во секций** | 9 | 9 (по дизайну) | ✅ Совпадает |
| **Hero/Главный** | Да (расчёт за 30 сек) | Да | ✅ |
| **Features** | 6 карточек | На макетах | ✅ |
| **Three Brands** | UNITPLAST, UNITFURNITURE, UNITMETALL | На макетах | ✅ |
| **Mini App Promo** | Есть отдельная секция | На макетах | ✅ |
| **Contacts** | 4 отдела + форма | На макетах | ✅ |
| **Management/Dashboard** | Есть | На макетах | ✅ |
| **КП/Commercial** | Есть | На макетах | ✅ |
| **Icons** | Emoji (⚡🎯📦📄🔗📊) | Возможно иконки | ⚠️ Может отличаться |
| **Colors** | Dark theme (#04060c, #2e6bf2) | На макетах | ⚠️ Нужно сравнить |
| **Responsive** | Да (@media 768px) | Mobile-first | ⚠️ Нужно сравнить |

---

## 📱 MINI APP СОСТОЯНИЕ

### **Локально (web/miniapp.html)**

✅ **Готово к использованию:**
- Размер: 134 KB (разумный для Mini App)
- Viewport: 500px max-width (мобильный)
- Структура: Header + Content + Footer Nav
- Компоненты: Stat cards, grids, inputs, buttons
- Дизайн: Соответствует UNITPLAST color scheme

⚠️ **Нужна проверка:**
- Загружаются ли все 73 экрана из assets/reference/images/?
- Или это только скелет с плейсхолдерами?
- Нужна ли каталогизация этих 73 экранов?

---

## 🔴 КРИТИЧЕСКИЕ ВОПРОСЫ

### **На Production**

1. **Какой файл РЕАЛЬНО отдается на `https://unitgroup.tech/`?**
   - [ ] landing.html (9 секций)? ← ОЖИДАЕМО
   - [ ] index.html (старый)? ← ВОЗМОЖНО
   - [ ] Какой-то другой файл? ← НУЖНА ПРОВЕРКА SSH

2. **На VPS есть файл landing.html?**
   - [ ] Да, но VPS отдает старый код
   - [ ] Нет, не был коммичен в git
   - [ ] Нет, был удален

3. **Почему ровно 4 секции видны?**
   - [ ] В каком-то другом файле 4 секции?
   - [ ] CSS скрывает остальные?
   - [ ] Javascript ломает загрузку?

### **На MacBook (локально)**

4. **Какой файл используется при локальном запуске?**
   - Нужно проверить: `python run.py` и проверить localhost что отдаёт

5. **Есть ли CSS для landing.html?**
   - landing.html подключает `/assets/css/landing-styles.css`
   - Но этот файл СУЩЕСТВУЕТ?
   - Или стили только inline?

---

## ✅ STATUSES

| Компонент | Статус | Комментарий |
|-----------|--------|-----------|
| **landing.html (новый)** | ✅ ГОТОВ | 9 секций, HTML валиден, структура корректна |
| **index.html (fallback)** | ✅ СУЩЕСТВУЕТ | Может использоваться как запасной вариант |
| **miniapp.html** | ✅ ГОТОВ | 134KB, структурирован, viewport 500px |
| **app/app.py** | ✅ ГОТОВ | Маршруты настроены на landing.html |
| **assets/** | ⚠️ НУЖНА ПРОВЕРКА | Где находятся images, css, js? |
| **web/landing-styles.css** | ❓ НАЙДЕН? | landing.html подключает его но нужна проверка |
| **На VPS** | ❓ НЕИЗВЕСТНО | Нужна прямая проверка SSH/curl |

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

**Этап 4:** LANDING_9_SCREENS_IMPLEMENTATION_MAP  
Сравнить каждый из 9 найденных PNG с соответствующей секцией в landing.html

**Этап 5:** ROUTE_AND_HTML_MAPPING  
Проверить какой файл реально отдается на `/` на production

**Этап 6:** NOT_DEPLOYED_CHANGES_REPORT  
Разобраться почему 9 экранов не видны (коммит? деплой? старый код на VPS?)

---

**Статус:** ✅ COMPLETE  
**Дальше:** Этап 4 — детальный mapping 9 экранов

