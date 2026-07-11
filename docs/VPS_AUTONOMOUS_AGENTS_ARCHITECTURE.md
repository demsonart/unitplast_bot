# 🤖 VPS AUTONOMOUS AGENTS ARCHITECTURE — Этапы 22-33
**Дата:** 2026-07-12  
**Статус:** ARCHITECTURE DESIGN  
**Goal:** Агенты работают на VPS без Mac, Mac можно выключить

---

## 🎯 ГЛАВНАЯ ЦЕЛЬ

**Production VPS должен быть полностью автономным:**
- ✅ Landing работает
- ✅ Mini App работает
- ✅ Агенты работают 24/7
- ✅ Mac можно выключить
- ✅ Мониторинг и логи на VPS

---

## 📊 АГЕНТЫ В ПРОЕКТЕ

### Найдены в коде:

1. **Telegram UNITPLAST Bot** (app/telegram_final_bot.py)
   - Main bot
   - Commands: /menu, /health, /id, /test, /checkmail, /orders, /kp, /miniapp, /settings
   - Status: ⚠️ Может отправлять сообщения

2. **Telegram Media Bot** (app/telegram_media_bot.py)
   - Media publishing
   - Status: 🔴 DANGEROUS — может отправлять в канал

3. **Email Polling Agent** (app/email_reader.py или встроен в main.py)
   - IMAP email reading
   - Order detection
   - Status: 🔴 DANGEROUS — может менять данные

4. **Bot Dispatcher** (app/bot_dispatcher.py)
   - Routes messages to correct bot
   - Status: ⚠️ Support infrastructure

5. **KP Calculator** (app/kp_calculator.py)
   - Расчет коммерческих предложений
   - Status: ✅ Safe (read-only math)

6. **Health Monitor** (встроен в app/app.py)
   - /health endpoint
   - Status: ✅ Safe (read-only)

7. **Order Parser** (встроен в app/email_reader.py или main.py)
   - Parse emails for orders
   - Status: ⚠️ Can modify DB

---

## 🔴 ОПАСНЫЕ АГЕНТЫ (ЗАПРЕЩЕНО ЗАПУСКАТЬ ПОКА)

**До отдельного подтверждения пользователя:**
- ❌ Email polling (может удалять/менять письма)
- ❌ Media bot (может публиковать в канал)
- ❌ Order auto-processing (может менять БД)
- ❌ Auto-sending Telegram (может спамить)

**Переменные для блокировки:**
```bash
SAFE_MODE=true
DRY_RUN=true
AUTOPUBLISH=false
SEND_TELEGRAM=false
SEND_EMAIL=false
ENABLE_EMAIL_POLLING=false
ENABLE_MEDIA_BOT=false
```

---

## 🟢 БЕЗОПАСНЫЕ АГЕНТЫ (МОЖНО ЗАПУСТИТЬ СЕЙЧАС)

### 1. Health Monitor Agent
```bash
Purpose: Monitor /health every 60s
Output: /var/www/unitplast_bot/logs/health_monitor.log
Status: READ-ONLY
Risk: 🟢 LOW
```

### 2. Agent Status Collector
```bash
Purpose: Collect systemd status every 5m
Output: /var/www/unitplast_bot/data/agents_status.json
Status: READ-ONLY
Risk: 🟢 LOW
```

### 3. VPS System Monitor
```bash
Purpose: Monitor disk, memory, CPU
Output: /var/www/unitplast_bot/logs/system_monitor.log
Status: READ-ONLY
Risk: 🟢 LOW
```

---

## 🏗️ АРХИТЕКТУРА

### Структура папок:

