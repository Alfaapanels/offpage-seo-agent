#!/usr/bin/env python3
"""Daily backlink builder for alfaapanels.com.

Runs an AI agent each day to discover, score, and prepare high-quality
backlink opportunities in the SMM-panel niche. Results are persisted to
backlink_tracker.json and a dated markdown report in reports/.

Usage:
  python daily_backlink_builder.py              # run once immediately
  python daily_backlink_builder.py --schedule   # loop daily at 09:00 UTC
  python daily_backlink_builder.py --schedule --time=14:30
"""

import json
import os
import schedule
import sys
import time
from datetime import date, datetime
from pathlib import Path

import anthropic
from anthropic import beta_tool

# ── Client ────────────────────────────────────────────────────────────────────
client = anthropic.Anthropic()

# ── Site config ───────────────────────────────────────────────────────────────
DOMAIN = "alfaapanels.com"
BRAND = "Alfa Panels"
NICHE = "SMM panel social media marketing services"
SITE_DESCRIPTION = (
    "Alfa Panels is a premium SMM panel offering affordable, fast social media "
    "marketing services: Instagram followers/likes/views, YouTube views/subscribers, "
    "TikTok followers/likes, Twitter/X followers, Facebook page likes, Telegram "
    "members, and many more platforms. Reseller API available. 24/7 support, "
    "instant delivery, cheapest prices."
)
TARGET_KEYWORDS = [
    "smm panel",
    "best smm panel",
    "cheapest smm panel",
    "smm panel 2024",
    "buy instagram followers",
    "youtube views panel",
    "tiktok smm panel",
    "social media marketing panel",
    "smm reseller panel",
    "smm api panel",
    "instagram smm panel",
    "cheapest smm services",
]
KEY_URLS = {
    "home": f"https://{DOMAIN}",
    "services": f"https://{DOMAIN}/services",
    "register": f"https://{DOMAIN}/register",
    "api_docs": f"https://{DOMAIN}/api",
}
COMPETITORS = [
    "justanotherpanel.com",
    "peakerr.com",
    "smmworld.co",
    "socialwick.com",
    "panel.town",
    "smmstone.com",
]

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
REPORTS_DIR = BASE_DIR / "reports"
TRACKER_FILE = BASE_DIR / "backlink_tracker.json"
REPORTS_DIR.mkdir(exist_ok=True)


# ── Tracker helpers ───────────────────────────────────────────────────────────
def _load_tracker() -> dict:
    if TRACKER_FILE.exists():
        try:
            return json.loads(TRACKER_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "opportunities": [],
        "completed": [],
        "daily_counts": {},
        "visited_urls": [],
    }


def _save_tracker(data: dict) -> None:
    TRACKER_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ── Agent tools ───────────────────────────────────────────────────────────────
@beta_tool
def save_backlink_opportunity(
    url: str,
    page_title: str,
    opportunity_type: str,
    relevance_score: int,
    action_required: str,
    draft_content: str,
    target_url: str,
) -> str:
    """Save a discovered backlink opportunity to the persistent tracker.

    Args:
        url: URL of the page where the backlink will be placed.
        page_title: Title or name of the target page or site.
        opportunity_type: One of: forum_post, blog_comment, guest_post,
            directory_submission, qa_answer, resource_page_addition,
            outreach_email, profile_link.
        relevance_score: Topical relevance to SMM/social media, 1-10
            (10 = directly about SMM panels).
        action_required: Exact step needed to secure this backlink (e.g.
            "Reply to thread with draft below", "Submit form at /add-listing").
        draft_content: Complete ready-to-use content — forum reply, blog
            comment, outreach email, or directory description.
        target_url: Which alfaapanels.com page to link to (home, services,
            register, or api_docs).
    """
    tracker = _load_tracker()
    today = str(date.today())

    existing_urls = {o["url"] for o in tracker["opportunities"]}
    if url in existing_urls:
        return f"Skipped duplicate: {url}"

    opp_id = len(tracker["opportunities"]) + 1
    opp = {
        "id": opp_id,
        "url": url,
        "page_title": page_title,
        "type": opportunity_type,
        "relevance_score": min(10, max(1, int(relevance_score))),
        "action_required": action_required,
        "draft_content": draft_content,
        "target_url": target_url,
        "found_date": today,
        "status": "pending",
    }
    tracker["opportunities"].append(opp)
    tracker["daily_counts"][today] = tracker["daily_counts"].get(today, 0) + 1
    tracker.setdefault("visited_urls", []).append(url)
    _save_tracker(tracker)
    return f"Saved #{opp_id}: [{opportunity_type}] {page_title} (score {relevance_score}/10)"


