#!/bin/bash
set -e

# ═══════════════════════════════════════════════════════════════════════════════
# UNITGROUP - PostgreSQL Backup Script
# ═══════════════════════════════════════════════════════════════════════════════

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +%F_%H-%M-%S)

mkdir -p "$BACKUP_DIR"

echo "📦 Backing up PostgreSQL database..."

cd "$PROJECT_DIR"

# Dump database
docker compose exec -T db pg_dump \
  -U "${POSTGRES_USER:-unitgroup}" \
  "${POSTGRES_DB:-unitgroup}" > "$BACKUP_DIR/unitgroup_${DATE}.sql"

echo "✅ Backup created: $BACKUP_DIR/unitgroup_${DATE}.sql"

# Remove old backups (keep last 30 days)
echo "🧹 Cleaning old backups (older than 30 days)..."
find "$BACKUP_DIR" -type f -name "unitgroup_*.sql" -mtime +30 -delete

echo "✅ Backup complete!"
