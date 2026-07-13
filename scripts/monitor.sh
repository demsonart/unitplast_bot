#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# UNITGROUP - Monitoring Script (check container health)
# ═══════════════════════════════════════════════════════════════════════════════

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$PROJECT_DIR"

# Load env
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

CONTAINERS=("unitgroup-nginx" "unitgroup-backend" "unitgroup-bot" "unitgroup-db")
ALERT_TOKEN="${ALERT_BOT_TOKEN}"
CHAT_ID="${ALERT_CHAT_ID}"

# Check each container
for CONTAINER in "${CONTAINERS[@]}"; do
    STATE=$(docker inspect -f '{{.State.Status}}' "$CONTAINER" 2>/dev/null || echo "not-found")
    HEALTH=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$CONTAINER" 2>/dev/null || echo "error")

    # Alert if not running or unhealthy
    if [ "$STATE" != "running" ] || [ "$HEALTH" = "unhealthy" ]; then
        MESSAGE="🚨 UNITGROUP ALERT: $CONTAINER
State: $STATE
Health: $HEALTH
Time: $(date '+%Y-%m-%d %H:%M:%S')"

        # Send Telegram alert if configured
        if [ -n "$ALERT_TOKEN" ] && [ -n "$CHAT_ID" ]; then
            curl -s -X POST "https://api.telegram.org/bot${ALERT_TOKEN}/sendMessage" \
                -d chat_id="${CHAT_ID}" \
                -d text="${MESSAGE}" \
                -d parse_mode="Markdown" >/dev/null 2>&1 || true
        fi

        echo "⚠️  $MESSAGE"
    else
        echo "✅ $CONTAINER: OK"
    fi
done
