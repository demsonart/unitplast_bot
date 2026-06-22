# 🚀 UNITPLAST BOT - Railway Deployment Guide

**Status:** MVP Deployment Instructions  
**Platform:** Railway.app  
**Target:** Flask + Telegram Bot + Background Jobs

---

## 📋 Prerequisites

1. GitHub repository connected to Railway
2. Railway project created
3. Environment variables ready

---

## 1️⃣ Create Railway Project

```bash
# Install Railway CLI (optional, can use web UI)
npm install -g @railway/cli

# Login
railway login

# Link to existing Railway project or create new
railway link
```

Or use Railway Web Dashboard:
1. Go to railway.app
2. Create New Project
3. Connect GitHub repository
4. Select branch (main)

---

## 2️⃣ Set Environment Variables

In Railway Dashboard → Variables:

```env
# TELEGRAM BOT (REQUIRED)
TELEGRAM_BOT_TOKEN=<your_token_from_botfather>
TELEGRAM_GROUP_ID=<your_group_id>

# YANDEX EMAIL (REQUIRED for email processing)
YANDEX_EMAIL=<sales_email@yandex.ru>
YANDEX_PASSWORD=<app_password>

# COMPANY INFO
COMPANY_NAME=Юнитпласт
COMPANY_EMAIL=id@unitplast.ru
COMPANY_PHONE=+7 (495) 924-50-96

# DATABASE
DATABASE_PATH=data/unitplast.db

# OPTIONAL
ENABLE_AI=false
PORT=5000
```

**IMPORTANT:** Do NOT paste real tokens in this guide. Add them through Railway UI.

---

## 3️⃣ Update Railway Configuration

File: `railway.json`

Current (if not working):
```json
{
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "startCommand": "python app.py",
    "restartPolicyMaxRetries": 5,
    "restartPolicyWindow": 600
  }
}
```

Recommended (for MVP):
```json
{
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "startCommand": "python app/main.py",
    "restartPolicyMaxRetries": 5,
    "restartPolicyWindow": 600
  }
}
```

---

## 4️⃣ Dockerfile Check

Current `Dockerfile` is good:
```dockerfile
FROM python:3.13-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

**Note:** Change `CMD` to use `app/main.py` instead of `app.py`:
```dockerfile
CMD ["python", "app/main.py"]
```

---

## 5️⃣ Deploy to Railway

### Via Railway Web UI:

1. Go to railway.app dashboard
2. Select your project
3. Click "Deploy"
4. Monitor logs in real-time

### Via Railway CLI:

```bash
railway up
```

---

## 6️⃣ Verify Deployment

### Check Status
```bash
railway status
```

### View Logs
```bash
# Via CLI
railway logs

# Via Web UI
Dashboard → Logs
```

### Test Endpoints

```bash
# Health check (replace with your Railway URL)
curl https://unitplast-bot.railway.app/health

# Landing page
https://unitplast-bot.railway.app/

# Mini App
https://unitplast-bot.railway.app/app/miniapp
```

Expected responses:
- Health: `{"status": "OK", "service": "UNITPLAST API", "version": "1.0"}`
- Landing: HTML page
- Mini App: Telegram Mini App HTML

---

## 7️⃣ Data Persistence

### SQLite Issue on Railway

Railway has **ephemeral filesystem** - data is lost on redeploy.

**Solution 1: Use Railway Volumes** (Quick)
```
Dashboard → Variables → Volume → Add Volume
Path: /app/data
Mount: /app/data
```

**Solution 2: Migrate to PostgreSQL** (Better)
```bash
# On Railway dashboard, add PostgreSQL add-on
# Update config to use DATABASE_URL instead of SQLite
```

**For MVP:** Use Volume solution.

---

## 8️⃣ Monitoring

### Railway Logs
```bash
railway logs --follow
```

### Expected Startup Output
```
2026-06-22T20:00:00.000Z [INFO] Starting Flask server
2026-06-22T20:00:00.000Z [INFO] Starting Telegram bot
2026-06-22T20:00:00.000Z [INFO] Health check endpoint: /health
2026-06-22T20:00:00.000Z [INFO] Flask running on 0.0.0.0:5000
```

### Alerts to Watch
- ❌ Missing TELEGRAM_BOT_TOKEN
- ❌ Database connection errors
- ❌ Email IMAP failures
- ⚠️ Memory leaks (Telegram polling)

---

## 9️⃣ Rollback

If deployment fails:

```bash
# View deployment history
railway deployments

# Rollback to previous version
railway rollback <deployment-id>
```

---

## 🔟 Production Checklist

- [ ] Environment variables set (no secrets in code)
- [ ] Railway project linked
- [ ] Dockerfile updated with correct CMD
- [ ] Volume mounted for SQLite data
- [ ] Health check endpoint working
- [ ] Telegram bot token valid
- [ ] Email credentials correct (if using)
- [ ] Logs monitored
- [ ] Domain/URL configured (if custom domain needed)

---

## 📞 Support

### Common Issues

**Issue: Application crashes on startup**
```
railway logs
# Check: TELEGRAM_BOT_TOKEN missing or invalid
```

**Issue: 404 Application not found**
```
# Make sure health endpoint is working
curl https://your-app.railway.app/health
```

**Issue: Email not processing**
```
# Check: YANDEX_EMAIL and YANDEX_PASSWORD in variables
# Test with: --check-once flag locally first
```

---

## 🎯 Next Steps After Deployment

1. Test Telegram bot commands
2. Monitor email processing (if enabled)
3. Check database backups
4. Set up alerts/monitoring
5. Plan PostgreSQL migration (Phase 2)

---

See SETUP.md for local testing before deployment.
