# 🚀 UNITPLAST BOT - Local Setup Guide

**Status:** MVP Recovery in Progress  
**Target:** Telegram Bot + Mini App + Landing + Backend

---

## 📋 Requirements

- Python 3.13+
- pip / venv
- Telegram Bot token (from @BotFather)
- Yandex email + app password (for email processing)

---

## 1️⃣ Install Dependencies

```bash
# Clone repository
git clone https://github.com/demsonart/unitplast_bot.git
cd unitplast_bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 2️⃣ Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your values
nano .env
# or use your editor

# Minimum required:
TELEGRAM_BOT_TOKEN=xxxxx
TELEGRAM_GROUP_ID=-1001234567890
```

---

## 3️⃣ Start the Application

### Option A: Run Flask Server + Telegram Bot (RECOMMENDED)

```bash
python app/main.py
```

Expected output:
```
============================================================
🤖 UNITPLAST BOT STARTED
============================================================
2026-06-22 20:00:00 - app.main - INFO - Starting Flask server on 0.0.0.0:5000
2026-06-22 20:00:00 - app.telegram_final_bot - INFO - Starting Telegram bot...
```

### Option B: Run Flask Server Only (for web testing)

```bash
python app.py
```

Expected: Flask runs on `http://localhost:5000`

---

## 4️⃣ Test the Application

### Health Check
```bash
curl http://localhost:5000/health
# Expected: {"status": "OK", "service": "UNITPLAST API", "version": "1.0"}
```

### Landing Page
```
Open: http://localhost:5000/
```

### Mini App
```
Open: http://localhost:5000/app/miniapp
```

### Telegram Bot
- Add bot to any Telegram chat
- Send `/start` command
- Bot should respond with main menu

### Email Processing (if configured)
```bash
# Check once without continuous polling
python app/main.py --check-once
```

---

## 📊 Database

SQLite database is auto-created:
```
data/unitplast.db
```

To inspect database:
```bash
sqlite3 data/unitplast.db
.tables
.schema
```

---

## 🔍 Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Make sure venv is activated and requirements installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: TELEGRAM_BOT_TOKEN not found
**Solution:** Create .env file and add your token
```bash
cp .env.example .env
# Edit and add: TELEGRAM_BOT_TOKEN=your_token
```

### Issue: Port 5000 already in use
**Solution:** Change port in code or kill the process
```bash
# Find process on port 5000
lsof -i :5000
# Kill it
kill -9 <PID>
```

### Issue: Email not connecting
**Solution:** Check YANDEX_EMAIL and app password
- Use app-specific password, not main password
- Enable IMAP in Yandex Mail settings

---

## 📝 Log Files

Logs are printed to console (see logs/ directory if configured):
```bash
tail -f logs/unitplast.log
```

---

## ✅ Checklist Before Deployment

- [ ] Flask server starts without errors
- [ ] Health check endpoint responds
- [ ] Landing page loads (http://localhost:5000)
- [ ] Mini App loads (http://localhost:5000/app/miniapp)
- [ ] Telegram bot responds to /start
- [ ] Database file created (data/unitplast.db)
- [ ] No secrets in console output
- [ ] .env file NOT committed to git

---

## 🆘 Support

Check README.md for architecture overview.

For deployment to Railway, see DEPLOYMENT.md.
