"""
Daily backlink builder for alfaapanels.com.

Rotates through 7 link-building strategies (one per weekday) and saves a
date-stamped markdown report under reports/.  All discovered opportunities
are logged to backlinks.db so the same URL is never re-processed.

Usage:
    python daily_backlink_builder.py                    # run today's strategy
    python daily_backlink_builder.py --strategy guest_posts
    python daily_backlink_builder.py --list-strategies
"""

import argparse
import logging
import os
import sys
from datetime import date

import anthropic
from anthropic import beta_tool
from dotenv import load_dotenv

from backlink_tracker import init_db, log_daily_run

load_dotenv()

# ── Site configuration ────────────────────────────────────────────────────────

DOMAIN = "alfaapanels.com"
BRAND  = "Alfaapanels"
NICHE  = "SMM panel social media marketing services reseller panel"
COMPETITORS = [
    "peakerr.com",
    "smmking.com",
    "justanotherpanel.com",
    "smm-world.com",
    "smmvaly.com",
]

REPORTS_DIR = os.environ.get("REPORTS_DIR", "reports")

# ── Weekly strategy rotation (0 = Monday … 6 = Sunday) ───────────────────────

STRATEGIES = {
    "brand_mentions":   "Brand Mention Audit",
    "competitor_gaps":  "Competitor Backlink Gap Analysis",
    "resource_pages":   "Resource Page Link Building",
    "guest_posts":      "Guest Post Prospecting",
    "broken_links":     "Broken Link Building",
    "community_links":  "Community & Forum Links",
    "directories":      "Directory & Listing Submissions",
}

_WEEKDAY_ROTATION = [
    "brand_mentions",
    "competitor_gaps",
    "resource_pages",
    "guest_posts",
    "broken_links",
    "community_links",
    "directories",
]

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("backlink_builder.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ── Claude client ─────────────────────────────────────────────────────────────

client = anthropic.Anthropic()

# ── Tools ─────────────────────────────────────────────────────────────────────


@beta_tool
def score_link_prospect(page_url: str, page_title: str, page_content_snippet: str, your_niche: str) -> str:
    """Score a potential link building prospect from 0 to 100.

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

    high_value_types = ["resource", "guide", "tools", "best", "top", "list", "review", "comparison"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/list/review page (+30)")

    if any(s in page_url for s in [".edu", ".gov", ".org"]):
        score += 30
        reasons.append("Authority domain (.edu/.gov/.org) (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")

    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 [{priority}]\nURL: {page_url}\n" + "\n".join(reasons)


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    signals = []
    generic_anchors = ["click here", "website", "here", "link", "read more", "visit"]
    if anchor_text.lower().strip() in generic_anchors:
        signals.append("Warning: Generic anchor text – low SEO value")
    else:
        signals.append(f"Good: Descriptive anchor text – '{anchor_text}'")

    toxic_terms = ["spam", "casino", "viagra", "adult", "xxx", "pharma"]
    if any(t in backlink_url.lower() for t in toxic_terms):
        signals.append("TOXIC link – disavow recommended")
    else:
        signals.append("Domain appears clean")

    return "\n".join(signals)


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
            f"I was reading your {their_page_topic} page on {prospect_site} and spotted a broken link.\n"
            f"My resource at {your_content_url} would be a perfect replacement – it covers the same topic "
            f"and is actively maintained.\n\n"
            f"Would you consider swapping it out?\n\nBest regards,\n[Your Name] | {your_site}"
        ),
        "guest_post": (
            f"Subject: Guest post idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I love your content on {their_page_topic} at {prospect_site} – it's exactly what "
            f"practitioners in our space need.\n\n"
            f"I run {your_site} and would love to contribute a guest post. I have a few angles in mind "
            f"that would add genuine value for your audience.\n\n"
            f"Would you be open to a quick pitch?\n\nBest,\n[Your Name] | {your_site}"
        ),
        "resource": (
            f"Subject: Suggestion for your {their_page_topic} resource page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is one of the best I've seen.\n\n"
            f"I recently published {your_content_url} which I think would complement your existing "
            f"resources nicely. It's been well-received by our users.\n\n"
            f"Would you be open to adding it?\n\nThanks,\n[Your Name] | {your_site}"
        ),
        "mention": (
            f"Subject: Thank you for mentioning {your_site}!\n\n"
            f"Hi {prospect_name},\n\n"
            f"I noticed you mentioned {your_site} in your piece on {their_page_topic} – thank you!\n\n"
            f"Would you consider linking directly to {your_content_url}? It would make it easier "
            f"for your readers to find the resource.\n\n"
            f"Either way, I really appreciate the mention.\n\nThanks,\n[Your Name] | {your_site}"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(competitor_domain: str, your_domain: str, linking_page_topic: str) -> str:
    """Identify if a competitor backlink is an opportunity for your domain.

    Args:
        competitor_domain: Competitor's domain.
        your_domain: Your domain.
        linking_page_topic: Topic of the page linking to the competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site:  {your_domain}\n"
        f"Topic:      {linking_page_topic}\n\n"
        f"Action plan:\n"
        f"1. Identify what content earned {competitor_domain} this link\n"
        f"2. Create superior or equivalent content for {your_domain}\n"
        f"3. Pitch your resource to the linking page editor"
    )


