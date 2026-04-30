#!/bin/bash
# Run the daily backlink builder for alfaapanels.com
# Schedule with cron: 0 9 * * * /path/to/run_daily.sh >> /path/to/cron.log 2>&1

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY is not set"
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting daily backlink builder..."
python alfaapanels_daily_backlinks.py
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Done."
