#!/usr/bin/env python3
"""Daily backlink builder for alfaapanels.com.

Run once:   python daily_backlink_builder.py
Scheduler:  python daily_backlink_builder.py --schedule
"""

import json
import os
import schedule
import sys
import time
from datetime import date
from pathlib import Path

import anthropic
from anthropic import beta_tool

# ── Site configuration ────────────────────────────────────────────────────────
DOMAIN = "alfaapanels.com"
BRAND = "Alfa Panels"
NICHE = "aluminum composite panels building facades exterior cladding architectural panels ACP"
SITE_DESCRIPTION = (
    "Alfa Panels supplies premium aluminum composite panels (ACP), facade cladding, "
    "and architectural panel systems for commercial and residential buildings."
)
COMPETITORS = ["alucobond.com", "etalbond.com", "reynobond.com"]

# ── Storage ───────────────────────────────────────────────────────────────────
BACKLINK_LOG_FILE = "backlink_log.json"
REPORTS_DIR = "daily_reports"

# ── 7-day rotating strategy (0 = Monday … 6 = Sunday) ────────────────────────
STRATEGY_ROTATION = [
    "business_directories",   # Mon
    "industry_directories",   # Tue
    "forum_participation",    # Wed
    "social_bookmarking",     # Thu
    "guest_post_outreach",    # Fri
    "resource_page_links",    # Sat
    "broken_link_building",   # Sun
]

