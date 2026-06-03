"""Daily backlink builder runner for alfaapanels.com.

Run this script daily (via cron or GitHub Actions) to build backlinks.
Tracks previously found opportunities in a JSON log to avoid duplicates.
"""

import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

from offpage_seo_agent import run_offpage_seo_agent, SITE_CONFIG

TRACKER_FILE = "backlink_tracker.json"
REPORTS_DIR = Path("reports")


def load_tracker() -> dict:
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {"runs": [], "opportunities": {}, "submitted": []}


def save_tracker(tracker: dict):
    with open(TRACKER_FILE, "w") as f:
        json.dump(tracker, f, indent=2)


def record_run(tracker: dict, report_date: str, report_file: str):
    tracker["runs"].append({
        "date": report_date,
        "report": report_file,
        "timestamp": datetime.utcnow().isoformat(),
    })
    save_tracker(tracker)


def already_ran_today(tracker: dict, today: str) -> bool:
    return any(run["date"] == today for run in tracker.get("runs", []))


def print_summary(tracker: dict):
    runs = tracker.get("runs", [])
    print("\n" + "=" * 60)
    print(f"BACKLINK BUILDING SUMMARY FOR {SITE_CONFIG['domain']}")
    print("=" * 60)
    print(f"Total daily runs completed : {len(runs)}")
    if runs:
        print(f"Last run                   : {runs[-1]['date']}")
    reports = list(REPORTS_DIR.glob("seo_report_*.md")) if REPORTS_DIR.exists() else []
    print(f"Reports generated          : {len(reports)}")
    print("=" * 60)


def main():
    today = str(date.today())
    tracker = load_tracker()

    force = "--force" in sys.argv

    if already_ran_today(tracker, today) and not force:
        print(f"Backlink building already ran today ({today}). Use --force to rerun.")
        print_summary(tracker)
        return

    print(f"\nStarting daily backlink building for {SITE_CONFIG['domain']}")
    print(f"Date: {today}")

    report_file = run_offpage_seo_agent(report_date=today)

    record_run(tracker, today, report_file)
    print_summary(tracker)


if __name__ == "__main__":
    main()
