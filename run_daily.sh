#!/usr/bin/env bash
# Daily backlink builder runner for alfaapanels.com
# Add to crontab with:  0 8 * * * /path/to/run_daily.sh >> /path/to/cron.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if present
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting daily backlink session for alfaapanels.com"

python daily_backlink_builder.py

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Daily session complete"
