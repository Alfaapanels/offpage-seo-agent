#!/usr/bin/env bash
# Run daily at 9 AM via cron:
#   0 9 * * * /bin/bash /path/to/offpage-seo-agent/run_daily.sh >> /var/log/backlink_builder.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting daily backlink builder for alfaapanels.com"

# Activate virtualenv if present
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Require ANTHROPIC_API_KEY
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "[ERROR] ANTHROPIC_API_KEY is not set. Export it before running." >&2
    exit 1
fi

python daily_backlink_builder.py

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Done."
