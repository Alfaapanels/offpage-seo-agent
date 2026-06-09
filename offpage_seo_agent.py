import anthropic
import os
import json
import argparse
from datetime import date
from pathlib import Path
from anthropic import beta_tool

client = anthropic.Anthropic()

DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "aluminum composite panels facade cladding building materials"
COMPETITORS = [
    "alucobond.com",
    "reynobond.com",
    "alpolic.com",
    "dibond.com",
    "alucoil.com",
]

REPORTS_DIR = Path("reports")
OPPORTUNITIES_FILE = Path("seen_opportunities.json")


def load_seen_opportunities() -> set:
    if OPPORTUNITIES_FILE.exists():
        with open(OPPORTUNITIES_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen_opportunities(seen: set):
    with open(OPPORTUNITIES_FILE, "w") as f:
        json.dump(list(seen), f, indent=2)


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    quality_signals = []
    exact_match_keywords = ["click here", "website", "here", "link"]
    if anchor_text.lower() in exact_match_keywords:
        quality_signals.append("Warning: Generic anchor text - low value")
    else:
        quality_signals.append(f"Good: Descriptive anchor: '{anchor_text}'")
    if any(word in backlink_url.lower() for word in ["spam", "casino", "viagra"]):
        quality_signals.append("TOXIC link - disavow recommended")
    else:
        quality_signals.append("Domain appears clean")
    return "\n".join(quality_signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "durable", "premium"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor"]
    pos_score = sum(1 for w in positive_words if w in mention_text.lower())
    neg_score = sum(1 for w in negative_words if w in mention_text.lower())
    if pos_score > neg_score:
        sentiment = "Positive"
    elif neg_score > pos_score:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    return f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\nAction: {'Monitor' if has_link else 'Reach out to add your link'}"


@beta_tool
def score_link_prospect(page_url: str, page_title: str, page_content_snippet: str, your_niche: str) -> str:
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
        reasons.append("High relevance to your niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "supplier", "manufacturer", "directory"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide/directory page - high link value (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Prospect Score: {score}/100 - {priority}\nURL: {page_url}\nReasons:\n" + "\n".join(reasons)


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
        link_type: Type: 'guest_post', 'broken_link', 'resource', 'mention'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I noticed a broken link on your {their_page_topic} page on {prospect_site}.\n\n"
            f"I have a comprehensive guide at {your_content_url} that would be a great replacement.\n\n"
            f"Would you consider updating the link?\n\nBest,\n[Your Name]\nAlfa Panels | alfaapanels.com"
        ),
        "guest_post": (
            f"Subject: Guest Post Idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I love your content on {prospect_site} about {their_page_topic}.\n\n"
            f"I'd love to contribute a guest post on aluminum composite panels or facade cladding solutions. "
            f"I write for {your_site} and have hands-on expertise in ACP installation and specification.\n\n"
            f"Would you be open to a collaboration?\n\nBest,\n[Your Name]\nAlfa Panels | alfaapanels.com"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is excellent! "
            f"I created {your_content_url} which covers aluminum composite panels, facade systems, "
            f"and building cladding — it may add value for your readers.\n\n"
            f"Would you take a look?\n\nBest,\n[Your Name]\nAlfa Panels | alfaapanels.com"
        ),
        "mention": (
            f"Subject: You mentioned {your_site} - thank you!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {your_site} in your article about {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {your_content_url} so your readers can learn more?\n\n"
            f"Thanks,\n[Your Name]\nAlfa Panels | alfaapanels.com"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(competitor_domain: str, your_domain: str, linking_page_topic: str) -> str:
    """Identify if a competitor backlink is an opportunity for you.

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
        f"Actions:\n"
        f"1. Find what content earned {competitor_domain} this link\n"
        f"2. Create better/more specific content on the same topic for {your_domain}\n"
        f"3. Reach out to the linking page with your resource\n"
        f"4. Highlight Alfa Panels' unique differentiators (product range, delivery, certifications)"
    )


def run_offpage_seo_agent(run_date: str | None = None):
    today = run_date or date.today().isoformat()
    print(f"\nStarting Off-Page SEO Agent for: {DOMAIN} | Date: {today}\n")
    print("=" * 60)

    seen = load_seen_opportunities()

    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / f"seo_report_{today}.md"

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO strategist working for {DOMAIN}.

Run date: {today}
Domain: {DOMAIN}
Brand: {BRAND_NAME}
Niche: {NICHE}
Competitors: {', '.join(COMPETITORS)}

Previously seen opportunity URLs (skip these to avoid duplicates):
{json.dumps(list(seen), indent=2) if seen else "None yet — this is the first run."}

Execute ALL of the following tasks and provide actionable output for EACH:

TASK 1 — Brand Mention Audit
Search for "{BRAND_NAME}" and "alfaapanels" mentions across the web.
Find unlinked mentions that could be converted to backlinks.
Search queries to try:
  - "{BRAND_NAME}" -site:{DOMAIN}
  - "alfaapanels" -site:{DOMAIN}
  - "alfa panels" building materials -site:{DOMAIN}

TASK 2 — Competitor Backlink Gap Analysis
For EACH competitor in [{', '.join(COMPETITORS)}], search for pages that link to them
but not to {DOMAIN}. Focus on:
  - Architecture and construction directories
  - Building materials supplier lists
  - ACP/facade cladding resource pages
  - Industry associations and trade bodies
Use identify_link_gap_opportunity for each find.

TASK 3 — Fresh Link Building Opportunities (find NEW ones today)
Search for:
  - Resource pages: "aluminum composite panel" + "resources" OR "suppliers" OR "manufacturers"
  - Guest post opportunities: "facade cladding" + "write for us" OR "guest post"
  - Broken link opportunities: "aluminum panel" site:construction OR architecture blogs
  - Directory listings: building materials directories, construction supplier directories
  - Industry blogs and publications that accept contributor content
Score each with score_link_prospect. Focus on domains NOT in the seen list above.

TASK 4 — Outreach Email Templates
Generate personalized outreach emails for the TOP 3 prospects found today.
Use generate_outreach_template for each.

TASK 5 — Today's Action Plan
Provide a concise prioritized list of 5–10 specific actions to take TODAY to build
backlinks for {DOMAIN}. Include direct URLs where possible.
Format as a numbered checklist with effort level (easy/medium/hard) for each item."""
        }],
    )

    full_report = []
    new_urls: list[str] = []

    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)
                # Naive extraction: collect http URLs from the report to track as seen
                import re
                found = re.findall(r"https?://[^\s\)\]\"']+", block.text)
                new_urls.extend(found)

    with open(report_path, "w") as f:
        f.write(f"# Off-Page SEO Report: {DOMAIN}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(full_report))

    # Update seen opportunities
    seen.update(new_urls)
    save_seen_opportunities(seen)

    print(f"\nReport saved to: {report_path}")
    print(f"Total tracked opportunities: {len(seen)}")
    return str(report_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily off-page SEO agent for alfaapanels.com")
    parser.add_argument("--date", help="Override run date (YYYY-MM-DD)", default=None)
    args = parser.parse_args()
    run_offpage_seo_agent(run_date=args.date)
