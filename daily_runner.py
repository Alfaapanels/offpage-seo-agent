"""Daily scheduler for the alfaapanels.com backlink building agent.

Run this script to start the scheduler. It will execute the backlink agent
immediately on startup and then again every day at 09:00.

Usage:
    python daily_runner.py

To run at a different time, change the schedule below.
"""

import logging
import time

import schedule

from offpage_seo_agent import run_offpage_seo_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler("backlink_scheduler.log"),
        logging.StreamHandler(),
    ],
)


def daily_job() -> None:
    logging.info("Starting daily backlink building run for alfaapanels.com")
    try:
        run_offpage_seo_agent()
        logging.info("Daily backlink building run complete")
    except Exception as exc:
        logging.error("Daily run failed: %s", exc, exc_info=True)


# Run every day at 09:00 local time.  Change the time string to suit your timezone.
schedule.every().day.at("09:00").do(daily_job)

if __name__ == "__main__":
    logging.info("Backlink builder scheduler started — running now, then daily at 09:00")
    daily_job()  # Run immediately so you don't wait until 09:00 on first launch
    while True:
        schedule.run_pending()
        time.sleep(60)
