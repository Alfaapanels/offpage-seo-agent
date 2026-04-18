"""Daily scheduler — runs build_daily_backlinks() every day at 09:00."""

import schedule
import time
import traceback
from daily_backlink_builder import build_daily_backlinks

RUN_AT = "09:00"


def job():
    try:
        build_daily_backlinks()
    except Exception:
        traceback.print_exc()


schedule.every().day.at(RUN_AT).do(job)

print(f"Backlink scheduler started. Runs daily at {RUN_AT}.")
print("Running immediately for today, then waiting for next scheduled run.")
print("Press Ctrl+C to stop.\n")

job()

while True:
    schedule.run_pending()
    time.sleep(60)
