# 🚀 STAGE 25: LANDING REDESIGN IMPLEMENTATION
**Дата:** 2026-07-12  
**Статус:** 🔵 IN PROGRESS  
**Objetivo:** Improve landing page with design assets (9 sections)

---

## 📋 DESIGN ANALYSIS

**Design Screen 1 (0AD9C031...):** Hero + Mini App Showcase
```
✅ Navigation bar (logo, menu, CTA button)
✅ Hero section with headline
✅ Mobile phone mockup with mini app
✅ QR code for quick install
✅ Download buttons (App Store, Google Play, RuStore)
✅ Access methods (Web, Telegram Mini App)
✅ Platform icons (iOS, Android, Web, Telegram)
✅ 3D product render
```

---

## 🎯 IMPLEMENTATION PLAN

### Phase 1: Navigation Enhancement (30 min)
```
Current:  Basic HTML structure
Target:   Professional nav bar with logo + menu + CTA
Add:
  ✅ UNITPLAST logo with icon
  ✅ Navigation menu (Solutions, Industries, Features, Cases, Contacts)
  ✅ Blue CTA button "Request Demo" with arrow icon
  ✅ Mobile hamburger menu
```

### Phase 2: Hero Section Upgrade (1-2 hours)
```
Current:  Text + 3D image on right
Target:   Full featured hero matching design
Add:
  ✅ Larger, bolder headline
  ✅ Mobile phone mockup (left-center)
  ✅ QR code display
  ✅ Download buttons (3x app stores)
  ✅ Better visual hierarchy
```

### Phase 3: Access Methods Section (45 min)
```
Current:  None
Target:   "Other ways to access" with Web + Telegram Mini App
Add:
  ✅ Card-based layout
  ✅ Icons for each method
  ✅ Descriptions
  ✅ Arrow indicators
```

### Phase 4: Platform Icons (15 min)
```
Current:  None
Target:   iOS, Android, Web, Telegram icons at bottom
Add:
  ✅ 4 platform icon cards
  ✅ Descriptions for each
  ✅ Responsive grid layout
```

---

## 📊 CURRENT LANDING STATUS

### Already Implemented ✅
```
✅ Section 1 - Hero (basic, needs enhancement)
✅ Section 2 - Features (6 cards, looks good)
✅ Section 3 - КП (commercial offers)
✅ Section 4 - Mini App (showcase)
✅ Section 5 - Management (dashboard)
✅ Section 6 - Three Brands (UNITPLAST, UNITFURNITURE, UNITMETALL)
✅ Section 7 - Contacts
✅ Section 8 - CTA Block
✅ Section 9 - Footer
```

### To Enhance
```
🔵 Hero - Add navigation, phone mockup, QR code, download buttons
🔵 Access Methods - Add Web + Telegram Mini App section
🔵 Platform Icons - Add iOS, Android, Web, Telegram
🔵 Visual Polish - Ensure matches design aesthetic
```

---

## 💻 IMPLEMENTATION STEPS

### Step 1: Add Navigation Bar
```html
<nav class="navbar">
  <div class="nav-logo">
    <img src="/assets/icons/unitplast-logo.svg" alt="UNITPLAST">
    <span>UNITPLAST</span>
  </div>
  <div class="nav-menu">
    <a href="#solutions">Решения</a>
    <a href="#industries">Отрасли</a>
    <a href="#features">Возможности</a>
    <a href="#cases">Кейсы</a>
    <a href="#contacts">Контакты</a>
  </div>
  <button class="nav-cta">Запросить демо →</button>
</nav>
```

