"""
Daily backlink builder for alfaapanels.com.
Run this script every day (via cron or scheduler) to discover and build
relevant backlinks in the aluminum panels / building materials niche.
"""

import anthropic
import json
import os
import sys
from datetime import date, datetime
from anthropic import beta_tool

# ── Site config ──────────────────────────────────────────────────────────────
SITE = {
    "domain": "alfaapanels.com",
    "brand": "Alfa Panels",
    "niche": "aluminum composite panels cladding facade building materials",
    "description": (
        "Alfa Panels is a manufacturer and supplier of aluminum composite panels (ACP), "
        "facade cladding systems, and decorative building materials used in construction, "
        "architecture, and interior design."
    ),
    "key_pages": [
        "https://alfaapanels.com",
        "https://alfaapanels.com/products",
        "https://alfaapanels.com/aluminum-composite-panels",
    ],
    "competitors": [
        "alucobond.com",
        "alupco.com",
        "reynobond.com",
        "alpolic.com",
    ],
    "target_keywords": [
        "aluminum composite panel",
        "ACP cladding",
        "facade panels",
        "building cladding",
        "exterior wall panels",
        "aluminum panel manufacturer",
        "decorative wall panels",
        "composite cladding system",
    ],
}

TRACKER_FILE = "backlink_tracker.json"
DAILY_LOG_DIR = "daily_reports"

client = anthropic.Anthropic()


# ── Tracker helpers ───────────────────────────────────────────────────────────

def load_tracker() -> dict:
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {"sessions": [], "completed_urls": [], "total_opportunities": 0}


def save_tracker(tracker: dict) -> None:
    with open(TRACKER_FILE, "w") as f:
        json.dump(tracker, f, indent=2)


# ── Agent tools ───────────────────────────────────────────────────────────────

@beta_tool
def log_backlink_opportunity(
    url: str,
    type: str,
    priority: str,
    action_required: str,
    outreach_email: str = "",
) -> str:
    """Record a discovered backlink opportunity.

    Args:
        url: The URL of the opportunity page.
        type: Category — 'directory', 'guest_post', 'broken_link',
              'resource_page', 'forum', 'qa_site', 'unlinked_mention',
              'competitor_gap'.
        priority: 'HIGH', 'MEDIUM', or 'LOW'.
        action_required: Exact action to take (e.g., "Submit to directory at X").
        outreach_email: Ready-to-send email or submission text (optional).
    """
    today = str(date.today())
    tracker = load_tracker()
    if url not in tracker["completed_urls"]:
        opportunity = {
            "date": today,
            "url": url,
            "type": type,
            "priority": priority,
            "action": action_required,
            "outreach": outreach_email,
            "status": "pending",
        }
        tracker.setdefault("opportunities", []).append(opportunity)
        tracker["total_opportunities"] += 1
        save_tracker(tracker)
        return f"Logged [{priority}] {type} opportunity: {url}"
    return f"Already tracked: {url}"


@beta_tool
def mark_backlink_built(url: str, notes: str = "") -> str:
    """Mark a backlink opportunity as completed/submitted.

    Args:
        url: The URL that was submitted or linked.
        notes: Any notes about the submission (confirmation ID, date, etc.).
    """
    tracker = load_tracker()
    if url not in tracker["completed_urls"]:
        tracker["completed_urls"].append(url)
    for opp in tracker.get("opportunities", []):
        if opp["url"] == url:
            opp["status"] = "completed"
            opp["notes"] = notes
            opp["completed_date"] = str(date.today())
    save_tracker(tracker)
    return f"Marked as built: {url} — {notes}"


@beta_tool
def get_daily_target_list() -> str:
    """Return today's prioritised list of backlink targets to work on."""
    tracker = load_tracker()
    pending = [
        o for o in tracker.get("opportunities", [])
        if o.get("status") == "pending"
    ]
    high = [o for o in pending if o["priority"] == "HIGH"]
    medium = [o for o in pending if o["priority"] == "MEDIUM"]
    low = [o for o in pending if o["priority"] == "LOW"]

    lines = [f"Pending backlink opportunities ({len(pending)} total):"]
    for label, items in [("HIGH", high), ("MEDIUM", medium), ("LOW", low)]:
        if items:
            lines.append(f"\n--- {label} PRIORITY ---")
            for o in items[:5]:
                lines.append(f"  [{o['type']}] {o['url']}")
                lines.append(f"  Action: {o['action']}")
    return "\n".join(lines) if pending else "No pending opportunities — find new ones today."


