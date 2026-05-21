import anthropic
from anthropic import beta_tool
import os
import json
from datetime import date
from pathlib import Path

client = anthropic.Anthropic()

SITE_CONFIG = {
    "domain": "alfaapanels.com",
    "brand": "Alfa Panels",
    "niche": "aluminum composite panels building cladding facade materials",
    "competitors": [
        "alucobond.com",
        "reynobond.com",
        "alpolic.com",
        "alubond.com",
    ],
    "key_pages": [
        "https://alfaapanels.com",
        "https://alfaapanels.com/products",
        "https://alfaapanels.com/about",
    ],
}

# Strategy rotated by weekday (Monday=0 … Sunday=6)
DAILY_STRATEGIES = {
    0: "directory_submissions",
    1: "guest_post_outreach",
    2: "broken_link_building",
    3: "resource_page_links",
    4: "competitor_gap_analysis",
    5: "brand_mention_audit",
    6: "forum_engagement",
}

REPORTS_DIR = Path("reports")
DATA_DIR = Path("data")


# ── Tools ─────────────────────────────────────────────────────────────────────

@beta_tool
def log_backlink_opportunity(
    opportunity_type: str,
    target_url: str,
    prospect_url: str,
    notes: str,
    priority: str,
) -> str:
    """Save a backlink opportunity to the daily log.

    Args:
        opportunity_type: Type such as 'directory', 'guest_post', 'broken_link', 'resource', 'mention'.
        target_url: The alfaapanels.com page the backlink should point to.
        prospect_url: The external URL where the backlink opportunity exists.
        notes: Key notes or contact information.
        priority: 'high', 'medium', or 'low'.
    """
    today = date.today().isoformat()
    log_file = DATA_DIR / "opportunities.jsonl"
    DATA_DIR.mkdir(exist_ok=True)
    entry = {
        "date": today,
        "type": opportunity_type,
        "target_url": target_url,
        "prospect_url": prospect_url,
        "notes": notes,
        "priority": priority,
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return f"Logged {priority} priority {opportunity_type} opportunity: {prospect_url}"


@beta_tool
def get_processed_domains() -> str:
    """Return domains already processed to avoid duplicate outreach."""
    processed_file = DATA_DIR / "processed_domains.txt"
    if not processed_file.exists():
        return "No domains processed yet."
    domains = processed_file.read_text().splitlines()
    return f"Already processed {len(domains)} domains:\n" + "\n".join(domains[:50])


@beta_tool
def mark_domain_processed(domain: str) -> str:
    """Mark a domain as processed so it is not targeted again.

    Args:
        domain: The domain to mark as processed (e.g. 'example.com').
    """
    DATA_DIR.mkdir(exist_ok=True)
    processed_file = DATA_DIR / "processed_domains.txt"
    with open(processed_file, "a") as f:
        f.write(domain + "\n")
    return f"Marked {domain} as processed."


@beta_tool
def score_link_prospect(
    page_url: str, page_title: str, page_content_snippet: str, your_niche: str
) -> str:
    """Score a potential link building prospect 0-100.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
        your_niche: Your website niche/topic.
    """
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for w in niche_words if w in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    for page_type in ["resource", "guide", "tools", "blog", "directory", "list", "best"]:
        if page_type in page_url.lower() or page_type in page_title.lower():
            score += 30
            reasons.append(f"Resource/list page type (+30)")
            break
    for authority in [".edu", ".gov", ".org"]:
        if authority in page_url:
            score += 30
            reasons.append("High-authority domain (+30)")
            break
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 [{priority}] — {page_url}\n" + "\n".join(reasons)


@beta_tool
def generate_outreach_email(
    prospect_name: str,
    prospect_site: str,
    their_topic: str,
    link_type: str,
    your_content_url: str,
) -> str:
    """Generate a personalised outreach email for a backlink opportunity.

    Args:
        prospect_name: Name of the site owner/editor.
        prospect_site: Their website name.
        their_topic: Topic of the page where the link would appear.
        link_type: 'guest_post', 'broken_link', 'resource', or 'mention'.
        your_content_url: The alfaapanels.com URL to be linked.
    """
    brand = SITE_CONFIG["brand"]
    domain = SITE_CONFIG["domain"]
    templates = {
        "broken_link": (
            f"Subject: Broken link found on your {their_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your {their_topic} page on {prospect_site} and noticed a broken link. "
            f"We have a detailed resource at {your_content_url} that covers the same topic and "
            f"would be a great replacement for your readers.\n\n"
            f"Would you be open to updating it?\n\nBest regards,\n{brand} Team\n{domain}"
        ),
        "guest_post": (
            f"Subject: Guest post idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I enjoy your content on {their_topic} at {prospect_site}. "
            f"I write for {brand} ({domain}) and would love to contribute a practical, "
            f"in-depth guest post for your audience on aluminum composite panels and facade solutions.\n\n"
            f"Would you be open to a collaboration?\n\nBest regards,\n{brand} Team\n{domain}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_topic} is very helpful! "
            f"We recently published {your_content_url} which covers ACP panel selection, "
            f"installation tips, and case studies — it might add value for your visitors.\n\n"
            f"Would you consider adding it?\n\nBest regards,\n{brand} Team\n{domain}"
        ),
        "mention": (
            f"Subject: Re: Your mention of {brand}\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {brand} in your article about {their_topic} on {prospect_site}! "
            f"Would you be willing to turn that mention into a direct link to {your_content_url}? "
            f"It would make it easier for your readers to find us.\n\nThanks,\n{brand} Team\n{domain}"
        ),
    }
    return templates.get(link_type, templates["resource"])


# ── Strategy prompts ───────────────────────────────────────────────────────────

def _build_prompt(strategy: str) -> str:
    cfg = SITE_CONFIG
    domain = cfg["domain"]
    brand = cfg["brand"]
    niche = cfg["niche"]
    competitors = ", ".join(cfg["competitors"])
    today = date.today().isoformat()

    base = (
        f"You are an expert off-page SEO strategist working for {brand} ({domain}).\n"
        f"Date: {today}\n"
        f"Niche: {niche}\n"
        f"Competitors: {competitors}\n\n"
        "Use the tools available — including web_search and web_fetch — to complete today's tasks. "
        "For every opportunity you find, call log_backlink_opportunity to save it. "
        "Call mark_domain_processed for each domain you fully research. "
        "First call get_processed_domains to skip domains already handled.\n\n"
    )

    strategies = {
        "directory_submissions": (
            "TODAY'S STRATEGY: Directory & Citation Building\n\n"
            "1. Search for high-authority business directories relevant to building materials, "
            "construction, and facade panels (both general directories like Yelp/Manta and "
            "niche industry directories).\n"
            "2. For each directory found, score it with score_link_prospect.\n"
            "3. Log all MEDIUM+ scoring directories as 'directory' opportunities with "
            "submission URL and any notes about the submission process.\n"
            "4. Aim to find and log at least 15 directories.\n"
            "5. End with a summary: number found, top 5 by priority."
        ),
        "guest_post_outreach": (
            "TODAY'S STRATEGY: Guest Post Outreach\n\n"
            "1. Search for blogs, magazines and trade publications that publish guest posts about "
            "construction, architecture, building materials, facade design, or ACP panels.\n"
            "   Queries to try: 'write for us' + 'construction materials', "
            "'submit guest post' + 'architecture', 'contribute' + 'building facade'.\n"
            "2. Fetch each candidate page to verify they accept guest posts.\n"
            "3. Score each with score_link_prospect.\n"
            "4. For the top 5 prospects, generate a personalised outreach email using "
            "generate_outreach_email with link_type='guest_post'.\n"
            "5. Log all prospects as 'guest_post' opportunities.\n"
            "6. End with a ranked outreach list."
        ),
        "broken_link_building": (
            "TODAY'S STRATEGY: Broken Link Building\n\n"
            f"1. Search for resource pages, guides, and 'best of' lists in the {niche} niche.\n"
            "2. Fetch each page and look for broken or outdated external links (404 errors, "
            "discontinued products, old domains).\n"
            "3. For each broken link found, determine which alfaapanels.com page is the best "
            "replacement.\n"
            "4. Generate a broken_link outreach email with generate_outreach_email.\n"
            "5. Log every broken-link opportunity.\n"
            "6. Summarise: pages checked, broken links found, top opportunities."
        ),
        "resource_page_links": (
            "TODAY'S STRATEGY: Resource Page Link Building\n\n"
            f"1. Search for resource pages, 'useful links' pages, and curated guides about "
            f"{niche}, construction materials, green building, or architectural cladding.\n"
            "2. Fetch and evaluate each page.\n"
            "3. Score each with score_link_prospect.\n"
            "4. For the top 5, generate a 'resource' outreach email.\n"
            "5. Log all as 'resource' opportunities.\n"
            "6. Produce a summary with contact details where available."
        ),
        "competitor_gap_analysis": (
            "TODAY'S STRATEGY: Competitor Backlink Gap Analysis\n\n"
            f"1. For each competitor ({competitors}), search for sites that link to them "
            f"but likely don't link to {domain}.\n"
            "   Example searches: 'alucobond.com site:*.com -site:alfaapanels.com resource'\n"
            "2. Fetch candidate linking pages and verify the competitor link.\n"
            "3. Score each prospect.\n"
            "4. Identify the content type that earned the competitor link.\n"
            "5. For each gap opportunity, log it and generate the appropriate outreach email.\n"
            "6. Summarise: competitors analysed, gaps found, actionable items."
        ),
        "brand_mention_audit": (
            "TODAY'S STRATEGY: Brand Mention Audit & Conversion\n\n"
            f'1. Search for unlinked mentions of "{brand}" and "Alfa Panels" across the web:\n'
            f'   - "{brand}" -site:{domain}\n'
            f'   - "alfaapanels" -site:{domain}\n'
            "2. Fetch each result to confirm the mention is real and check if it links back.\n"
            "3. For unlinked mentions, generate a 'mention' outreach email.\n"
            "4. Log each unlinked mention as a high-priority 'mention' opportunity.\n"
            "5. Identify the sentiment (positive/neutral/negative) of each mention.\n"
            "6. Summarise: total mentions, linked vs unlinked, top conversion targets."
        ),
        "forum_engagement": (
            "TODAY'S STRATEGY: Forum & Community Engagement\n\n"
            f"1. Find active forums, subreddits, Quora topics, LinkedIn groups, and online "
            f"communities about {niche}, construction, architecture, and building materials.\n"
            "2. Identify recent unanswered questions or discussions where alfaapanels.com "
            "content could genuinely help (NOT spam — only where it adds real value).\n"
            "3. For each opportunity, note:\n"
            "   - Platform URL\n"
            "   - Question/thread URL\n"
            "   - Recommended alfaapanels.com page to reference\n"
            "   - Suggested reply approach (2–3 sentences)\n"
            "4. Log each as a 'forum' opportunity.\n"
            "5. Summarise: platforms found, top 10 engagement opportunities."
        ),
    }
    return base + strategies[strategy]


# ── Runner ─────────────────────────────────────────────────────────────────────

def run_daily():
    today = date.today()
    strategy_key = DAILY_STRATEGIES[today.weekday()]
    prompt = _build_prompt(strategy_key)

    REPORTS_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)

    report_path = REPORTS_DIR / f"{today.isoformat()}_{strategy_key}.md"

    print(f"\n{'='*60}")
    print(f"  Alfa Panels Daily Backlink Builder")
    print(f"  Date     : {today.isoformat()}")
    print(f"  Strategy : {strategy_key.replace('_', ' ').title()}")
    print(f"  Report   : {report_path}")
    print(f"{'='*60}\n")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
        max_tokens=16000,
        tools=[
            log_backlink_opportunity,
            get_processed_domains,
            mark_domain_processed,
            score_link_prospect,
            generate_outreach_email,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{"role": "user", "content": prompt}],
    )

    report_sections = [
        f"# Alfa Panels Backlink Report — {today.isoformat()}\n",
        f"**Strategy:** {strategy_key.replace('_', ' ').title()}\n",
    ]

    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_sections.append(block.text)

    report_path.write_text("\n\n".join(report_sections))
    print(f"\nReport saved → {report_path}")
    return report_path


if __name__ == "__main__":
    run_daily()