@beta_tool
def get_pending_opportunities(limit: int = 10) -> str:
    """Return the highest-priority pending backlink opportunities.

    Args:
        limit: Maximum number of results to return (default 10).
    """
    tracker = _load_tracker()
    pending = sorted(
        [o for o in tracker["opportunities"] if o["status"] == "pending"],
        key=lambda x: x["relevance_score"],
        reverse=True,
    )
    if not pending:
        return "No pending opportunities yet."
    lines = [f"Top {min(limit, len(pending))} pending opportunities:\n"]
    for o in pending[:limit]:
        lines.append(
            f"#{o['id']} [{o['type']}] Score: {o['relevance_score']}/10 — {o['page_title']}\n"
            f"  URL: {o['url']}\n"
            f"  Action: {o['action_required']}\n"
            f"  Target: {o['target_url']}\n"
        )
    return "\n".join(lines)


@beta_tool
def get_daily_summary() -> str:
    """Return today's backlink-building activity and all-time stats."""
    tracker = _load_tracker()
    today = str(date.today())
    today_new = tracker["daily_counts"].get(today, 0)
    total = len(tracker["opportunities"])
    pending = sum(1 for o in tracker["opportunities"] if o["status"] == "pending")
    completed = len(tracker["completed"])

    by_type: dict[str, int] = {}
    for o in tracker["opportunities"]:
        by_type[o["type"]] = by_type.get(o["type"], 0) + 1

    top_pending = sorted(
        [o for o in tracker["opportunities"] if o["status"] == "pending"],
        key=lambda x: x["relevance_score"],
        reverse=True,
    )[:5]

    type_lines = "\n".join(f"  {t}: {c}" for t, c in sorted(by_type.items()))
    top_lines = "\n".join(
        f"  #{o['id']} {o['page_title']} ({o['type']}, {o['relevance_score']}/10)"
        for o in top_pending
    )

    return (
        f"=== Backlink Tracker Summary — {today} ===\n"
        f"New opportunities found today : {today_new}\n"
        f"Total opportunities tracked   : {total}\n"
        f"Pending action                : {pending}\n"
        f"Completed / actioned          : {completed}\n\n"
        f"By type:\n{type_lines}\n\n"
        f"Top 5 priorities:\n{top_lines}"
    )


