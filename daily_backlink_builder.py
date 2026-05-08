#!/usr/bin/env python3
"""Daily scheduler that runs the off-page SEO backlink building agent for alfaapanels.com."""

import json
import logging
import os
import sys
import time
from datetime import date, datetime
from pathlib import Path

import schedule

from offpage_seo_agent import run_daily_backlink_session, TARGET_DOMAIN

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
REPORTS_DIR = BASE_DIR / "reports"
LOG_DIR = BASE_DIR / "logs"
TRACKER_FILE = BASE_DIR / "backlink_tracker.json"

REPORTS_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "daily_builder.log"),
    ],
)
log = logging.getLogger(__name__)

# ── Tracker ────────────────────────────────────────────────────────────────────

def load_tracker() -> dict:
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {"sessions": [], "total_opportunities": 0, "started": date.today().isoformat()}


def save_tracker(data: dict) -> None:
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)


def record_session(tracker: dict, date_str: str, report_path: str, status: str) -> None:
    tracker["sessions"].append({
        "date": date_str,
        "report": report_path,
        "status": status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })
    tracker["total_opportunities"] = len(tracker["sessions"])
    save_tracker(tracker)


# ── Daily job ──────────────────────────────────────────────────────────────────

def daily_job() -> None:
    today = date.today().isoformat()
    log.info("Starting daily backlink session for %s — %s", TARGET_DOMAIN, today)

    tracker = load_tracker()

    # Skip if already ran today
    ran_today = any(s["date"] == today for s in tracker["sessions"])
    if ran_today:
        log.info("Session already completed for %s, skipping.", today)
        return

    try:
        report_content = run_daily_backlink_session(today)

        report_path = REPORTS_DIR / f"report_{today}.md"
        with open(report_path, "w") as f:
            f.write(f"# Daily Backlink Report — {TARGET_DOMAIN}\n")
            f.write(f"**Date:** {today}\n\n")
            f.write(report_content)

        log.info("Report saved: %s", report_path)
        record_session(tracker, today, str(report_path), "success")
        log.info("Session complete. Total sessions tracked: %d", len(tracker["sessions"]))

    except Exception as exc:
        log.error("Session failed: %s", exc, exc_info=True)
        record_session(tracker, today, "", "failed")
        raise


# ── Scheduler ─────────────────────────────────────────────────────────────────

def start_scheduler(run_time: str = "09:00") -> None:
    """Schedule the daily job at run_time (HH:MM, 24h) and block forever."""
    log.info("Scheduling daily backlink build for %s at %s UTC", TARGET_DOMAIN, run_time)
    schedule.every().day.at(run_time).do(daily_job)

    # Also run immediately on first startup so today is not missed
    log.info("Running initial session now...")
    daily_job()

    log.info("Scheduler running. Next run at %s UTC. Press Ctrl+C to stop.", run_time)
    while True:
        schedule.run_pending()
        time.sleep(60)


# ── CLI ────────────────────────────────────────────────────────────────────────

def print_status() -> None:
    tracker = load_tracker()
    print(f"\nBacklink Tracker — {TARGET_DOMAIN}")
    print("=" * 50)
    print(f"Tracking since : {tracker.get('started', 'unknown')}")
    print(f"Total sessions : {len(tracker['sessions'])}")
    successful = [s for s in tracker["sessions"] if s["status"] == "success"]
    failed = [s for s in tracker["sessions"] if s["status"] == "failed"]
    print(f"Successful     : {len(successful)}")
    print(f"Failed         : {len(failed)}")
    if successful:
        print(f"Last run       : {successful[-1]['date']}")
        print(f"Last report    : {successful[-1]['report']}")
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=f"Daily backlink builder for {TARGET_DOMAIN}")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run one session immediately")

    sched_parser = subparsers.add_parser("schedule", help="Start the daily scheduler")
    sched_parser.add_argument(
        "--time",
        default=os.environ.get("BACKLINK_RUN_TIME", "09:00"),
        help="Daily run time in HH:MM UTC (default 09:00, or BACKLINK_RUN_TIME env var)",
    )

    subparsers.add_parser("status", help="Show session history")

    args = parser.parse_args()

    if args.command == "run":
        daily_job()

    elif args.command == "schedule":
        start_scheduler(run_time=args.time)

    elif args.command == "status":
        print_status()

    else:
        # Default: run once
        daily_job()
