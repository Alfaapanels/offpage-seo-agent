#!/usr/bin/env bash
# Sets up a cron job to run the daily backlink builder at 08:00 every day.
# Run once: bash setup_cron.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$(which python3)"
CRON_JOB="0 8 * * * cd $SCRIPT_DIR && ANTHROPIC_API_KEY=\$ANTHROPIC_API_KEY $PYTHON daily_backlink_builder.py >> $SCRIPT_DIR/cron.log 2>&1"

# Check if the cron job already exists
if crontab -l 2>/dev/null | grep -q "daily_backlink_builder.py"; then
    echo "Cron job already exists. No changes made."
else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Cron job installed: runs daily at 08:00"
    echo "Logs will be written to: $SCRIPT_DIR/cron.log"
fi

echo ""
echo "Current crontab:"
crontab -l
