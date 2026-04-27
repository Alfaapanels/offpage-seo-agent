#!/usr/bin/env python3
"""
Daily Backlink Builder for alfaapanels.com

Discovers, scores, and tracks relevant backlink opportunities every day.
Saves all prospects to a SQLite database with ready-to-send outreach emails.

Usage:
    python daily_backlink_builder.py              # Run once immediately
    python daily_backlink_builder.py --schedule   # Run on daily schedule (09:00 UTC)

Results:
    - Database: backlinks.db  (all opportunities + run history)
    - Reports:  reports/backlinks_YYYY-MM-DD.md   (daily markdown report)
    - Logs:     backlink_builder.log
"""

import sys
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

import anthropic
from anthropic import beta_tool

# ─── Configuration ────────────────────────────────────────────────────────────

TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
DB_PATH = Path("backlinks.db")
REPORTS_DIR = Path("reports")
LOG_FILE = "backlink_builder.log"

# ─── Logging ──────────────────────────────────────────────────────────────────

REPORTS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ─── Database ─────────────────────────────────────────────────────────────────


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            found_date  TEXT NOT NULL,
            url         TEXT UNIQUE,
            site_name   TEXT,
            opp_type    TEXT,
            score       INTEGER,
            contact     TEXT,
            notes       TEXT,
            outreach    TEXT,
            status      TEXT DEFAULT 'new'
        );
        CREATE TABLE IF NOT EXISTS daily_runs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date    TEXT NOT NULL,
            found       INTEGER DEFAULT 0,
            report_file TEXT,
            success     INTEGER DEFAULT 1,
            error       TEXT
        );
    """)
    conn.commit()
    conn.close()
    logger.info("Database ready at %s", DB_PATH)


# ─── Tools ────────────────────────────────────────────────────────────────────


@beta_tool
def save_opportunity(
    url: str,
    site_name: str,
    opportunity_type: str,
    relevance_score: int,
    contact_info: str,
    notes: str,
    outreach_template: str,
) -> str:
    """Save a discovered backlink opportunity to the tracking database.

    Args:
        url: Full URL of the page where we can earn a backlink.
        site_name: Name of the website or publication.
        opportunity_type: One of: guest_post, resource_page, broken_link,
            unlinked_mention, directory, forum, comment, interview.
        relevance_score: Relevance and quality score from 0 to 100.
        contact_info: Editor email address or contact/submission form URL.
        notes: Why this is a good opportunity and the best angle to approach it.
        outreach_template: Complete, ready-to-send email or submission text.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """INSERT OR IGNORE INTO opportunities
               (found_date, url, site_name, opp_type, score, contact, notes, outreach, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'new')""",
            (today, url, site_name, opportunity_type, relevance_score,
             contact_info, notes, outreach_template),
        )
        conn.commit()
        changed = conn.execute("SELECT changes()").fetchone()[0]
        if changed:
            return f"Saved: [{opportunity_type}] {site_name} | score={relevance_score} | {url}"
        return f"Already tracked (skipped): {url}"
    finally:
        conn.close()


