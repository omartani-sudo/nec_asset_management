#!/bin/bash
# NEC Asset Management — Auto Deploy Script
# Runs via cron on VPS. Checks for new commits, pulls, rebuilds if needed.
set -e

# ---- Config: adjust these paths on your VPS ----
PROJECT_DIR="/opt/nec_asset_management"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
LOG_FILE="/var/log/nec-deploy.log"

# ---- Script ----
exec 1> >(tee -a "$LOG_FILE") 2>&1

cd "$PROJECT_DIR" || { echo "[$(date)] ERROR: $PROJECT_DIR not found"; exit 1; }

echo "[$(date)] Checking for updates..."

# Ensure we have the latest remote refs
git fetch origin main 2>/dev/null || { echo "[$(date)] ERROR: git fetch failed"; exit 1; }

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "[$(date)] New commits found ($(git log --oneline $LOCAL..$REMOTE | wc -l) commits)"
    echo "[$(date)] Pulling changes..."
    git pull origin main

    echo "[$(date)] Rebuilding containers..."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build

    echo "[$(date)] Restarting services..."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --force-recreate --remove-orphans

    echo "[$(date)] Running migrations..."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T web python manage.py migrate --noinput 2>/dev/null || true

    echo "[$(date)] Collecting static files..."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T web python manage.py collectstatic --noinput 2>/dev/null || true

    echo "[$(date)] Deploy complete. Now running: $(git rev-parse --short HEAD)"
else
    echo "[$(date)] Already up to date ($(git rev-parse --short HEAD))"
fi
