# Missing 6 Screens — Decision

**Date:** 2026-07-12

---

## Статус

```
Reference screens found: 4
Functional screens defined (landing): 9
Target total: 88

Gap: 88 - 4 - 9 = 75 remaining

Но это неправильный расчёт. Нужно переопределить:
```

---

## Реальная задача

### Phase 1: Landing (9 функциональных экранов)

1. **HERO** — Главная секция, заголовок, CTA
2. **FEATURES** — 6 возможностей
3. **THREE BRANDS** — UNITPLAST, UNIFURNITURE, UNIMETALL
4. **COMMERCIAL** — Коммерческие предложения
5. **MINI APP** — Демонстрация
6. **MANAGEMENT** — Управленческие функции
7. **CALCULATOR** — Калькулятор
8. **CTA** — Призыв к действию
9. **CONTACTS** — Контактная информация

**Status:** REFERENCE_NONE, FUNCTIONAL_SCREENS_WITHOUT_REFERENCE

### Phase 2: Mini App (73 функциональных экрана)

Категории:
- Home / Dashboard (~8)
- Calculations (~18)
- Orders (~23)
- Profile / Settings (~14)
- Modals / Dialogs (~8)
- Onboarding (~2)

**Status:** REFERENCE_PARTIAL (4 files), FUNCTIONAL_SCREENS_UNDEFINED

---

## Заключение

Целевое число 88 экранов = **88 функциональных требований**, а не reference PNG файлов.

Reference PNG: 4 (для стиля)  
Функциональные: 82 (9 landing + 73 Mini App)  
Итого: 86 (всё что реально нужно)

**Или целевое 88:**
- 9 landing
- 73 Mini App
- 6 additional functional screens (TBD)

