"""
Daily scheduler for the alfaapanels.com backlink builder.
Runs the backlink building agent once per day at the configured time.

Usage:
    python scheduler.py               # runs continuously, triggers daily at RUN_TIME
    python scheduler.py --now         # run immediately once, then exit
    python scheduler.py --cron        # print the cron expression and exit (for crontab setup)
"""

import argparse
import logging
import sys
import time

import schedule

from daily_backlink_builder import run_daily_backlink_builder

# Time to run each day (24-hour format, server local time)
RUN_TIME = "08:00"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

CRON_EXPRESSION = f"0 8 * * *  python /home/user/offpage-seo-agent/daily_backlink_builder.py"


def job():
    log.info("Starting daily backlink building session…")
    try:
        report = run_daily_backlink_builder()
        log.info("Session complete. Report: %s", report)
    except Exception as exc:
        log.error("Session failed: %s", exc, exc_info=True)


def main():
    parser = argparse.ArgumentParser(description="Daily backlink builder scheduler")
    parser.add_argument("--now", action="store_true", help="Run once immediately and exit")
    parser.add_argument("--cron", action="store_true", help="Print cron expression and exit")
    args = parser.parse_args()

    if args.cron:
        print("Add this line to your crontab (crontab -e):")
        print(f"  {CRON_EXPRESSION}")
        sys.exit(0)

    if args.now:
        log.info("Running immediately (--now flag set).")
        job()
        sys.exit(0)

    schedule.every().day.at(RUN_TIME).do(job)
    log.info("Scheduler started. Next run at %s daily. Press Ctrl+C to stop.", RUN_TIME)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
