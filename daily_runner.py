import logging
import schedule
import time
from offpage_seo_agent import run_daily_backlink_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("backlink_agent.log"),
        logging.StreamHandler(),
    ],
)


def run_daily_job():
    logging.info("Starting daily backlink building job...")
    try:
        report_path = run_daily_backlink_agent()
        logging.info(f"Job completed successfully. Report: {report_path}")
    except Exception as e:
        logging.error(f"Job failed: {e}", exc_info=True)


# Run immediately on start, then daily at 09:00 UTC
schedule.every().day.at("09:00").do(run_daily_job)

if __name__ == "__main__":
    logging.info("Daily backlink agent scheduler started.")
    logging.info("Running initial job now...")
    run_daily_job()

    logging.info("Scheduler active — next run daily at 09:00.")
    while True:
        schedule.run_pending()
        time.sleep(60)
