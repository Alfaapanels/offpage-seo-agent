"""
Daily Backlink Builder for alfaapanels.com

Run this script daily (via cron or scheduler) to automatically find and
build relevant backlinks. Each day rotates through a different strategy.

Usage:
    python daily_backlink_builder.py              # Run today's strategy
    python daily_backlink_builder.py --strategy 0 # Force a specific strategy (0-6)
    python daily_backlink_builder.py --dry-run    # Preview without saving
"""

import anthropic
import json
import os
import argparse
import sys
from datetime import datetime, date
from pathlib import Path
from anthropic import beta_tool

from config import SITE_CONFIG, DAILY_STRATEGIES

# ── paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
TRACKER_FILE = BASE_DIR / "backlink_tracker.json"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

client = anthropic.Anthropic()


# ── tracker ────────────────────────────────────────────────────────────────

def load_tracker() -> dict:
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {
        "domain": SITE_CONFIG["domain"],
        "total_sessions": 0,
        "total_opportunities_found": 0,
        "strategies_run": {},
        "history": [],
    }


def save_tracker(tracker: dict) -> None:
    with open(TRACKER_FILE, "w") as f:
        json.dump(tracker, f, indent=2)


# ── beta tools ─────────────────────────────────────────────────────────────

@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    signals = []
    generic = ["click here", "website", "here", "link", "read more"]
    if anchor_text.lower() in generic:
        signals.append("Warning: Generic anchor text - low value")
    else:
        signals.append(f"Good: Descriptive anchor: '{anchor_text}'")
    toxic = ["spam", "casino", "viagra", "porn", "adult", "gambling"]
    if any(w in backlink_url.lower() for w in toxic):
        signals.append("TOXIC link - disavow recommended")
    else:
        signals.append("Domain appears clean")
    return "\n".join(signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and assess sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positives = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "reliable"]
    negatives = ["bad", "worst", "avoid", "scam", "terrible", "poor", "fake"]
    pos = sum(1 for w in positives if w in mention_text.lower())
    neg = sum(1 for w in negatives if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else "Negative" if neg > pos else "Neutral"
    kind = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    action = "Monitor and nurture" if has_link else "Reach out to add your link"
    return f"Brand: {brand_name}\nType: {kind}\nSentiment: {sentiment}\nAction: {action}"


@beta_tool
def score_link_prospect(page_url: str, page_title: str, page_content_snippet: str, your_niche: str) -> str:
    """Score a potential link building prospect on a 0-100 scale.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
        your_niche: Your website's niche/topic.
    """
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    content = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for w in niche_words if w in content)
    if relevance >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low relevance (+0)")
    high_value = ["resource", "guide", "tools", "blog", "list", "best", "top", "directory", "supplier"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("Resource/guide/directory page (+30)")
    authority = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority):
        score += 30
        reasons.append("High-authority domain (.edu/.gov/.org) (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 — {priority}\nURL: {page_url}\nReasons:\n" + "\n".join(f"  • {r}" for r in reasons)


@beta_tool
def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    your_site: str,
    your_content_url: str,
    link_type: str,
) -> str:
    """Generate a personalized outreach email for link building.

    Args:
        prospect_name: Name of the website owner/editor (use 'Team' if unknown).
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        your_site: Your website name.
        your_content_url: URL of your content to be linked.
        link_type: Type: 'guest_post', 'broken_link', 'resource', 'mention', 'directory'.
    """
    brand = SITE_CONFIG["brand_name"]
    contact = SITE_CONFIG["contact_email"]
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was researching {their_page_topic} and came across your page on {prospect_site}. "
            f"I noticed one of the links appears to be broken.\n\n"
            f"We have a detailed resource at {your_content_url} that covers this topic comprehensively "
            f"and would be a great replacement for your readers.\n\n"
            f"Would you consider updating the link?\n\n"
            f"Best regards,\n{brand} Team\n{contact}"
        ),
        "guest_post": (
            f"Subject: Guest Post Collaboration — {their_page_topic} for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following {prospect_site} and love your coverage of {their_page_topic}. "
            f"We're the team at {brand} ({your_site}), specialising in aluminum composite panels and facade cladding systems.\n\n"
            f"I'd love to contribute a guest article on topics like:\n"
            f"• Choosing the right ACP panels for commercial projects\n"
            f"• Fire-rated vs standard aluminum composite panels: what architects need to know\n"
            f"• How to specify facade cladding systems for high-rise buildings\n\n"
            f"Would you be open to a collaboration?\n\n"
            f"Best,\n{brand} Team\n{contact}"
        ),
        "resource": (
            f"Subject: Useful resource for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is an excellent reference. "
            f"I wanted to suggest adding {your_content_url} from {brand} — "
            f"it covers aluminum composite panel specifications, installation guides, and fire ratings "
            f"that your readers in the construction and architecture space would find valuable.\n\n"
            f"Would you take a look?\n\n"
            f"Best,\n{brand} Team\n{contact}"
        ),
        "mention": (
            f"Subject: Thank you for mentioning {brand}!\n\n"
            f"Hi {prospect_name},\n\n"
            f"We noticed you mentioned {brand} in your article on {their_page_topic} — thank you!\n\n"
            f"Would you be open to linking directly to {your_content_url}? "
            f"It would make it easier for your readers to find us and explore our full product range.\n\n"
            f"Thanks,\n{brand} Team\n{contact}"
        ),
        "directory": (
            f"Subject: Listing submission — {brand} (Aluminum Composite Panel Manufacturer)\n\n"
            f"Hi {prospect_name},\n\n"
            f"We'd like to submit {brand} for inclusion in your {their_page_topic} directory.\n\n"
            f"Company: {brand}\n"
            f"Website: {your_site}\n"
            f"Category: Building Materials / Aluminum Composite Panels / Facade Cladding\n"
            f"Description: {SITE_CONFIG['description']}\n\n"
            f"Please let us know if you need any additional information.\n\n"
            f"Best,\n{brand} Team\n{contact}"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(competitor_domain: str, your_domain: str, linking_page_topic: str) -> str:
    """Identify if a competitor backlink is an opportunity for your site.

    Args:
        competitor_domain: Competitor's domain.
        your_domain: Your domain.
        linking_page_topic: Topic of the page linking to competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Action plan:\n"
        f"1. Identify the exact page/content on {competitor_domain} that earned this link\n"
        f"2. Create a superior version of that content for {your_domain}\n"
        f"3. Reach out to the linking page and pitch your improved resource\n"
        f"4. Highlight your unique value: {SITE_CONFIG['description']}"
    )


@beta_tool
def log_backlink_opportunity(
    target_url: str,
    opportunity_type: str,
    prospect_domain: str,
    prospect_contact: str,
    priority: str,
    notes: str,
) -> str:
    """Log a discovered backlink opportunity to the tracker.

    Args:
        target_url: The page on alfaapanels.com that should receive the link.
        opportunity_type: Type: 'directory', 'forum', 'resource', 'guest_post', 'broken_link', 'mention'.
        prospect_domain: Domain of the site to reach out to.
        prospect_contact: Contact info or contact page URL if found.
        priority: 'high', 'medium', or 'low'.
        notes: Brief notes on the opportunity.
    """
    entry = {
        "date": date.today().isoformat(),
        "target_url": target_url,
        "opportunity_type": opportunity_type,
        "prospect_domain": prospect_domain,
        "prospect_contact": prospect_contact,
        "priority": priority,
        "status": "discovered",
        "notes": notes,
    }
    tracker = load_tracker()
    tracker["history"].append(entry)
    tracker["total_opportunities_found"] = len(tracker["history"])
    save_tracker(tracker)
    return f"Logged: {opportunity_type} opportunity at {prospect_domain} [{priority} priority]"


# ── main runner ────────────────────────────────────────────────────────────

def build_daily_prompt(strategy: dict, today_str: str) -> str:
    cfg = SITE_CONFIG
    competitors_str = ", ".join(cfg["competitors"])
    keywords_str = ", ".join(cfg["target_keywords"][:8])
    queries_str = "\n".join(f"  • {q}" for q in strategy["search_queries"])

    return f"""You are an expert off-page SEO strategist executing a daily backlink-building session.

TARGET SITE: {cfg["domain"]}
BRAND: {cfg["brand_name"]}
NICHE: {cfg["niche"]}
DESCRIPTION: {cfg["description"]}
KEY KEYWORDS: {keywords_str}
COMPETITORS: {competitors_str}
DATE: {today_str}

TODAY'S STRATEGY: {strategy["name"]}
GOAL: {strategy["description"]}
TARGET: Find at least {strategy["target_count"]} actionable opportunities.

SUGGESTED SEARCH QUERIES (start with these, then expand):
{queries_str}

INSTRUCTIONS:
1. Use web_search to find real, live pages matching today's strategy focus.
2. Use web_fetch to visit promising pages and verify they are live and relevant.
3. For each opportunity found:
   - Score it with score_link_prospect (skip anything scoring below 30)
   - Generate an outreach template with generate_outreach_template
   - Log it with log_backlink_opportunity
4. For brand mentions found, use categorize_brand_mention to assess them.
5. For competitor backlinks, use identify_link_gap_opportunity.
6. After logging, compile a structured daily report.

QUALITY STANDARDS:
- Only log sites that are live and relevant to building materials, construction, or architecture
- Prioritise .edu, .gov, .org, and established industry publications
- Avoid link farms, low-quality directories, or unrelated niches
- Ensure each outreach template is personalised to the specific page/site

FINAL OUTPUT FORMAT:
## Daily Backlink Report — {today_str}
### Strategy: {strategy["name"]}
### Opportunities Found: [N]

#### High Priority (score 70+)
[List each with URL, type, why it's valuable, outreach template]

#### Medium Priority (score 40–69)
[List each]

#### Low Priority / Monitor
[List each]

### Recommended Actions for Tomorrow
[3-5 specific next steps]

### Running Totals
- Total opportunities logged today: [N]
- Strategy coverage: {strategy["name"]}
"""


def run_daily_session(strategy_override: int = None, dry_run: bool = False) -> str:
    today = date.today()
    today_str = today.strftime("%Y-%m-%d (%A)")
    day_index = strategy_override if strategy_override is not None else today.weekday()
    strategy = DAILY_STRATEGIES[day_index % 7]

    print(f"\n{'='*65}")
    print(f"  ALFA PANELS — Daily Backlink Builder")
    print(f"  Date     : {today_str}")
    print(f"  Strategy : {strategy['name']}")
    print(f"  Domain   : {SITE_CONFIG['domain']}")
    print(f"{'='*65}\n")

    if dry_run:
        print("[DRY RUN] Would execute strategy:", strategy["name"])
        print("Search queries:")
        for q in strategy["search_queries"]:
            print(f"  • {q}")
        return "Dry run complete."

    tracker = load_tracker()
    tracker["total_sessions"] = tracker.get("total_sessions", 0) + 1
    key = str(day_index)
    tracker["strategies_run"][key] = tracker["strategies_run"].get(key, 0) + 1
    save_tracker(tracker)

    prompt = build_daily_prompt(strategy, today_str)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            log_backlink_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{"role": "user", "content": prompt}],
    )

    report_lines = []
    print("Running agent...\n")
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_lines.append(block.text)

    report_text = "\n\n".join(report_lines)
    report_filename = REPORTS_DIR / f"backlink_report_{today.isoformat()}_{strategy['focus']}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Daily Backlink Report — {today_str}\n")
        f.write(f"**Strategy:** {strategy['name']}\n")
        f.write(f"**Domain:** {SITE_CONFIG['domain']}\n\n")
        f.write(report_text)

    print(f"\n{'='*65}")
    print(f"  Report saved: {report_filename}")
    tracker = load_tracker()
    print(f"  Total opportunities logged (all time): {tracker['total_opportunities_found']}")
    print(f"  Total sessions run: {tracker['total_sessions']}")
    print(f"{'='*65}\n")
    return str(report_filename)


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Daily backlink builder for alfaapanels.com"
    )
    parser.add_argument(
        "--strategy",
        type=int,
        choices=range(7),
        metavar="0-6",
        help="Force a specific strategy day (0=Mon … 6=Sun)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview strategy without running the agent",
    )
    parser.add_argument(
        "--list-strategies",
        action="store_true",
        help="List all 7 strategies and exit",
    )
    args = parser.parse_args()

    if args.list_strategies:
        print("\nALFA PANELS — 7-Day Backlink Strategy Rotation\n")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i, (day, strat) in enumerate(zip(days, DAILY_STRATEGIES.values())):
            print(f"  Day {i} ({day:>9}): {strat['name']}")
            print(f"               → {strat['description']}")
        print()
        sys.exit(0)

    run_daily_session(
        strategy_override=args.strategy,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
