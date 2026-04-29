import anthropic
from anthropic import beta_tool
import json
import os
from datetime import date, timedelta

# ── Configuration ────────────────────────────────────────────────────────────
DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "solar panels LED display panels electrical panels home improvement energy"
COMPETITORS = [
    "sunpowercorp.com",
    "lgelectronics.com",
    "enphase.com",
    "solaredge.com",
]
LOG_FILE = "backlink_log.json"
REPORTS_DIR = "reports"

client = anthropic.Anthropic()


# ── Tracking helpers ─────────────────────────────────────────────────────────

def load_log() -> dict:
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return {"contacted_sites": {}, "submitted_directories": [], "daily_summaries": []}


def save_log(log: dict) -> None:
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


# ── Tools ────────────────────────────────────────────────────────────────────

@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate the quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL that is linking to you.
        anchor_text: The anchor text used for the link.
    """
    signals = []
    generic = ["click here", "website", "here", "link", "this page"]
    if anchor_text.lower() in generic:
        signals.append("Warning: Generic anchor text – low SEO value")
    else:
        signals.append(f"Good: Descriptive anchor '{anchor_text}'")
    toxic = ["spam", "casino", "viagra", "adult", "pharma"]
    if any(t in backlink_url.lower() for t in toxic):
        signals.append("TOXIC domain – add to disavow file")
    else:
        signals.append("Domain appears clean")
    return "\n".join(signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and determine its sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive = ["great", "best", "excellent", "recommend", "love", "amazing", "top", "leading"]
    negative = ["bad", "worst", "avoid", "scam", "terrible", "poor", "fake"]
    pos = sum(1 for w in positive if w in mention_text.lower())
    neg = sum(1 for w in negative if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else "Negative" if neg > pos else "Neutral"
    mention_type = "Linked mention" if has_link else "Unlinked mention (link-building opportunity!)"
    action = "Monitor" if has_link else "Reach out to convert mention to a backlink"
    return (
        f"Brand: {brand_name}\nType: {mention_type}\n"
        f"Sentiment: {sentiment}\nAction: {action}"
    )


@beta_tool
def score_link_prospect(
    page_url: str, page_title: str, page_content_snippet: str, your_niche: str
) -> str:
    """Score a potential link-building prospect (0–100).

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
        your_niche: Your website's niche / topic keywords.
    """
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    text = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for w in niche_words if w in text)
    if relevance >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value = ["resource", "guide", "tools", "blog", "list", "best", "directory", "roundup"]
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
    return f"Score: {score}/100 – {priority}\nURL: {page_url}\n" + "\n".join(reasons)


@beta_tool
def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    your_site: str,
    your_content_url: str,
    link_type: str,
) -> str:
    """Generate a personalized outreach email for a link-building opportunity.

    Args:
        prospect_name: Name of the website owner or editor.
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link placed.
        your_site: Your website name.
        your_content_url: URL of your content to be linked.
        link_type: 'guest_post', 'broken_link', 'resource', or 'mention'.
    """
    t = {
        "broken_link": (
            f"Subject: Broken link found on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\nI came across a broken link on your {their_page_topic} "
            f"page at {prospect_site}. I have a comprehensive resource at {your_content_url} "
            f"that would make a perfect replacement.\n\nWould you consider swapping it in?\n\n"
            f"Best regards,\n[Your Name] – {your_site}"
        ),
        "guest_post": (
            f"Subject: Guest post idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\nI really enjoy your content about {their_page_topic} on "
            f"{prospect_site}. I'd love to contribute a guest article – I write for {your_site} "
            f"and cover topics your audience would find valuable.\n\nWould you be open to a "
            f"collaboration?\n\nBest regards,\n[Your Name] – {your_site}"
        ),
        "resource": (
            f"Subject: Useful resource for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\nYour {their_page_topic} resource page on {prospect_site} "
            f"is excellent! I recently published {your_content_url} which I think would be "
            f"a great addition for your readers.\n\nWould you take a look?\n\n"
            f"Best regards,\n[Your Name] – {your_site}"
        ),
        "mention": (
            f"Subject: Thank you for mentioning {your_site}!\n\n"
            f"Hi {prospect_name},\n\nThank you for mentioning {your_site} in your article "
            f"about {their_page_topic}! Would you be open to turning that mention into a "
            f"direct link to {your_content_url}? It would help your readers find us easily.\n\n"
            f"Thanks,\n[Your Name] – {your_site}"
        ),
    }
    return t.get(link_type, t["resource"])


@beta_tool
def identify_link_gap_opportunity(
    competitor_domain: str, your_domain: str, linking_page_topic: str
) -> str:
    """Identify whether a competitor backlink is an opportunity for your site.

    Args:
        competitor_domain: Competitor's domain.
        your_domain: Your domain.
        linking_page_topic: Topic of the page that links to the competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\nYour site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Action steps:\n"
        f"1. Identify the content on {competitor_domain} that earned this link.\n"
        f"2. Create better or more comprehensive content on {your_domain}.\n"
        f"3. Reach out to the linking page with your improved resource."
    )


