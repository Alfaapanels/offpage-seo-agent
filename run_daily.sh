#!/usr/bin/env bash
# Daily backlink builder runner for alfaapanels.com
# Add to cron:  0 9 * * * /path/to/offpage-seo-agent/run_daily.sh >> /path/to/offpage-seo-agent/cron.log 2>&1

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "Running daily backlink builder: $(date)"
echo "========================================"

# Activate virtualenv if present
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Verify API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY is not set. Exiting."
    exit 1
fi

python daily_backlink_builder.py
echo "Done: $(date)"
