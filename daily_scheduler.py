"""Daily backlink building scheduler for alfaapanels.com.

Run this script once; it stays alive and triggers the SEO agent every day
at the configured RUN_TIME. Alternatively, point a cron job at run_once.py
for OS-level scheduling.

Usage:
    python daily_scheduler.py              # runs daily at 08:00 (default)
    RUN_TIME=06:30 python daily_scheduler.py
"""

import logging
import os
import time
from datetime import datetime

import schedule

from offpage_seo_agent import ALFAAPANELS_CONFIG, run_offpage_seo_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

RUN_TIME = os.getenv("RUN_TIME", "08:00")


def daily_job():
    log.info("Starting daily backlink-building run for alfaapanels.com")
    try:
        report_path = run_offpage_seo_agent(**ALFAAPANELS_CONFIG)
        log.info("Run complete. Report: %s", report_path)
    except Exception:
        log.exception("SEO agent run failed")


def main():
    log.info("Scheduler starting — daily job at %s", RUN_TIME)
    schedule.every().day.at(RUN_TIME).do(daily_job)

    # Run immediately on first startup so today's report is generated right away.
    log.info("Running initial job now (%s)", datetime.now().strftime("%Y-%m-%d %H:%M"))
    daily_job()

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
