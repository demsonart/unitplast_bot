# ✅ UNITPLAST BOT - Manual Verification Checklist

Use this checklist to verify the MVP is working correctly before deploying to Railway.

---

## 🏠 Prerequisites

- [ ] Python 3.13+ installed
- [ ] Git repository cloned
- [ ] Virtual environment created: `python3 -m venv venv`
- [ ] Activated: `source venv/bin/activate`
- [ ] Dependencies installed: `pip install -r requirements.txt`

---

## 🚀 Quick Start Test (5 minutes)

### 1. Copy Configuration

```bash
cp .env.example .env
```

- [ ] File `.env` created (not tracked by git)
- [ ] Can be opened: `cat .env`

### 2. Start Application

```bash
python run.py
```

**Expected Output:**
```
============================================================
🤖 UNITPLAST BOT - UNIFIED STARTUP
============================================================
2026-06-22 ... - INFO - Flask server thread started
2026-06-22 ... - INFO - Starting Telegram bot in main thread...
```

- [ ] Script starts without errors
- [ ] Flask server message appears
- [ ] Telegram bot message appears
- [ ] No "Error" or "Traceback" in output
- [ ] Terminal shows "Flask running on 0.0.0.0:5000"

### 3. Test Health Endpoint (in another terminal)

```bash
curl http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "OK",
  "service": "UNITPLAST BOT",
  "version": "2.0",
  "timestamp": "2026-06-22T...",
  "endpoints": {...}
}
```

- [ ] Returns HTTP 200
- [ ] JSON format is valid
- [ ] Contains "status": "OK"
- [ ] Timestamp is current

### 4. Test Landing Page

```bash
curl http://localhost:5000/ | head -20
```

**Expected:** HTML content starting with `<!DOCTYPE html>` or `<html>`

- [ ] Returns HTML (not JSON error)
- [ ] Contains "UNITPLAST SALES OS" or similar title
- [ ] No error messages

### 5. Test Mini App

```bash
curl http://localhost:5000/app/miniapp | head -20
```

**Expected:** HTML with Telegram Mini App

- [ ] Returns HTML content
- [ ] Contains "telegram-web-app.js" or similar
- [ ] No 404 error

### 6. Test API Endpoint

```bash
curl http://localhost:5000/api/materials
```

**Expected JSON:**
```json
{
  "success": true,
  "materials": [...]
}
```

- [ ] Returns JSON
- [ ] "success": true
- [ ] Materials array exists

---

## 💾 Database Test

### 1. Check Database Created

```bash
ls -la data/
```

- [ ] Directory `data/` exists
- [ ] File `unitplast.db` exists
- [ ] File size > 0 bytes

### 2. Inspect Database

```bash
sqlite3 data/unitplast.db ".tables"
```

**Expected:** List of tables like `processed_emails`, `orders`, `commercial_offers`

- [ ] At least one table exists
- [ ] Can open database without errors

### 3. Check Schema

```bash
sqlite3 data/unitplast.db ".schema processed_emails"
```

**Expected:** Table structure with columns

- [ ] Schema defined correctly
- [ ] Columns exist (message_id, subject, etc.)

---

## 🤖 Telegram Bot Test

### 1. Add Bot to Telegram

- [ ] Bot token is valid (obtained from @BotFather)
- [ ] Bot added to personal Telegram chat
- [ ] Bot name appears in chat

### 2. Send /start Command

```
User: /start
```

**Expected:** Bot responds with main menu

- [ ] Bot responds quickly (< 5 sec)
- [ ] Menu displays with options
- [ ] No error messages in console

### 3. Send /help Command

```
User: /help
```

**Expected:** Help text appears

- [ ] Bot responds
- [ ] Help information is useful
- [ ] No crashes in console

### 4. Test Order Form

```
User: /order
```

**Expected:** Bot starts form asking for material

- [ ] Bot responds with question
- [ ] Form state is saved
- [ ] Can continue with /cancel to abort

- [ ] Order form FSM works
- [ ] Can cancel with /cancel
- [ ] States flow correctly

---

## 🔒 Security Checks

### 1. No Secrets in Code

```bash
grep -r "sk-" app/
grep -r "telegram_bot_token" app/
grep -r "password" app/ | grep -v "YANDEX_PASSWORD"
```

**Expected:** No output (or only variable names)

- [ ] No hardcoded tokens found
- [ ] No hardcoded passwords
- [ ] Secrets only in .env

### 2. .env Not Committed

```bash
git status | grep .env
```

**Expected:** No `.env` file listed

- [ ] .env file not in git
- [ ] .env in .gitignore
- [ ] Secrets are safe

### 3. Check .gitignore

```bash
cat .gitignore | grep -E "\.env|\.db|__pycache__"
```

**Expected:** All three patterns present

- [ ] .env* is ignored
- [ ] *.db is ignored
- [ ] __pycache__ is ignored

---

## 📊 Performance Tests

### 1. Response Time

```bash
time curl http://localhost:5000/health
```

**Expected:** < 100ms

- [ ] Health check responds quickly
- [ ] Real-time (not cached delay)

### 2. Memory Usage