@beta_tool
def get_tracked_urls(status: str = "all") -> str:
    """Return previously tracked opportunity URLs to avoid saving duplicates.

    Args:
        status: Filter by status: 'all', 'new', 'contacted', 'acquired', 'rejected'.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        if status == "all":
            rows = conn.execute(
                "SELECT url, site_name, opp_type, score, status "
                "FROM opportunities ORDER BY score DESC LIMIT 100"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT url, site_name, opp_type, score, status "
                "FROM opportunities WHERE status=? ORDER BY score DESC LIMIT 100",
                (status,),
            ).fetchall()
    finally:
        conn.close()

    if not rows:
        return "No existing opportunities tracked yet — discover freely."
    lines = [f"[{r[4]}] {r[1]} ({r[2]}) score={r[3]} → {r[0]}" for r in rows]
    return f"Already tracked ({len(rows)}):\n" + "\n".join(lines)


@beta_tool
def score_link_prospect(
    page_url: str,
    page_title: str,
    page_content_snippet: str,
    niche: str,
) -> str:
    """Score a potential link building prospect from 0 to 100.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of the page content (200+ chars ideal).
        niche: Space-separated niche keywords to match against (e.g. 'solar panels energy').
    """
    score = 0
    reasons = []

    niche_words = niche.lower().split()
    content = (page_title + " " + page_content_snippet + " " + page_url).lower()
    hits = sum(1 for w in niche_words if w in content)
    if hits >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif hits >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (+0)")

    for t in ["resource", "guide", "tools", "blog", "list", "best", "top", "review", "directory"]:
        if t in page_url.lower() or t in page_title.lower():
            score += 30
            reasons.append(f"High-value page type '{t}' (+30)")
            break

    for s in [".edu", ".gov", ".org"]:
        if s in page_url:
            score += 30
            reasons.append(f"Authority domain {s} (+30)")
            break
    else:
        score += 10
        reasons.append("Standard domain (+10)")

    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 [{priority}]\n" + "\n".join(f"  • {r}" for r in reasons)


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality signals of an existing or prospective backlink.

    Args:
        url: Target URL receiving the backlink.
        backlink_url: The URL that links (or would link) to the target.
        anchor_text: The anchor text of the link.
    """
    signals = []
    generic = {"click here", "website", "here", "link", "read more", "this page"}
    if anchor_text.lower().strip() in generic:
        signals.append("Warning: Generic anchor text — low SEO value")
    else:
        signals.append(f"Good: Descriptive anchor: '{anchor_text}'")

    toxic = ["spam", "casino", "viagra", "porn", "gambling", "pharma", "pills"]
    if any(w in backlink_url.lower() for w in toxic):
        signals.append("TOXIC domain — add to disavow file")
    else:
        signals.append("Domain appears clean")

    return "\n".join(signals)


@beta_tool
def generate_outreach_email(
    prospect_name: str,
    prospect_site: str,
    topic: str,
    link_type: str,
    your_page_url: str,
) -> str:
    """Generate a personalized, ready-to-send outreach email.

    Args:
        prospect_name: First name of editor or site owner. Use 'there' if unknown.
        prospect_site: Their website name.
        topic: Topic of the page where we want a backlink.
        link_type: One of: guest_post, broken_link, resource, unlinked_mention,
            directory, interview, forum.
        your_page_url: Our specific page URL to be linked (e.g. a product or blog page).
    """
    t = {
        "broken_link": (
            f"Subject: Broken link on your {topic} page — quick fix\n\n"
            f"Hi {prospect_name},\n\n"
            f"I came across your excellent {topic} page on {prospect_site} and noticed "
            f"one of the links appears to be broken.\n\n"
            f"I run {BRAND_NAME} ({TARGET_DOMAIN}) and have a detailed, up-to-date resource "
            f"that would be a perfect replacement: {your_page_url}\n\n"
            f"Happy to help keep your page accurate — would you consider swapping it in?\n\n"
            f"Best regards,\n{BRAND_NAME} Team\n{TARGET_DOMAIN}"
        ),
        "guest_post": (
            f"Subject: Guest post pitch for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"Love the work on {prospect_site} — your coverage of {topic} is spot-on.\n\n"
            f"I'm the team at {BRAND_NAME} ({TARGET_DOMAIN}) and I'd love to contribute "
            f"a guest article your audience would find genuinely useful. "
            f"I have a few topic ideas in mind — happy to share if you're open to it.\n\n"
            f"Would you be interested in collaborating?\n\n"
            f"Best,\n{BRAND_NAME} Team\n{TARGET_DOMAIN}"
        ),
        "resource": (
            f"Subject: One more resource for your {topic} page?\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your {topic} resource page on {prospect_site} is excellent — "
            f"one of the most comprehensive I've seen.\n\n"
            f"I thought your readers might also find this useful: {your_page_url}\n"
            f"It covers [unique angle not already on your list].\n\n"
            f"Would you be open to adding it?\n\n"
            f"Thank you,\n{BRAND_NAME} Team\n{TARGET_DOMAIN}"
        ),
        "unlinked_mention": (
            f"Subject: Thanks for mentioning {BRAND_NAME}!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {BRAND_NAME} in your article about {topic} on {prospect_site} — "
            f"it means a lot to our team!\n\n"
            f"Would you be open to linking directly to {your_page_url}? "
            f"It gives your readers a direct path to the resource you referenced.\n\n"
            f"Thanks again,\n{BRAND_NAME} Team\n{TARGET_DOMAIN}"
        ),
        "directory": (
            f"Subject: {BRAND_NAME} listing submission — {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'd like to submit {BRAND_NAME} to your {topic} directory on {prospect_site}.\n\n"
            f"Website: https://{TARGET_DOMAIN}\n"
            f"Description: [Brief 1–2 sentence description of the product/service]\n\n"
            f"Please let me know if you need anything else for the listing!\n\n"
            f"Best,\n{BRAND_NAME} Team\n{TARGET_DOMAIN}"
        ),
        "interview": (
            f"Subject: Expert interview contribution — {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I love the expert roundups on {prospect_site} about {topic}.\n\n"
            f"I'm part of the {BRAND_NAME} team and would love to contribute insights "
            f"for a future piece. We have hands-on experience with [relevant topic] "
            f"that I think your readers would value.\n\n"
            f"Would you consider including us in an upcoming roundup or Q&A?\n\n"
            f"Best,\n{BRAND_NAME} Team\n{TARGET_DOMAIN}"
        ),
    }
    return t.get(link_type, t["resource"])


