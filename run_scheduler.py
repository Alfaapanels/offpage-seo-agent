"""Run daily_backlink_builder on a schedule (once per day at 09:00).
Usage: python run_scheduler.py
Or for cron: 0 9 * * * cd /path/to/offpage-seo-agent && python daily_backlink_builder.py
"""
import schedule
import time
from daily_backlink_builder import run_daily_backlink_builder

schedule.every().day.at("09:00").do(run_daily_backlink_builder)

print("Scheduler started – will run daily at 09:00. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(60)