# ── Strategy prompts ──────────────────────────────────────────────────────────

def _build_prompt(strategy_key: str) -> str:
    today = date.today().strftime("%B %d, %Y")
    competitors_str = ", ".join(COMPETITORS)

    header = (
        f"You are an expert off-page SEO strategist. Today is {today}.\n"
        f"Target domain : {DOMAIN}\n"
        f"Brand name    : {BRAND}\n"
        f"Niche         : {NICHE}\n"
        f"Competitors   : {competitors_str}\n\n"
        f"Instructions:\n"
        f"- Use web_search and web_fetch to find REAL, currently-live pages.\n"
        f"- Call score_link_prospect for every candidate URL you find.\n"
        f"- Generate outreach templates for the top 5 opportunities.\n"
        f"- Focus on relevance to the SMM panel / social media marketing niche.\n\n"
    )

    body = {
        "brand_mentions": (
            f"## TODAY'S STRATEGY: Brand Mention Audit\n\n"
            f'Search for mentions of "{BRAND}" and "alfaapanels" across blogs, forums, review sites, '
            f"and social media that do NOT include a link back to {DOMAIN}.\n\n"
            f'Suggested searches:\n'
            f'  • "{BRAND}" -site:{DOMAIN}\n'
            f'  • "alfaapanels" review\n'
            f'  • "alfaapanels" SMM panel\n\n'
            f"Find at least 10 unlinked mentions. For each:\n"
            f"1. Score the page with score_link_prospect\n"
            f"2. Note whether it's positive, neutral, or negative sentiment\n"
            f"3. Generate a 'mention' outreach template to convert it into a backlink"
        ),
        "competitor_gaps": (
            f"## TODAY'S STRATEGY: Competitor Backlink Gap Analysis\n\n"
            f"Find sites that link to our competitors but not to {DOMAIN}.\n\n"
            f"Suggested searches:\n"
            f'  • "best SMM panels" OR "top SMM panel" list\n'
            f'  • "SMM panel review" OR "SMM panel comparison"\n'
            f'  • site that mentions {COMPETITORS[0]} OR {COMPETITORS[1]}\n\n'
            f"For each competitor, identify at least 3 linking domains they have that we lack.\n"
            f"Score each with score_link_prospect and call identify_link_gap_opportunity.\n"
            f"Provide a gap report and outreach templates for the top 5 opportunities."
        ),
        "resource_pages": (
            f"## TODAY'S STRATEGY: Resource Page Link Building\n\n"
            f"Find resource pages in the social media marketing / digital marketing space "
            f"where {DOMAIN} would be a natural addition.\n\n"
            f"Suggested searches:\n"
            f'  • intitle:"resources" "social media marketing tools"\n'
            f'  • intitle:"best tools" "SMM" OR "social media"\n'
            f'  • "recommended tools" digital marketing site:.com\n'
            f'  • inurl:resources "social media" OR "digital marketing"\n\n'
            f"Find 10+ relevant resource pages, score each, then generate 'resource' outreach templates "
            f"for the top 5."
        ),
        "guest_posts": (
            f"## TODAY'S STRATEGY: Guest Post Prospecting\n\n"
            f"Find blogs and publications that accept guest posts in our niche.\n\n"
            f"Suggested searches:\n"
            f'  • "write for us" "social media marketing"\n'
            f'  • "guest post" "digital marketing" OR "SMM"\n'
            f'  • "contribute" "social media" blog\n'
            f'  • "submit a post" "content marketing"\n\n'
            f"Find 10+ blogs with engaged audiences. Score each and assess:\n"
            f"- Domain relevance to the SMM / social media niche\n"
            f"- Whether they have published sponsored or third-party content before\n\n"
            f"Generate 'guest_post' pitch templates for the top 5."
        ),
        "broken_links": (
            f"## TODAY'S STRATEGY: Broken Link Building\n\n"
            f"Find pages about SMM panels or social media services tools that have "
            f"outdated or broken external links we could replace.\n\n"
            f"Suggested searches:\n"
            f'  • "SMM panel" tools list\n'
            f'  • "social media marketing tools" resource page\n'
            f'  • "buy followers" recommended services\n'
            f'  • "social media growth" tools comparison\n\n'
            f"Fetch the most promising pages and look for:\n"
            f"- Links to defunct SMM services or tools that no longer exist\n"
            f"- Outdated 'best of' lists that could include {DOMAIN}\n\n"
            f"Score prospects and generate 'broken_link' outreach templates for the top 5."
        ),
        "community_links": (
            f"## TODAY'S STRATEGY: Community & Forum Link Building\n\n"
            f"Find active questions and discussions where recommending {DOMAIN} would add genuine value.\n\n"
            f"Search targets:\n"
            f"- Reddit: r/socialmedia, r/digital_marketing, r/SEO, r/Entrepreneur\n"
            f"- Quora: questions about SMM panels, buying social media services, growing accounts\n"
            f"- Niche forums: digital marketing forums, growth hacking communities\n\n"
            f"Suggested searches:\n"
            f'  • site:reddit.com "SMM panel" recommendation\n'
            f'  • site:quora.com "best SMM panel"\n'
            f'  • "social media marketing panel" forum recommend\n\n'
            f"Find 10+ threads. For each, draft a helpful, non-spammy response that naturally "
            f"mentions or recommends {DOMAIN} where relevant. Score each opportunity."
        ),
        "directories": (
            f"## TODAY'S STRATEGY: Directory & Listing Submissions\n\n"
            f"Find reputable directories and listing sites where {DOMAIN} can be listed to earn "
            f"authoritative backlinks.\n\n"
            f"Target categories:\n"
            f"- Software/SaaS directories: G2, Capterra, AlternativeTo, Product Hunt\n"
            f"- Digital marketing tool directories\n"
            f"- SMM panel comparison/listing sites\n"
            f"- 'Best SMM panels' roundup articles that accept new submissions\n\n"
            f"Suggested searches:\n"
            f'  • "submit your tool" "digital marketing" OR "social media"\n'
            f'  • "add listing" SMM panel directory\n'
            f'  • "best SMM panels {date.today().year}" list\n\n'
            f"Find 10+ directories/listings where {DOMAIN} is NOT yet present. "
            f"Score each and provide direct submission URLs and instructions."
        ),
    }

    footer = (
        f"\n\n## REQUIRED OUTPUT FORMAT\n\n"
        f"Structure your final report as:\n"
        f"1. **Executive Summary** – what you found today (3–5 sentences)\n"
        f"2. **Top 10 Opportunities** – ranked table: URL | Type | Score | Why it matters\n"
        f"3. **Outreach Templates** – ready-to-send emails for the top 5\n"
        f"4. **Quick Wins for Tomorrow** – 2–3 immediate actions to follow up on"
    )

    return header + body.get(strategy_key, body["resource_pages"]) + footer