# ─── Daily Run ────────────────────────────────────────────────────────────────


def run_daily_backlink_session() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    logger.info("=" * 60)
    logger.info("Daily backlink session started — %s", today)

    client = anthropic.Anthropic()

    conn = sqlite3.connect(DB_PATH)
    run_id = conn.execute(
        "INSERT INTO daily_runs (run_date) VALUES (?)", (today,)
    ).lastrowid
    conn.commit()
    conn.close()

    try:
        runner = client.beta.messages.tool_runner(
            model="claude-opus-4-6",
            max_tokens=16000,
            tools=[
                save_opportunity,
                get_tracked_urls,
                score_link_prospect,
                analyze_backlink_quality,
                generate_outreach_email,
                {"type": "web_search_20260209", "name": "web_search"},
                {"type": "web_fetch_20260209", "name": "web_fetch"},
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a senior off-page SEO specialist. Your mission today ({today}):
Find and save at least 10 NEW, HIGH-QUALITY, RELEVANT backlink opportunities for {TARGET_DOMAIN} (brand: {BRAND_NAME}).

━━━ STEP 1 — Understand the business ━━━
Fetch https://{TARGET_DOMAIN} to understand exactly what {BRAND_NAME} sells, their niche,
target audience, and key pages (products, blog, about). Note the industry and keywords.

━━━ STEP 2 — Check existing tracking ━━━
Call get_tracked_urls("all") — do NOT re-submit URLs already in the database.

━━━ STEP 3 — Find backlink opportunities ━━━
Run multiple targeted web_search queries. For each type below, run at least 2 searches:

A) Resource Pages
   Search: [niche] + "useful resources" OR "recommended links" OR "resource page"
   Search: [niche] + "best websites" OR "top sites" site:.org OR site:.edu

B) Guest Post Opportunities
   Search: [niche] + "write for us" OR "guest post guidelines" OR "submit article"
   Search: [niche] + "contributors" OR "become a contributor" OR "guest author"

C) Broken Link Building
   Search: [niche] + "links" OR "resources" intitle:"top" OR intitle:"best" -2025 -2026
   (find outdated pages likely to have dead links — our content can replace them)

D) Unlinked Brand Mentions
   Search: "{BRAND_NAME}" -site:{TARGET_DOMAIN}
   Search: "{TARGET_DOMAIN}" -site:{TARGET_DOMAIN}

E) Niche Directories & Listings
   Search: [niche] + "business directory" OR "company listing" OR "add your business"
   Search: [niche] + "submit site" OR "submit listing"

F) Competitor Backlink Gaps
   Find 2–3 direct competitors of {TARGET_DOMAIN}. For each, search:
   "site:[competitor]" to discover the kind of sites that link to them.
   Then find those pages and save them as opportunities.

