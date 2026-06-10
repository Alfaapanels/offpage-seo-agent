import anthropic
import json
from datetime import datetime
from anthropic import beta_tool

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
        f"Brand: {brand_name}\n"
        f"Type: {mention_type}\n"
        f"Sentiment: {sentiment}\n"
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
            f"Subject: You mentioned {your_site} — thank you!\n\n"
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
        f"Competitor: {competitor_domain}\n"
        f"Your site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Actions:\n"
        f"1. Find what content earned {competitor_domain} this link\n"
        f"2. Create better content on the same topic for {your_domain}\n"
        f"3. Reach out to the linking page with your resource"
    )


@beta_tool
def track_prospect(domain: str, page_url: str, contact_email: str, link_type: str, notes: str) -> str:
    """Save a new link building prospect to the persistent tracking database.

    Args:
        domain: The prospect's domain.
        page_url: The specific page URL where we want a link.
        contact_email: Contact email if found, or 'unknown'.
        link_type: Type: 'guest_post', 'broken_link', 'resource', 'mention'.
        notes: Any relevant notes about this prospect.
    """
    db_path = "prospects_db.json"
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        with open(db_path, "r") as f:
            db = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        db = {"prospects": [], "total_found": 0}

    existing = [p for p in db["prospects"] if p.get("page_url") == page_url]
    if existing:
        return f"Already tracked: {page_url} (first seen {existing[0]['date_found']})"

    db["prospects"].append({
        "domain": domain,
        "page_url": page_url,
        "contact_email": contact_email,
        "link_type": link_type,
        "notes": notes,
        "date_found": today,
        "status": "new",
    })
    db["total_found"] = len(db["prospects"])

    with open(db_path, "w") as f:
        json.dump(db, f, indent=2)

    return f"New prospect tracked: {page_url} | Type: {link_type} | Date: {today}"


@beta_tool
def get_tracked_prospects(status_filter: str) -> str:
    """Retrieve previously tracked prospects to avoid chasing the same sites twice.

    Args:
        status_filter: 'all', 'new', 'contacted', or 'converted'.
    """
    db_path = "prospects_db.json"
    try:
        with open(db_path, "r") as f:
            db = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return "No prospects tracked yet — this is a fresh start!"

    prospects = db.get("prospects", [])
    if status_filter != "all":
        prospects = [p for p in prospects if p.get("status") == status_filter]

    if not prospects:
        return f"No prospects with status '{status_filter}'."

    lines = [f"Total in database: {db.get('total_found', len(prospects))} prospects\n"]
    for p in prospects[-30:]:
        lines.append(
            f"- {p['domain']} | {p['link_type']} | {p.get('status', 'new')} | found: {p['date_found']}"
        )
    return "\n".join(lines)


def run_offpage_seo_agent(
    your_domain: str = "alfaapanels.com",
    brand_name: str = "Alfa Panels",
    niche: str = "aluminum composite panels building facade cladding architectural",
    competitors: list = None,
):
    if competitors is None:
        competitors = ["alucobond.com", "reynobond.com", "alpolic.com", "dibond.com"]

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n[{today}] Starting Daily Off-Page SEO Agent for: {your_domain}\n")
    print("=" * 60)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            track_prospect,
            get_tracked_prospects,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO strategist running the DAILY backlink building routine for {your_domain}.

Today's date: {today}
Domain: {your_domain}
Brand: {brand_name}
Niche: {niche} (building materials, architectural panels, wall cladding, facade systems)
Competitors: {', '.join(competitors)}

STEP 0 — Check Existing Database
Call get_tracked_prospects("all") first. Do NOT pursue already-tracked prospects today — only find NEW ones.

TASK 1 — Brand Mention Audit
Search for unlinked brand mentions:
  • web_search: "{brand_name}" -site:{your_domain}
  • web_search: "alfaapanels" panels review OR mentioned
For each mention found, call categorize_brand_mention and track new opportunities with track_prospect.

TASK 2 — Competitor Backlink Gap Research
For each competitor, find sites that link to them but not to {your_domain}:
  • web_search: "recommended {competitors[0]}" building facade
  • web_search: site linking to aluminum composite panels supplier
Call identify_link_gap_opportunity for each gap, then track_prospect for new ones.

TASK 3 — Fresh Daily Link Opportunities (core task)
Run these targeted searches to find NEW link prospects:
  • "best aluminum composite panels" guide OR resource
  • "aluminum cladding" blog OR resource page
  • "building facade materials" list site:.org OR site:.edu
  • "ACP panels" supplier review OR directory
  • construction architecture blog "write for us" OR "guest post"
  • "wall cladding" buying guide
For each result, call score_link_prospect. Track any HIGH or MEDIUM priority prospects with track_prospect.

TASK 4 — Outreach Templates
For the top 3 NEW prospects found today, call generate_outreach_template with appropriate link_type (guest_post / broken_link / resource / mention).

TASK 5 — Daily Summary Report
Write a clear summary with:
1. New prospects found today (count + list)
2. Top 3 actionable outreach emails
3. Unlinked brand mentions to follow up
4. Best competitor backlink gap to pursue this week
5. One recommended action for tomorrow""",
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_filename = f"seo_report_{your_domain.replace('.', '_')}_{today}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Daily Off-Page SEO Report: {your_domain}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(full_report))
    print(f"\nReport saved to: {report_filename}")
    return report_filename


if __name__ == "__main__":
    run_offpage_seo_agent()
