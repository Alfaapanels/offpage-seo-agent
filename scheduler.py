"""
Daily scheduler for the alfaapanels.com backlink builder.

Runs daily_backlink_builder.run_daily() every day at a configurable time.

Usage:
    python scheduler.py                    # runs daily at 09:00 (default)
    DAILY_RUN_TIME=14:30 python scheduler.py

Alternative – use cron instead of running this process continuously:
    0 9 * * * cd /path/to/offpage-seo-agent && python daily_backlink_builder.py
"""

import logging
import os
import sys
import time
from datetime import datetime

import schedule
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

RUN_TIME = os.environ.get("DAILY_RUN_TIME", "09:00")


def job():
    from daily_backlink_builder import run_daily
    log.info("Scheduled job triggered at %s", datetime.now().isoformat())
    try:
        report_path = run_daily()
        log.info("Daily build complete → %s", report_path)
    except Exception:
        log.exception("Daily build failed")


def main():
    log.info("Scheduler starting – daily run at %s UTC", RUN_TIME)
    schedule.every().day.at(RUN_TIME).do(job)

    # Show next scheduled run
    next_run = schedule.next_run()
    log.info("Next run: %s", next_run)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