STRATEGIES = {
    "business_directories": {
        "name": "Business Directory Submissions",
        "description": "Submit to high-authority general business directories",
        "task": (
            f"Execute business directory link building for {DOMAIN}:\n\n"
            "1. Search for existing listings: search \"Alfa Panels\" in major directories\n"
            "2. Find directories NOT yet listing us and prioritise:\n"
            "   Google My Business, Bing Places, Apple Maps, Yelp, Yellow Pages,\n"
            "   Foursquare, Manta, Hotfrog, Cylex, Trustpilot\n"
            "3. For each unlisted directory use log_backlink_opportunity to record:\n"
            "   - Directory URL and direct submission page URL\n"
            "   - Category to select during submission\n"
            "   - Ready-to-paste business description\n"
            f"4. Generate a 150-word business description optimised for \"{NICHE}\"\n"
            "5. Rank top 5 directories by authority and list their submission URLs"
        ),
    },
    "industry_directories": {
        "name": "Industry-Specific Directory Links",
        "description": "Get listed in construction, architecture, and building-materials directories",
        "task": (
            f"Execute industry directory link building for {DOMAIN}:\n\n"
            "1. Search: \"aluminum composite panel suppliers directory\"\n"
            "2. Search: \"building materials manufacturer directory site:.org OR site:.com\"\n"
            "3. Search: \"construction product directory architectural panels\"\n"
            "4. Target categories:\n"
            "   Architecture & design (Architizer, ArchDaily supplier directory)\n"
            "   Construction materials (Thomasnet, GlobalSpec, Arcat, Sweets Network)\n"
            "   Trade directories (Kompass, Europages, BIMobject)\n"
            "5. Score each prospect with score_link_prospect\n"
            "6. Log top 5 with log_backlink_opportunity\n"
            "7. Generate submission copy for the top 3 prospects"
        ),
    },
    "forum_participation": {
        "name": "Forum & Community Participation",
        "description": "Build authority links through expert forum contributions",
        "task": (
            f"Execute forum participation link building for {DOMAIN}:\n\n"
            "1. Search: \"aluminum composite panel forum discussion\"\n"
            "2. Search: \"building facade community architects forum\"\n"
            "3. Search: \"ACP cladding questions site:reddit.com\"\n"
            "4. Find opportunities on:\n"
            "   Reddit (r/architecture, r/construction, r/DIY)\n"
            "   Quora questions about aluminum panels and facades\n"
            "   SkyscraperCity, Houzz community, LinkedIn groups\n"
            f"5. For Quora: find 3 questions we can answer linking to {DOMAIN}\n"
            "6. For forums: identify threads needing expert input\n"
            "7. Log each with log_backlink_opportunity\n"
            "8. Write 3 sample expert replies that provide real value and naturally reference our site"
        ),
    },
    "social_bookmarking": {
        "name": "Social Bookmarking & Content Sharing",
        "description": "Build links by sharing content on bookmarking platforms",
        "task": (
            f"Execute social bookmarking link building for {DOMAIN}:\n\n"
            "Target platforms: Pinterest, Tumblr, Medium, Mix, Scoop.it, Flipboard\n\n"
            "Create 5 shareable content pieces:\n"
            "  1. Top 10 Uses of Aluminum Composite Panels in Modern Architecture\n"
            "  2. ACP vs Traditional Cladding: Complete 2026 Comparison\n"
            "  3. How to Choose the Right Facade Panel for Your Building\n"
            "  4. ACP Installation: What Architects and Contractors Must Know\n"
            "  5. Latest Building Facade Design Trends 2026\n\n"
            "For each piece generate:\n"
            "  - Engaging title and 100-word description\n"
            "  - 8-10 relevant tags\n"
            "  - Platform-specific optimisation tip\n"
            "  - Direct submission/post URL for each platform\n"
            "Log each platform as an opportunity with log_backlink_opportunity"
        ),
    },
    "guest_post_outreach": {
        "name": "Guest Post Outreach",
        "description": "Pitch guest articles to architecture and construction blogs",
        "task": (
            f"Execute guest post outreach for {DOMAIN}:\n\n"
            "1. Search: \"architecture blog write for us 2026\"\n"
            "2. Search: \"construction blog guest post guidelines\"\n"
            "3. Search: \"building materials blog contributor wanted\"\n"
            "4. Search: \"interior design blog accept guest posts\"\n"
            "5. Find 5 high-quality blogs that accept guest posts covering\n"
            "   architecture, construction, or building materials\n"
            "6. Score each with score_link_prospect\n"
            "7. Generate a personalised outreach email for each using\n"
            "   generate_outreach_template (link_type='guest_post')\n"
            "8. Log all with log_backlink_opportunity\n"
            "9. Provide a ranked shortlist with editor contact info"
        ),
    },
    "resource_page_links": {
        "name": "Resource Page Link Building",
        "description": "Get listed on curated resource pages for building materials",
        "task": (
            f"Execute resource page link building for {DOMAIN}:\n\n"
            "1. Search: \"aluminum composite panel resources\" intitle:resources\n"
            "2. Search: \"building materials resources links site:.edu\"\n"
            "3. Search: \"facade cladding guide recommended suppliers\"\n"
            "4. Search: \"architecture materials reference list\"\n"
            "5. Find 5 resource/link pages where Alfa Panels should appear:\n"
            "   University architecture departments\n"
            "   Professional association supplier lists\n"
            "   Industry guide pages and buying guides\n"
            "   Product comparison directories\n"
            "6. Score each with score_link_prospect\n"
            "7. Generate personalised outreach (link_type='resource') for top 3\n"
            "8. Log all with log_backlink_opportunity"
        ),
    },
    "broken_link_building": {
        "name": "Broken Link Building",
        "description": "Find broken links on relevant sites and offer Alfa Panels content as replacement",
        "task": (
            f"Execute broken link building for {DOMAIN}:\n\n"
            "1. Search: \"aluminum composite panels guide site:archdaily.com\"\n"
            "2. Search: \"ACP cladding resources\" on major architecture sites\n"
            "3. Search: \"building facade panel supplier\" – look for outdated/dead links\n"
            "4. Use web_fetch to check promising pages for 404 or redirect links\n"
            "5. Find 3-5 broken link opportunities where our content can replace:\n"
            "   Outdated supplier links\n"
            "   Discontinued product pages\n"
            "   Moved or deleted resource pages\n"
            "6. For each opportunity:\n"
            "   - Record page URL, broken link URL, and replacement suggestion\n"
            "   - Generate outreach with generate_outreach_template (link_type='broken_link')\n"
            "7. Log all with log_backlink_opportunity"
        ),
    },
}


# ── Backlink log helpers ───────────────────────────────────────────────────────
def _load_log() -> dict:
    if os.path.exists(BACKLINK_LOG_FILE):
        with open(BACKLINK_LOG_FILE) as f:
            return json.load(f)
    return {"total_opportunities": 0, "entries": []}


