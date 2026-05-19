#!/usr/bin/env python3
"""Daily backlink builder for alfaapanels.com

Runs a rotating set of backlink-building strategies each day, tracks
what has already been contacted to avoid duplicate outreach, and saves
a date-stamped markdown report for every run.

Usage:
    python daily_backlink_builder.py           # auto-detects today's strategy
    python daily_backlink_builder.py --task brand_mentions
    python daily_backlink_builder.py --task competitor_gaps
    python daily_backlink_builder.py --task resource_pages
    python daily_backlink_builder.py --task guest_posts
    python daily_backlink_builder.py --task broken_links
    python daily_backlink_builder.py --task directory_listings
    python daily_backlink_builder.py --task weekly_summary
"""

import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

import anthropic
from anthropic import beta_tool

# ── Site configuration ──────────────────────────────────────────────────────

SITE_CONFIG = {
    "domain": "alfaapanels.com",
    "brand_name": "Alfa Panels",
    "niche": "solar panels, PV modules, solar energy systems, renewable energy",
    "competitors": [
        "sunpower.com",
        "canadiansolar.com",
        "jinko-solar.com",
        "longi-solar.com",
        "solaria.com",
    ],
    "target_keywords": [
        "solar panels",
        "solar energy panels",
        "PV modules",
        "solar installation",
        "alfaapanels",
        "alfa panels",
    ],
}

# ── Daily strategy rotation (weekday index 0=Mon … 6=Sun) ───────────────────

DAILY_ROTATION = {
    0: "brand_mentions",
    1: "competitor_gaps",
    2: "resource_pages",
    3: "guest_posts",
    4: "broken_links",
    5: "directory_listings",
    6: "weekly_summary",
}

TASK_DESCRIPTIONS = {
    "brand_mentions": "Find unlinked brand mentions of Alfa Panels / alfaapanels.com and prepare outreach to convert them to backlinks.",
    "competitor_gaps": "Find high-authority sites that link to competitors but NOT to alfaapanels.com and create a prioritised gap list.",
    "resource_pages": "Discover solar-energy / renewable-energy resource pages and guides that could link to alfaapanels.com.",
    "guest_posts": "Find solar-energy blogs and news sites that accept guest posts or contributor articles relevant to alfaapanels.com.",
    "broken_links": "Search for broken outbound links on authoritative solar / renewable-energy pages that alfaapanels.com content could replace.",
    "directory_listings": "Find reputable business directories, solar-energy directories, and niche listings where alfaapanels.com is missing.",
    "weekly_summary": "Review all opportunities found this week, rank the top 10 by priority, and produce a consolidated action plan.",
}

REPORTS_DIR = Path("reports")
TRACKING_FILE = Path("backlink_tracking.json")

# ── Persistent tracking helpers ──────────────────────────────────────────────


def load_tracking() -> dict:
    if TRACKING_FILE.exists():
        with open(TRACKING_FILE) as f:
            return json.load(f)
    return {"contacted": [], "opportunities": [], "runs": []}


def save_tracking(data: dict) -> None:
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f, indent=2)


def record_run(tracking: dict, task: str, report_path: str) -> None:
    tracking.setdefault("runs", []).append(
        {
            "date": str(date.today()),
            "task": task,
            "report": report_path,
        }
    )


def already_contacted(tracking: dict, domain: str) -> bool:
    return domain.lower() in [c.lower() for c in tracking.get("contacted", [])]


