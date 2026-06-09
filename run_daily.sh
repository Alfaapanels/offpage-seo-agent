#!/usr/bin/env bash
# Daily backlink-building runner for alfaapanels.com
# Add to cron: 0 8 * * * /path/to/offpage-seo-agent/run_daily.sh >> /path/to/offpage-seo-agent/logs/cron.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p logs reports

LOG_FILE="logs/run_$(date +%Y-%m-%d).log"

echo "========================================" | tee -a "$LOG_FILE"
echo "Run started: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "ERROR: ANTHROPIC_API_KEY is not set." | tee -a "$LOG_FILE"
    exit 1
fi

python3 offpage_seo_agent.py 2>&1 | tee -a "$LOG_FILE"

echo "Run finished: $(date)" | tee -a "$LOG_FILE"
