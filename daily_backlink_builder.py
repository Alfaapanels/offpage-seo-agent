"""
Daily backlink builder for alfaapanels.com.

Runs once per day, discovers fresh link-building opportunities, avoids
re-contacting sites already logged in outreach_log.json, and saves a
dated Markdown report under reports/.
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

SITE_CONFIG = {
    "domain": "alfaapanels.com",
    "brand_name": "Alfa Panels",
    "niche": "aluminum composite panels cladding facade building materials",
    "competitors": [
        "alucobond.com",
        "reynobond.com",
        "alpolic.com",
        "dibond.com",
    ],
    "key_pages": [
        "https://alfaapanels.com/products",
        "https://alfaapanels.com/about",
        "https://alfaapanels.com",
    ],
    "target_anchor_texts": [
        "aluminum composite panels",
        "ACP panels",
        "facade cladding",
        "building cladding panels",
        "Alfa Panels",
    ],
}

OUTREACH_LOG = Path("outreach_log.json")
REPORTS_DIR = Path("reports")

# ---------------------------------------------------------------------------
# Outreach log helpers
# ---------------------------------------------------------------------------

def load_outreach_log() -> dict:
    if OUTREACH_LOG.exists():
        with open(OUTREACH_LOG) as f:
            return json.load(f)
    return {"contacted": [], "opportunities": []}


def save_outreach_log(log: dict) -> None:
    with open(OUTREACH_LOG, "w") as f:
        json.dump(log, f, indent=2)


def already_contacted(domain: str, log: dict) -> bool:
    return domain in log.get("contacted", [])


def mark_contacted(domain: str, log: dict) -> None:
    if domain not in log["contacted"]:
        log["contacted"].append(domain)

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

client = anthropic.Anthropic()


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    quality_signals = []
    generic_anchors = ["click here", "website", "here", "link", "read more"]
    if anchor_text.lower() in generic_anchors:
        quality_signals.append("Warning: Generic anchor text - low value")
    else:
        quality_signals.append(f"Good: Descriptive anchor: '{anchor_text}'")

    toxic_words = ["spam", "casino", "viagra", "adult", "pharma"]
    if any(w in backlink_url.lower() for w in toxic_words):
        quality_signals.append("TOXIC link - disavow recommended")
    else:
        quality_signals.append("Domain appears clean")

    authority_tlds = [".edu", ".gov", ".org"]
    if any(t in backlink_url for t in authority_tlds):
        quality_signals.append("High authority TLD (+bonus)")

    return "\n".join(quality_signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "durable"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor", "cheap", "fake"]
    pos = sum(1 for w in positive_words if w in mention_text.lower())
    neg = sum(1 for w in negative_words if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else "Negative" if neg > pos else "Neutral"
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    action = "Monitor" if has_link else "Reach out to request a link"
    return f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\nAction: {action}"


@beta_tool
def score_link_prospect(page_url: str, page_title: str, page_content_snippet: str, your_niche: str) -> str:
    """Score a potential link building prospect (0-100).

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
        reasons.append("High relevance to niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")

    resource_signals = ["resource", "guide", "tools", "blog", "list", "best", "review", "supplier", "manufacturer"]
    if any(t in page_url.lower() or t in page_title.lower() for t in resource_signals):
        score += 30
        reasons.append("Resource/guide page (+30)")

    authority_tlds = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_tlds):
        score += 30
        reasons.append("High authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")

    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 [{priority}]\nURL: {page_url}\n" + "\n".join(f"  - {r}" for r in reasons)


@beta_tool
def generate_outreach_email(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    your_content_url: str,
    link_type: str,
) -> str:
    """Generate a personalized outreach email for alfaapanels.com.

    Args:
        prospect_name: Name of the website owner/editor (use 'Team' if unknown).
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        your_content_url: URL of alfaapanels.com content to be linked.
        link_type: One of: 'guest_post', 'broken_link', 'resource', 'mention'.
    """
    base = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your article on {their_page_topic} at {prospect_site} and noticed a broken link.\n\n"
            f"We have a detailed resource on aluminum composite panels at {your_content_url} that would be a perfect replacement and add real value to your readers.\n\n"
            f"Would you consider updating the link? Happy to help in any way.\n\n"
            f"Best regards,\nAlfa Panels Team\nalfaapanels.com"
        ),
        "guest_post": (
            f"Subject: Guest Post Collaboration – ACP Panels for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following {prospect_site}'s coverage of {their_page_topic} — great work!\n\n"
            f"I'm from Alfa Panels (alfaapanels.com), a leading supplier of aluminum composite panels. "
            f"We'd love to contribute an expert guest post on ACP panel applications, installation tips, or facade design trends.\n\n"
            f"Our reference: {your_content_url}\n\n"
            f"Would you be open to a collaboration?\n\n"
            f"Best,\nAlfa Panels Team"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is really comprehensive. "
            f"We recently published a detailed guide/product page that your readers in the construction and architecture space might find very useful:\n\n"
            f"{your_content_url}\n\n"
            f"We are Alfa Panels — specialists in aluminum composite cladding panels for commercial and residential facades.\n\n"
            f"Would you consider adding it to your resources?\n\n"
            f"Thanks,\nAlfa Panels Team\nalfaapanels.com"
        ),
        "mention": (
            f"Subject: Thank you for mentioning Alfa Panels!\n\n"
            f"Hi {prospect_name},\n\n"
            f"We noticed you mentioned Alfa Panels in your article about {their_page_topic} — thank you!\n\n"
            f"Would you be open to linking directly to {your_content_url} so your readers can easily find us?\n\n"
            f"Thanks again for the mention!\n\n"
            f"Alfa Panels Team\nalfaapanels.com"
        ),
    }
    return base.get(link_type, base["resource"])


