#!/usr/bin/env python3
"""Daily backlink builder for alfaapanels.com.

Runs every day to discover and build relevant backlinks.
Usage:
  python daily_backlink_builder.py                  # run once immediately
  python daily_backlink_builder.py --schedule 09:00 # schedule daily at 09:00
"""

import json
import os
import sys
import time
from datetime import date, datetime

import anthropic
import schedule
from anthropic import beta_tool

# ── Configuration ────────────────────────────────────────────────────────────

TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "aluminum panels, composite panels, building cladding, facade systems, construction materials"
COMPETITORS = ["alucobond.com", "reynobond.com", "alpolic.com"]
DAILY_QUOTA = 10

TRACKING_FILE = "backlink_tracking.json"
REPORTS_DIR = "reports"

client = anthropic.Anthropic()

# ── Tracking helpers ──────────────────────────────────────────────────────────

def _load_tracking() -> dict:
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE) as f:
            return json.load(f)
    return {"attempts": [], "completed": [], "dates_run": []}


def _save_tracking(data: dict) -> None:
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Tools ─────────────────────────────────────────────────────────────────────

@beta_tool
def get_already_contacted_sites() -> str:
    """Return a list of sites already tracked to avoid duplicate outreach.

    Call this first at the start of every daily session.
    """
    data = _load_tracking()
    if not data["attempts"]:
        return "No sites tracked yet — this is a fresh start."

    lines = [
        f"- {a['url']}  (type={a['type']}, score={a['score']}, date={a['date_found']}, status={a['status']})"
        for a in data["attempts"]
    ]
    completed = len(data["completed"])
    return (
        f"Tracked {len(lines)} prospects so far | {completed} backlinks completed.\n"
        + "\n".join(lines[:80])
    )


@beta_tool
def record_backlink_opportunity(
    target_url: str,
    link_type: str,
    relevance_score: int,
    notes: str,
) -> str:
    """Record a newly discovered backlink opportunity to the tracking file.

    Args:
        target_url: Full URL of the page that could link to alfaapanels.com.
        link_type: One of: directory, guest_post, forum, resource_page,
                   broken_link, unlinked_mention, comment.
        relevance_score: Relevance to alfaapanels.com niche, 1–10.
        notes: Short notes — page topic, why it's relevant, contact info if found.
    """
    data = _load_tracking()
    today = date.today().isoformat()

    existing_urls = {a["url"] for a in data["attempts"]}
    if target_url in existing_urls:
        return f"Already tracked: {target_url}"

    data["attempts"].append({
        "url": target_url,
        "type": link_type,
        "score": relevance_score,
        "notes": notes,
        "date_found": today,
        "status": "pending",
    })
    _save_tracking(data)
    return f"Recorded: {target_url}  (score={relevance_score}/10, type={link_type})"


@beta_tool
def generate_directory_submission(
    directory_name: str,
    directory_url: str,
    category: str,
    site_title: str,
    site_description: str,
    keywords: str,
) -> str:
    """Generate a ready-to-submit directory listing for alfaapanels.com.

    Args:
        directory_name: Human name of the web directory (e.g. "DMOZ Alternative").
        directory_url: URL of the directory's submission page.
        category: Category path to submit under.
        site_title: Title for the listing (keep under 60 chars).
        site_description: Description text (100–200 chars, no spammy keywords).
        keywords: Comma-separated relevant keywords.
    """
    return f"""DIRECTORY SUBMISSION
====================
Directory : {directory_name}
Submit at : {directory_url}
Category  : {category}

URL         : https://{TARGET_DOMAIN}
Title       : {site_title}
Description : {site_description}
Keywords    : {keywords}

STATUS: Ready — visit the submit URL above and paste these details.
"""


@beta_tool
def create_forum_post_template(
    forum_name: str,
    thread_url: str,
    discussion_topic: str,
    helpful_post_body: str,
    allows_signature_link: bool,
) -> str:
    """Create a genuine, helpful forum post template that earns a backlink.

    Args:
        forum_name: Name of the forum or community.
        thread_url: URL of the specific thread or question to reply to.
        discussion_topic: Brief description of what the thread is about.
        helpful_post_body: The actual post content — must be genuinely useful,
                           NOT promotional. Mention alfaapanels.com only if
                           directly relevant to the question.
        allows_signature_link: True if the forum allows a link in the signature.
    """
    sig = (
        "\n\n---\n"
        f"[Alfa Panels](https://{TARGET_DOMAIN}) — Aluminium & Composite Panel Solutions"
    ) if allows_signature_link else ""

    return f"""FORUM POST TEMPLATE
===================
Forum  : {forum_name}
Thread : {thread_url}
Topic  : {discussion_topic}

--- POST CONTENT ---
{helpful_post_body}{sig}
--- END CONTENT ---

Link type: {"Signature backlink" if allows_signature_link else "Contextual / natural link in body"}
Action: Log in to {forum_name}, navigate to the thread, and post the above.
"""


@beta_tool
def mark_backlink_completed(
    referring_url: str,
    linked_to_url: str,
    anchor_text: str,
) -> str:
    """Mark a backlink as successfully placed.

    Call this once a link is live or outreach has been sent.

    Args:
        referring_url: The page that now contains (or will contain) the link.
        linked_to_url: The alfaapanels.com page being linked to.
        anchor_text: The anchor text used for the link.
    """
    data = _load_tracking()
    today = date.today().isoformat()

    for attempt in data["attempts"]:
        if attempt["url"] == referring_url:
            attempt["status"] = "completed"
            attempt["date_completed"] = today
            attempt["anchor_text"] = anchor_text
            attempt["linked_to"] = linked_to_url
            break

    data["completed"].append({
        "referring_url": referring_url,
        "linked_url": linked_to_url,
        "anchor_text": anchor_text,
        "date": today,
    })
    _save_tracking(data)

    total = len(data["completed"])
    return (
        f"Backlink recorded! Total built: {total}\n"
        f"  From : {referring_url}\n"
        f"  To   : {linked_to_url}\n"
        f"  Text : '{anchor_text}'"
    )


