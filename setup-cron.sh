#!/bin/bash
# NEC Asset Management — VPS Cron Setup
# Run this ONCE on the VPS to install the auto-deploy cron job.
#
# Usage (on VPS):
#   chmod +x setup-cron.sh
#   ./setup-cron.sh
#
# This will:
#   1. Copy deploy.sh to /opt/nec_asset_management/deploy.sh
#   2. Add a cron entry that runs every 2 minutes
#   3. Create log directory

set -e

DEPLOY_SCRIPT="deploy.sh"
PROJECT_DIR="/opt/nec_asset_management"
CRON_SCHEDULE="*/2 * * * *"
CRON_CMD="cd $PROJECT_DIR && bash deploy.sh >> /var/log/nec-deploy.log 2>&1"

echo "=== NEC Asset Management — Cron Setup ==="
echo ""

# Step 1: Ensure project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: $PROJECT_DIR not found."
    echo "Clone the repo first: git clone https://github.com/omartani-sudo/nec_asset_management.git $PROJECT_DIR"
    exit 1
fi
echo "[OK] Project directory exists: $PROJECT_DIR"

# Step 2: Copy deploy script
if [ -f "./$DEPLOY_SCRIPT" ]; then
    cp "./$DEPLOY_SCRIPT" "$PROJECT_DIR/$DEPLOY_SCRIPT"
    chmod +x "$PROJECT_DIR/$DEPLOY_SCRIPT"
    echo "[OK] Deploy script installed: $PROJECT_DIR/$DEPLOY_SCRIPT"
else
    echo "ERROR: $DEPLOY_SCRIPT not found in current directory."
    echo "Run this script from the repo root where deploy.sh exists."
    exit 1
fi

# Step 3: Create log directory
mkdir -p /var/log
touch /var/log/nec-deploy.log
echo "[OK] Log file ready: /var/log/nec-deploy.log"

# Step 4: Add cron entry
if crontab -l 2>/dev/null | grep -q "nec_asset_management"; then
    echo "[SKIP] Cron entry already exists for NEC"
else
    (crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $CRON_CMD") | crontab -
    echo "[OK] Cron entry added: $CRON_SCHEDULE $CRON_CMD"
fi

# Step 5: Add nightly DB/media backup cron (02:17 daily)
BACKUP_CRON_CMD="cd $PROJECT_DIR && bash backups/backup.sh >> /var/log/nec-backup.log 2>&1"
if crontab -l 2>/dev/null | grep -q "backups/backup.sh"; then
    echo "[SKIP] Backup cron already exists"
else
    (crontab -l 2>/dev/null; echo "17 2 * * * $BACKUP_CRON_CMD") | crontab -
    echo "[OK] Backup cron added: daily 02:17 -> $BACKUP_CRON_CMD"
fi

# Step 6: Add daily reorder email alerts cron (07:23 daily)
REORDER_CRON_CMD="cd $PROJECT_DIR && docker compose exec -T web python manage.py send_reorder_alerts >> /var/log/nec-reorder.log 2>&1"
if crontab -l 2>/dev/null | grep -q "send_reorder_alerts"; then
    echo "[SKIP] Reorder alerts cron already exists"
else
    (crontab -l 2>/dev/null; echo "23 7 * * * $REORDER_CRON_CMD") | crontab -
    echo "[OK] Reorder alerts cron added: daily 07:23 -> $REORDER_CRON_CMD"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Cron schedule: Every 2 minutes"
echo "Deploy script: $PROJECT_DIR/deploy.sh"
echo "Log file:      /var/log/nec-deploy.log"
echo ""
echo "To test manually: cd $PROJECT_DIR && bash deploy.sh"
echo "To watch logs:    tail -f /var/log/nec-deploy.log"
echo "To list crons:    crontab -l"
