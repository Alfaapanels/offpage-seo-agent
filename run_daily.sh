#!/bin/bash
# Daily cron runner for the alfaapanels.com backlink builder.
# Add to crontab:  0 8 * * * /path/to/offpage-seo-agent/run_daily.sh >> /path/to/offpage-seo-agent/cron.log 2>&1

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting daily backlink builder..."
python daily_backlink_builder.py
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Done."