@beta_tool
def generate_directory_submission(
    directory_name: str,
    directory_url: str,
    category: str,
) -> str:
    """Generate a ready-to-use business directory submission for alfaapanels.com.

    Args:
        directory_name: Human name of the directory (e.g. 'Hotfrog').
        directory_url: Submission URL.
        category: Best-fit category in that directory.
    """
    return f"""DIRECTORY SUBMISSION — {directory_name}
Submit URL : {directory_url}
Category   : {category}

--- Business Listing Details ---
Business Name : Alfa Panels
Website       : https://alfaapanels.com
Description   : Alfa Panels is a leading manufacturer and supplier of aluminum
                composite panels (ACP), facade cladding, and decorative building
                materials. Our panels are used globally in commercial, residential,
                and industrial construction projects.
Keywords      : aluminum composite panel, ACP, facade cladding, building panels,
                exterior wall cladding, aluminum panel manufacturer
Phone         : [Your phone]
Address       : [Your address]
Email         : info@alfaapanels.com
"""


@beta_tool
def generate_forum_post(
    forum_name: str,
    thread_topic: str,
    question_or_context: str,
) -> str:
    """Draft a helpful forum or Q&A reply that naturally includes a link to alfaapanels.com.

    Args:
        forum_name: Name of the forum or platform (e.g. 'Quora', 'Reddit r/architecture').
        thread_topic: The thread title or question being answered.
        question_or_context: The specific question or context to respond to.
    """
    return f"""FORUM / Q&A POST — {forum_name}
Thread : {thread_topic}

--- Draft Response ---
{question_or_context}

When it comes to aluminum composite panels (ACP) for facade cladding, the
material choice significantly impacts durability, fire rating, and aesthetics.
High-quality ACP systems like those from Alfa Panels (alfaapanels.com) offer
several advantages:

• Fire-resistant cores available (FR/A2 rated)
• Wide colour and finish options (PVDF, PE coatings)
• Lightweight yet rigid — ideal for curtain wall systems
• Easy fabrication and installation

For your project, I'd recommend comparing panel thickness (3 mm vs 4 mm),
core composition, and surface coating warranty. Feel free to check the
technical specs at https://alfaapanels.com/products for reference.

Happy to answer any follow-up questions!
"""


