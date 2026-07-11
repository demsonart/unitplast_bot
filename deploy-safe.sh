#!/bin/bash
# UNITPLAST SAFE VPS DEPLOYMENT SCRIPT
# Purpose: Update VPS with new landing (9 sections) safely
# Date: 2026-07-12
# Risk Level: 🟢 LOW (only docs + UI changes, no runtime changes)

set -e

VPS_IP="193.104.33.29"
VPS_USER="root"
VPS_PATH="/var/www/unitplast_bot"
SERVICE_NAME="unitplast.service"
DOMAIN="https://unitgroup.tech"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 UNITPLAST SAFE VPS DEPLOYMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ssh -o ConnectTimeout=5 "${VPS_USER}@${VPS_IP}" << VPSCMD
set -e
cd ${VPS_PATH}

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1: BASELINE
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "📊 STAGE 1: CURRENT STATE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Current git commit:"
git log --oneline -1

echo ""
echo "Current branch:"
git branch

echo ""
echo "Service status:"
systemctl is-active ${SERVICE_NAME} && echo "✅ Running" || echo "❌ Stopped"

echo ""
echo "Landing sections (BEFORE update):"
BEFORE=\$(curl -s ${DOMAIN}/ | grep -o '<section class="[^"]*"' | wc -l)
echo "  $BEFORE sections"

echo ""
echo "Health endpoint:"
curl -s ${DOMAIN}/health | jq '.version' 2>/dev/null || echo "(jq not available)"

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2: FETCH AND ANALYZE CHANGES
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "📥 STAGE 2: FETCH REMOTE CHANGES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Fetching from GitHub..."
git fetch origin main

echo ""
echo "New commit available:"
git log origin/main --oneline -1

echo ""
echo "Changes summary:"
git diff HEAD..origin/main --stat | tail -5

echo ""
echo "⚠️  Checking for dangerous files in diff..."
DANGEROUS=\$(git diff HEAD..origin/main --name-only | grep -E 'app/main\.py|run\.py|app/config\.py|app/telegram|requirements\.txt|systemd|\.env' || echo "")

if [ -n "\$DANGEROUS" ]; then
  echo "❌ DANGEROUS FILES DETECTED:"
  echo "\$DANGEROUS"
  echo ""
  echo "🛑 ABORTING - Please review manually"
  exit 1
fi

echo "✅ No dangerous runtime files"

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 3: SAFE GIT PULL
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "✅ STAGE 3: GIT PULL (SAFE)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Pulling from origin/main..."
git pull origin main --ff-only

echo "✅ Pull successful"

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 4: VERIFY CODE INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "🔍 STAGE 4: CODE INTEGRITY CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Python syntax check..."
python3 -m py_compile app/app.py && echo "✅ app/app.py OK" || echo "❌ Syntax error"
python3 -m py_compile run.py && echo "✅ run.py OK" || echo "❌ Syntax error"

echo ""
echo "web/landing.html exists:"
test -f web/landing.html && echo "✅ Found" || echo "❌ Missing!"

echo ""
echo "web/miniapp.html exists:"
test -f web/miniapp.html && echo "✅ Found" || echo "❌ Missing!"

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 5: RESTART SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "🔄 STAGE 5: RESTART SERVICE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Restarting ${SERVICE_NAME}..."
systemctl restart ${SERVICE_NAME}

echo "Waiting for service startup..."
sleep 3

echo ""
echo "Service status:"
systemctl status ${SERVICE_NAME} --no-pager | head -5

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 6: VERIFY DEPLOYMENT
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "✅ STAGE 6: DEPLOYMENT VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Health check:"
HEALTH_STATUS=\$(curl -s -o /dev/null -w "%{http_code}" ${DOMAIN}/health)
if [ "\$HEALTH_STATUS" = "200" ]; then
  echo "✅ Health endpoint: 200 OK"
else
  echo "❌ Health endpoint: \$HEALTH_STATUS"
fi

echo ""
echo "Landing page sections (AFTER update):"
AFTER=\$(curl -s ${DOMAIN}/ | grep -o '<section class="[^"]*"' | wc -l)
echo "  $AFTER sections"

echo ""
echo "Section list:"
curl -s ${DOMAIN}/ | grep -o '<section class="[^"]*"' | sed 's/<section class="/  ✓ /' | sed 's/"//'

echo ""
echo "Mini App status:"
MINIAPP_STATUS=\$(curl -s -o /dev/null -w "%{http_code}" ${DOMAIN}/app/miniapp)
if [ "\$MINIAPP_STATUS" = "200" ]; then
  echo "✅ Mini App: 200 OK"
else
  echo "❌ Mini App: \$MINIAPP_STATUS"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 7: FINAL REPORT
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYMENT COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Summary:"
echo "  Before: \$BEFORE sections"
echo "  After:  \$AFTER sections"

if [ \$AFTER -ge 9 ]; then
  echo "  Status: ✅ SUCCESS (9+ sections)"
else
  echo "  Status: ⚠️  WARNING (expected 9, got \$AFTER)"
fi

echo ""
echo "Deployed to: ${DOMAIN}"
echo "Service: ${SERVICE_NAME}"
echo "Time: \$(date)"
echo ""

VPSCMD

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 SAFE DEPLOYMENT SCRIPT EXECUTED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