### Step 2: Enhance Hero Section
```html
<section class="hero">
  <div class="hero-container">
    <div class="hero-left">
      <h1>Скачайте приложение и подключитесь к платформе</h1>
      <p>Доступ ко всем возможностям UNITPLAST — на вашем устройстве...</p>
      
      <!-- Download buttons -->
      <div class="download-buttons">
        <a href="#" class="btn-app-store">
          <span>Загрузите в</span>
          <strong>App Store</strong>
        </a>
        <a href="#" class="btn-google-play">
          <span>Доступно в</span>
          <strong>Google Play</strong>
        </a>
        <a href="#" class="btn-rustore">
          <span>Скачайте из</span>
          <strong>RuStore</strong>
        </a>
      </div>
      
      <!-- Other access methods -->
      <div class="other-access">
        <h3>Другие способы доступа</h3>
        <div class="access-grid">
          <div class="access-card">
            <span class="access-icon">💻</span>
            <h4>Web версия</h4>
            <p>Полный доступ ко всем возможностям платформы через браузер...</p>
          </div>
          <div class="access-card">
            <span class="access-icon">✈️</span>
            <h4>Telegram Mini App</h4>
            <p>Быстрый доступ к ключевым функциям платформы прямо в Telegram...</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="hero-right">
      <!-- Mobile mockup -->
      <div class="mobile-mockup">
        <div class="phone">
          <div class="phone-screen">
            <img src="/assets/images/mini-app-preview.png" alt="Mini App">
          </div>
        </div>
        
        <!-- QR code -->
        <div class="qr-section">
          <p>Сканируйте QR-код для быстрой установки</p>
          <img src="/assets/images/qr-code.png" alt="QR Code" class="qr-code">
          <p>Откройте камерой и перейдите по ссылке</p>
        </div>
        
        <!-- 3D render -->
        <div class="hero-3d">
          <img src="/assets/images/hero-3d-render.png" alt="3D Render">
        </div>
      </div>
    </div>
  </div>
  
  <!-- Platform icons at bottom -->
  <div class="platform-icons">
    <div class="platform-card">
      <span class="icon">🍎</span>
      <h4>iOS</h4>
      <p>Оптимизировано для iPhone и iPad. Стабильная работа и быстрый доступ.</p>
    </div>
    <div class="platform-card">
      <span class="icon">🤖</span>
      <h4>Android</h4>
      <p>Полная функциональность на устройствах Android. Удобно и безопасно.</p>
    </div>
    <div class="platform-card">
      <span class="icon">🌐</span>
      <h4>Web</h4>
      <p>Работайте на любом браузере. Данные синхронизируются мгновенно.</p>
    </div>
    <div class="platform-card">
      <span class="icon">✈️</span>
      <h4>Telegram</h4>
      <p>Мини-приложение внутри Telegram. Удобно и безопасно.</p>
    </div>
  </div>
</section>
```

### Step 3: Add CSS Styling
```css
/* Navigation */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(4, 6, 12, 0.8);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: bold;
  color: var(--text-0);
}

.nav-menu {
  display: flex;
  gap: 30px;
}

.nav-cta {
  background: var(--blue);
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
}

/* Hero section */
.hero {
  display: flex;
  flex-direction: column;
}

.hero-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

/* Mobile mockup */
.mobile-mockup {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
}

.phone {
  width: 300px;
  height: 600px;
  border-radius: 50px;
  border: 12px solid #1a1a1a;
  background: #000;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(46, 107, 242, 0.3);
}

.qr-section {
  text-align: center;
  padding: 20px;
}

.qr-code {
  width: 150px;
  height: 150px;
  background: white;
  padding: 10px;
  border-radius: 10px;
}

/* Platform icons */
.platform-icons {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-top: 60px;
}

.platform-card {
  padding: 20px;
  border: 1px solid rgba(170, 178, 197, 0.2);
  border-radius: 10px;
  text-align: center;
}

.platform-card .icon {
  font-size: 32px;
  display: block;
  margin-bottom: 10px;
}

@media (max-width: 768px) {
  .hero-container {
    grid-template-columns: 1fr;
  }
  
  .platform-icons {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .nav-menu {
    display: none;
  }
}
```

---

## 📊 TESTING CHECKLIST

```
Navigation:
  [ ] Logo displays correctly
  [ ] Menu items visible
  [ ] CTA button clickable
  [ ] Mobile hamburger works

Hero Section:
  [ ] Headline displays
  [ ] Mobile mockup visible
  [ ] QR code shows
  [ ] Download buttons clickable

Download Buttons:
  [ ] App Store link works
  [ ] Google Play link works
  [ ] RuStore link works
  [ ] Hover effect visible

Platform Icons:
  [ ] All 4 icons display
  [ ] Text readable
  [ ] Grid responsive

Responsive:
  [ ] Desktop (1920px) ✅
  [ ] Tablet (768px) ✅
  [ ] Mobile (375px) ✅
```

---

## ⏭️ NEXT STEPS

1. **Now:** Implement navigation bar
2. **Next:** Enhance hero section
3. **Then:** Add access methods cards
4. **Finally:** Polish styling & test responsiveness

---

**Status:** 🔵 STAGE 25 STARTING  
**Time Estimate:** 2-4 hours for full hero enhancement  
**Risk Level:** 🟢 LOW (backward compatible changes)

