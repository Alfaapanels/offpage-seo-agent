#!/usr/bin/env bash
# Installs a daily cron job that runs the backlink builder at 09:00 every morning.
# Usage: bash setup_cron.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$(command -v python3 || command -v python)"
CRON_CMD="0 9 * * * cd ${SCRIPT_DIR} && ${PYTHON} daily_backlink_builder.py >> ${SCRIPT_DIR}/cron.log 2>&1"

# Append only if the job isn't already registered
if crontab -l 2>/dev/null | grep -qF "daily_backlink_builder.py"; then
    echo "Cron job already installed — no changes made."
else
    (crontab -l 2>/dev/null; echo "${CRON_CMD}") | crontab -
    echo "Cron job installed: runs daily at 09:00"
    echo "  Command: ${CRON_CMD}"
fi

echo ""
echo "Current crontab:"
crontab -l