@beta_tool
def track_outreach_contact(site_url: str, contact_type: str, status: str) -> str:
    """Record an outreach contact to prevent duplicate outreach.

    Args:
        site_url: The website URL contacted.
        contact_type: 'guest_post', 'resource', 'broken_link', or 'mention'.
        status: 'contacted', 'submitted', 'pending', 'accepted', or 'rejected'.
    """
    log = load_log()
    today = str(date.today())
    log["contacted_sites"].setdefault(site_url, [])
    log["contacted_sites"][site_url].append(
        {"date": today, "type": contact_type, "status": status}
    )
    save_log(log)
    return f"Tracked: {site_url} → {contact_type} → {status} on {today}"


@beta_tool
def check_already_contacted(site_url: str, days_threshold: int = 30) -> str:
    """Check whether a prospect was already contacted within the given window.

    Args:
        site_url: The website URL to check.
        days_threshold: Days to look back (default 30).
    """
    log = load_log()
    if site_url not in log["contacted_sites"]:
        return f"Never contacted – SAFE to reach out to {site_url}"
    cutoff = date.today() - timedelta(days=days_threshold)
    recent = [
        c for c in log["contacted_sites"][site_url]
        if date.fromisoformat(c["date"]) > cutoff
    ]
    if recent:
        last = recent[-1]
        return (
            f"Already contacted {site_url} on {last['date']} for {last['type']} – "
            f"SKIP (within {days_threshold}-day window)"
        )
    return f"Last contact was over {days_threshold} days ago – OK to re-engage {site_url}"


# ── Main runner ───────────────────────────────────────────────────────────────

def run_daily_backlink_builder() -> str:
    today = str(date.today())
    print(f"\n{'='*60}")
    print(f"  Daily Backlink Builder – {DOMAIN}")
    print(f"  Date: {today}")
    print(f"{'='*60}\n")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            track_outreach_contact,
            check_already_contacted,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO specialist. Today is {today}.
Your mission: find and document actionable backlink opportunities for {DOMAIN} (brand: "{BRAND_NAME}").

Niche: solar panels, LED display panels, electrical panels, home energy solutions.
Competitors to analyse: {', '.join(COMPETITORS)}

Complete ALL 6 tasks below. Use the provided tools throughout.

─────────────────────────────────────────────────────────────
TASK 1 – Brand Mention Mining
Search for "{BRAND_NAME}" and "alfaapanels" mentions across blogs, forums, news sites.
For each mention found, call categorize_brand_mention to classify it.
Prioritise unlinked mentions as link-building opportunities.

TASK 2 – Competitor Backlink Gap Analysis
For each competitor, search for recent content they earned links from.
Call identify_link_gap_opportunity for every actionable gap found.
Focus on: resource pages, roundups, "best solar panels" articles.

TASK 3 – Fresh Link Prospects
Run web searches for:
  • "solar panels" OR "LED panels" + "resources" OR "resource page"
  • "best solar panels" intitle:"resources" OR "best of"
  • "panels" + "write for us" OR "contribute" OR "guest post guidelines"
  • "panels" + "broken link" OR "dead link"
Score every prospect with score_link_prospect. Report only HIGH PRIORITY (70+) ones.

TASK 4 – Relevant Directory & Community Submissions
Search for high-quality directories and communities relevant to solar/panel industry:
  • Solar energy directories
  • Home improvement directories
  • B2B/trade directories
  • Reddit communities, forums, Q&A sites (Quora, Stack Exchange)
List the top 5 with submission URLs and note whether {DOMAIN} is already listed.

TASK 5 – Outreach Email Templates
For the top 5 prospects identified in Tasks 1–4, generate personalised outreach templates
using generate_outreach_template. Use the correct link_type for each case.
Before generating, call check_already_contacted to verify the site has not been approached recently.
After generating each template, call track_outreach_contact to log the prospect.

TASK 6 – Today's Priority Action Plan
Produce a numbered list of exactly 5 concrete actions to take TODAY to build backlinks for {DOMAIN}.
Each action must include: the specific URL to target, what to do, and the expected backlink type.
─────────────────────────────────────────────────────────────

Format the complete report with clear headings for each task."""
        }],
    )

    report_parts = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_parts.append(block.text)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_file = os.path.join(REPORTS_DIR, f"backlink_report_{today}.md")
    with open(report_file, "w") as f:
        f.write(f"# Daily Backlink Report: {DOMAIN}\n\n")
        f.write(f"**Date:** {today}  \n**Niche:** {NICHE}\n\n---\n\n")
        f.write("\n\n".join(report_parts))

    log = load_log()
    log["daily_summaries"].append({"date": today, "report": report_file})
    save_log(log)

    print(f"\nReport saved → {report_file}")
    return report_file


if __name__ == "__main__":
    run_daily_backlink_builder()
