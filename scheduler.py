"""Run daily_backlink_builder once a day at a configurable time.

Usage:
    python scheduler.py               # runs at 08:00 every day
    python scheduler.py --time 06:30  # runs at 06:30 every day
    python scheduler.py --now         # run immediately then schedule
"""

import argparse
import schedule
import time
import logging
from daily_backlink_builder import run_daily

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def job():
    log.info("Starting daily backlink build for alfaapanels.com …")
    try:
        report = run_daily()
        log.info("Completed. Report: %s", report)
    except Exception as exc:
        log.exception("Daily build failed: %s", exc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--time", default="08:00", help="HH:MM daily run time (default 08:00)")
    parser.add_argument("--now", action="store_true", help="Run immediately before scheduling")
    args = parser.parse_args()

    if args.now:
        job()

    schedule.every().day.at(args.time).do(job)
    log.info("Scheduler active — running daily at %s", args.time)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