```
/var/www/unitplast_bot/
├── agents/                    # Агент-скрипты
│   ├── health_monitor.py      # Health check loop
│   ├── agent_status.py        # systemd status collector
│   ├── system_monitor.py      # Disk/memory/CPU monitor
│   ├── email_agent.py         # Email polling (DISABLED)
│   ├── telegram_agent.py      # Telegram bot (DISABLED)
│   └── media_agent.py         # Media publishing (DISABLED)
│
├── systemd/                   # systemd unit files
│   ├── unitplast-health-monitor.service
│   ├── unitplast-agent-status.service
│   ├── unitplast-system-monitor.service
│   └── unitplast.service      # Main web service (already exists)
│
├── scripts/
│   ├── agent_manager.sh       # Start/stop agents
│   ├── health_check.sh        # Manual health check
│   └── deploy_agents.sh       # Deploy agent configs
│
├── logs/
│   ├── health_monitor.log
│   ├── agent_status.log
│   ├── system_monitor.log
│   └── unitplast.log
│
├── data/
│   ├── agents_status.json     # Current agent statuses
│   ├── health_history.json    # Health check history
│   └── alerts.json            # Alert log
│
└── app/
    ├── app.py                 # Flask (main)
    ├── agent_manager.py       # Agent lifecycle manager
    └── api_agents.py          # /api/agents/* endpoints
```

---

## 🔧 SYSTEMD UNITS

### Template (для всех безопасных агентов):

```ini
# /etc/systemd/system/unitplast-<agent>.service

[Unit]
Description=UNITPLAST Agent: <NAME>
After=network.target
Wants=unitplast.service

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/unitplast_bot
Environment="PYTHONUNBUFFERED=1"
Environment="SAFE_MODE=true"
Environment="DRY_RUN=true"
Environment="AUTOPUBLISH=false"
ExecStart=/var/www/unitplast_bot/venv/bin/python -m agents.<name>
Restart=always
RestartSec=10
StandardOutput=append:/var/www/unitplast_bot/logs/<name>.log
StandardError=append:/var/www/unitplast_bot/logs/<name>.error.log

[Install]
WantedBy=multi-user.target
```

### Конкретно: Health Monitor

```ini
[Unit]
Description=UNITPLAST Health Monitor Agent
After=network.target
Wants=unitplast.service

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/unitplast_bot
Environment="PYTHONUNBUFFERED=1"
ExecStart=/var/www/unitplast_bot/venv/bin/python -m agents.health_monitor
Restart=always
RestartSec=10
StandardOutput=append:/var/www/unitplast_bot/logs/health_monitor.log
StandardError=append:/var/www/unitplast_bot/logs/health_monitor.error.log

[Install]
WantedBy=multi-user.target
```

---

## 📝 AGENT IMPLEMENTATIONS

### agents/health_monitor.py

```python
#!/usr/bin/env python3
"""
UNITPLAST Health Monitor Agent
Monitors /health endpoint every 60 seconds
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
DATA_DIR = Path(__file__).parent.parent / "data"

HEALTH_URL = "https://unitgroup.tech/health"
CHECK_INTERVAL = 60  # seconds

def log_check(status, response):
    log_file = LOG_DIR / "health_monitor.log"
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "status": status,
        "response": response
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def main():
    while True:
        try:
            response = requests.get(HEALTH_URL, timeout=5, verify=False)
            if response.status_code == 200:
                log_check("OK", response.json())
            else:
                log_check("ERROR", {"code": response.status_code})
        except Exception as e:
            log_check("FAILED", {"error": str(e)})
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
```

### agents/agent_status.py

```python
#!/usr/bin/env python3
"""
UNITPLAST Agent Status Collector
Collects systemd service status every 5 minutes
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
SERVICES = [
    "unitplast.service",
    "unitplast-health-monitor.service",
    "unitplast-agent-status.service",
]

def get_service_status(service):
    try:
        result = subprocess.run(
            ["systemctl", "is-active", service],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except:
        return "unknown"

def main():
    while True:
        timestamp = datetime.now().isoformat()
        statuses = {}
        
        for service in SERVICES:
            statuses[service] = get_service_status(service)
        
        data = {
            "timestamp": timestamp,
            "agents": statuses
        }
        
        status_file = DATA_DIR / "agents_status.json"
        with open(status_file, "w") as f:
            json.dump(data, f, indent=2)
        
        time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    main()
```

