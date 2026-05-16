#!/usr/bin/env python3
"""
Daily scheduler for the alfaapanels.com backlink agent.

Usage:
  python daily_runner.py               # runs once immediately, then daily at 09:00
  python daily_runner.py --now         # run once right now and exit
  python daily_runner.py --time 08:30  # run daily at a custom time (HH:MM)

Cron alternative (no long-running process):
  0 9 * * * cd /path/to/offpage-seo-agent && python offpage_seo_agent.py >> logs/cron.log 2>&1
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import schedule

from offpage_seo_agent import run_daily_backlink_agent

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "runner.log"),
    ],
)
log = logging.getLogger(__name__)


def _job():
    log.info("Starting daily backlink session for alfaapanels.com…")
    try:
        report_path = run_daily_backlink_agent()
        log.info("Session complete. Report: %s", report_path)
    except Exception:
        log.exception("Session failed – will retry tomorrow")


def main():
    parser = argparse.ArgumentParser(description="Daily backlink agent scheduler")
    parser.add_argument("--now", action="store_true", help="Run once immediately and exit")
    parser.add_argument("--time", default="09:00", metavar="HH:MM", help="Daily run time (default: 09:00)")
    args = parser.parse_args()

    if args.now:
        _job()
        return

    run_time = args.time
    log.info("Scheduler starting – daily runs at %s", run_time)
    schedule.every().day.at(run_time).do(_job)

    # Run immediately on first start so there's no wait on day 1
    log.info("Running initial session now…")
    _job()

    log.info("Next run scheduled for %s tomorrow. Scheduler is running (Ctrl+C to stop).", run_time)
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
