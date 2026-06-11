"""
Daily Backlink Builder for alfaapanels.com
Runs each day to discover, score, and generate outreach for new backlink opportunities.
"""

import anthropic
import json
import os
from datetime import datetime
from anthropic import beta_tool

# ── Site configuration ────────────────────────────────────────────────────────
CONFIG = {
    "domain": "alfaapanels.com",
    "brand_name": "Alfa Panels",
    "niche": "aluminum composite panels ACP cladding facade building materials",
    "contact_email": "info@alfaapanels.com",
    "competitors": [
        "alucobond.com",
        "reynobond.com",
        "alpolic.com",
        "alucobondusa.com",
        "3acm.com",
    ],
    "target_keywords": [
        "aluminum composite panel",
        "ACP cladding",
        "facade panels",
        "building cladding",
        "exterior wall panels",
        "composite panel supplier",
        "ACP sheet",
        "aluminium composite material",
    ],
    "content_pages": [
        "https://alfaapanels.com/products",
        "https://alfaapanels.com/gallery",
        "https://alfaapanels.com/contact",
    ],
}

# ── Tools ─────────────────────────────────────────────────────────────────────

@beta_tool
def score_link_prospect(page_url: str, page_title: str, page_content_snippet: str, your_niche: str) -> str:
    """Score a potential link building prospect on a 0-100 scale.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
        your_niche: Your website's niche/topic keywords.
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
        reasons.append("Low relevance (0)")

    resource_signals = ["resource", "guide", "tools", "best", "list", "directory", "supplier", "manufacturer"]
    if any(t in page_url.lower() or t in page_title.lower() for t in resource_signals):
        score += 30
        reasons.append("Resource/directory page (+30)")

    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High-authority domain (.edu/.gov/.org) (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")

    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 [{priority}]\nURL: {page_url}\n" + "\n".join(f"  • {r}" for r in reasons)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorise a brand mention as linked/unlinked and determine sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "quality", "durable", "reliable", "professional"]
    negative_words = ["bad", "poor", "avoid", "scam", "terrible", "cheap", "low quality"]

    pos = sum(1 for w in positive_words if w in mention_text.lower())
    neg = sum(1 for w in negative_words if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else "Negative" if neg > pos else "Neutral"

    mention_type = "Linked mention" if has_link else "Unlinked mention — LINK OPPORTUNITY"
    action = "Monitor & engage" if has_link else "Contact site owner to add link to alfaapanels.com"
    return f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\nAction: {action}"


@beta_tool
def generate_outreach_email(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    link_type: str,
    target_url: str,
) -> str:
    """Generate a personalised outreach email for a backlink opportunity.

    Args:
        prospect_name: Contact name or 'the team' if unknown.
        prospect_site: Their website domain or name.
        their_page_topic: Topic/title of the page where you want the link.
        link_type: One of: broken_link | guest_post | resource | mention | directory.
        target_url: The alfaapanels.com URL you want them to link to.
    """
    sender = "The Alfa Panels Team"
    templates = {
        "broken_link": (
            f"Subject: Broken link found on your '{their_page_topic}' page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your page on {their_page_topic} at {prospect_site} and noticed one of the linked resources is returning a 404 error.\n\n"
            f"We maintain a comprehensive guide on aluminum composite panels and ACP cladding solutions at:\n{target_url}\n\n"
            f"It covers the same topic and might serve as a useful replacement for your readers.\n\n"
            f"Would you be open to updating that link?\n\nBest regards,\n{sender}\nalfaapanels.com"
        ),
        "guest_post": (
            f"Subject: Guest article idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following {prospect_site}'s content on {their_page_topic} — great work!\n\n"
            f"I'm from Alfa Panels (alfaapanels.com), a specialist manufacturer of aluminum composite panels. "
            f"I'd love to contribute a practical guest article — for example:\n\n"
            f"  • 'How to Choose the Right ACP Cladding for Commercial Buildings'\n"
            f"  • '5 Mistakes to Avoid When Installing Facade Panels'\n"
            f"  • 'ACP vs. Other Cladding Materials: A Contractor's Guide'\n\n"
            f"Happy to tailor a topic that fits your audience. Interested?\n\nBest,\n{sender}\nalfaapanels.com"
        ),
        "resource": (
            f"Subject: Resource suggestion for your '{their_page_topic}' page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is really helpful — I bookmarked it!\n\n"
            f"I wanted to suggest one more resource that might benefit your readers:\n{target_url}\n\n"
            f"It's a detailed guide from Alfa Panels covering aluminum composite panel specifications, installation tips, and supplier comparisons.\n\n"
            f"Would you consider adding it to your list?\n\nThanks,\n{sender}\nalfaapanels.com"
        ),
        "mention": (
            f"Subject: Thanks for mentioning Alfa Panels!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning Alfa Panels in your article about {their_page_topic} on {prospect_site}!\n\n"
            f"Would you be open to linking directly to our page so your readers can explore our products?\n{target_url}\n\n"
            f"Happy to return the favour — let us know if there's anything we can help with.\n\nWarm regards,\n{sender}\nalfaapanels.com"
        ),
        "directory": (
            f"Subject: Alfa Panels — submission for your building materials directory\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'd like to submit Alfa Panels for inclusion in your {their_page_topic} directory.\n\n"
            f"About us:\n"
            f"  • Specialist manufacturer of aluminum composite panels (ACP)\n"
            f"  • Products: facade cladding, interior panels, signage panels\n"
            f"  • Website: alfaapanels.com\n"
            f"  • Contact: info@alfaapanels.com\n\n"
            f"Please let me know if you need any additional information.\n\nBest,\n{sender}\nalfaapanels.com"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def log_backlink_opportunity(
    opportunity_type: str,
    target_url: str,
    prospect_url: str,
    score: int,
    notes: str,
) -> str:
    """Log a discovered backlink opportunity to the daily tracker.

    Args:
        opportunity_type: Category e.g. broken_link, guest_post, resource, mention, directory, forum.
        target_url: The alfaapanels.com URL to promote.
        prospect_url: URL of the site/page to reach out to.
        score: Priority score 0-100.
        notes: Any relevant notes or context.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = f"opportunities_{today}.jsonl"
    entry = {
        "date": today,
        "type": opportunity_type,
        "target_url": target_url,
        "prospect_url": prospect_url,
        "score": score,
        "notes": notes,
        "status": "discovered",
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return f"Logged [{opportunity_type}] score={score}: {prospect_url} → {target_url}"


@beta_tool
def analyze_backlink_quality(backlink_url: str, anchor_text: str) -> str:
    """Evaluate the quality of an existing or potential backlink.

    Args:
        backlink_url: The URL linking to alfaapanels.com.
        anchor_text: The anchor text used in the link.
    """
    signals = []
    generic_anchors = ["click here", "website", "here", "link", "read more", "visit"]
    if anchor_text.lower() in generic_anchors:
        signals.append("Weak anchor text — low SEO value")
    else:
        signals.append(f"Good descriptive anchor: '{anchor_text}'")

    spam_signals = ["casino", "viagra", "porn", "loan", "forex", "crypto-pump"]
    if any(s in backlink_url.lower() for s in spam_signals):
        signals.append("TOXIC — add to disavow file")
    else:
        signals.append("Domain appears clean")

    industry_signals = ["construction", "building", "architecture", "facade", "cladding", "panel", "material"]
    if any(s in backlink_url.lower() for s in industry_signals):
        signals.append("Industry-relevant domain — high value")

    return "\n".join(f"• {s}" for s in signals)


# ── Agent runner ──────────────────────────────────────────────────────────────

DAILY_PROMPT = """You are a senior link-building specialist working exclusively for alfaapanels.com.

Today's date: {today}
Domain: {domain}
Brand: {brand_name}
Niche: {niche}
Competitors: {competitors}
Contact email: {contact_email}

Your mission today is to find real, actionable backlink opportunities and produce outreach-ready emails.

──────────────────────────────────────────
TASK 1 — UNLINKED BRAND MENTION HUNT
──────────────────────────────────────────
Use web_search to find mentions of "Alfa Panels" OR "alfaapanels.com" that are NOT on alfaapanels.com itself.
Search query: "Alfa Panels" OR "alfaapanels.com" -site:alfaapanels.com

For each mention found:
1. Use categorize_brand_mention to classify it
2. If unlinked → use generate_outreach_email (link_type="mention") to create the email
3. Use log_backlink_opportunity to save it

──────────────────────────────────────────
TASK 2 — COMPETITOR BACKLINK GAP ANALYSIS
──────────────────────────────────────────
For each competitor, search for sites that link to them and could also link to alfaapanels.com.
Search queries like: link:alucobond.com site:construction OR link:reynobond.com architecture

For each gap found:
1. Use score_link_prospect to score it
2. Use generate_outreach_email with the most appropriate link_type
3. Use log_backlink_opportunity

──────────────────────────────────────────
TASK 3 — RESOURCE PAGE LINK BUILDING
──────────────────────────────────────────
Search for resource pages that list cladding, facade, or building material suppliers:
Queries: "aluminum composite panel" + "resources" OR "suppliers" OR "directory"
         "ACP cladding" + "resources" site:.org OR site:.edu
         "building materials" + "supplier list" OR "vendor directory"

For each relevant resource page:
1. Score it with score_link_prospect
2. Generate a resource outreach email
3. Log it

──────────────────────────────────────────
TASK 4 — BROKEN LINK BUILDING
──────────────────────────────────────────
Search for pages about ACP/facade panels that may have dead links:
Query: "aluminum composite panel" OR "ACP cladding" "404" OR "broken link" OR "page not found"

Also check competitor pages that might have been taken down:
For each broken link opportunity → generate_outreach_email (link_type="broken_link") and log it.

──────────────────────────────────────────
TASK 5 — GUEST POST PROSPECTING
──────────────────────────────────────────
Find construction, architecture, and building materials blogs that accept guest posts:
Queries: "write for us" + "construction" OR "architecture" OR "building materials"
         "guest post" + "facade" OR "cladding" OR "aluminum panels"
         "submit article" + "construction industry"

For each prospect:
1. Score it
2. Generate a guest post pitch email
3. Log it

──────────────────────────────────────────
TASK 6 — INDUSTRY DIRECTORY SUBMISSIONS
──────────────────────────────────────────
Find niche directories for manufacturers, building suppliers, and construction companies:
Queries: "building materials directory" site:.org OR site:.com submit
         "manufacturer directory" aluminum composite
         "construction supplier" directory listing

For each directory:
1. Score it
2. Generate a directory submission email
3. Log it

──────────────────────────────────────────
TASK 7 — FORUM & COMMUNITY OPPORTUNITIES
──────────────────────────────────────────
Find active forums and communities discussing ACP/cladding where alfaapanels.com could be referenced:
Queries: "aluminum composite panel" site:reddit.com OR site:quora.com OR site:stackexchange.com
         "ACP cladding" forum discussion

For each community thread:
1. Identify the question/discussion
2. Log the opportunity with notes on how to contribute

──────────────────────────────────────────
TASK 8 — DAILY REPORT
──────────────────────────────────────────
Produce a clean markdown report:

# Daily Backlink Report — {today}

## Summary
- Total opportunities found: X
- High priority (score 70+): X
- Medium priority (40-69): X
- Low priority (<40): X

## Top 5 Action Items (do these today)
Ranked by score, with the outreach email copy included for each.

## All Opportunities by Category
List every opportunity with URL, type, score, and next step.

## Outreach Emails Ready to Send
Include the full email copy for every HIGH priority opportunity.

## Tomorrow's Focus
Suggest the 2-3 most promising follow-up searches for tomorrow.
"""


def run_daily_builder():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*60}")
    print(f"  Daily Backlink Builder — alfaapanels.com")
    print(f"  Date: {today}")
    print(f"{'='*60}\n")

    client = anthropic.Anthropic()

    prompt = DAILY_PROMPT.format(
        today=today,
        domain=CONFIG["domain"],
        brand_name=CONFIG["brand_name"],
        niche=CONFIG["niche"],
        competitors=", ".join(CONFIG["competitors"]),
        contact_email=CONFIG["contact_email"],
    )

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_email,
            log_backlink_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{"role": "user", "content": prompt}],
    )

    report_sections = []
    print("Running agent...\n")

    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_sections.append(block.text)

    # Save full markdown report
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"backlink_report_{today}.md")
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report — alfaapanels.com — {today}\n\n")
        f.write("\n\n".join(report_sections))

    print(f"\n{'='*60}")
    print(f"  Report saved: {report_path}")

    # Also update opportunities log summary
    opp_file = f"opportunities_{today}.jsonl"
    if os.path.exists(opp_file):
        with open(opp_file) as f:
            lines = f.readlines()
        print(f"  Opportunities logged: {len(lines)}")

        # Move to reports dir
        import shutil
        shutil.move(opp_file, os.path.join(report_dir, opp_file))

    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_daily_builder()
