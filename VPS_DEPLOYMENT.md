# 🚀 UNITPLAST BOT - VPS Deployment Guide

**Domain:** unitgroup.tech (www.unitgroup.tech)  
**IP:** 193.104.33.29  
**OS:** Ubuntu 22.04 LTS (recommended)  
**Web Server:** Nginx + Gunicorn  
**SSL:** certbot (Let's Encrypt)

---

## 📋 Prerequisites

- SSH access to VPS (193.104.33.29)
- Domain unitgroup.tech configured with DNS A records:
  - `@` → 193.104.33.29
  - `www` → 193.104.33.29
- sudo access on VPS
- ~2GB disk space for application + logs
- Python 3.13+ preferred (or 3.11+)

---

## 1️⃣ VPS SETUP (Initial)

### 1.1 Connect to VPS

```bash
ssh root@193.104.33.29
# or ssh ubuntu@193.104.33.29 if non-root user
```

### 1.2 Update System

```bash
apt-get update
apt-get upgrade -y
apt-get install -y \
    git \
    python3.13 \
    python3.13-venv \
    python3.13-dev \
    build-essential \
    nginx \
    certbot \
    python3-certbot-nginx \
    curl \
    wget \
    htop
```

### 1.3 Create Application User

```bash
useradd -m -s /bin/bash unitplast
usermod -aG sudo unitplast
sudo -u unitplast mkdir -p /home/unitplast/.ssh
```

### 1.4 Clone Repository

```bash
cd /opt
git clone https://github.com/demsonart/unitplast_bot.git unitplast_bot
cd unitplast_bot
sudo chown -R unitplast:unitplast /opt/unitplast_bot
```

### 1.5 Create Python Virtual Environment

```bash
sudo -u unitplast python3.13 -m venv /opt/unitplast_bot/venv
sudo -u unitplast /opt/unitplast_bot/venv/bin/pip install --upgrade pip
sudo -u unitplast /opt/unitplast_bot/venv/bin/pip install -r requirements.txt
sudo -u unitplast /opt/unitplast_bot/venv/bin/pip install gunicorn
```

### 1.6 Create Data and Log Directories

```bash
sudo mkdir -p /app/data /var/log/unitplast
sudo chown -R unitplast:unitplast /app/data /var/log/unitplast
```

---

## 2️⃣ CONFIGURATION

### 2.1 Create Production .env File

```bash
sudo -u unitplast cp .env.production.example /opt/unitplast_bot/.env.production

# Edit with your production values:
sudo -u unitplast nano /opt/unitplast_bot/.env.production
```

**REQUIRED VALUES TO SET:**
```env
TELEGRAM_BOT_TOKEN=your_production_token
TELEGRAM_GROUP_ID=your_group_id
DATABASE_PATH=/app/data/unitplast.db
COMPANY_SITE=unitgroup.tech
# Optional: YANDEX_EMAIL, YANDEX_PASSWORD if using email
```

### 2.2 Setup systemd Service

```bash
sudo cp /opt/unitplast_bot/deploy/unitplast.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable unitplast
```

### 2.3 Test Service (Local Only)

```bash
# Test without starting permanently
sudo -u unitplast /opt/unitplast_bot/venv/bin/gunicorn \
    --workers 2 \
    --bind 127.0.0.1:5000 \
    app.app:create_app()
# Press Ctrl+C to stop
```

---

## 3️⃣ NGINX SETUP

### 3.1 Copy Nginx Configuration

```bash
sudo cp /opt/unitplast_bot/deploy/unitgroup.tech.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/unitgroup.tech.conf /etc/nginx/sites-enabled/
```

### 3.2 Remove Default Nginx Config

```bash
sudo rm -f /etc/nginx/sites-enabled/default
```

### 3.3 Test Nginx Configuration

```bash
sudo nginx -t
# Should output: nginx: configuration file test is successful
```

### 3.4 Reload Nginx

```bash
sudo systemctl reload nginx
```

---

## 4️⃣ SSL/HTTPS SETUP (Let's Encrypt)

### 4.1 Install SSL Certificate

```bash
sudo certbot --nginx \
    -d unitgroup.tech \
    -d www.unitgroup.tech \
    --non-interactive \
    --agree-tos \
    -m admin@unitgroup.tech
```

This will:
- Generate SSL certificate
- Update Nginx config automatically
- Set up auto-renewal

### 4.2 Verify Certificate

```bash
sudo certbot certificates
sudo ssl-update check unitgroup.tech
```

### 4.3 Test Auto-Renewal

```bash
sudo certbot renew --dry-run
```

---

## 5️⃣ START APPLICATION

### 5.1 Start Systemd Service

```bash
sudo systemctl start unitplast
sudo systemctl status unitplast
```

### 5.2 Check Logs

```bash
sudo journalctl -u unitplast -f
# or
tail -f /var/log/unitplast/error.log
tail -f /var/log/unitplast/access.log
```

### 5.3 Verify Application

```bash
curl http://localhost:5000/health
# Should return JSON: {"status": "OK", ...}

curl https://unitgroup.tech/health
# Should return: {"status": "OK", ...}
```

---

## 6️⃣ MONITORING & MAINTENANCE

### 6.1 Check Application Status

```bash
sudo systemctl status unitplast
ps aux | grep gunicorn
```

### 6.2 View Real-Time Logs

```bash
sudo journalctl -u unitplast -f --lines=50
```

### 6.3 Check Disk Space

```bash
df -h
du -sh /app/data
du -sh /var/log/unitplast
```

### 6.4 Certificate Renewal Status

```bash
sudo certbot certificates
sudo systemctl list-timers | grep cert
```

---

## 7️⃣ DEPLOYMENT UPDATES

### 7.1 Pull Latest Code

```bash
cd /opt/unitplast_bot
sudo -u unitplast git fetch origin
sudo -u unitplast git pull origin main
```

### 7.2 Update Dependencies

```bash
sudo -u unitplast /opt/unitplast_bot/venv/bin/pip install -r requirements.txt
```

### 7.3 Restart Application

```bash
sudo systemctl restart unitplast
sudo systemctl status unitplast
```

---

## 🔧 TROUBLESHOOTING

### Application not starting

```bash
# Check logs
sudo journalctl -u unitplast -n 50

# Check gunicorn directly
cd /opt/unitplast_bot
/opt/unitplast_bot/venv/bin/gunicorn --workers 1 --bind 127.0.0.1:5000 app.app:create_app()
```

### Nginx 502 Bad Gateway

```bash
# Check if application is running
sudo systemctl status unitplast

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Certificate issues

```bash
# Check certificate validity
sudo certbot certificates

# Renew manually
sudo certbot renew --force-renewal

# Check Nginx SSL config
sudo nginx -t
```

### Database permissions

```bash
# Ensure permissions are correct
sudo chown -R unitplast:unitplast /app/data

# Check database file
ls -la /app/data/unitplast.db
```

---

## 📊 SYSTEM RESOURCES

**Recommended Specs:**
- CPU: 1+ cores
- RAM: 512MB minimum, 1GB+ recommended
- Disk: 20GB+ (logs + database)
- Bandwidth: Unlimited (Flask app is lightweight)

**Typical Resource Usage:**
- CPU: <5% idle, <20% under load
- RAM: ~150MB (Flask + Gunicorn)
- Disk: ~100MB (application) + growth for logs/database

---

## 🔐 SECURITY CHECKLIST

- [ ] SSH key authentication configured (disable password login)
- [ ] Firewall (ufw) configured (allow 22, 80, 443 only)
- [ ] .env.production NOT in git
- [ ] Log rotation configured for /var/log/unitplast
- [ ] Regular backups of /app/data
- [ ] SSL certificate auto-renewal enabled
- [ ] Fail2ban configured (optional, for DDoS protection)

### Quick Security Setup

```bash
# Enable firewall
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# Configure log rotation
sudo cat > /etc/logrotate.d/unitplast << 'EOF'
/var/log/unitplast/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 unitplast unitplast
    sharedscripts
    postrotate
        sudo systemctl reload unitplast > /dev/null 2>&1 || true
    endscript
}
EOF
```

---

## 📞 SUPPORT

For issues:
1. Check logs: `sudo journalctl -u unitplast -f`
2. Verify connectivity: `curl https://unitgroup.tech/health`
3. Check resources: `free -h`, `df -h`
4. Review configuration: `sudo nginx -t`

---

## 📝 NEXT STEPS

1. Review all configuration files before deployment
2. Test locally with `./deploy/unitplast.service` in test mode
3. Create database backup strategy
4. Set up monitoring (optional)
5. Document any custom changes

---

**Version:** 1.0  
**Last Updated:** June 22, 2026  
**Domain:** unitgroup.tech  
**Status:** Ready for Deployment