---

## 📊 API ENDPOINTS (Flask)

### /api/agents/status

```python
@app.route('/api/agents/status')
def agents_status():
    """Get current status of all agents"""
    status_file = DATA_DIR / "agents_status.json"
    
    if status_file.exists():
        with open(status_file) as f:
            data = json.load(f)
        return jsonify(data), 200
    
    return jsonify({"error": "Status file not found"}), 404

@app.route('/api/agents/health')
def agents_health():
    """Get health check history"""
    health_file = LOG_DIR / "health_monitor.log"
    
    if not health_file.exists():
        return jsonify({"error": "Health log not found"}), 404
    
    # Return last 20 entries
    with open(health_file) as f:
        lines = f.readlines()[-20:]
    
    entries = [json.loads(line) for line in lines]
    return jsonify({"history": entries}), 200
```

---

## 🎯 MINI APP SCREEN: "AGENTS"

### Planned screen for /app/miniapp:

```
┌─────────────────────────────────────┐
│ AGENTS STATUS                       │
│ Все системные агенты на одном       │
└─────────────────────────────────────┘

Web Backend
  ✅ running (active)
  Last restart: 22 мин назад

Health Monitor
  ✅ running (active)
  Checks: 1,234
  Last check: 30 сек назад

Agent Status Collector
  ✅ running (active)
  Collections: 156
  Last collection: 5 мин назад

Telegram Bot
  ⏸️  disabled (safe mode)
  Reason: Waiting for user confirmation
  Enable: [кнопка]

Email Agent
  ⏸️  disabled (dry run)
  Reason: Production safety
  Enable: [кнопка]

Media Bot
  ⏸️  disabled (autopublish=false)
  Reason: No auto-publishing
  Enable: [кнопка]

Last Health Check
  ✅ OK
  Timestamp: 2026-07-12 22:38:30 UTC
  Version: 2.0
  Status: Operational
```

---

## 📋 DEPLOYMENT CHECKLIST (Этап 22-33)

- [ ] **Stage 22:** Current agents audit (какие есть)
- [ ] **Stage 23:** Architecture plan (как запустить)
- [ ] **Stage 24:** Create health_monitor.py
- [ ] **Stage 25:** Create agent_status.py
- [ ] **Stage 26:** Create systemd units (health-monitor.service)
- [ ] **Stage 27:** Create systemd units (agent-status.service)
- [ ] **Stage 28:** Deploy to VPS (systemctl enable)
- [ ] **Stage 29:** Test health monitor (curl /api/agents/health)
- [ ] **Stage 30:** Test agent status (curl /api/agents/status)
- [ ] **Stage 31:** Add Mini App screen "Agents"
- [ ] **Stage 32:** Create agent_manager.sh script
- [ ] **Stage 33:** Final verification (Mac turned off, agents running)

---

## 🚀 QUICK START (для пользователя)

После одобрения:

```bash
# На VPS:
cd /var/www/unitplast_bot

# Create agent directories
mkdir -p agents systemd logs data

# Copy agent files (будет реализовано в Stage 24-25)
cp agents/*.py agents/
cp systemd/*.service /etc/systemd/system/

# Enable and start
systemctl daemon-reload
systemctl enable unitplast-health-monitor.service
systemctl enable unitplast-agent-status.service
systemctl start unitplast-health-monitor.service
systemctl start unitplast-agent-status.service

# Verify
systemctl status unitplast-health-monitor.service
curl http://localhost:5000/api/agents/status
```

---

## 🎯 SUCCESS CRITERIA (Этап 33)

✅ **Agents fully autonomous:**
- Mac можно выключить
- VPS работает 24/7
- Мониторинг работает
- Логи собираются
- API доступны
- Mini App показывает статус
- Zero dependency on MacBook

---

**Status:** 🟢 ARCHITECTURE READY  
**Next:** Stage 22 — Current agents audit

