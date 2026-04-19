"""
Daily backlink builder for alfaapanels.com.

Run once to start the scheduler:
    python daily_runner.py

Or run immediately (skip scheduler):
    python daily_runner.py --now
"""

import argparse
import logging
import sys
import time
from datetime import datetime

import schedule

from offpage_seo_agent import run_offpage_seo_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("backlink_builder.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

RUN_TIME = "08:00"  # Run daily at 08:00 local time


def job():
    log.info("Starting daily backlink build for alfaapanels.com")
    try:
        run_offpage_seo_agent()
        log.info("Daily backlink build completed successfully")
    except Exception as e:
        log.error(f"Backlink build failed: {e}", exc_info=True)


def main():
    parser = argparse.ArgumentParser(description="Daily backlink builder for alfaapanels.com")
    parser.add_argument("--now", action="store_true", help="Run immediately instead of waiting for scheduled time")
    args = parser.parse_args()

    if args.now:
        log.info("Running immediately (--now flag)")
        job()
        return

    log.info(f"Scheduling daily backlink build at {RUN_TIME} every day")
    schedule.every().day.at(RUN_TIME).do(job)

    next_run = schedule.next_run()
    log.info(f"Next run: {next_run}")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
