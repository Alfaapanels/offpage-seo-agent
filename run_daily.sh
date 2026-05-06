#!/bin/bash
# Daily backlink builder for alfaapanels.com
# Add to cron: 0 9 * * * /home/user/offpage-seo-agent/run_daily.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/daily_cron.log"

cd "$SCRIPT_DIR"

echo "$(date '+%Y-%m-%d %H:%M:%S') — Starting daily backlink builder" >> "$LOG_FILE"
python3 daily_backlink_builder.py >> "$LOG_FILE" 2>&1
echo "$(date '+%Y-%m-%d %H:%M:%S') — Done" >> "$LOG_FILE"
