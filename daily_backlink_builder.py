"""
Daily Backlink Builder for alfaapanels.com
Schedule via cron: 0 9 * * * cd /path/to/project && python daily_backlink_builder.py
"""

import anthropic
from anthropic import beta_tool
import json
import os
from datetime import datetime, date

# ── Configuration ──────────────────────────────────────────────────────────────
TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "aluminum composite panels, facade cladding, insulated sandwich panels, building panels, architectural cladding systems"
COMPETITORS = [
    "alucobond.com",
    "reynobond.com",
    "kingspan.com",
    "rockpanel.com",
    "trespa.com",
]

LOG_FILE = "backlink_log.json"
REPORTS_DIR = "daily_reports"

# Each weekday gets a different link-building tactic
DAILY_STRATEGIES = {
    0: {
        "name": "Directory & Citation Building",
        "focus": (
            "business directories, construction industry directories, local citations, "
            "architectural product directories, building materials directories"
        ),
    },
    1: {
        "name": "Q&A & Forum Outreach",
        "focus": (
            "Quora questions about facade panels, Reddit r/architecture r/construction, "
            "ArchDaily forums, architecture and construction community boards"
        ),
    },
    2: {
        "name": "Guest Post Prospecting",
        "focus": (
            "architecture blogs, construction blogs, building materials blogs, "
            "facade design publications, interior design sites accepting guest posts"
        ),
    },
    3: {
        "name": "Broken Link Building",
        "focus": (
            "resource pages, guides, and roundups about cladding, facades, or building panels "
            "that contain broken outbound links"
        ),
    },
    4: {
        "name": "Resource Page Link Building",
        "focus": (
            "resource pages, tools pages, supplier lists, and buyer's guides "
            "in architecture, construction, and building materials niches"
        ),
    },
    5: {
        "name": "Unlinked Brand Mention Conversion",
        "focus": (
            "pages that mention 'Alfa Panels' or 'alfaapanels' without a hyperlink – "
            "convert them to linked citations"
        ),
    },
    6: {
        "name": "Competitor Backlink Gap Analysis",
        "focus": (
            "sites, blogs, and directories that link to alucobond.com, reynobond.com, "
            "or kingspan.com but do NOT currently link to alfaapanels.com"
        ),
    },
}

# ── Log helpers ────────────────────────────────────────────────────────────────

def load_log() -> dict:
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {
        "contacted_domains": [],
        "submitted_directories": [],
        "opportunities_log": [],
    }


def save_log(log_data: dict) -> None:
    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=2)


# ── Agent tools ────────────────────────────────────────────────────────────────

client = anthropic.Anthropic()


@beta_tool
def log_backlink_opportunity(
    opportunity_type: str,
    target_url: str,
    domain: str,
    description: str,
    outreach_email: str,
    priority: str,
) -> str:
    """Log a discovered backlink opportunity to the tracking system.

    Args:
        opportunity_type: One of: directory, guest_post, broken_link, resource_page, forum, q_and_a, brand_mention, competitor_gap
        target_url: The exact URL where we want a backlink placed
        domain: Root domain of the target site (e.g. example.com)
        description: Why this is a good opportunity and what the page is about
        outreach_email: Ready-to-send outreach email OR step-by-step submission instructions
        priority: high, medium, or low
    """
    log_data = load_log()

    already_done = set(log_data["contacted_domains"] + log_data["submitted_directories"])
    if domain in already_done:
        return f"SKIP: {domain} already tracked – no duplicate entry created"

    entry = {
        "date": date.today().isoformat(),
        "type": opportunity_type,
        "url": target_url,
        "domain": domain,
        "description": description,
        "outreach": outreach_email,
        "priority": priority,
        "status": "pending",
    }
    log_data["opportunities_log"].append(entry)

    if opportunity_type == "directory":
        log_data["submitted_directories"].append(domain)
    else:
        log_data["contacted_domains"].append(domain)

    save_log(log_data)
    return f"LOGGED [{priority.upper()}] {opportunity_type} opportunity → {domain}"


@beta_tool
def check_already_contacted(domain: str) -> str:
    """Check whether a domain has already been contacted or submitted.

    Args:
        domain: Root domain to check (e.g. example.com)
    """
    log_data = load_log()
    already_done = set(log_data["contacted_domains"] + log_data["submitted_directories"])
    if domain in already_done:
        return f"ALREADY_TRACKED: skip {domain}"
    return f"NEW_PROSPECT: {domain} not yet contacted – proceed"


