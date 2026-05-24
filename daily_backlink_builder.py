"""
Daily Backlink Builder for alfaapanels.com
Runs the SEO agent on a schedule and tracks completed opportunities.
"""

import json
import datetime
import logging
import sys
from pathlib import Path

from offpage_seo_agent import run_offpage_seo_agent

# ── Configuration ─────────────────────────────────────────────────────────────

DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "sandwich panels building materials construction insulation"
COMPETITORS = [
    "kingspan.com",
    "metecno.com",
    "isopan.com",
    "rockwool.com",
    "paroc.com",
]

TRACKER_FILE = Path("backlink_tracker.json")
REPORTS_DIR = Path("reports")
LOG_FILE = Path("seo_agent.log")

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ── Tracker helpers ───────────────────────────────────────────────────────────

def load_tracker() -> dict:
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {"runs": [], "opportunities": {}}


def save_tracker(tracker: dict) -> None:
    with open(TRACKER_FILE, "w") as f:
        json.dump(tracker, f, indent=2)


def record_run(tracker: dict, run_date: str, report_file: str) -> None:
    tracker["runs"].append({
        "date": run_date,
        "report": report_file,
        "completed_at": datetime.datetime.utcnow().isoformat() + "Z",
    })
    save_tracker(tracker)


def already_ran_today(tracker: dict, today: str) -> bool:
    return any(r["date"] == today for r in tracker.get("runs", []))


# ── Daily job ─────────────────────────────────────────────────────────────────

def run_daily_job(force: bool = False) -> None:
    today = datetime.date.today().isoformat()
    REPORTS_DIR.mkdir(exist_ok=True)

    tracker = load_tracker()

    if not force and already_ran_today(tracker, today):
        log.info("Already ran today (%s). Use --force to override.", today)
        return

    log.info("Starting daily backlink build for %s on %s", DOMAIN, today)

    try:
        report_text = run_offpage_seo_agent(
            your_domain=DOMAIN,
            brand_name=BRAND_NAME,
            niche=NICHE,
            competitors=COMPETITORS,
            run_date=today,
        )

        # Save report under reports/
        report_path = REPORTS_DIR / f"seo_report_{today}.md"
        with open(report_path, "w") as f:
            f.write(f"# Off-Page SEO Daily Report: {DOMAIN}\n")
            f.write(f"**Date:** {today}\n\n")
            f.write(report_text)

        record_run(tracker, today, str(report_path))
        log.info("Daily backlink build complete. Report: %s", report_path)

    except Exception:
        log.exception("Daily backlink build failed for %s", today)
        raise


# ── Scheduler ─────────────────────────────────────────────────────────────────

def start_scheduler(hour: int = 8, minute: int = 0) -> None:
    """Block and run the job every day at the given UTC hour:minute."""
    try:
        from apscheduler.schedulers.blocking import BlockingScheduler
    except ImportError:
        log.error("APScheduler not installed. Run: pip install apscheduler")
        sys.exit(1)

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        run_daily_job,
        trigger="cron",
        hour=hour,
        minute=minute,
        id="daily_backlink_build",
    )

    log.info(
        "Scheduler started. Daily backlink build for %s runs at %02d:%02d UTC.",
        DOMAIN,
        hour,
        minute,
    )

    # Run immediately on startup so we don't wait until tomorrow.
    run_daily_job()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Scheduler stopped.")


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Daily backlink builder for alfaapanels.com"
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run on a daily schedule (blocks the process).",
    )
    parser.add_argument(
        "--hour",
        type=int,
        default=8,
        help="UTC hour to run the daily job (default: 8).",
    )
    parser.add_argument(
        "--minute",
        type=int,
        default=0,
        help="UTC minute to run the daily job (default: 0).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Run even if already ran today.",
    )
    args = parser.parse_args()

    if args.schedule:
        start_scheduler(hour=args.hour, minute=args.minute)
    else:
        run_daily_job(force=args.force)