# ── Daily runner ──────────────────────────────────────────────────────────────

# Stable system context — cached daily (changes only when niche/config changes)
_SYSTEM_CONTEXT = f"""You are an expert off-page SEO strategist and link builder for {TARGET_DOMAIN}.

SITE PROFILE
  Domain  : {TARGET_DOMAIN}
  Brand   : {BRAND_NAME}
  Niche   : {NICHE}
  Competitors: {', '.join(COMPETITORS)}

LINK-QUALITY STANDARDS
- Only pursue RELEVANT sources in the panels, construction, building-materials,
  architecture, or sustainability niches.
- Prefer .org, .gov, .edu, industry associations, and established trade blogs.
- Reject link farms, low-DA directories, unrelated niches, or duplicate targets.

ANCHOR-TEXT ROTATION (follow this mix)
  30 % — brand URL    : "alfaapanels.com"
  25 % — brand name   : "Alfa Panels"
  20 % — keywords     : "aluminum panels", "composite cladding", "facade panels"
  15 % — variations   : "quality cladding solutions", "panel systems"
  10 % — generic      : "here", "this site"  (use sparingly)

LINK-TYPE PRIORITIES (highest value first)
  1. Unlinked brand mentions → ask for a link
  2. Broken-link replacement on relevant pages
  3. Resource / "best suppliers" page inclusions
  4. Guest posts on construction / architecture blogs
  5. Forum answers with contextual or signature links
  6. Quality business directories (construction / building sector)

TOOLS AVAILABLE
  • web_search / web_fetch — find opportunities and verify pages
  • get_already_contacted_sites — always call first to avoid duplicates
  • record_backlink_opportunity — log every new prospect found
  • generate_directory_submission — produce ready-to-submit directory listings
  • create_forum_post_template — draft genuine, helpful forum posts
  • mark_backlink_completed — record links that are live or outreach sent
"""


def run_daily_backlink_builder() -> None:
    """Execute the daily backlink-building session for alfaapanels.com."""
    today = date.today().isoformat()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{'='*60}")
    print(f"  Daily Backlink Builder  —  {now}")
    print(f"  Target: {TARGET_DOMAIN}")
    print(f"{'='*60}\n")

    tracking = _load_tracking()
    completed_so_far = len(tracking["completed"])

    os.makedirs(REPORTS_DIR, exist_ok=True)

    # Volatile part — changes every day (not cached)
    daily_task = f"""Today is {today}. Backlinks built to date: {completed_so_far}.

Your mission: build {DAILY_QUOTA} NEW, relevant backlinks for {TARGET_DOMAIN} today.

STEP-BY-STEP INSTRUCTIONS
1. Call get_already_contacted_sites() — review what's been done.
2. Use web_search to find 5+ fresh prospects NOT already tracked:
   • Search: site:construction-forum.com "aluminum panels" OR "composite cladding"
   • Search: intitle:"resources" OR intitle:"suppliers" "building panels" -site:{TARGET_DOMAIN}
   • Search: "{BRAND_NAME}" -site:{TARGET_DOMAIN}   (unlinked mentions)
   • Search: "{', '.join(COMPETITORS)}" link building   (competitor backlinks)
3. For each promising result, call web_fetch to verify the page is live and relevant.
4. Call record_backlink_opportunity() for every valid prospect found.
5. Call generate_directory_submission() for 3 relevant business/construction directories.
6. Call create_forum_post_template() for 2 relevant construction/architecture forums.
7. Call mark_backlink_completed() for any prospects you've confirmed as done.
8. Generate outreach emails for the top 3 prospects (include in the final report).

FINAL REPORT FORMAT (end your response with this section)
## Daily Backlink Report — {today}
### New Prospects Found: [count]
### Action Items (prioritised):
1. …
### Top 3 Outreach Emails:
…
### Running Total Backlinks: [count]
"""

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        tools=[
            get_already_contacted_sites,
            record_backlink_opportunity,
            generate_directory_submission,
            create_forum_post_template,
            mark_backlink_completed,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    # Stable prefix — eligible for prompt caching
                    {
                        "type": "text",
                        "text": _SYSTEM_CONTEXT,
                        "cache_control": {"type": "ephemeral"},
                    },
                    # Daily-volatile part — not cached
                    {
                        "type": "text",
                        "text": daily_task,
                    },
                ],
            }
        ],
    )

    report_parts: list[str] = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_parts.append(block.text)

    # Save daily report
    report_path = os.path.join(REPORTS_DIR, f"backlinks_{today}.md")
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report: {TARGET_DOMAIN}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(report_parts))

    # Record that today's run completed
    tracking = _load_tracking()
    if today not in tracking["dates_run"]:
        tracking["dates_run"].append(today)
        _save_tracking(tracking)

    print(f"\nReport saved → {report_path}")


# ── Scheduler ─────────────────────────────────────────────────────────────────

def start_scheduler(run_time: str = "09:00") -> None:
    """Run the daily backlink builder every day at run_time (HH:MM)."""
    print(f"Scheduler started — daily run at {run_time} for {TARGET_DOMAIN}")
    print("Press Ctrl+C to stop.\n")

    schedule.every().day.at(run_time).do(run_daily_backlink_builder)

    while True:
        schedule.run_pending()
        time.sleep(30)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--schedule" in sys.argv:
        idx = sys.argv.index("--schedule")
        run_time = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "09:00"
        start_scheduler(run_time)
    else:
        run_daily_backlink_builder()
