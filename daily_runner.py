"""
Daily backlink building scheduler for alfaapanels.com.
Runs the off-page SEO agent every day at RUN_TIME.
Start once and leave running: python daily_runner.py
"""

import logging
import schedule
import time
from offpage_seo_agent import run_offpage_seo_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("daily_runner.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "aluminum composite panels building facade cladding architectural"
COMPETITORS = ["alucobond.com", "reynobond.com", "alpolic.com", "dibond.com"]
RUN_TIME = "09:00"


def daily_backlink_job():
    logger.info(f"Starting daily backlink job for {DOMAIN}")
    try:
        report_file = run_offpage_seo_agent(
            your_domain=DOMAIN,
            brand_name=BRAND_NAME,
            niche=NICHE,
            competitors=COMPETITORS,
        )
        logger.info(f"Daily job complete. Report: {report_file}")
    except Exception as e:
        logger.error(f"Daily job failed: {e}", exc_info=True)


if __name__ == "__main__":
    logger.info(f"Daily SEO runner started — scheduled at {RUN_TIME} every day.")
    logger.info("Running first job now...")
    daily_backlink_job()

    schedule.every().day.at(RUN_TIME).do(daily_backlink_job)
    logger.info(f"Scheduler active. Next run at {RUN_TIME} daily. Press Ctrl+C to stop.")

    while True:
        schedule.run_pending()
        time.sleep(60)
