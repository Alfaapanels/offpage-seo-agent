"""
Scheduler: runs daily_backlink_builder once per day at a configurable time.

Usage:
    python scheduler.py              # runs at 08:00 daily
    python scheduler.py --time 06:30 # runs at 06:30 daily
    python scheduler.py --now        # run immediately then start schedule
"""

import argparse
import logging
import schedule
import time
from daily_backlink_builder import run_daily_build

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def job():
    log.info("Starting daily backlink build job…")
    try:
        report_path = run_daily_build()
        log.info("Job complete. Report: %s", report_path)
    except Exception as exc:
        log.error("Job failed: %s", exc, exc_info=True)


def main():
    parser = argparse.ArgumentParser(description="Daily backlink builder scheduler")
    parser.add_argument("--time", default="08:00", help="Daily run time HH:MM (default 08:00)")
    parser.add_argument("--now", action="store_true", help="Run immediately before starting schedule")
    args = parser.parse_args()

    if args.now:
        log.info("Running immediately as requested…")
        job()

    schedule.every().day.at(args.time).do(job)
    log.info("Scheduler started — daily run at %s", args.time)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
