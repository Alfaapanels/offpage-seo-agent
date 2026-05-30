"""
Daily backlink builder for alfaapanels.com.

Run once manually or schedule via cron:
    0 9 * * * /usr/bin/python3 /path/to/daily_backlink_builder.py

Each day executes a different strategy from the weekly rotation,
saving a dated Markdown report under reports/ and logging all
discovered opportunities to backlink_opportunities.json.
"""

import json
import os
from datetime import date, datetime
from pathlib import Path

import anthropic
from anthropic import beta_tool

# ---------------------------------------------------------------------------
# Site configuration
# ---------------------------------------------------------------------------

DOMAIN = "alfaapanels.com"
BRAND = "Alfa Panels"
NICHE = "aluminium composite panels ACP cladding facade building materials construction"
COMPETITORS = [
    "eurobond.com.tr",
    "alucobond.com",
    "reynobond.com",
    "alpolic.com",
    "alucoworld.com",
]

REPORTS_DIR = Path("reports")
OPPORTUNITIES_LOG = Path("backlink_opportunities.json")

# Weekly strategy rotation (weekday 0=Monday … 6=Sunday)
DAILY_STRATEGY = {
    0: "brand_mentions",
    1: "directory_submissions",
    2: "competitor_gap",
    3: "resource_pages",
    4: "guest_posts",
    5: "forum_communities",
    6: "content_syndication",
}

