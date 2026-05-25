#!/bin/bash
# =============================================================
# setup_cron.sh — Register the ETL pipeline as a cron job
# =============================================================
# This script adds a crontab entry to run etl_pipeline.py
# every day at 2:00 AM.
#
# Usage:
#   chmod +x setup_cron.sh
#   ./setup_cron.sh
# =============================================================

# Absolute path to this project (edit if needed)
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="$(which python3)"
LOG_FILE="$PROJECT_DIR/logs/cron.log"

CRON_JOB="0 2 * * * cd $PROJECT_DIR && $PYTHON_BIN etl_pipeline.py >> $LOG_FILE 2>&1"

# Check if cron job already exists
(crontab -l 2>/dev/null | grep -q "etl_pipeline.py") && {
    echo "Cron job already registered. Nothing changed."
    exit 0
}

# Append new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Cron job added:"
echo "   $CRON_JOB"
echo ""
echo "Verify with:  crontab -l"
echo "Remove with:  crontab -e   (then delete the line manually)"
