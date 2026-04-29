"""
Daily backlink builder scheduler for alfaapanels.com.

Run this script to start the scheduler. It will:
  - Execute the daily backlink builder immediately on startup.
  - Re-run every day at RUN_AT_TIME (default 09:00).

Usage:
  python scheduler.py               # run at 09:00 daily
  python scheduler.py --time 08:30  # custom time
  python scheduler.py --now         # run once immediately and exit

To run as a background service, use nohup or a systemd unit:
  nohup python scheduler.py > scheduler.log 2>&1 &
"""

import argparse
import logging
import sys
import time
from datetime import datetime

import schedule

from daily_backlink_builder import run_daily_backlink_builder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

DEFAULT_RUN_TIME = "09:00"


def job() -> None:
    log.info("Starting daily backlink builder for alfaapanels.com …")
    try:
        report_file = run_daily_backlink_builder()
        log.info("Completed. Report: %s", report_file)
    except Exception as exc:
        log.error("Daily builder failed: %s", exc, exc_info=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily backlink builder scheduler")
    parser.add_argument(
        "--time",
        default=DEFAULT_RUN_TIME,
        help=f"Time to run daily (HH:MM, 24-hour). Default: {DEFAULT_RUN_TIME}",
    )
    parser.add_argument(
        "--now",
        action="store_true",
        help="Run once immediately and exit (no scheduling)",
    )
    args = parser.parse_args()

    if args.now:
        job()
        return

    schedule.every().day.at(args.time).do(job)
    log.info(
        "Scheduler started. Daily backlink builder will run at %s every day.", args.time
    )
    log.info("Press Ctrl+C to stop.\n")

    # Run immediately on first start so there is no wait on day one.
    job()

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
