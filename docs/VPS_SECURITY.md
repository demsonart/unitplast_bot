# 🔒 UNITGROUP - VPS Security Guide

**VPS IP:** 193.104.33.29  
**OS:** Ubuntu 22.04 LTS  
**Firewall:** UFW

---

## Security Checklist

### 1. SSH Security

✅ **Disable password login:**
```bash
sudo nano /etc/ssh/sshd_config
# Set:
# PermitRootLogin no
# PasswordAuthentication no
# PubkeyAuthentication yes
sudo systemctl restart sshd
```

✅ **Use SSH keys only:**
```bash
ssh-keygen -t ed25519 -C "deploy@unitgroup"
ssh-copy-id -i ~/.ssh/id_ed25519.pub deploy@193.104.33.29
```

✅ **Test login with key before disabling passwords:**
```bash
ssh -i ~/.ssh/id_ed25519 deploy@193.104.33.29
```

### 2. Firewall (UFW)

✅ **Setup UFW:**
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

✅ **Verify:**
```bash
sudo ufw status verbose
sudo ss -tulpn
```

### 3. Docker Security

❌ **NEVER expose these to internet:**
- PostgreSQL port 5432
- Redis port 6379
- Backend internal ports
- Admin panels

✅ **Check exposed ports:**
```bash
docker compose ps
sudo ss -tulpn | grep -E "LISTEN|Active"
```

✅ **Correct docker-compose.yml:**
```yaml
db:
  ports:
    - "127.0.0.1:5432:5432"  # ✅ Local only
    # NOT: "5432:5432"        # ❌ Never do this
```

### 4. Environment Variables

❌ **Never commit these:**
- `.env` file
- `TELEGRAM_BOT_TOKEN`
- `POSTGRES_PASSWORD`
- `YANDEX_PASSWORD`
- API keys

✅ **Safe approach:**
```bash
# On VPS
cp .env.example .env
nano .env  # Edit with real values
chmod 600 .env  # Read-only by owner
```

✅ **Check git is clean:**
```bash
git status
git ls-files | grep ".env"  # Should be empty
```

### 5. File Permissions

✅ **Set proper permissions:**
```bash
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 700 ~/.ssh
chmod 700 ~/backups
chmod 600 ~/backups/*
```

### 6. Database Security

✅ **PostgreSQL is not accessible from outside:**
```bash
# This should fail:
nc -zv 193.104.33.29 5432  # Connection refused ✅

# This should work:
docker compose exec db psql -U unitgroup
```

✅ **Strong database password:**
```env
POSTGRES_PASSWORD=generate_random_32_char_string
```

### 7. SSL/TLS

✅ **Certificate is valid:**
```bash
certbot certificates
```

✅ **Auto-renewal works:**
```bash
sudo certbot renew --dry-run
```

### 8. Monitoring & Alerts

✅ **Telegram alerts for failures:**
```bash
# Test alert
curl -X POST "https://api.telegram.org/bot${ALERT_BOT_TOKEN}/sendMessage" \
    -d chat_id="${ALERT_CHAT_ID}" \
    -d text="Test alert from UNITGROUP"
```

✅ **Monitor runs every minute:**
```bash
crontab -l | grep monitor
# Output: * * * * * /home/deploy/unitgroup_ai/scripts/monitor.sh
```

### 9. Logs & Disk Space

✅ **Monitor disk usage:**
```bash
df -h
du -sh /var/lib/docker/
```

✅ **Log rotation is configured:**
```bash
docker compose config | grep -A 5 "logging:"
# Should show max-size and max-file
```

### 10. Backups

✅ **Backups run daily:**
```bash
crontab -l | grep backup
# Output: 0 3 * * * /home/deploy/unitgroup_ai/scripts/backup.sh
```

✅ **Test restore procedure (monthly):**
```bash
cd /home/deploy/unitgroup_ai

# Create test DB
docker compose exec -T db createdb -U unitgroup unitgroup_test

# Restore
cat backups/latest.sql | \
    docker compose exec -T db psql -U unitgroup -d unitgroup_test

# Verify
docker compose exec db psql -U unitgroup -d unitgroup_test -c "SELECT COUNT(*) FROM orders;"

# Cleanup
docker compose exec -T db dropdb -U unitgroup unitgroup_test
```

---

## Security Incident Response

### If .env is exposed

**Immediately:**
1. Rotate all tokens and passwords
2. Update `.env` with new values
3. Remove old `.env` from Git history
4. Restart containers with new secrets

```bash
# Rotate Telegram token (get new bot from @BotFather)
# Rotate PostgreSQL password:
docker compose exec db psql -U postgres
ALTER USER unitgroup WITH PASSWORD 'new_password';

# Update .env and restart
nano .env
docker compose up -d --build
```

### If server is compromised

1. Take snapshot
2. Backup database and files
3. Terminate server and launch new one
4. Restore from backups

### If SSL certificate expires

```bash
certbot renew --force-renewal
./scripts/deploy.sh
```

---

## Auditing

### Check what's listening

```bash
sudo ss -tulpn
```

Should show only:
- 22/tcp (SSH)
- 80/tcp (HTTP)
- 443/tcp (HTTPS)

### Check Docker images

```bash
docker images
docker system df
```

### Check for unauthorized containers

```bash
docker ps -a
docker container ls --all
```

---

## Compliance

- ✅ No plaintext passwords
- ✅ No exposed databases
- ✅ No SSH with passwords
- ✅ No unnecessary open ports
- ✅ Regular backups with testing
- ✅ HTTPS everywhere
- ✅ Monitoring & alerts
- ✅ Secrets not in version control

---

## Monthly Security Review

```bash
#!/bin/bash
echo "📋 Monthly Security Review"

# 1. Check UFW rules
sudo ufw status verbose

# 2. Check SSH config
sudo grep -E "^(PermitRootLogin|PasswordAuthentication)" /etc/ssh/sshd_config

# 3. Check exposed ports
sudo ss -tulpn

# 4. Check .env not in Git
git ls-files | grep ".env"

# 5. Check backups exist and are recent
ls -l backups/ | tail -5

# 6. Check certificate expiry
certbot certificates

# 7. Check disk space
df -h

# 8. Review logs for errors
docker compose logs --tail=50 | grep -i error
```

---

## References

- [SSH Security](https://linux.die.net/man/5/sshd_config)
- [UFW Firewall](https://help.ubuntu.com/community/UFW)
- [Docker Security](https://docs.docker.com/engine/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/sql-createrole.html)
- [Certbot](https://certbot.eff.org/)