```bash
ps aux | grep python
```

**Expected:** Process uses reasonable memory (< 500MB)

- [ ] Memory usage is acceptable
- [ ] No memory leak (doesn't grow over time)

### 3. Database Performance

```bash
time sqlite3 data/unitplast.db "SELECT COUNT(*) FROM processed_emails;"
```

**Expected:** < 10ms

- [ ] Database queries are fast
- [ ] No timeout issues

---

## 🔧 Configuration Tests

### 1. Environment Variables Load

```bash
python -c "from app.config import TELEGRAM_BOT_TOKEN; print('✓ Config loaded')"
```

**Expected:** `✓ Config loaded`

- [ ] Config module loads without errors
- [ ] Environment variables are readable
- [ ] No validation errors

### 2. Database Path

```bash
python -c "from app.config import DATABASE_PATH; print(DATABASE_PATH)"
```

**Expected:** Path like `data/unitplast.db`

- [ ] Database path is correct
- [ ] Path exists and is accessible

### 3. Company Info

```bash
python -c "from app.config import COMPANY_NAME, COMPANY_PHONE; print(COMPANY_NAME, COMPANY_PHONE)"
```

**Expected:** `Юнитпласт +7 (495) 924-50-96`

- [ ] Company info loaded correctly
- [ ] Can be used in templates

---

## 🚨 Error Handling Tests

### 1. Invalid Endpoint

```bash
curl http://localhost:5000/nonexistent
```

**Expected:** 404 JSON error

- [ ] Returns 404 status
- [ ] Error message is JSON (not HTML)
- [ ] Graceful error handling

### 2. Missing Mini App File

Temporarily rename: `mv web/unitplast_app.html web/unitplast_app.html.bak`

```bash
curl http://localhost:5000/app/miniapp
```

**Expected:** 404 error

- [ ] Returns 404 status
- [ ] Helpful error message
- [ ] Doesn't crash server

Then restore: `mv web/unitplast_app.html.bak web/unitplast_app.html`

- [ ] File restored
- [ ] Endpoint works again

### 3. Invalid Config

Remove TELEGRAM_BOT_TOKEN from .env temporarily and restart:

```bash
# Edit .env, remove TELEGRAM_BOT_TOKEN
python run.py
```

**Expected:** Error about missing token

- [ ] Application fails to start
- [ ] Error message is clear
- [ ] Tell user what's missing

Then restore the token.

- [ ] Application starts again

---

## 📋 Code Quality Tests

### 1. No Syntax Errors

```bash
python3 -m py_compile run.py app/app.py app/main.py
```

**Expected:** No output (success)

- [ ] All files compile
- [ ] No Python syntax errors

### 2. Import Check

```bash
python3 -c "import run; import app.app; import app.main"
```

**Expected:** No import errors

- [ ] All modules can be imported
- [ ] No circular dependencies
- [ ] Dependencies are installed

### 3. Logging Works

Look for log output in console when running `python run.py`

- [ ] Timestamps appear
- [ ] Log levels (INFO, ERROR) shown
- [ ] Messages are readable

---

## 🧹 Cleanup Tests

### 1. Clean Git Status

```bash
git status
```

**Expected Output:** Only new files and modified config files

- [ ] Only expected files modified
- [ ] .env file not listed
- [ ] No accidental changes

### 2. Legacy Folders Exist

```bash
ls -la app/legacy/
ls -la web/legacy/
```

**Expected:** Folders exist with README.md and old files

- [ ] app/legacy/ directory exists
- [ ] web/legacy/ directory exists
- [ ] Both have README.md explaining why archived

### 3. Documentation Complete

```bash
ls -la *.md
```

**Expected:** SETUP.md, DEPLOYMENT.md, README.md, PROGRESS_REPORT.md

- [ ] SETUP.md exists (local setup guide)
- [ ] DEPLOYMENT.md exists (railway guide)
- [ ] PROGRESS_REPORT.md exists (what was done)
- [ ] README.md updated

---

## ✅ Final Sign-Off

If all checks pass:

- [ ] **Ready for local testing:** YES ✅
- [ ] **Ready for Railway deployment:** YES (after env vars added)
- [ ] **No breaking changes:** Verified
- [ ] **All features working:** Confirmed

---

## 🆘 Troubleshooting

### If Flask doesn't start

1. Check port: `lsof -i :5000`
2. Check dependencies: `pip list`
3. Check Python version: `python3 --version`

### If Telegram bot doesn't respond

1. Check token validity
2. Check TELEGRAM_BOT_TOKEN in .env
3. Check console for errors

### If database doesn't initialize

1. Check `data/` directory exists
2. Check write permissions: `touch data/test.txt`
3. Check SQLite: `sqlite3 --version`

### If API returns 404

1. Check Flask is running on 5000
2. Check files exist: `ls web/*.html`
3. Check routes in app/app.py

---

## 📞 Need Help?

See SETUP.md for local testing guide
See DEPLOYMENT.md for Railway deployment guide
Check PROGRESS_REPORT.md for what was changed

---

**Next Step:** After all checks pass, follow DEPLOYMENT.md to deploy to Railway.