# ── Custom SEO tools (registered with @beta_tool) ────────────────────────────


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    signals = []
    generic = {"click here", "website", "here", "link", "read more"}
    if anchor_text.lower() in generic:
        signals.append("Warning: Generic anchor text – low SEO value")
    else:
        signals.append(f"Good: Descriptive anchor '{anchor_text}'")
    toxic_terms = ["spam", "casino", "viagra", "porn", "gambling"]
    if any(t in backlink_url.lower() for t in toxic_terms):
        signals.append("TOXIC link – disavow recommended")
    else:
        signals.append("Domain appears clean")
    return "\n".join(signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorise a brand mention as linked/unlinked and detect sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive = ["great", "best", "excellent", "recommend", "love", "amazing", "leading"]
    negative = ["bad", "worst", "avoid", "scam", "terrible", "poor", "fake"]
    pos = sum(1 for w in positive if w in mention_text.lower())
    neg = sum(1 for w in negative if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else ("Negative" if neg > pos else "Neutral")
    mention_type = "Linked mention" if has_link else "Unlinked mention (outreach opportunity)"
    action = "Monitor existing link" if has_link else "Reach out to add your link"
    return (
        f"Brand: {brand_name}\n"
        f"Type: {mention_type}\n"
        f"Sentiment: {sentiment}\n"
        f"Action: {action}"
    )


@beta_tool
def score_link_prospect(
    page_url: str, page_title: str, page_content_snippet: str, your_niche: str
) -> str:
    """Score a potential link-building prospect 0-100.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
        your_niche: Your website's niche/topic.
    """
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    combined = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for w in niche_words if w in combined)
    if relevance >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value = ["resource", "guide", "tools", "blog", "list", "best", "top", "directory"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("Resource / guide page (+30)")
    authority = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority):
        score += 30
        reasons.append("High-authority TLD (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH" if score >= 70 else ("MEDIUM" if score >= 40 else "LOW")
    return (
        f"Score: {score}/100 – {priority} PRIORITY\n"
        f"URL: {page_url}\n"
        "Reasons:\n" + "\n".join(f"  • {r}" for r in reasons)
    )


@beta_tool
def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    your_site: str,
    your_content_url: str,
    link_type: str,
) -> str:
    """Generate a personalised outreach email for link building.

    Args:
        prospect_name: Name of the website owner/editor.
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        your_site: Your website name.
        your_content_url: URL of your content to be linked.
        link_type: One of 'guest_post', 'broken_link', 'resource', 'mention'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"While reading your {their_page_topic} page on {prospect_site} I noticed a broken link "
            f"that may be frustrating your readers.\n\n"
            f"I have a comprehensive, up-to-date resource at {your_content_url} that would be a "
            f"great replacement.\n\n"
            "Would you consider updating it?\n\nBest regards,\n[Your Name] – Alfa Panels"
        ),
        "guest_post": (
            f"Subject: Guest Post Idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I really enjoy your content on {prospect_site}, especially around {their_page_topic}.\n\n"
            f"I write for {your_site} and would love to contribute a practical guest post "
            f"your audience would find useful.\n\n"
            "Would you be open to a collaboration?\n\nBest regards,\n[Your Name] – Alfa Panels"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page covering {their_page_topic} is excellent! I created "
            f"{your_content_url}, which goes deeper on the topic and might add extra value "
            f"for your readers.\n\n"
            "Would you take a look?\n\nBest regards,\n[Your Name] – Alfa Panels"
        ),
        "mention": (
            f"Subject: Thanks for mentioning {your_site}!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {your_site} in your article about {their_page_topic} – "
            f"really appreciate it!\n\n"
            f"Would you be open to linking directly to {your_content_url} so readers can "
            f"find the resource easily?\n\nThanks,\n[Your Name] – Alfa Panels"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(
    competitor_domain: str, your_domain: str, linking_page_topic: str
) -> str:
    """Identify a competitor backlink gap as an opportunity for your site.

    Args:
        competitor_domain: Competitor's domain.
        your_domain: Your domain.
        linking_page_topic: Topic of the page linking to the competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site:  {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Action plan:\n"
        f"  1. Identify the specific content on {competitor_domain} that earned this link\n"
        f"  2. Create a better / more up-to-date version for {your_domain}\n"
        f"  3. Reach out to the linking page with your improved resource"
    )


@beta_tool
def log_prospect(domain: str, contact_email: str, opportunity_type: str, notes: str) -> str:
    """Log a new outreach prospect to the persistent tracking file.

    Args:
        domain: The prospect's domain.
        contact_email: Their contact email (or 'unknown').
        opportunity_type: One of 'broken_link', 'resource', 'guest_post', 'mention', 'directory'.
        notes: Short notes about the opportunity.
    """
    tracking = load_tracking()
    if already_contacted(tracking, domain):
        return f"SKIPPED: {domain} already in outreach history"
    entry = {
        "domain": domain,
        "contact_email": contact_email,
        "type": opportunity_type,
        "notes": notes,
        "discovered": str(date.today()),
        "status": "new",
    }
    tracking.setdefault("opportunities", []).append(entry)
    save_tracking(tracking)
    return f"LOGGED: {domain} – {opportunity_type} opportunity saved to tracking file"


# ── Task prompts ─────────────────────────────────────────────────────────────


def build_prompt(task: str, config: dict, tracking: dict) -> str:
    already = tracking.get("contacted", [])
    skip_note = (
        f"\n\nIMPORTANT – skip these domains already contacted: {', '.join(already[:20])}"
        if already
        else ""
    )

    base = (
        f"You are an expert off-page SEO strategist working for {config['domain']} "
        f"({config['brand_name']}), a {config['niche']} company.\n\n"
        f"Today's date: {date.today().isoformat()}\n"
        f"Today's focus: {task.upper()} – {TASK_DESCRIPTIONS[task]}{skip_note}\n\n"
    )

    task_prompts = {
        "brand_mentions": (
            f"TASK: Brand Mention Backlink Conversion\n\n"
            f"1. Use web_search to find unlinked mentions of '{config['brand_name']}' and "
            f"'alfaapanels.com' across blogs, news sites, and forums:\n"
            f"   • Search: \"{config['brand_name']}\" -site:{config['domain']}\n"
            f"   • Search: \"alfaapanels\" -site:{config['domain']}\n"
            f"2. For each mention found, use categorize_brand_mention to classify it.\n"
            f"3. For unlinked positive/neutral mentions, use score_link_prospect to rate the site.\n"
            f"4. Use log_prospect to record each new opportunity.\n"
            f"5. Use generate_outreach_template (type='mention') for the top 5 prospects.\n"
            f"6. Summarise findings in a structured report with a priority table."
        ),
        "competitor_gaps": (
            f"TASK: Competitor Backlink Gap Analysis\n\n"
            f"Competitors to analyse: {', '.join(config['competitors'])}\n\n"
            f"1. For EACH competitor listed above, use web_search to find sites linking to them:\n"
            f"   • Search: \"<competitor_domain>\" recommended resources  (replace with each domain)\n"
            f"   • Search: <competitor_domain> backlinks solar panels\n"
            f"2. Use identify_link_gap_opportunity for each gap found.\n"
            f"3. Use score_link_prospect to prioritise opportunities.\n"
            f"4. Use log_prospect to record each new opportunity.\n"
            f"5. Generate outreach templates for the top 5 gaps using generate_outreach_template.\n"
            f"6. Produce a gap table ranked by score."
        ),
        "resource_pages": (
            f"TASK: Resource Page Link Building\n\n"
            f"1. Use web_search to find resource/guide pages in the solar energy niche:\n"
            f"   • 'solar energy resources' intitle:resources\n"
            f"   • 'best solar panel guides' intitle:guide\n"
            f"   • 'renewable energy tools' intitle:tools\n"
            f"   • 'solar panel installation resources' site:.org OR site:.edu\n"
            f"2. Fetch 3-5 promising pages with web_fetch to verify they accept external links.\n"
            f"3. Score each with score_link_prospect.\n"
            f"4. Log all HIGH and MEDIUM prospects with log_prospect.\n"
            f"5. Prepare outreach emails (type='resource') for the top 5.\n"
            f"6. Summarise with a priority table."
        ),
        "guest_posts": (
            f"TASK: Guest Post Opportunity Prospecting\n\n"
            f"1. Use web_search to find solar/renewable energy blogs accepting guest posts:\n"
            f"   • '\"write for us\" solar energy'\n"
            f"   • '\"guest post\" solar panels renewable'\n"
            f"   • '\"contribute\" solar energy blog'\n"
            f"   • '\"submit article\" photovoltaic OR solar'\n"
            f"2. Fetch submission guidelines from the top 5 prospects.\n"
            f"3. Score each with score_link_prospect.\n"
            f"4. Log qualifying prospects with log_prospect.\n"
            f"5. Draft outreach emails (type='guest_post') for the top 3.\n"
            f"6. List each site with their guidelines and a relevance note."
        ),
        "broken_links": (
            f"TASK: Broken Link Reclamation\n\n"
            f"1. Use web_search to find authoritative solar/renewable pages with possible broken links:\n"
            f"   • 'best solar panel resources' inurl:resources OR inurl:links\n"
            f"   • 'solar energy guide' site:.org OR site:.edu inurl:links\n"
            f"   • 'photovoltaic resources' inurl:resources\n"
            f"2. Fetch the top 5 pages and look for HTTP 404 or dead links in the content.\n"
            f"3. For each broken link found, identify if alfaapanels.com content could replace it.\n"
            f"4. Use score_link_prospect and log_prospect for each opportunity.\n"
            f"5. Generate broken_link outreach emails for the top 3.\n"
            f"6. Summarise broken link opportunities with replacement suggestions."
        ),
        "directory_listings": (
            f"TASK: Business Directory & Niche Listing Submissions\n\n"
            f"1. Use web_search to find reputable solar/renewable energy directories:\n"
            f"   • 'solar company directory submit'\n"
            f"   • 'renewable energy business listings'\n"
            f"   • 'solar panel manufacturer directory'\n"
            f"   • 'green energy company directory'\n"
            f"2. Also check general high-authority directories (BBB, Yelp, Google My Business prompts).\n"
            f"3. Fetch submission pages to verify they are free or low-cost.\n"
            f"4. Score each directory with score_link_prospect.\n"
            f"5. Log all HIGH and MEDIUM directories with log_prospect (type='directory').\n"
            f"6. Produce a sorted list with submission URLs and any notes."
        ),
        "weekly_summary": (
            f"TASK: Weekly Backlink Strategy Summary\n\n"
            f"Opportunities logged this week (from tracking data):\n"
            f"{json.dumps(tracking.get('opportunities', [])[-50:], indent=2)}\n\n"
            f"1. Review and group all opportunities by type (brand_mention, resource, guest_post, "
            f"broken_link, directory, competitor_gap).\n"
            f"2. Rank the top 10 overall by estimated SEO value and effort required.\n"
            f"3. For each top-10 item, confirm a ready-to-send outreach template.\n"
            f"4. Summarise this week's progress: new opportunities found, types breakdown, "
            f"recommended actions for next week.\n"
            f"5. Produce a clean action table: Rank | Domain | Type | Template Ready | Priority."
        ),
    }

    return base + task_prompts[task]


# ── Main runner ───────────────────────────────────────────────────────────────


def run_daily_task(task: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  Alfa Panels Daily Backlink Builder")
    print(f"  Date : {date.today().isoformat()}")
    print(f"  Task : {task}")
    print(f"{'=' * 60}\n")

    tracking = load_tracking()
    prompt = build_prompt(task, SITE_CONFIG, tracking)

    client = anthropic.Anthropic()
    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            log_prospect,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{"role": "user", "content": prompt}],
    )

    report_parts: list[str] = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_parts.append(block.text)

    # ── Save report ────────────────────────────────────────────────────────
    REPORTS_DIR.mkdir(exist_ok=True)
    report_filename = REPORTS_DIR / f"{date.today().isoformat()}_{task}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Alfa Panels Backlink Report – {task}\n")
        f.write(f"**Date:** {date.today().isoformat()}  \n")
        f.write(f"**Domain:** {SITE_CONFIG['domain']}  \n\n")
        f.write("---\n\n")
        f.write("\n\n".join(report_parts))
    print(f"\nReport saved → {report_filename}")

    # ── Update tracking ────────────────────────────────────────────────────
    tracking = load_tracking()  # reload in case log_prospect updated it
    record_run(tracking, task, str(report_filename))
    save_tracking(tracking)
    print(f"Tracking updated → {TRACKING_FILE}")


# ── CLI entry point ───────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily backlink builder for alfaapanels.com")
    parser.add_argument(
        "--task",
        choices=list(TASK_DESCRIPTIONS.keys()),
        default=None,
        help="Strategy to run (default: auto-selected by weekday)",
    )
    args = parser.parse_args()

    task = args.task or DAILY_ROTATION[date.today().weekday()]
    run_daily_task(task)


if __name__ == "__main__":
    main()
