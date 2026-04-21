import anthropic
import json
import logging
import os
import schedule
import time
from anthropic import beta_tool
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("seo_agent.log"),
    ],
)
logger = logging.getLogger(__name__)

STATE_FILE = "seo_state.json"
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "electrical panels, distribution boards, panel manufacturing"
COMPETITORS = [
    "hager.com",
    "legrand.com",
    "schneider-electric.com",
]

client = anthropic.Anthropic()


def load_state() -> dict:
    if Path(STATE_FILE).exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"runs": [], "contacted_domains": [], "disavow_list": []}


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


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
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing"]
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
    return (
        f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\n"
        f"Action: {'Monitor' if has_link else 'Reach out to add your link'}"
    )


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
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide page - high link value (+30)")
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
            f"Would you consider updating the link?\n\nBest,\n[Your Name]"
        ),
        "guest_post": (
            f"Subject: Guest Post Idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I love your content on {prospect_site} about {their_page_topic}.\n\n"
            f"I'd love to contribute a guest post. I write for {your_site}.\n\n"
            f"Would you be open to a collaboration?\n\nBest,\n[Your Name]"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is great! "
            f"I created {your_content_url} which might help your readers.\n\n"
            f"Would you take a look?\n\nBest,\n[Your Name]"
        ),
        "mention": (
            f"Subject: You mentioned {your_site} - thank you!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {your_site} in your article about {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {your_content_url}?\n\nThanks,\n[Your Name]"
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
        f"Competitor: {competitor_domain}\nYour site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Actions:\n"
        f"1. Find what content earned {competitor_domain} this link\n"
        f"2. Create better content on the same topic for {your_domain}\n"
        f"3. Reach out to the linking page with your resource"
    )


def run_offpage_seo_agent(your_domain: str, brand_name: str, niche: str, competitors: list):
    today = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Starting Off-Page SEO Agent for: {your_domain} | Date: {today}")
    print("=" * 60)

    state = load_state()

    if today in state["runs"]:
        logger.info(f"Already ran today ({today}). Skipping.")
        return

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
            "content": f"""You are an expert off-page SEO strategist.
Perform a complete off-page SEO analysis for: {your_domain}

Brand name: {brand_name}
Niche: {niche}
Competitors: {', '.join(competitors)}
Date: {today}

Previously contacted domains (skip these): {', '.join(state['contacted_domains']) or 'None yet'}

Execute these tasks:

TASK 1 - Brand Mention Audit
Search for "{brand_name}" mentions. Find unlinked mentions and opportunities.
Search: "{brand_name}" -site:{your_domain}

TASK 2 - Competitor Backlink Research
For each competitor, find sites linking to them but not to {your_domain}.
Focus on electrical/industrial directories, trade publications, and engineering blogs.

TASK 3 - Link Building Opportunities
Find resource pages, guest post opportunities, broken links in {niche} niche.
Target: electrical engineering blogs, trade directories, industry associations,
manufacturing resource pages.

TASK 4 - Outreach Templates
Generate personalized email templates for top 3 NEW prospects (not in contacted list).

TASK 5 - Final Daily Report
Create a prioritized daily action plan with:
- Top 5 backlink opportunities found today
- Outreach emails ready to send
- Any toxic links to disavow
- Progress notes for tomorrow""",
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_path = REPORTS_DIR / f"seo_report_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Off-Page SEO Daily Report: {your_domain}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(full_report))

    state["runs"].append(today)
    save_state(state)

    logger.info(f"Report saved to: {report_path}")
    print(f"\nReport saved to: {report_path}")


def daily_job():
    run_offpage_seo_agent(
        your_domain=DOMAIN,
        brand_name=BRAND_NAME,
        niche=NICHE,
        competitors=COMPETITORS,
    )


if __name__ == "__main__":
    # Run immediately on startup, then schedule daily at 08:00
    daily_job()

    schedule.every().day.at("08:00").do(daily_job)
    logger.info("Scheduler started — running daily at 08:00")

    while True:
        schedule.run_pending()
        time.sleep(60)