# ── Main agent session ────────────────────────────────────────────────────────
def run_daily_backlink_session() -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*60}")
    print(f"  Daily Backlink Builder — {DOMAIN}")
    print(f"  {today}")
    print(f"{'='*60}\n")

    tracker = _load_tracker()
    already_visited = tracker.get("visited_urls", [])
    existing_count = len(tracker["opportunities"])

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
        max_tokens=16000,
        tools=[
            save_backlink_opportunity,
            get_pending_opportunities,
            get_daily_summary,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert off-page SEO specialist building
high-quality, relevant backlinks for {DOMAIN}.

ABOUT THE SITE
--------------
{SITE_DESCRIPTION}

Domain      : {DOMAIN}
Brand       : {BRAND}
Key pages   : {json.dumps(KEY_URLS, indent=2)}
Keywords    : {', '.join(TARGET_KEYWORDS)}
Competitors : {', '.join(COMPETITORS)}

Already tracked URLs (skip these):
{json.dumps(already_visited[:60], indent=2) if already_visited else "None — everything is new!"}

TODAY'S GOAL
------------
Find 10-15 NEW, high-quality backlink opportunities and save each one
using the save_backlink_opportunity tool. Cover all 7 types below.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 1 — FORUM POSTS  (target: 3-4 opportunities)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Search for active forum threads about SMM panels on high-traffic forums:
  • web_search: "smm panel" forum discussion site:blackhatworld.com 2024
  • web_search: "best smm panel" forum site:warriorforum.com
  • web_search: "smm reseller panel" forum review discussion
  • web_search: "social media panel" forum recommend thread

For each thread: draft a 150-200 word helpful reply that naturally
mentions {DOMAIN} as a recommended panel with a direct link.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 2 — Q&A ANSWERS  (target: 2-3 opportunities)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Find questions about SMM panels on Quora and Reddit:
  • web_search: site:quora.com "best smm panel" OR "smm panel recommendation"
  • web_search: site:reddit.com/r/bigseo "smm panel" 2024
  • web_search: site:reddit.com/r/socialmedia "social media marketing panel"
  • web_search: "what is the best smm panel" question answer

For each question: write a genuine 200-250 word answer that helps the
asker and recommends {DOMAIN} with a link.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 3 — BLOG COMMENTS  (target: 2-3 opportunities)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Find recent blog posts about SMM panels or social media marketing tools:
  • web_search: "smm panel review 2024" blog
  • web_search: "best smm panel" site:medium.com OR site:wordpress.com
  • web_search: "social media marketing tools comparison" blog

web_fetch promising articles to confirm comments are enabled.
Write a thoughtful, value-adding comment that includes a link to {DOMAIN}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 4 — DIRECTORY SUBMISSIONS  (target: 2 opportunities)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Find directories listing SMM panels or digital marketing tools:
  • web_search: "smm panel list" directory listing 2024
  • web_search: "add your smm panel" OR "submit smm panel" directory
  • web_search: digital marketing tools directory "add site" free
  • web_search: "social media marketing tools" directory free listing

For each: provide submission URL, ideal category, site description,
and anchor text to use.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 5 — GUEST POST OUTREACH  (target: 1-2 opportunities)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Find blogs in the SMM/digital marketing space that accept guest posts:
  • web_search: "social media marketing" "write for us" guest post 2024
  • web_search: "smm" blog "submit guest post" OR "guest article"
  • web_search: "digital marketing" "guest post guidelines" 2024

For each prospect: write a complete outreach email with 3 article title
ideas relevant to their audience, pitched from the {BRAND} team.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 6 — RESOURCE PAGE ADDITIONS  (target: 1-2 opportunities)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Find resource pages or "best of" lists for SMM tools:
  • web_search: "best smm tools" resource page link addition
  • web_search: "social media marketing resources" list tools 2024
  • web_search: "smm panel" OR "social media panel" resources "suggest a tool"

For each: write a 60-word description of {DOMAIN} for submission.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 7 — COMPETITOR BACKLINK GAPS  (target: 1 opportunity)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Identify sites that link to competitors but not {DOMAIN}:
  • web_search: "justanotherpanel.com" listed OR reviewed directory
  • web_search: "peakerr.com" link site listing
  • web_fetch competitor pages to spot directory/community links

For each gap found: save it with action steps to get the same link.

QUALITY RULES
─────────────
✓ Minimum relevance score 6 — focus on SMM / social media / digital marketing
✓ Real, engaged sites only (not obvious link farms or spam)
✓ All draft content must be genuine, helpful, and naturally worded
✓ Use varied anchor texts: brand name, partial keyword, bare URL
✓ Mix link types for a natural backlink profile
✗ Do NOT repeat any URL from the already-tracked list above

After completing all tasks, call get_daily_summary to show today's
results, then provide a concise TOP 5 action list for today.""",
            }
        ],
    )

    full_report: list[str] = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_path = REPORTS_DIR / f"backlink_report_{today}.md"
    report_path.write_text(
        f"# Daily Backlink Report: {DOMAIN}\n\n"
        f"**Date:** {today}  \n"
        f"**Previously tracked:** {existing_count} opportunities\n\n"
        + "\n\n---\n\n".join(full_report),
        encoding="utf-8",
    )
    print(f"\nReport saved: {report_path}")
    return str(report_path)


# ── Scheduler ─────────────────────────────────────────────────────────────────
def run_scheduled(run_time: str = "09:00") -> None:
    """Loop forever, running the backlink session once per day at run_time."""
    schedule.every().day.at(run_time).do(run_daily_backlink_session)
    print(f"Scheduler active — daily at {run_time} UTC for {DOMAIN}")
    print("Press Ctrl+C to stop.\n")
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    if "--schedule" in sys.argv:
        run_time = "09:00"
        for arg in sys.argv:
            if arg.startswith("--time="):
                run_time = arg.split("=", 1)[1]
        run_scheduled(run_time)
    else:
        run_daily_backlink_session()