# ── Main runner ───────────────────────────────────────────────────────────────

def run_daily(strategy_key: str | None = None) -> str:
    """Execute one daily backlink-building session. Returns the saved report path."""
    init_db()

    today = date.today()
    weekday = today.weekday()

    if strategy_key is None:
        strategy_key = _WEEKDAY_ROTATION[weekday]

    strategy_label = STRATEGIES.get(strategy_key, strategy_key.replace("_", " ").title())

    log.info("Daily backlink build | domain=%s | strategy=%s", DOMAIN, strategy_label)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_path = os.path.join(REPORTS_DIR, f"backlinks_{today.isoformat()}_{strategy_key}.md")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            score_link_prospect,
            analyze_backlink_quality,
            generate_outreach_template,
            identify_link_gap_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209",  "name": "web_fetch"},
        ],
        messages=[{"role": "user", "content": _build_prompt(strategy_key)}],
    )

    report_sections = [
        f"# Daily Backlink Report – {DOMAIN}\n"
        f"**Date:** {today}  |  **Strategy:** {strategy_label}\n"
    ]

    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_sections.append(block.text)

    with open(report_path, "w") as f:
        f.write("\n\n".join(report_sections))

    log.info("Report saved → %s", report_path)
    log_daily_run(strategy_key, strategy_label, 0, report_path)
    return report_path


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=f"Daily backlink builder for {DOMAIN}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--strategy",
        choices=list(STRATEGIES.keys()),
        default=None,
        help="Override today's scheduled strategy (default: based on weekday)",
    )
    parser.add_argument(
        "--list-strategies",
        action="store_true",
        help="Print the weekly strategy schedule and exit",
    )
    args = parser.parse_args()

    if args.list_strategies:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        print(f"\nWeekly strategy schedule for {DOMAIN}:\n")
        for i, key in enumerate(_WEEKDAY_ROTATION):
            marker = " ← today" if i == date.today().weekday() else ""
            print(f"  {days[i]:10s}  {STRATEGIES[key]}{marker}")
        print()
        sys.exit(0)

    report = run_daily(args.strategy)
    print(f"\nDone. Report: {report}")
