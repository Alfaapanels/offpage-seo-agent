#!/usr/bin/env python3
"""Scheduler: runs the alfaapanels.com backlink building agent every day at 09:00 UTC."""

import logging
import schedule
import time

from offpage_seo_agent import run_daily_backlink_building

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("backlink_agent.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def job():
    logger.info("Scheduled daily backlink job triggered.")
    try:
        run_daily_backlink_building()
    except Exception as e:
        logger.error("Daily backlink job failed: %s", e, exc_info=True)


if __name__ == "__main__":
    logger.info("Daily backlink scheduler started – runs every day at 09:00 UTC.")
    logger.info("Press Ctrl+C to stop.\n")

    # Run immediately on startup so the first day isn't skipped
    job()

    schedule.every().day.at("09:00").do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)
