"""
Daily backlink builder for alfaapanels.com.
Runs every day, rotates through 7 link-building strategies, tracks progress,
and saves a dated Markdown report in ./daily_reports/.
"""

import json
import os
import time
import schedule
from datetime import datetime, date

from offpage_seo_agent import run_offpage_seo_agent, TARGET_DOMAIN

TRACKER_FILE = "backlink_tracker.json"
REPORTS_DIR = "daily_reports"

# Rotate strategies across the week so every run targets a different tactic.
DAY_STRATEGIES = {
    0: "directory",          # Monday
    1: "guest_post",         # Tuesday
    2: "resource_page",      # Wednesday
    3: "broken_link",        # Thursday
    4: "brand_mention",      # Friday
    5: "qa_backlinks",       # Saturday
    6: "competitor_analysis",# Sunday
}


# ---------------------------------------------------------------------------
# Tracker helpers
# ---------------------------------------------------------------------------

def load_tracker() -> dict:
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE) as fh:
            return json.load(fh)
    return {
        "pursued_urls": [],
        "built_links": [],
        "daily_runs": [],
        "total_opportunities_found": 0,
        "last_run": None,
    }


def save_tracker(data: dict) -> None:
    with open(TRACKER_FILE, "w") as fh:
        json.dump(data, fh, indent=2)


def extract_opportunity_urls(report_text: str) -> list:
    """Parse [OPPORTUNITY] lines from the agent report."""
    urls = []
    for line in report_text.splitlines():
        if line.startswith("[OPPORTUNITY]"):
            parts = line.split("|")
            if parts:
                url = parts[0].replace("[OPPORTUNITY]", "").strip()
                if url:
                    urls.append(url)
    return urls


# ---------------------------------------------------------------------------
# Report helpers
# ---------------------------------------------------------------------------

def save_daily_report(report_text: str, strategy: str, run_date: str) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    filename = os.path.join(REPORTS_DIR, f"{run_date}_{strategy}.md")
    with open(filename, "w") as fh:
        fh.write(f"# Off-Page SEO Daily Report — {TARGET_DOMAIN}\n")
        fh.write(f"**Date:** {run_date}  \n")
        fh.write(f"**Strategy:** {strategy}  \n\n")
        fh.write("---\n\n")
        fh.write(report_text)
    return filename


def print_summary(tracker: dict) -> None:
    print("\n" + "=" * 60)
    print(f"CUMULATIVE PROGRESS FOR {TARGET_DOMAIN}")
    print("=" * 60)
    print(f"Total runs completed : {len(tracker['daily_runs'])}")
    print(f"Total opportunities  : {tracker['total_opportunities_found']}")
    print(f"URLs tracked         : {len(tracker['pursued_urls'])}")
    print(f"Last run             : {tracker.get('last_run', 'N/A')}")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Core daily job
# ---------------------------------------------------------------------------

def run_daily_job() -> None:
    today = date.today()
    run_date = today.isoformat()
    strategy = DAY_STRATEGIES[today.weekday()]

    print(f"\n{'=' * 60}")
    print(f"DAILY BACKLINK BUILD — {run_date}")
    print(f"Strategy: {strategy.upper()}")
    print("=" * 60)

    tracker = load_tracker()

    # Skip if already ran today.
    if tracker.get("last_run") == run_date:
        print(f"Already ran today ({run_date}). Skipping.")
        print_summary(tracker)
        return

    pursued = tracker.get("pursued_urls", [])

    try:
        report = run_offpage_seo_agent(strategy=strategy, pursued_urls=pursued)
    except Exception as exc:
        print(f"Agent error: {exc}")
        return

    new_urls = extract_opportunity_urls(report)
    unique_new = [u for u in new_urls if u not in pursued]

    # Update tracker.
    tracker["pursued_urls"].extend(unique_new)
    tracker["total_opportunities_found"] += len(unique_new)
    tracker["last_run"] = run_date
    tracker["daily_runs"].append({
        "date": run_date,
        "strategy": strategy,
        "new_opportunities": len(unique_new),
    })
    save_tracker(tracker)

    report_path = save_daily_report(report, strategy, run_date)

    print(f"\nNew opportunities found : {len(unique_new)}")
    print(f"Report saved to        : {report_path}")
    print_summary(tracker)


# ---------------------------------------------------------------------------
# Scheduler entry point
# ---------------------------------------------------------------------------

def start_scheduler(run_time: str = "09:00") -> None:
    """Schedule the daily job and block until interrupted.

    Args:
        run_time: 24-hour HH:MM string for when to run each day.
    """
    schedule.every().day.at(run_time).do(run_daily_job)
    print(f"Daily backlink builder scheduled at {run_time} every day.")
    print(f"Target: {TARGET_DOMAIN}")
    print("Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=f"Daily backlink builder for {TARGET_DOMAIN}"
    )
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Execute today's backlink job immediately instead of waiting for the schedule.",
    )
    parser.add_argument(
        "--strategy",
        default=None,
        help="Override today's strategy (directory, guest_post, resource_page, broken_link, "
             "brand_mention, qa_backlinks, competitor_analysis, comprehensive).",
    )
    parser.add_argument(
        "--time",
        default="09:00",
        help="Daily run time in HH:MM format (default: 09:00).",
    )
    args = parser.parse_args()

    if args.strategy:
        # Patch strategy for this run.
        today_weekday = date.today().weekday()
        DAY_STRATEGIES[today_weekday] = args.strategy

    if args.run_now:
        run_daily_job()
    else:
        start_scheduler(run_time=args.time)
