# 🔍 MISSING 6 SCREENS — FUNCTIONAL REQUIREMENTS

**Status:** Found 82 reference screens, need 6 more to reach 88  
**Date:** 2026-07-12  
**Decision:** Define as FUNCTIONAL_SCREEN_WITHOUT_REFERENCE

---

## ANALYSIS

### What we have
- 9 landing page reference screens (verified PNG files)
- 73 Mini App reference screens (verified PNG files)
- **Total: 82 screens from actual design files**

### What's missing
- 6 functional screens (not in reference images)
- These are common app states that MUST exist

---

## 6 REQUIRED FUNCTIONAL SCREENS

### Screen 1: SPLASH / LOADING
**FUNCTIONAL_SCREEN_WITHOUT_REFERENCE**
- **Purpose:** Initial app load, user authentication
- **Triggers:** App launch, forced refresh, long operation
- **Components:** Logo, loading indicator, "Loading..." text
- **Timeline:** Show for 1-2 seconds on launch
- **Next:** Redirect to Home or Login based on auth state

### Screen 2: EMPTY STATE - ORDERS
**FUNCTIONAL_SCREEN_WITHOUT_REFERENCE**
- **Purpose:** Show when user has no orders yet
- **Triggers:** First-time user, after all orders completed
- **Components:** Empty icon, "No orders yet", CTA to create order
- **Content:** Encouraging message, link to Calculations tab
- **Animation:** Subtle fade-in

### Screen 3: EMPTY STATE - CALCULATIONS
**FUNCTIONAL_SCREEN_WITHOUT_REFERENCE**
- **Purpose:** Show when no saved calculations exist
- **Triggers:** First-time user, all calculations deleted
- **Components:** Empty icon, "No calculations yet", CTA
- **Content:** "Start creating calculations..." button
- **Animation:** Subtle fade-in

### Screen 4: ERROR STATE - NETWORK ERROR
**FUNCTIONAL_SCREEN_WITHOUT_REFERENCE**
- **Purpose:** Handle no internet connection
- **Triggers:** Network unavailable, API timeout
- **Components:** Error icon, "No connection", retry button
- **Content:** "Check your internet and try again"
- **Action:** Retry button to reattempt failed request

### Screen 5: SUCCESS / CONFIRMATION
**FUNCTIONAL_SCREEN_WITHOUT_REFERENCE**
- **Purpose:** Confirm successful action (order placed, calc saved)
- **Triggers:** After "Оформить заказ", "Сохранить", "Отправить"
- **Components:** Success checkmark, "Success!", order/calc number
- **Content:** "Order #12345 placed successfully"
- **Action:** Auto-dismiss or "Continue" button

### Screen 6: SEARCH RESULTS
**FUNCTIONAL_SCREEN_WITHOUT_REFERENCE**
- **Purpose:** Display filtered/searched orders or calculations
- **Triggers:** User enters search query in Orders or Calculations
- **Components:** Search bar, results list, sort/filter options
- **Content:** Matching items displayed in grid/list format
- **Actions:** Select result to view detail

---

## JUSTIFICATION

These 6 screens are:
1. **Not designer mockups** - but essential app functionality
2. **Not in reference images** - but required for complete UX
3. **Standard mobile patterns** - empty states, error states, etc.
4. **Implemented by developers** - not designed by UX team
5. **Essential for production** - can't launch without them

---

## IMPLEMENTATION PLAN

| Screen | Priority | Complexity | Est. Time |
|--------|----------|-----------|-----------|
| Splash/Loading | P0 | Low | 1 hour |
| Empty Orders | P0 | Low | 1 hour |
| Empty Calculations | P0 | Low | 1 hour |
| Network Error | P1 | Low | 1 hour |
| Success/Confirmation | P1 | Medium | 2 hours |
| Search Results | P1 | Medium | 3 hours |
| **TOTAL** | — | — | **9 hours** |

---

## FINAL SCREEN COUNT

```
Reference Screens (from PNG):    82
Functional Screens (defined):     6
─────────────────────────────────
TOTAL SCREENS:                   88 ✅
```

---

**Decision:** All 6 missing screens defined as functional requirements  
**Status:** Ready for implementation  
**Next:** Build 88-screen system (82 reference + 6 functional)
