#!/bin/bash
set -e

# ═══════════════════════════════════════════════════════════════════════════════
# UNITGROUP - Deploy Script
# ═══════════════════════════════════════════════════════════════════════════════

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 UNITGROUP DEPLOYMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Git pull
echo -e "\n📦 Pulling latest code..."
git pull origin main

# 2. Docker build
echo -e "\n🐳 Building Docker containers..."
docker compose build

# 3. Docker up
echo -e "\n🚀 Starting containers..."
docker compose up -d

# 4. Wait for services
echo -e "\n⏳ Waiting for services to start..."
sleep 5

# 5. Check health
echo -e "\n🏥 Checking health..."
docker compose ps

# 6. Check API
echo -e "\n✅ Testing API health..."
if curl -sf http://localhost/health > /dev/null 2>&1; then
    echo "✅ Landing page health: OK"
else
    echo "❌ Landing page health: FAILED"
    docker compose logs nginx | tail -20
fi

if curl -sf http://localhost/api/health > /dev/null 2>&1; then
    echo "✅ Backend health: OK"
else
    echo "❌ Backend health: FAILED"
    docker compose logs backend | tail -20
fi

echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Deployment complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
