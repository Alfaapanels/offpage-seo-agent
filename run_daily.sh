#!/usr/bin/env bash
# Daily Backlink Builder — cron wrapper for alfaapanels.com
#
# Add to crontab to run every day at 8:00 AM:
#   0 8 * * * /path/to/offpage-seo-agent/run_daily.sh >> /path/to/offpage-seo-agent/cron.log 2>&1
#
# Or with a virtual environment:
#   0 8 * * * cd /path/to/offpage-seo-agent && bash run_daily.sh >> cron.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo "  Alfa Panels — Daily Backlink Builder"
echo "  Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Require ANTHROPIC_API_KEY
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "ERROR: ANTHROPIC_API_KEY environment variable is not set." >&2
    exit 1
fi

python daily_backlink_builder.py "$@"

echo "Finished: $(date '+%Y-%m-%d %H:%M:%S')"
