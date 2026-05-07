"""
Lightweight daily scheduler for the backlink builder.

Usage
-----
  python scheduler.py          # run once at startup, then every 24 h
  python scheduler.py --now    # run immediately, then every 24 h
  python scheduler.py --cron   # print cron installation instructions & exit

Alternatively, install via cron (recommended for production):
  crontab -e  →  0 8 * * * cd /path/to/offpage-seo-agent && python daily_backlink_builder.py >> logs/cron.log 2>&1
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path


SCRIPT = Path(__file__).parent / "daily_backlink_builder.py"
INTERVAL_HOURS = 24
LOG_DIR = Path(__file__).parent / "logs"


def _run():
    LOG_DIR.mkdir(exist_ok=True)
    log_path = LOG_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    print(f"[{datetime.now().isoformat()}] Starting daily backlink builder → {log_path}")
    with open(log_path, "w") as log:
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        log.write(result.stdout)
    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    print(f"[{datetime.now().isoformat()}] Run complete (exit {result.returncode})")


def _print_cron_help():
    cwd = Path(__file__).parent.resolve()
    python = sys.executable
    print(
        "\nTo run daily at 08:00 via cron, add this line with `crontab -e`:\n\n"
        f"  0 8 * * * cd {cwd} && {python} daily_backlink_builder.py "
        f">> {cwd}/logs/cron.log 2>&1\n\n"
        "To run the in-process scheduler instead:\n\n"
        f"  python {Path(__file__).name}\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Daily backlink builder scheduler")
    parser.add_argument("--now", action="store_true", help="Run immediately then loop")
    parser.add_argument("--cron", action="store_true", help="Print cron setup & exit")
    args = parser.parse_args()

    if args.cron:
        _print_cron_help()
        return

    if args.now:
        _run()

    next_run = datetime.now() + timedelta(hours=INTERVAL_HOURS)
    print(f"Next run scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

    while True:
        now = datetime.now()
        if now >= next_run:
            _run()
            next_run = now + timedelta(hours=INTERVAL_HOURS)
            print(f"Next run scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(60)


if __name__ == "__main__":
    main()