STRATEGY_PROMPTS = {
    "brand_mentions": f"""
DAILY TASK: Brand Mention Audit for {DOMAIN}

1. Search for unlinked brand mentions:
   - Search: "{BRAND}" -site:{DOMAIN}
   - Search: "alfa panels" construction -site:{DOMAIN}
   - Search: "alfaapanels" -site:{DOMAIN}

2. For each mention found:
   - Use categorize_brand_mention() to classify it
   - If unlinked, score it as a link prospect using score_link_prospect()
   - Generate an outreach email using generate_outreach_template() with type "mention"

3. Output:
   - List of top 10 unlinked mentions with contact info where possible
   - Ready-to-send outreach emails for top 5
   - Summary count: linked vs unlinked mentions
""",
    "directory_submissions": f"""
DAILY TASK: Business Directory Submissions for {DOMAIN}

1. Find high-quality free directories in these categories:
   - General business directories (Google Business, Yelp, Bing Places, etc.)
   - Construction industry directories
   - Building materials supplier directories
   - B2B directories (Europages, Kompass, ThomasNet, etc.)
   - Regional/country-specific directories for target markets

2. Search for:
   - "construction materials suppliers directory"
   - "aluminium panel manufacturers directory"
   - "building cladding suppliers list"
   - "ACP panel suppliers directory submit"

3. For each directory found:
   - Fetch the submission page URL
   - Note whether it's free or paid
   - Score it using score_link_prospect()

4. Output:
   - Top 15 directories to submit to today (free ones prioritized)
   - Submission instructions for each
   - Pre-filled business description for {BRAND}: manufacturer of aluminium composite panels for architectural facade and cladding applications
""",
    "competitor_gap": f"""
DAILY TASK: Competitor Backlink Gap Analysis for {DOMAIN}

Competitors to analyze: {', '.join(COMPETITORS)}

1. For each competitor, search for sites that link to them:
   - Search: link:{competitor} OR "linking to {competitor}"
   - Search: site mentions referencing the competitor

2. Find sites that link to 2+ competitors but NOT to {DOMAIN}:
   - These are high-priority targets

3. For each gap opportunity:
   - Use identify_link_gap_opportunity() to document it
   - Score the linking page with score_link_prospect()
   - Generate an outreach template

4. Focus on these link types:
   - Resource pages listing panel suppliers
   - Comparison articles about ACP brands
   - Industry blogs and news sites
   - Architect and contractor recommendation pages

5. Output:
   - Top 10 competitor backlink gaps with URLs
   - Outreach strategy for each
   - Content suggestions to earn these links
""",
    "resource_pages": f"""
DAILY TASK: Resource Page Link Building for {DOMAIN}

1. Find resource pages in the construction/building materials niche:
   - Search: inurl:resources "aluminium panels" OR "ACP panels" OR "cladding"
   - Search: "useful links" "building materials" construction facade
   - Search: "recommended suppliers" "panel manufacturers" construction
   - Search: intitle:"resources" "facade cladding" architects

2. Find link roundups and curated lists:
   - Search: "best aluminium panel manufacturers" 2024 OR 2025 OR 2026
   - Search: "top ACP suppliers" list
   - Search: "cladding manufacturers" roundup guide

3. For each resource page found:
   - Fetch the page content
   - Score it using score_link_prospect()
   - Generate outreach with link_type "resource"

4. Output:
   - Top 10 resource pages to target
   - Personalized pitch for each explaining why {BRAND} belongs on their list
   - {BRAND} value proposition: [premium aluminium composite panels for architectural facades,
     competitive pricing, custom sizes, international shipping]
""",
    "guest_posts": f"""
DAILY TASK: Guest Post Prospecting for {DOMAIN}

1. Find sites that accept guest posts in the niche:
   - Search: "write for us" "construction" OR "building materials" OR "architecture"
   - Search: "guest post" "submit" "cladding" OR "facade" OR "aluminium panels"
   - Search: "contribute" "building industry" blog
   - Search: "accept guest posts" "architects" OR "contractors" OR "construction"

2. Find architecture and construction blogs:
   - Search: top construction blogs 2025
   - Search: architecture material review blogs
   - Search: facade design blogs guest post

3. For each prospect:
   - Fetch the guest post guidelines page
   - Score it with score_link_prospect()
   - Generate a guest_post outreach template with 3 content ideas:
     * "Complete Guide to Aluminium Composite Panels in Modern Architecture"
     * "ACP vs Traditional Cladding: Cost, Durability and Design Comparison"
     * "How to Specify Aluminium Panels for Fire-Safe Facades"

4. Output:
   - Top 10 guest post opportunities with DA/traffic estimates where findable
   - 3 pitches ready to send
   - Content brief for highest-priority guest post
""",
    "forum_communities": f"""
DAILY TASK: Forum & Community Engagement for {DOMAIN}

1. Find active communities where {BRAND} can add value:
   - Search: "aluminium panels" forum discussion questions
   - Search: "ACP cladding" reddit OR quora OR stackexchange
   - Search: "facade materials" forum help questions
   - Search: construction professional forums 2024 2025

2. Find unanswered/poorly answered questions:
   - Search: "which aluminium panel" site:reddit.com OR site:quora.com
   - Search: "best cladding supplier" site:forums OR site:community
   - Search: "ACP panel specifications" help

3. For each community/question found:
   - Note the URL and question/topic
   - Draft a helpful answer that naturally mentions {DOMAIN}
   - Note community guidelines about links

4. Also find:
   - LinkedIn groups for architects and builders
   - Facebook groups for construction professionals
   - Industry-specific forums (ArchiExpo, Archilovers, etc.)

5. Output:
   - Top 10 threads/questions worth engaging with
   - Draft helpful responses (200-300 words each) for top 3
   - List of communities to join and participate in regularly
""",
    "content_syndication": f"""
DAILY TASK: Content Syndication & PR for {DOMAIN}

1. Find content syndication opportunities:
   - Search: "republish" OR "syndicate" construction building materials blog
   - Search: press release distribution construction industry free
   - Search: "submit article" building materials architecture industry

2. Find industry publications accepting submissions:
   - Search: construction industry magazines online submissions
   - Search: "submit news" building products manufacturer
   - Search: architecture design publication news submissions

3. Find free PR/press release sites:
   - PRWeb, PR Newswire free, EIN Presswire, PRLog
   - Construction-specific news wires

4. Create a press release template for {BRAND}:
   - Angle: product quality, international availability, or project showcase
   - Include: {DOMAIN} as the canonical link
   - Distribute to at least 5 free PR sites

5. Find podcast/interview opportunities:
   - Search: construction podcast guest interviews
   - Search: building materials startup podcast

6. Output:
   - Top 10 syndication/PR opportunities
   - Ready-to-distribute press release (400 words)
   - List of podcasts to pitch for interviews
""",
}

# ---------------------------------------------------------------------------
# Custom tools
# ---------------------------------------------------------------------------

