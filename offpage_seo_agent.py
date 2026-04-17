#!/usr/bin/env python3
"""Daily backlink building agent for alfaapanels.com"""

import anthropic
import json
import logging
import os
from datetime import date, datetime
from pathlib import Path
from anthropic import beta_tool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("backlink_agent.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

client = anthropic.Anthropic()

SITE_CONFIG = {
    "domain": "alfaapanels.com",
    "brand_name": "Alfa Panels",
    "niche": "solar panels, building panels, construction materials, panel installation",
    "competitors": [
        "canadiansolar.com",
        "jinko-solar.com",
        "longi-solar.com",
        "trinasolar.com",
    ],
    "target_keywords": [
        "alfa panels",
        "alfaapanels",
        "solar panel supplier",
        "building panels supplier",
        "panel installation services",
        "construction panels",
        "solar energy panels",
    ],
}

TRACKING_FILE = "backlink_tracker.json"
REPORTS_DIR = "daily_reports"

# Rotating daily strategies (index by weekday: 0=Mon...6=Sun)
DAILY_STRATEGIES = {
    0: "directory_submissions",
    1: "forum_link_building",
    2: "resource_page_outreach",
    3: "broken_link_building",
    4: "guest_post_outreach",
    5: "competitor_backlink_replication",
    6: "brand_mention_conversion",
}

STRATEGY_PROMPTS = {
    "directory_submissions": """
Focus: Find high-quality business and niche directories to submit alfaapanels.com.
1. Search for "solar panel companies directory site:*.com" and "building panels supplier directory"
2. Find 10 relevant directories that accept free or paid listings
3. Score each directory using score_link_prospect
4. Generate submission-ready business descriptions for the top 5
5. Check if alfaapanels.com is already listed in any major directories""",

    "forum_link_building": """
Focus: Find forums, Q&A sites, and communities where alfaapanels.com can add value.
1. Search for active forums about solar panels, construction, and building materials
2. Find recent questions/threads about panel suppliers, installation, or solar energy
3. Identify 8 threads where a helpful answer mentioning alfaapanels.com would be natural
4. Generate helpful, non-spammy responses for the top 5 opportunities
5. Look for Quora, Reddit, and industry-specific forum opportunities""",

    "resource_page_outreach": """
Focus: Find resource/links pages that should include alfaapanels.com.
1. Search: intitle:"resources" OR intitle:"useful links" "solar panels" OR "building panels"
2. Search: intitle:"recommended suppliers" "panels" OR "solar"
3. Find 10 resource pages in the panels/solar/construction niche
4. Score each using score_link_prospect
5. Generate personalized outreach emails for the top 5 using generate_outreach_template with type "resource"
6. Identify the contact email/form for each prospect""",

    "broken_link_building": """
Focus: Find broken links on competitor and niche sites to replace with alfaapanels.com content.
1. Search for "solar panel supplier" OR "panel installation" resource pages
2. Fetch 5 high-authority pages and check for outdated/broken links
3. Identify which alfaapanels.com pages could replace broken resources
4. Generate broken link replacement outreach using generate_outreach_template with type "broken_link"
5. Prioritize .edu, .gov, and .org pages with relevant content""",

    "guest_post_outreach": """
Focus: Find guest post opportunities in the solar/panels/construction niche.
1. Search: "write for us" "solar energy" OR "solar panels" OR "renewable energy"
2. Search: "guest post" "construction materials" OR "building panels" OR "panel suppliers"
3. Find 10 blogs accepting guest contributions
4. Score relevance using score_link_prospect
5. Generate 3 guest post pitches using generate_outreach_template with type "guest_post"
6. Suggest specific article topics that would provide value to each blog's audience""",

    "competitor_backlink_replication": """
Focus: Replicate the best backlinks pointing to competitors.
1. For each competitor, search: link:canadiansolar.com OR link:jinko-solar.com site:*.com
2. Also search: "canadiansolar.com" OR "jinko-solar.com" reviews OR directory OR supplier
3. Find 10 sites linking to competitors but not alfaapanels.com
4. Use identify_link_gap_opportunity for the top opportunities
5. Generate outreach strategy for replicating the 5 best competitor backlinks
6. Score each opportunity using score_link_prospect""",

    "brand_mention_conversion": """
Focus: Find unlinked mentions of Alfa Panels and convert them to backlinks.
1. Search: "alfa panels" -site:alfaapanels.com
2. Search: "alfaapanels" -site:alfaapanels.com
3. Search: "alfaapanels.com" -site:alfaapanels.com
4. Categorize each mention using categorize_brand_mention
5. Find contact information for top 5 unlinked mentions
6. Generate link request emails using generate_outreach_template with type "mention"
7. Check quality of existing backlinks using analyze_backlink_quality""",
}


def load_tracker() -> dict:
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE) as f:
            return json.load(f)
    return {
        "opportunities": [],
        "submitted": [],
        "outreach_sent": [],
        "daily_runs": [],
        "total_opportunities_found": 0,
    }