G) Expert Roundups & Interviews
   Search: [niche] + "expert roundup" OR "industry experts" OR "interview with"

H) Forum & Community Participation
   Search: [niche] + "forum" OR "community" OR "reddit" OR "Q&A"
   (find places where contributing adds value and a profile/signature link is appropriate)

━━━ STEP 4 — Evaluate & save each opportunity ━━━
For every promising result:
1. Fetch the page to verify it's live, relevant, and accepts links/contributions
2. Score it with score_link_prospect
3. Generate outreach with generate_outreach_email
4. Save it with save_opportunity (include full outreach template in the field)

Only save sites that are:
- Genuinely relevant to {TARGET_DOMAIN}'s niche
- Clearly live and active (published within last 2 years, or evergreen resource pages)
- Not toxic, spammy, or low-quality

━━━ STEP 5 — Final summary ━━━
Write a clear daily report covering:
- Business niche confirmed for {TARGET_DOMAIN}
- Total opportunities discovered and saved today
- Top 5 highest-priority actions (with URLs and why)
- Recommended outreach order (highest ROI first)
- Any quick-win opportunities (e.g. directories that auto-approve)
- 1 sentence on what to focus on tomorrow

Be thorough, systematic, and specific. Quantity AND quality matter.""",
                }
            ],
        )

        report_parts: list[str] = []
        for message in runner:
            for block in message.content:
                if block.type == "text":
                    snippet = block.text[:300].replace("\n", " ")
                    logger.info("Agent: %s%s", snippet, "…" if len(block.text) > 300 else "")
                    report_parts.append(block.text)

        report_path = REPORTS_DIR / f"backlinks_{today}.md"
        with open(report_path, "w") as f:
            f.write(f"# Daily Backlink Report — {TARGET_DOMAIN}\n")
            f.write(f"**Date:** {today}\n\n")
            f.write("---\n\n")
            f.write("\n\n".join(report_parts))

        conn = sqlite3.connect(DB_PATH)
        found_today = conn.execute(
            "SELECT COUNT(*) FROM opportunities WHERE found_date=?", (today,)
        ).fetchone()[0]
        conn.execute(
            "UPDATE daily_runs SET found=?, report_file=?, success=1 WHERE id=?",
            (found_today, str(report_path), run_id),
        )
        conn.commit()
        conn.close()

        logger.info("Session complete. New opportunities saved today: %d", found_today)
        logger.info("Report: %s", report_path)

    except Exception as exc:
        logger.error("Session failed: %s", exc, exc_info=True)
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE daily_runs SET success=0, error=? WHERE id=?", (str(exc), run_id)
        )
        conn.commit()
        conn.close()
        raise


# ─── Entry Point ──────────────────────────────────────────────────────────────


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description=f"Daily Backlink Builder for {TARGET_DOMAIN}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python daily_backlink_builder.py               # Run once right now
  python daily_backlink_builder.py --schedule    # Run on daily cron at 09:00 UTC

Cron alternative (add to crontab with: crontab -e):
  0 9 * * * cd /path/to/offpage-seo-agent && python daily_backlink_builder.py >> backlink_builder.log 2>&1
        """,
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Keep running and execute daily at 09:00 UTC (uses APScheduler)",
    )
    args = parser.parse_args()

    init_db()

    if args.schedule:
        try:
            from apscheduler.schedulers.blocking import BlockingScheduler
            from apscheduler.triggers.cron import CronTrigger
        except ImportError:
            logger.error("APScheduler not installed. Run: pip install apscheduler")
            sys.exit(1)

        scheduler = BlockingScheduler(timezone="UTC")
        scheduler.add_job(
            run_daily_backlink_session,
            CronTrigger(hour=9, minute=0),
            id="daily_backlink_build",
            name=f"Daily Backlink Builder — {TARGET_DOMAIN}",
            replace_existing=True,
            misfire_grace_time=3600,
        )
        logger.info("Scheduler started. Daily run at 09:00 UTC for %s.", TARGET_DOMAIN)
        logger.info("Press Ctrl+C to stop.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped.")
    else:
        run_daily_backlink_session()


if __name__ == "__main__":
    main()
