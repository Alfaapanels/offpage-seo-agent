"""
Daily backlink builder for alfaapanels.com.

Usage:
    python daily_runner.py          # run once immediately, then schedule daily
    python daily_runner.py --now    # run once and exit
    python daily_runner.py --time 03:00  # schedule at a specific time (24h format)
"""

import argparse
import logging
import os
import time
from datetime import datetime

import schedule

from offpage_seo_agent import run_offpage_seo_agent, TARGET_DOMAIN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("daily_runner.log"),
    ],
)
log = logging.getLogger(__name__)

REPORTS_DIR = "reports"


def save_report(report_text: str) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(REPORTS_DIR, f"seo_report_{TARGET_DOMAIN.replace('.', '_')}_{date_str}.md")
    with open(filename, "w") as f:
        f.write(f"# Off-Page SEO Report: {TARGET_DOMAIN}\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write(report_text)
    return filename


def daily_job():
    log.info("Starting daily backlink building job for %s", TARGET_DOMAIN)
    try:
        report = run_offpage_seo_agent()
        if report:
            path = save_report(report)
            log.info("Report saved to %s", path)
        else:
            log.warning("Agent returned an empty report")
    except Exception as exc:
        log.error("Job failed: %s", exc, exc_info=True)


def main():
    parser = argparse.ArgumentParser(description="Daily SEO backlink builder for alfaapanels.com")
    parser.add_argument("--now", action="store_true", help="Run once immediately and exit")
    parser.add_argument(
        "--time",
        default="03:00",
        metavar="HH:MM",
        help="Daily run time in 24h format (default: 03:00)",
    )
    args = parser.parse_args()

    if args.now:
        daily_job()
        return

    # Run once immediately on startup, then on schedule
    log.info("Running initial job on startup...")
    daily_job()

    log.info("Scheduling daily job at %s", args.time)
    schedule.every().day.at(args.time).do(daily_job)

    log.info("Scheduler running. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