def save_tracker(tracker: dict):
    with open(TRACKING_FILE, "w") as f:
        json.dump(tracker, f, indent=2)


def get_today_strategy() -> tuple[str, str]:
    weekday = date.today().weekday()
    strategy_key = DAILY_STRATEGIES[weekday]
    return strategy_key, STRATEGY_PROMPTS[strategy_key]


def already_ran_today(tracker: dict) -> bool:
    today = date.today().isoformat()
    return any(run["date"] == today for run in tracker.get("daily_runs", []))


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    quality_signals = []
    generic_anchors = ["click here", "website", "here", "link", "read more", "visit"]
    if anchor_text.lower() in generic_anchors:
        quality_signals.append("Warning: Generic anchor text - low SEO value")
    else:
        quality_signals.append(f"Good: Descriptive anchor text: '{anchor_text}'")
    toxic_words = ["spam", "casino", "viagra", "adult", "forex", "crypto-scam"]
    if any(word in backlink_url.lower() for word in toxic_words):
        quality_signals.append("TOXIC link detected - disavow recommended")
    else:
        quality_signals.append("Domain appears clean - no toxic signals")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in backlink_url for s in authority_signals):
        quality_signals.append("High authority domain - excellent link value")
    return "\n".join(quality_signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and analyze sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "reliable", "trusted"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor", "fake", "unreliable"]
    pos_score = sum(1 for w in positive_words if w in mention_text.lower())
    neg_score = sum(1 for w in negative_words if w in mention_text.lower())
    if pos_score > neg_score:
        sentiment = "Positive"
    elif neg_score > pos_score:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    mention_type = "Linked mention" if has_link else "Unlinked mention (backlink opportunity!)"
    action = "Monitor and track" if has_link else "Contact site owner to request link addition"
    return (
        f"Brand: {brand_name}\n"
        f"Type: {mention_type}\n"
        f"Sentiment: {sentiment}\n"
        f"Action: {action}"
    )


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
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for word in niche_words if word in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low niche relevance (+0)")
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "top", "directory", "supplier"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/directory page type (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High authority domain (.edu/.gov/.org) (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM PRIORITY" if score >= 40 else "LOW PRIORITY"
    return f"Score: {score}/100 [{priority}]\nURL: {page_url}\nSignals:\n" + "\n".join(f"  - {r}" for r in reasons)


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
        prospect_name: Name of the website owner/editor (use "Editor" if unknown).
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        your_site: Your website name.
        your_content_url: URL of your content to be linked.
        link_type: One of: 'guest_post', 'broken_link', 'resource', 'mention'.
    """
    templates = {
        "broken_link": (
            f"Subject: Found a broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was browsing your excellent {their_page_topic} page on {prospect_site} and noticed a broken link.\n\n"
            f"We have a comprehensive resource at {your_content_url} on {your_site} that would be a perfect replacement for your readers.\n\n"
            f"Would you consider updating the broken link? Happy to help your audience find a working resource.\n\n"
            f"Best regards,\n[Your Name]\n{your_site}"
        ),
        "guest_post": (
            f"Subject: Guest Post Idea for {prospect_site} – {their_page_topic}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following {prospect_site}'s content on {their_page_topic} – great work!\n\n"
            f"I'm from {your_site} and would love to contribute a guest post that adds value for your readers.\n\n"
            f"I can write about [specific topic idea related to {their_page_topic}] with actionable insights your audience will appreciate.\n\n"
            f"Would you be open to a collaboration?\n\n"
            f"Best,\n[Your Name]\n{your_site}"
        ),
        "resource": (
            f"Subject: Useful resource for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} at {prospect_site} is really helpful!\n\n"
            f"I wanted to suggest adding {your_content_url} from {your_site} – it covers [specific value] that your readers looking for {their_page_topic} resources would find useful.\n\n"
            f"Would you take a look?\n\n"
            f"Best,\n[Your Name]\n{your_site}"
        ),
        "mention": (
            f"Subject: Linking to {your_site} from your {their_page_topic} article\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {your_site} in your article about {their_page_topic} on {prospect_site}!\n\n"
            f"Would you consider adding a direct link to {your_content_url}? It would make it easier for your readers to find us.\n\n"
            f"Thanks so much,\n[Your Name]\n{your_site}"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(competitor_domain: str, your_domain: str, linking_page_topic: str) -> str:
    """Identify a competitor backlink as an opportunity for your site.

    Args:
        competitor_domain: Competitor's domain.
        your_domain: Your domain.
        linking_page_topic: Topic of the page linking to the competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY IDENTIFIED\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Action plan:\n"
        f"1. Research what specific content on {competitor_domain} earned this backlink\n"
        f"2. Identify if {your_domain} has equivalent or better content on the same topic\n"
        f"3. If not, create superior content targeting '{linking_page_topic}'\n"
        f"4. Reach out to the linking page with your {your_domain} resource as an alternative\n"
        f"5. Pitch the unique value {your_domain} offers vs {competitor_domain}"
    )


def run_daily_backlink_building():
    tracker = load_tracker()
    today = date.today().isoformat()

    if already_ran_today(tracker):
        logger.info("Daily backlink run already completed for %s. Skipping.", today)
        return

    strategy_key, strategy_prompt = get_today_strategy()
    cfg = SITE_CONFIG

    logger.info("Starting daily backlink building – Strategy: %s", strategy_key)
    print("\n" + "=" * 70)
    print(f"DAILY BACKLINK BUILDING – {today}")
    print(f"Site: {cfg['domain']}  |  Strategy: {strategy_key.replace('_', ' ').title()}")
    print("=" * 70 + "\n")

    Path(REPORTS_DIR).mkdir(exist_ok=True)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
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
            "content": f"""You are an expert off-page SEO specialist building relevant, high-quality backlinks for {cfg['domain']}.

SITE DETAILS:
- Domain: {cfg['domain']}
- Brand: {cfg['brand_name']}
- Niche: {cfg['niche']}
- Target keywords: {', '.join(cfg['target_keywords'])}
- Competitors: {', '.join(cfg['competitors'])}

TODAY'S DATE: {today}
TODAY'S STRATEGY: {strategy_key.replace('_', ' ').upper()}

{strategy_prompt}

IMPORTANT RULES:
- Only find RELEVANT backlink sources in the panels/solar/construction niche
- Focus on quality over quantity – prefer high-authority, niche-relevant sites
- All outreach must be personalized and professional, never spammy
- Use your tools to research real opportunities via web search and fetch
- Score every prospect using score_link_prospect before recommending it
- Generate complete, ready-to-send outreach emails for the top opportunities

DELIVERABLES:
1. List of discovered backlink opportunities (with scores)
2. Top 5 HIGH PRIORITY targets with full details
3. Ready-to-use outreach emails for each top target
4. Estimated monthly search traffic/authority of target sites if available
5. Summary table: Opportunity | Score | Strategy | Status

End with a clear NEXT STEPS section for the site owner to take action today.""",
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_path = Path(REPORTS_DIR) / f"backlinks_{today}_{strategy_key}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report – {cfg['domain']}\n")
        f.write(f"**Date:** {today}  |  **Strategy:** {strategy_key.replace('_', ' ').title()}\n\n")
        f.write("\n\n".join(full_report))

    tracker["daily_runs"].append({
        "date": today,
        "strategy": strategy_key,
        "report": str(report_path),
        "timestamp": datetime.utcnow().isoformat(),
    })
    tracker["total_opportunities_found"] = tracker.get("total_opportunities_found", 0) + 1
    save_tracker(tracker)

    logger.info("Daily backlink run complete. Report saved to %s", report_path)
    print(f"\nReport saved: {report_path}")
    return str(report_path)


def run_offpage_seo_agent(your_domain: str, brand_name: str, niche: str, competitors: list):
    """Full off-page SEO audit (run manually for comprehensive analysis)."""
    print(f"\nStarting full Off-Page SEO audit for: {your_domain}\n")
    print("=" * 60)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
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

Execute these tasks:

TASK 1 – Brand Mention Audit
Search for "{brand_name}" mentions. Find unlinked mentions and opportunities.

TASK 2 – Competitor Backlink Research
For each competitor, find sites linking to them but not to {your_domain}.

TASK 3 – Link Building Opportunities
Find resource pages, guest post opportunities, and broken links in the {niche} niche.

TASK 4 – Outreach Templates
Generate personalized email templates for top 3 prospects.

TASK 5 – Final Report
Create a prioritized 30-day off-page SEO action plan.""",
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_filename = f"seo_report_{your_domain.replace('.', '_')}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Off-Page SEO Report: {your_domain}\n\n")
        f.write("\n\n".join(full_report))
    print(f"\nReport saved to: {report_filename}")


if __name__ == "__main__":
    run_daily_backlink_building()
