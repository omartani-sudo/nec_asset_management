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
