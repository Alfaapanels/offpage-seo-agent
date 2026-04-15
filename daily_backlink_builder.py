"""
Daily Backlink Builder for alfaapanels.com
==========================================
Runs the off-page SEO agent once per day using a rotating weekly strategy.
Can be executed in two ways:

1. One-shot (run today's task immediately):
       python daily_backlink_builder.py

2. Persistent daemon (runs every 24 h automatically):
       python daily_backlink_builder.py --daemon

Cron alternative (no daemon needed) — add to crontab:
       0 8 * * * /usr/bin/python3 /path/to/daily_backlink_builder.py
"""

import argparse
import os
import sys
import time
import datetime
import schedule

import backlink_tracker as bt
from config import SITE_CONFIG, DAILY_TASK_ROTATION
from offpage_seo_agent import run_offpage_seo_agent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_report_dir() -> str:
    report_dir = SITE_CONFIG.get("report_output_dir", "reports")
    os.makedirs(report_dir, exist_ok=True)
    return report_dir


def _save_report(report_blocks: list[str], strategy_name: str, run_date: str) -> str:
    report_dir = _ensure_report_dir()
    safe_name = strategy_name.lower().replace(" ", "_").replace("&", "and")
    filename = os.path.join(report_dir, f"{run_date}_{safe_name}.md")
    domain = SITE_CONFIG["domain"]
    with open(filename, "w") as f:
        f.write(f"# Off-Page SEO Report: {domain}\n")
        f.write(f"**Date**: {run_date}  \n")
        f.write(f"**Strategy**: {strategy_name}\n\n")
        f.write("---\n\n")
        f.write("\n\n".join(report_blocks))
    print(f"\nReport saved: {filename}")
    return filename


def _get_today_strategy() -> dict:
    """Pick the strategy for today's weekday (0=Monday … 6=Sunday)."""
    weekday = datetime.date.today().weekday()
    return DAILY_TASK_ROTATION[weekday]


# ---------------------------------------------------------------------------
# Main daily job
# ---------------------------------------------------------------------------

def run_daily_job() -> None:
    run_date = datetime.date.today().isoformat()
    strategy = _get_today_strategy()

    print(f"\n{'='*60}")
    print(f" Daily Backlink Builder — alfaapanels.com")
    print(f" Date     : {run_date}")
    print(f" Strategy : {strategy['name']}")
    print(f"{'='*60}\n")

    # Show running totals before starting
    bt.print_summary()

    # Run the AI agent
    report_blocks = run_offpage_seo_agent(
        your_domain=SITE_CONFIG["domain"],
        brand_name=SITE_CONFIG["brand_name"],
        niche=SITE_CONFIG["niche"],
        competitors=SITE_CONFIG["competitors"],
        daily_strategy=strategy,
    )

    # Save the Markdown report
    report_file = _save_report(report_blocks, strategy["name"], run_date)

    # Count how many new opportunities were recorded today by diffing the tracker
    summary_after = bt.get_summary()
    opportunities_today = summary_after["total"]
    bt.log_daily_run(run_date, strategy["name"], opportunities_today, report_file)

    # Show updated totals
    bt.print_summary()
    print(f"\nDaily job complete. Next run: tomorrow at the same time.\n")


# ---------------------------------------------------------------------------
# Scheduler / daemon mode
# ---------------------------------------------------------------------------

def _schedule_and_run() -> None:
    """Schedule the job daily at 08:00 local time and block forever."""
    run_time = os.environ.get("DAILY_RUN_TIME", "08:00")
    print(f"Daemon mode active — job scheduled daily at {run_time}")
    print("Press Ctrl+C to stop.\n")

    schedule.every().day.at(run_time).do(run_daily_job)

    # Run immediately on first start so there is no wait on day 1
    run_daily_job()

    while True:
        schedule.run_pending()
        time.sleep(60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Daily backlink builder for alfaapanels.com"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Keep running and execute the job every 24 h (default: run once and exit)",
    )
    parser.add_argument(
        "--strategy",
        type=int,
        choices=range(7),
        metavar="0-6",
        help="Override the weekday strategy (0=Mon … 6=Sun)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print the tracker summary and exit",
    )
    args = parser.parse_args()

    if args.summary:
        bt.print_summary()
        pending = bt.get_pending_outreach(limit=10)
        if pending:
            print("Top pending outreach opportunities:")
            for p in pending:
                print(f"  [{p['prospect_score']:3d}] {p['link_type']:<15} {p['url']}")
        sys.exit(0)

    # Allow manual strategy override
    if args.strategy is not None:
        DAILY_TASK_ROTATION_OVERRIDE = DAILY_TASK_ROTATION[args.strategy]
        # Monkey-patch _get_today_strategy for this run
        import daily_backlink_builder as _self
        _self._get_today_strategy = lambda: DAILY_TASK_ROTATION_OVERRIDE  # noqa: E731

    if args.daemon:
        _schedule_and_run()
    else:
        run_daily_job()


if __name__ == "__main__":
    main()
