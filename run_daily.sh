#!/usr/bin/env bash
# Daily backlink builder for alfaapanels.com
# Add to crontab: 0 9 * * * /path/to/run_daily.sh >> /var/log/backlink_builder.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "ERROR: ANTHROPIC_API_KEY is not set" >&2
  exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting daily backlink build for alfaapanels.com"
python daily_backlink_builder.py
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Done"
