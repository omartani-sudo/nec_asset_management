#!/bin/bash
# NEC Asset Management — Database & Media Backup
# Run nightly via cron (see setup-cron.sh). Backs up PostgreSQL + media
# files to /opt/nec_backups, keeps 14 days, optionally copies offsite.
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/opt/nec_asset_management}"
BACKUP_DIR="${BACKUP_DIR:-/opt/nec_backups}"
OFFSITE_DIR="${OFFSITE_DIR:-}"            # optional, e.g. /mnt/offsite-backups
RETENTION_DAYS="${RETENTION_DAYS:-14}"
TS=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
cd "$PROJECT_DIR"

# 1. PostgreSQL dump from the db container (credentials come from the container env)
docker compose exec -T db pg_dump -U nec_user -d nec_asset_management \
    | gzip > "$BACKUP_DIR/nec_db_$TS.sql.gz"
echo "[$(date)] DB dump: $BACKUP_DIR/nec_db_$TS.sql.gz ($(du -h "$BACKUP_DIR/nec_db_$TS.sql.gz" | cut -f1))"

# 2. Media files (photos) tarball via the web container's mounted volume
docker compose exec -T web tar -czf - -C /app/media . \
    > "$BACKUP_DIR/nec_media_$TS.tar.gz"
echo "[$(date)] Media backup: $BACKUP_DIR/nec_media_$TS.tar.gz ($(du -h "$BACKUP_DIR/nec_media_$TS.tar.gz" | cut -f1))"

# 3. Optional offsite copy
if [ -n "$OFFSITE_DIR" ]; then
    mkdir -p "$OFFSITE_DIR"
    cp "$BACKUP_DIR/nec_db_$TS.sql.gz" "$OFFSITE_DIR/"
    echo "[$(date)] Offsite copy: $OFFSITE_DIR/nec_db_$TS.sql.gz"
fi

# 4. Retention
find "$BACKUP_DIR" \( -name 'nec_db_*.sql.gz' -o -name 'nec_media_*.tar.gz' \) \
    -mtime +$RETENTION_DAYS -delete
echo "[$(date)] Retention: removed backups older than $RETENTION_DAYS days"

echo "[$(date)] Backup complete."