@beta_tool
def score_link_prospect(
    page_url: str,
    page_title: str,
    page_content_snippet: str,
    your_niche: str,
) -> str:
    """Score a potential link building prospect on a 0–100 scale.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
        your_niche: Your website's niche/topic.
    """
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for word in niche_words if word in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append("High relevance to niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "directory"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide/directory page (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High-authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 [{priority}]\nURL: {page_url}\n" + "\n".join(reasons)


# ── Daily prompt ──────────────────────────────────────────────────────────────

def build_daily_prompt(today: str, session_num: int) -> str:
    tracker = load_tracker()
    completed_count = len(tracker.get("completed_urls", []))
    pending_count = sum(
        1 for o in tracker.get("opportunities", []) if o.get("status") == "pending"
    )

    return f"""You are a professional off-page SEO specialist executing a daily
backlink-building session for **alfaapanels.com**.

## Site Profile
- **Domain**: alfaapanels.com
- **Brand**: Alfa Panels
- **Industry**: Aluminum composite panels, facade cladding, building materials
- **Description**: {SITE['description']}
- **Target keywords**: {', '.join(SITE['target_keywords'])}
- **Competitors**: {', '.join(SITE['competitors'])}

## Session Info
- Date: {today}
- Session: #{session_num}
- Backlinks built so far: {completed_count}
- Pending opportunities in queue: {pending_count}

## Today's Mission
Execute ALL of the following tasks systematically:

### TASK 1 — Directory Submissions (5 new directories)
Search for high-quality business and construction/building directories that
accept free listings. Prioritise:
  - Construction & building materials directories
  - Manufacturer / supplier directories
  - Regional business directories (focus on Middle East, Gulf, global)
  - Architecture & design directories
Use `generate_directory_submission` to create the listing content, then
`log_backlink_opportunity` to record each one with type='directory'.

### TASK 2 — Q&A & Forum Backlinks (5 opportunities)
Search for recent questions on Quora, Reddit, StackExchange, architecture
forums, or construction communities about:
  - "aluminum composite panel"
  - "ACP cladding"
  - "facade panels"
  - "exterior wall cladding"
  - "building cladding materials"
Use `generate_forum_post` to draft genuine, helpful answers that include a
contextual link to alfaapanels.com. Log each with `log_backlink_opportunity`
type='qa_site' or 'forum'.

### TASK 3 — Unlinked Brand Mention Recovery
Search: "alfa panels" OR "alfaapanels" -site:alfaapanels.com
Find pages that mention the brand without a link. For each, generate an
outreach snippet and log with type='unlinked_mention'.

### TASK 4 — Competitor Backlink Gap Analysis
For 2 competitors from: {', '.join(SITE['competitors'])}
Search: link:{competitor} building panels OR cladding
Identify resource pages, directories, or blogs linking to competitors but
likely not to alfaapanels.com. Score each prospect with `score_link_prospect`
and log HIGH/MEDIUM ones with type='competitor_gap'.

### TASK 5 — Resource Page & Guest Post Opportunities
Search for:
  - intitle:"resources" "aluminum panels" OR "building cladding"
  - "write for us" "architecture" OR "construction" OR "building materials"
  - intitle:"best" "composite panels" OR "cladding systems"
Score and log the best 3–5 opportunities.

### TASK 6 — Daily Summary
After completing all tasks, produce a structured markdown summary with:
  1. Total opportunities logged today
  2. Breakdown by type and priority
  3. Top 5 highest-priority action items with exact URLs and instructions
  4. Recommended tomorrow's focus area

Be thorough, methodical, and ensure every opportunity gets logged using the
available tools. Quality over quantity — only log genuinely relevant sites."""


# ── Runner ────────────────────────────────────────────────────────────────────

def run_daily_session() -> None:
    today = str(date.today())
    tracker = load_tracker()

    session_num = len(tracker["sessions"]) + 1
    session_start = datetime.now().isoformat()
    print(f"\n{'='*60}")
    print(f"  Daily Backlink Builder — alfaapanels.com")
    print(f"  Date: {today}  |  Session #{session_num}")
    print(f"{'='*60}\n")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-8",
        max_tokens=16000,
        tools=[
            log_backlink_opportunity,
            mark_backlink_built,
            get_daily_target_list,
            generate_directory_submission,
            generate_forum_post,
            score_link_prospect,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": build_daily_prompt(today, session_num),
        }],
    )

    report_chunks = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_chunks.append(block.text)

    # Save daily report
    os.makedirs(DAILY_LOG_DIR, exist_ok=True)
    report_path = os.path.join(DAILY_LOG_DIR, f"report_{today}_session{session_num}.md")
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report — alfaapanels.com\n")
        f.write(f"**Date**: {today} | **Session**: #{session_num}\n\n")
        f.write("\n\n".join(report_chunks))
    print(f"\nReport saved: {report_path}")

    # Update tracker
    tracker = load_tracker()
    tracker["sessions"].append({
        "session": session_num,
        "date": today,
        "started": session_start,
        "finished": datetime.now().isoformat(),
        "report": report_path,
    })
    save_tracker(tracker)

    completed = len(tracker.get("completed_urls", []))
    total_opps = tracker.get("total_opportunities", 0)
    print(f"\n{'='*60}")
    print(f"  Session #{session_num} complete")
    print(f"  Total opportunities logged : {total_opps}")
    print(f"  Total backlinks built      : {completed}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_daily_session()