def _save_log(log: dict) -> None:
    with open(BACKLINK_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


# ── Beta tools (executed locally by the tool_runner) ─────────────────────────
client = anthropic.Anthropic()


@beta_tool
def log_backlink_opportunity(
    source_url: str,
    link_type: str,
    priority: str,
    submission_url: str,
    notes: str,
    outreach_email: str = "",
) -> str:
    """Log a discovered backlink opportunity to the tracker file.

    Args:
        source_url: URL of the site where we can earn a backlink.
        link_type: One of: directory, forum, guest_post, resource, broken_link, social.
        priority: HIGH, MEDIUM, or LOW.
        submission_url: Direct URL for submission or editor contact.
        notes: Action notes — how to build this link.
        outreach_email: Ready-to-send outreach email (optional).
    """
    log = _load_log()
    entry = {
        "id": log["total_opportunities"] + 1,
        "date": str(date.today()),
        "source_url": source_url,
        "link_type": link_type,
        "priority": priority,
        "submission_url": submission_url,
        "notes": notes,
        "outreach_email": outreach_email,
        "status": "pending",
    }
    log["entries"].append(entry)
    log["total_opportunities"] += 1
    _save_log(log)
    return f"Logged #{entry['id']}: {source_url} [{priority} / {link_type}]"


@beta_tool
def get_backlink_stats() -> str:
    """Return a summary of all backlink opportunities logged so far."""
    log = _load_log()
    if not log["entries"]:
        return "No backlink opportunities logged yet."

    by_type: dict = {}
    by_priority = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    by_status = {"pending": 0, "submitted": 0, "live": 0}

    for e in log["entries"]:
        t = e.get("link_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
        p = e.get("priority", "MEDIUM")
        if p in by_priority:
            by_priority[p] += 1
        s = e.get("status", "pending")
        if s in by_status:
            by_status[s] += 1

    lines = [
        f"Total opportunities: {log['total_opportunities']}",
        f"By priority: {by_priority}",
        f"By type:     {by_type}",
        f"By status:   {by_status}",
        "Latest 5 entries:",
    ]
    for e in log["entries"][-5:]:
        lines.append(f"  #{e['id']} [{e['date']}] {e['source_url']} — {e['priority']}")
    return "\n".join(lines)


@beta_tool
def score_link_prospect(
    page_url: str,
    page_title: str,
    page_content_snippet: str,
    your_niche: str,
) -> str:
    """Score a potential link building prospect from 0 to 100.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short excerpt of page content.
        your_niche: Your website's niche/topic keywords.
    """
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    content = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for w in niche_words if w in content)
    if relevance >= 3:
        score += 40
        reasons.append(f"High niche relevance ({relevance} terms matched) (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append(f"Moderate niche relevance ({relevance} term) (+20)")
    else:
        reasons.append("Low niche relevance (+0)")
    value_signals = ["resource", "guide", "directory", "suppliers", "list", "blog", "tools"]
    if any(s in page_url.lower() or s in page_title.lower() for s in value_signals):
        score += 30
        reasons.append("Resource/directory page — high link value (+30)")
    authority_tlds = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_tlds):
        score += 30
        reasons.append("High-authority TLD (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 — {priority}\n" + "\n".join(f"  • {r}" for r in reasons)


@beta_tool
def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    link_type: str,
) -> str:
    """Generate a personalised outreach email for link building.

    Args:
        prospect_name: Editor/webmaster name (use 'Editor' if unknown).
        prospect_site: Their website name.
        their_page_topic: Topic of the page where a link is wanted.
        link_type: guest_post | broken_link | resource | mention.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I spotted what looks like a broken link on your {their_page_topic} page at {prospect_site}.\n\n"
            f"We recently published a comprehensive resource at {DOMAIN} that covers this topic in depth "
            f"and could serve as a great replacement for your readers.\n\n"
            f"Happy to share the exact URL if you'd like to check it out.\n\n"
            f"Best,\n[Your Name]\n{BRAND} | {DOMAIN}"
        ),
        "guest_post": (
            f"Subject: Guest Post Pitch for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been enjoying your content on {their_page_topic} at {prospect_site} — great work.\n\n"
            f"I'm with {BRAND} ({DOMAIN}), specialists in aluminum composite panels and facade systems. "
            f"I'd love to contribute a guest article that would genuinely help your audience.\n\n"
            f"Possible topics:\n"
            f"• Modern ACP Facade Design Trends in 2026\n"
            f"• How to Specify the Right Cladding System for Commercial Projects\n"
            f"• ACP vs Traditional Facades: A Cost & Performance Breakdown\n\n"
            f"Would any of these be a fit? I'm happy to tailor the angle to your audience.\n\n"
            f"Best,\n[Your Name]\n{BRAND} | {DOMAIN}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} at {prospect_site} is really helpful.\n\n"
            f"We have a detailed guide at {DOMAIN} covering aluminum composite panels, facade selection, "
            f"and installation best practices that your readers might find useful.\n\n"
            f"Would you consider adding it to the list?\n\n"
            f"Thanks,\n[Your Name]\n{BRAND} | {DOMAIN}"
        ),
        "mention": (
            f"Subject: Thank you for mentioning {BRAND}!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for the mention in your article on {their_page_topic} at {prospect_site}!\n\n"
            f"Would you be open to linking directly to {DOMAIN}? It would make it easier "
            f"for your readers to find us.\n\n"
            f"Thanks again,\n[Your Name]\n{BRAND} | {DOMAIN}"
        ),
    }
    return templates.get(link_type, templates["resource"])


# ── Daily runner ──────────────────────────────────────────────────────────────
def get_todays_strategy() -> dict:
    key = STRATEGY_ROTATION[date.today().weekday()]
    return {"key": key, **STRATEGIES[key]}


def run_daily_backlink_agent() -> str:
    today = date.today()
    strategy = get_todays_strategy()

    print(f"\n{'='*60}")
    print(f"Alfa Panels Daily Backlink Builder — {today}")
    print(f"Strategy: {strategy['name']}")
    print("=" * 60 + "\n")

    system_prompt = (
        f"You are an expert link builder working exclusively for {DOMAIN} ({BRAND}).\n\n"
        f"Business: {SITE_DESCRIPTION}\n"
        f"Target keywords: aluminum composite panels, ACP panels, building facades, "
        f"exterior cladding, facade cladding, architectural panel systems\n"
        f"Domain: {DOMAIN}\n"
        f"Niche: {NICHE}\n"
        f"Competitors: {', '.join(COMPETITORS)}\n\n"
        f"Today's mission: {strategy['description']}\n\n"
        "Rules:\n"
        "- Use web_search to find REAL, current opportunities (not hypothetical)\n"
        "- Use web_fetch to verify the best prospects before logging\n"
        "- Use score_link_prospect to evaluate each candidate\n"
        "- Use log_backlink_opportunity to record EVERY valid opportunity (aim for ≥5)\n"
        "- Use generate_outreach_template for guest posts, broken links, and resource pages\n"
        "- Focus on relevance and domain authority over volume\n"
        "- Always include the direct submission URL or contact page in submissions"
    )

    user_message = (
        f"{strategy['task']}\n\n"
        "After completing the search:\n"
        "1. Call get_backlink_stats to show today's progress\n"
        "2. Summarise the top 3 opportunities with specific next steps\n"
        "3. Output a prioritised action list for the Alfa Panels team"
    )

    Path(REPORTS_DIR).mkdir(exist_ok=True)
    report_lines: list[str] = []

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        system=system_prompt,
        tools=[
            log_backlink_opportunity,
            get_backlink_stats,
            score_link_prospect,
            generate_outreach_template,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{"role": "user", "content": user_message}],
    )

    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_lines.append(block.text)

    report_path = Path(REPORTS_DIR) / f"backlink_report_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Backlink Building Report — {today}\n")
        f.write(f"**Strategy:** {strategy['name']}\n\n")
        f.write("---\n\n")
        f.write("\n\n".join(report_lines))

    print(f"\nReport saved: {report_path}")
    return str(report_path)


# ── Scheduler (--schedule flag) ───────────────────────────────────────────────
def run_scheduler() -> None:
    print(f"Backlink scheduler started for {DOMAIN}")
    print("Runs daily at 09:00. Press Ctrl-C to stop.\n")
    schedule.every().day.at("09:00").do(run_daily_backlink_agent)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    if "--schedule" in sys.argv:
        run_scheduler()
    else:
        run_daily_backlink_agent()