@beta_tool
def identify_link_gap(competitor_domain: str, your_domain: str, linking_page_topic: str) -> str:
    """Identify a competitor backlink as an opportunity for your site.

    Args:
        competitor_domain: Competitor's domain.
        your_domain: Your domain.
        linking_page_topic: Topic of the page linking to the competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Action plan:\n"
        f"1. Identify the specific content on {competitor_domain} that earned this link.\n"
        f"2. Create superior content on {your_domain} covering the same topic.\n"
        f"3. Reach out to the linking site with your improved resource."
    )

# ---------------------------------------------------------------------------
# Agent runner
# ---------------------------------------------------------------------------

def build_daily_prompt(config: dict, contacted_sites: list, today: str) -> str:
    avoided = ", ".join(contacted_sites[-20:]) if contacted_sites else "none yet"
    return f"""You are an expert off-page SEO strategist working exclusively for {config['domain']}.

Today's date: {today}
Target domain: {config['domain']}
Brand name: {config['brand_name']}
Niche: {config['niche']}
Competitors: {', '.join(config['competitors'])}
Key pages to build links to: {', '.join(config['key_pages'])}
Preferred anchor texts: {', '.join(config['target_anchor_texts'])}

Sites already contacted (do NOT repeat these): {avoided}

TODAY'S TASKS — find NEW, fresh opportunities only:

## TASK 1 — Brand Mention Hunt
Search for "{config['brand_name']}" and "alfaapanels.com" mentions across the web.
Identify unlinked mentions and reach out opportunities.
Use web_search: '"{config['brand_name']}" -site:{config['domain']}'

## TASK 2 — Competitor Backlink Gap Analysis
For each competitor ({', '.join(config['competitors'])}), find pages that link to them
but NOT to {config['domain']}. These are prime outreach targets.
Search patterns: 'link:{competitor}' or 'site:{competitor} aluminum composite panels'

## TASK 3 — Fresh Link Prospects
Find TODAY'S fresh prospects using these searches (use web_search for each):
- 'aluminum composite panels suppliers directory'
- 'ACP panels architecture blog write for us'
- 'building cladding resources page'
- 'facade materials contractor guide'
- 'aluminum panels installation guide site:.org OR site:.edu'
Score each prospect with score_link_prospect. Focus on HIGH PRIORITY targets.

## TASK 4 — Outreach Email Drafts
For the top 5 NEW prospects found today, generate ready-to-send outreach emails
using generate_outreach_email. Be specific and personalised.

## TASK 5 — Daily Action Report
Produce a structured Markdown report with:
- Executive summary (3 bullet points)
- Ranked list of today's top 10 link opportunities (URL + score + outreach type)
- 5 ready-to-send outreach email drafts
- Anchor text recommendations for each link
- Tomorrow's priority actions

Be concrete: real URLs, real prospects, real emails. Skip anything generic."""


def run_daily_builder():
    today = date.today().isoformat()
    print(f"\n{'='*60}")
    print(f"  Alfa Panels Daily Backlink Builder — {today}")
    print(f"{'='*60}\n")

    REPORTS_DIR.mkdir(exist_ok=True)
    log = load_outreach_log()

    prompt = build_daily_prompt(SITE_CONFIG, log["contacted"], today)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_email,
            identify_link_gap,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{"role": "user", "content": prompt}],
    )

    report_parts = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_parts.append(block.text)

    report_text = "\n\n".join(report_parts)
    report_path = REPORTS_DIR / f"backlinks_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Alfa Panels Backlink Report — {today}\n\n")
        f.write(report_text)

    # Update outreach log with any new domains mentioned in the report
    # (simple heuristic: extract domains from the report text)
    import re
    found_domains = re.findall(r'https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-z]{2,})', report_text)
    new_domains = [
        d for d in set(found_domains)
        if d not in SITE_CONFIG["domain"]
        and not any(d in c for c in SITE_CONFIG["competitors"])
        and not already_contacted(d, log)
    ]
    for domain in new_domains[:10]:  # log top 10 new prospects per day
        mark_contacted(domain, log)
    log["opportunities"].append({"date": today, "domains": new_domains[:10]})
    save_outreach_log(log)

    print(f"\nReport saved: {report_path}")
    print(f"Logged {len(new_domains[:10])} new prospects to outreach_log.json")
    return str(report_path)


if __name__ == "__main__":
    run_daily_builder()
