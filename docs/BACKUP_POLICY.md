# 💾 UNITGROUP - Backup & Recovery Policy

**Backup Location:** `/home/deploy/unitgroup_ai/backups/`  
**Backup Schedule:** Daily at 3:00 AM UTC  
**Retention:** 30 days  
**Database:** PostgreSQL

---

## Backup Strategy

### What We Backup

✅ **PostgreSQL Database**
- All orders
- All users  
- All calculations
- Configuration

❌ **NOT backed up** (can be recreated)
- Docker images
- Node modules
- Python venv
- Build artifacts

### Backup Schedule

```
Every day at 3:00 AM UTC
Retention: Last 30 days
Format: SQL dump (plaintext)
Size: ~10-50 MB per backup
```

---

## Automated Backup

### Cron Job

```bash
crontab -l
# Output:
# 0 3 * * * /home/deploy/unitgroup_ai/scripts/backup.sh
```

### Manual Backup

```bash
cd /home/deploy/unitgroup_ai
./scripts/backup.sh
```

### Output

```
📦 Backing up PostgreSQL database...
pg_dump: saving database schema... OK
pg_dump: saving table public.orders... OK
✅ Backup created: backups/unitgroup_2024-01-15_03-00-00.sql
🧹 Cleaning old backups (older than 30 days)...
✅ Backup complete!
```

---

## Backup Verification

### List Recent Backups

```bash
ls -lh backups/ | tail -10
```

### Check Backup Integrity

```bash
# Verify file can be read
head -c 200 backups/unitgroup_2024-01-15_03-00-00.sql

# Count tables in backup
grep "CREATE TABLE" backups/unitgroup_2024-01-15_03-00-00.sql | wc -l
```

### Estimate Restore Time

```bash
# Get file size
du -h backups/unitgroup_2024-01-15_03-00-00.sql

# Rough estimate: 1MB takes ~1 second to restore
# 50MB backup ≈ 50 seconds
```

---

## Recovery Procedure

### Scenario 1: Data Corruption

**Symptom:** Database has bad data  
**Recovery Time:** 5 minutes  

```bash
cd /home/deploy/unitgroup_ai

# 1. Stop the app (optional, to prevent writes during restore)
docker compose down

# 2. Restore from backup
cat backups/unitgroup_2024-01-15_03-00-00.sql | \
    docker compose exec -T db psql -U unitgroup -d unitgroup

# 3. Start the app
docker compose up -d

# 4. Verify
curl https://unitgroup.tech/api/health
```

### Scenario 2: Accidental Deletion

**Symptom:** Some data was deleted  
**Recovery Time:** 10 minutes  

```bash
# 1. Create temporary DB
docker compose exec -T db createdb -U unitgroup unitgroup_restore

# 2. Restore to temp DB
cat backups/unitgroup_2024-01-15_03-00-00.sql | \
    docker compose exec -T db psql -U unitgroup -d unitgroup_restore

# 3. Query restored data
docker compose exec db psql -U unitgroup -d unitgroup_restore \
    -c "SELECT * FROM orders ORDER BY created_at DESC LIMIT 10;"

# 4. Manually copy data back to production DB
docker compose exec db psql -U unitgroup -d unitgroup \
    -c "INSERT INTO orders SELECT * FROM unitgroup_restore.orders WHERE id > 1000;"

# 5. Cleanup
docker compose exec -T db dropdb -U unitgroup unitgroup_restore
```

### Scenario 3: Full Database Corruption

**Symptom:** DB won't start  
**Recovery Time:** 15 minutes  

```bash
cd /home/deploy/unitgroup_ai

# 1. Stop services
docker compose down

# 2. Stop and remove DB container
docker stop unitgroup-db
docker rm unitgroup-db

# 3. Remove data volume (⚠️  THIS IS DESTRUCTIVE)
docker volume rm unitgroup_ai_pgdata

# 4. Start fresh DB
docker compose up -d db

# 5. Wait for DB to initialize
sleep 5

# 6. Create database
docker compose exec -T db createdb -U unitgroup -d unitgroup

# 7. Restore from backup
cat backups/unitgroup_2024-01-15_03-00-00.sql | \
    docker compose exec -T db psql -U unitgroup -d unitgroup

# 8. Start all services
docker compose up -d

# 9. Verify
docker compose logs db | tail -20
```