client = anthropic.Anthropic()


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "quality", "reliable"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor"]
    pos_score = sum(1 for w in positive_words if w in mention_text.lower())
    neg_score = sum(1 for w in negative_words if w in mention_text.lower())
    sentiment = "Positive" if pos_score > neg_score else ("Negative" if neg_score > pos_score else "Neutral")
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    return (
        f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\n"
        f"Action: {'Monitor' if has_link else 'Reach out to add your link'}"
    )


@beta_tool
def score_link_prospect(
    page_url: str,
    page_title: str,
    page_content_snippet: str,
    your_niche: str,
) -> str:
    """Score a potential link building prospect.

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
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "directory", "suppliers"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/list/guide page (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 [{priority}]\nURL: {page_url}\n" + "\n".join(reasons)


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
        your_site: Your website name (use 'Alfa Panels').
        your_content_url: URL of your content to be linked.
        link_type: 'guest_post', 'broken_link', 'resource', or 'mention'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was browsing your {their_page_topic} page on {prospect_site} and noticed a broken link.\n\n"
            f"We have a detailed resource at {your_content_url} that would be a perfect replacement "
            "for your readers interested in aluminium composite panels.\n\n"
            "Would you consider updating the link? Happy to help with anything else too.\n\n"
            "Best regards,\n[Your Name]\nAlfa Panels Team\nalfaapanels.com"
        ),
        "guest_post": (
            f"Subject: Guest contribution idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following {prospect_site}'s coverage of {their_page_topic} — great content.\n\n"
            f"I'm with {your_site} and would love to contribute a guest article. "
            "Some ideas:\n"
            "• ACP Panels in Modern Facade Design: Material Selection Guide\n"
            "• Fire Safety Standards for Aluminium Composite Cladding (2025 update)\n"
            "• How Architects Are Using ACP to Achieve Net-Zero Building Envelopes\n\n"
            "Each would be 800–1200 words, original, and tailored to your audience. Interested?\n\n"
            "Best,\n[Your Name]\nAlfa Panels | alfaapanels.com"
        ),
        "resource": (
            f"Subject: Addition suggestion for your {their_page_topic} resource\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is one of the most complete I've seen.\n\n"
            f"We recently published {your_content_url} — a detailed guide on aluminium composite panel "
            "specifications, fire ratings, and installation that your readers may find useful.\n\n"
            "Would you consider adding it to your list?\n\n"
            "Thanks for your time,\n[Your Name]\nAlfa Panels | alfaapanels.com"
        ),
        "mention": (
            f"Subject: Thank you for mentioning Alfa Panels\n\n"
            f"Hi {prospect_name},\n\n"
            f"I came across your article on {their_page_topic} — thank you for the mention!\n\n"
            f"If you ever want to link directly to {your_content_url} for your readers' convenience, "
            "we'd really appreciate it.\n\n"
            "We're also happy to share your article with our audience if that's of interest.\n\n"
            "Thanks again,\n[Your Name]\nAlfa Panels | alfaapanels.com"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(
    competitor_domain: str,
    your_domain: str,
    linking_page_topic: str,
) -> str:
    """Identify if a competitor backlink is an opportunity for you.

    Args:
        competitor_domain: Competitor's domain.
        your_domain: Your domain (use 'alfaapanels.com').
        linking_page_topic: Topic of the page linking to competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Actions:\n"
        f"1. Find the specific content on {competitor_domain} that earned this link\n"
        f"2. Create a better or more up-to-date version for {your_domain}\n"
        f"3. Reach out to the linking page with your resource as an alternative or addition\n"
        f"4. If it is a directory or list — submit {your_domain} directly"
    )


