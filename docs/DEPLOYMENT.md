# 🚀 UNITGROUP - Deployment Guide

**Status:** Production-Ready  
**Domain:** https://unitgroup.tech  
**VPS:** 193.104.33.29 (Ubuntu 22.04)

---

## Quick Start

### 1. Local Development

```bash
# Setup
git clone https://github.com/demsonart/unitplast_bot.git
cd unitplast_bot
cp .env.example .env
# Edit .env with your values

# Run
docker compose up -d
docker compose logs -f
```

### 2. Deploy to Production VPS

```bash
ssh root@193.104.33.29

cd /home/deploy/unitgroup_ai

# Deploy with script
./scripts/deploy.sh
```

---

## VPS Setup (First Time)

### Prerequisites

- SSH access to VPS
- Domain pointed to VPS (A records)
- 2GB+ disk space
- Ubuntu 22.04 LTS

### Step 1: Connect & Update

```bash
ssh root@193.104.33.29
apt-get update && apt-get upgrade -y
apt-get install -y \
    git \
    docker.io \
    docker-compose \
    curl \
    wget \
    certbot \
    python3-certbot-nginx
```

### Step 2: Clone Repository

```bash
mkdir -p /home/deploy
cd /home/deploy
git clone https://github.com/demsonart/unitplast_bot.git unitgroup_ai
cd unitgroup_ai
```

### Step 3: Setup Environment

```bash
cp .env.example .env
# Edit .env with real values
nano .env
```

### Step 4: Create SSL Certificate

```bash
certbot certonly --standalone \
    -d unitgroup.tech \
    -d www.unitgroup.tech
```

Copy to Docker:
```bash
mkdir -p certbot/conf
mkdir -p certbot/www
cp -r /etc/letsencrypt/* certbot/conf/
```

### Step 5: Start Services

```bash
./scripts/deploy.sh
```

### Step 6: Setup Monitoring & Backups

```bash
# Add to crontab
crontab -e

# Backups every day at 3 AM
0 3 * * * /home/deploy/unitgroup_ai/scripts/backup.sh

# Monitoring every minute
* * * * * /home/deploy/unitgroup_ai/scripts/monitor.sh
```

---

## Checking Status

### Container Status
```bash
docker compose ps
```

### Logs
```bash
docker compose logs -f
docker compose logs --tail=100 backend
docker compose logs --tail=100 bot
```

### Health Check
```bash
curl https://unitgroup.tech/health
curl https://unitgroup.tech/api/health
```

---

## Updating Application

```bash
cd /home/deploy/unitgroup_ai
./scripts/deploy.sh
```

---

## Troubleshooting

### Container won't start
```bash
docker compose logs backend
docker compose up -d --build
```

### SSL certificate expired
```bash
certbot renew --force-renewal
./scripts/deploy.sh
```

### Database connection error
```bash
docker compose exec db psql -U unitgroup -d unitgroup
```

### Backend API not responding
```bash
docker compose restart backend
curl http://localhost:8000/health
```

---

## Monitoring

Check if services are healthy:
```bash
docker compose ps
docker compose logs --tail=5
```

Telegram alerts are sent if:
- Container stops
- Healthcheck fails
- Database is unreachable

Configure in `.env`:
```env
ALERT_BOT_TOKEN=your_bot_token
ALERT_CHAT_ID=your_chat_id
```

---

## Backup & Recovery

### Manual Backup
```bash
./scripts/backup.sh
```

### List Backups
```bash
ls -la backups/
```

### Restore from Backup
```bash
cat backups/unitgroup_2024-01-01_03-00-00.sql | \
    docker compose exec -T db psql -U unitgroup -d unitgroup
```

---

## Security Checklist

- [ ] `.env` not in Git
- [ ] Database not exposed to internet
- [ ] SSL certificate valid
- [ ] UFW firewall configured
- [ ] SSH keys for deployment
- [ ] Backups tested
- [ ] Monitoring alerts working

---

## Resources

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Nginx Docs](https://nginx.org/en/docs/)
- [Certbot](https://certbot.eff.org/)
- [PostgreSQL](https://www.postgresql.org/docs/)