@beta_tool
def get_opportunities_summary() -> str:
    """Return a summary of all logged backlink opportunities."""
    log_data = load_log()
    opps = log_data["opportunities_log"]
    if not opps:
        return "No opportunities logged yet."

    by_priority = {"high": 0, "medium": 0, "low": 0}
    by_type: dict = {}
    for o in opps:
        by_priority[o.get("priority", "low")] = by_priority.get(o.get("priority", "low"), 0) + 1
        t = o.get("type", "other")
        by_type[t] = by_type.get(t, 0) + 1

    lines = [
        f"Total opportunities logged: {len(opps)}",
        f"  High priority : {by_priority['high']}",
        f"  Medium priority: {by_priority['medium']}",
        f"  Low priority  : {by_priority['low']}",
        f"Domains contacted: {len(log_data['contacted_domains'])}",
        f"Directories submitted: {len(log_data['submitted_directories'])}",
        "Breakdown by type:",
    ]
    for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
        lines.append(f"  {t}: {count}")
    return "\n".join(lines)


# ── Main runner ────────────────────────────────────────────────────────────────

def run_daily_backlink_builder() -> None:
    today = date.today()
    strategy = DAILY_STRATEGIES[today.weekday()]

    os.makedirs(REPORTS_DIR, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"DAILY BACKLINK BUILDER  –  {today.strftime('%A, %B %d, %Y')}")
    print(f"Target  : {TARGET_DOMAIN}")
    print(f"Strategy: {strategy['name']}")
    print(f"{'=' * 60}\n")

    log_data = load_log()
    already_done = log_data["contacted_domains"] + log_data["submitted_directories"]
    skip_preview = json.dumps(already_done[:30])
    if len(already_done) > 30:
        skip_preview = skip_preview.rstrip("]") + f', "...and {len(already_done) - 30} more"]'

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            log_backlink_opportunity,
            check_already_contacted,
            get_opportunities_summary,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert link-building specialist. Today is {today.strftime('%A, %B %d, %Y')}.

TARGET WEBSITE : {TARGET_DOMAIN}
BRAND NAME     : {BRAND_NAME}
NICHE          : {NICHE}
COMPETITORS    : {', '.join(COMPETITORS)}

TODAY'S STRATEGY: {strategy['name']}
FOCUS AREA     : {strategy['focus']}

ALREADY-CONTACTED DOMAINS (skip these to avoid duplicates):
{skip_preview}

── STEP-BY-STEP INSTRUCTIONS ──────────────────────────────────────

STEP 1 – Understand the target
  • Fetch https://{TARGET_DOMAIN} to understand their products, target market, and USP.
  • Note key phrases, product names, and markets they serve.

STEP 2 – Find 10–15 genuine backlink opportunities
  • Use web_search with queries tailored to today's focus: "{strategy['focus']}"
  • Combine search operators:
      – intitle:"resources" OR intitle:"links" {NICHE.split(',')[0]}
      – inurl:blog {NICHE.split(',')[0]} "write for us"
      – site:reddit.com OR site:quora.com {NICHE.split(',')[0]} panels facade
  • For each result, use web_fetch to verify the page is live and relevant.

STEP 3 – For each opportunity
  a) Call check_already_contacted(domain) – skip if already tracked.
  b) Score quality: .edu/.gov/.org = HIGH; niche industry blog = HIGH;
     generic directory = MEDIUM; low-relevance = LOW.
  c) Write a SHORT, specific outreach email (or exact submission steps for directories):
     – Reference the specific page URL
     – Explain why {TARGET_DOMAIN} adds value for their readers
     – Suggest the exact anchor text and landing page on {TARGET_DOMAIN}
  d) Call log_backlink_opportunity(...) with all details.

STEP 4 – Call get_opportunities_summary() to show running totals.

STEP 5 – Produce a final report containing:
  • Today's top 3 HIGH-priority actions (paste the outreach emails verbatim)
  • Medium-priority list with one-line descriptions
  • Estimated SEO impact (Domain Authority boost, referral traffic potential)
  • Recommended anchor texts to use this week for {TARGET_DOMAIN}

── QUALITY RULES ───────────────────────────────────────────────────
  • Only log opportunities genuinely relevant to construction, facades, cladding,
    architectural panels, or building materials.
  • Never log spammy directories (DA < 20, thin content).
  • Outreach emails must be SPECIFIC – reference the actual page, not a generic template.
  • Include the exact URL where the link should appear on their site.
""",
            }
        ],
    )

    report_parts = [
        f"# Daily Backlink Report: {today.strftime('%B %d, %Y')}\n",
        f"**Target**: {TARGET_DOMAIN}  \n**Strategy**: {strategy['name']}\n",
    ]

    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_parts.append(block.text)

    report_path = os.path.join(REPORTS_DIR, f"backlinks_{today.isoformat()}.md")
    with open(report_path, "w") as f:
        f.write("\n\n".join(report_parts))

    print(f"\n{'=' * 60}")
    print(f"Report saved : {report_path}")
    print(f"Log updated  : {LOG_FILE}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    run_daily_backlink_builder()