### Scenario 4: Server Disaster

**Symptom:** Entire VPS is gone  
**Recovery Time:** 30 minutes  

```bash
# On new VPS (193.104.33.29)

# 1. Install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# 2. Clone repo
git clone https://github.com/demsonart/unitplast_bot.git
cd unitplast_bot

# 3. Restore .env
# (Get from secure location or recreate)
cp .env.example .env
nano .env

# 4. Start services
docker compose up -d

# 5. Restore database
cat backups/unitgroup_latest.sql | \
    docker compose exec -T db psql -U unitgroup -d unitgroup

# 6. Get SSL certificate
certbot certonly --standalone -d unitgroup.tech

# 7. Update deployment
docker compose restart nginx
```

---

## Monthly Verification

Run this script monthly to verify backups work:

```bash
#!/bin/bash
set -e

PROJECT_DIR="/home/deploy/unitgroup_ai"
BACKUP_DIR="$PROJECT_DIR/backups"

cd "$PROJECT_DIR"

echo "🧪 Monthly Backup Verification"

# Get latest backup
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/unitgroup_*.sql 2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ No backups found!"
    exit 1
fi

echo "📦 Testing restore from: $LATEST_BACKUP"

# Create test DB
docker compose exec -T db createdb -U unitgroup unitgroup_verify || true

# Restore
cat "$LATEST_BACKUP" | \
    docker compose exec -T db psql -U unitgroup -d unitgroup_verify 2>/dev/null

# Verify data exists
COUNT=$(docker compose exec -T db psql -U unitgroup -d unitgroup_verify -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null || echo "0")

if [ "$COUNT" -gt 0 ]; then
    echo "✅ Backup verified: $COUNT tables restored"
else
    echo "❌ Backup verification failed!"
fi

# Cleanup
docker compose exec -T db dropdb -U unitgroup unitgroup_verify || true

echo "✅ Verification complete"
```

Save as `scripts/verify-backup.sh`:
```bash
chmod +x scripts/verify-backup.sh
./scripts/verify-backup.sh
```

---

## Retention Policy

| Age | Action |
|-----|--------|
| 0-7 days | Keep all |
| 7-30 days | Keep daily |
| 30+ days | Delete |

Automatic deletion happens in `scripts/backup.sh`:
```bash
find "$BACKUP_DIR" -type f -name "unitgroup_*.sql" -mtime +30 -delete
```

---

## Off-Site Backup (Optional)

To protect against VPS data center disaster:

```bash
# Upload to S3
aws s3 cp backups/unitgroup_latest.sql s3://unitgroup-backups/

# Or to Google Drive
gdrive upload backups/unitgroup_latest.sql

# Or to external server
scp backups/unitgroup_latest.sql backup-user@backup-server:/backups/
```

Add to cron after daily backup:
```bash
0 4 * * * aws s3 sync /home/deploy/unitgroup_ai/backups/ s3://unitgroup-backups/
```

---

## Disaster Recovery Plan

### Lost Latest Backup
→ Restore from 2nd most recent backup  
→ Replay logs/transactions manually if possible  

### Lost All Backups
→ Try to recover from Docker volume snapshots  
→ Use application crash recovery features  

### VPS Provider Outage
→ Check backup copies on off-site storage  
→ Spin up new VPS  
→ Restore from off-site backup  

---

## Testing Schedule

- **Weekly:** Verify latest backup file exists
- **Monthly:** Test restore to temp DB
- **Quarterly:** Full disaster recovery drill
- **Annually:** Review and update backup policy

---

## References

- [PostgreSQL pg_dump](https://www.postgresql.org/docs/current/app-pgdump.html)
- [PostgreSQL psql](https://www.postgresql.org/docs/current/app-psql.html)
- [Docker Volume Backups](https://docs.docker.com/storage/volumes/)
- [3-2-1 Backup Rule](https://www.backblaze.com/blog/the-3-2-1-backup-strategy/)