@beta_tool
def log_opportunity(
    url: str,
    opportunity_type: str,
    priority: str,
    notes: str,
    outreach_ready: bool,
) -> str:
    """Log a discovered link building opportunity to the tracking file.

    Args:
        url: The prospect URL.
        opportunity_type: E.g. 'resource_page', 'directory', 'guest_post', 'unlinked_mention'.
        priority: 'HIGH', 'MEDIUM', or 'LOW'.
        notes: Brief description of the opportunity.
        outreach_ready: True if an outreach email has been drafted.
    """
    entry = {
        "date": date.today().isoformat(),
        "url": url,
        "type": opportunity_type,
        "priority": priority,
        "notes": notes,
        "outreach_ready": outreach_ready,
        "status": "new",
    }
    existing: list = []
    if OPPORTUNITIES_LOG.exists():
        try:
            existing = json.loads(OPPORTUNITIES_LOG.read_text())
        except json.JSONDecodeError:
            existing = []
    # Avoid duplicates by URL
    known_urls = {e.get("url") for e in existing}
    if url not in known_urls:
        existing.append(entry)
        OPPORTUNITIES_LOG.write_text(json.dumps(existing, indent=2))
        return f"Logged: {url} [{priority}]"
    return f"Already tracked: {url}"


# ---------------------------------------------------------------------------
# Daily runner
# ---------------------------------------------------------------------------

def get_todays_strategy() -> tuple[str, str]:
    weekday = date.today().weekday()
    strategy_key = DAILY_STRATEGY[weekday]
    return strategy_key, STRATEGY_PROMPTS[strategy_key]


def run_daily_session(strategy_key: str | None = None) -> str:
    """Run one daily backlink building session and return the report path."""
    if strategy_key is None:
        strategy_key, strategy_prompt = get_todays_strategy()
    else:
        strategy_prompt = STRATEGY_PROMPTS[strategy_key]

    today = date.today().isoformat()
    report_dir = REPORTS_DIR / today
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{strategy_key}.md"

    print(f"\n{'='*60}")
    print(f"Daily Backlink Builder — {today}")
    print(f"Strategy: {strategy_key.replace('_', ' ').title()}")
    print(f"Domain: {DOMAIN}")
    print(f"{'='*60}\n")

    system_prompt = (
        f"You are an expert off-page SEO and link building specialist working for {BRAND} ({DOMAIN}), "
        f"a manufacturer of aluminium composite panels (ACP) for architectural facades and cladding. "
        f"Your job today is to find real, actionable backlink opportunities. "
        f"Always use the available tools to score prospects and log opportunities. "
        f"Be specific with URLs, contact details, and outreach copy. "
        f"Focus on quality over quantity — a DA40+ relevant link is worth more than 10 low-quality ones."
    )

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        tools=[
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            log_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[
            {
                "role": "user",
                "content": strategy_prompt.strip(),
            }
        ],
    )

    report_sections = [
        f"# Daily Backlink Report: {DOMAIN}\n",
        f"**Date:** {today}  \n**Strategy:** {strategy_key.replace('_', ' ').title()}\n",
        "---\n",
    ]

    for message in runner:
        for block in message.content:
            if block.type == "text" and block.text.strip():
                print(block.text)
                report_sections.append(block.text)

    report_content = "\n\n".join(report_sections)
    report_path.write_text(report_content)
    print(f"\nReport saved: {report_path}")

    # Append a daily summary line to the master log
    master_log = REPORTS_DIR / "daily_log.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(master_log, "a") as f:
        f.write(f"- {timestamp} | {strategy_key} | {report_path}\n")

    return str(report_path)


# ---------------------------------------------------------------------------
# Scheduler entry point
# ---------------------------------------------------------------------------

def schedule_daily(run_time: str = "09:00"):
    """Run the builder every day at run_time (HH:MM, local time)."""
    try:
        import schedule
        import time
    except ImportError:
        raise SystemExit("Install 'schedule': pip install schedule")

    print(f"Backlink builder scheduled daily at {run_time} for {DOMAIN}")
    schedule.every().day.at(run_time).do(run_daily_session)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]

    if "--schedule" in args:
        run_time = "09:00"
        for arg in args:
            if arg.startswith("--time="):
                run_time = arg.split("=", 1)[1]
        schedule_daily(run_time)
    elif "--strategy" in args:
        idx = args.index("--strategy")
        key = args[idx + 1] if idx + 1 < len(args) else None
        if key not in STRATEGY_PROMPTS:
            print(f"Available strategies: {', '.join(STRATEGY_PROMPTS)}")
            sys.exit(1)
        run_daily_session(strategy_key=key)
    else:
        # Default: run today's strategy
        run_daily_session()
