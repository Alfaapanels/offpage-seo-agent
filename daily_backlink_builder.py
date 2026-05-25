"""
Daily backlink builder for alfaapanels.com.
Finds and logs fresh link-building opportunities every day using Claude AI.
"""

import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

import anthropic
from anthropic import beta_tool

# ── Site configuration ────────────────────────────────────────────────────────
SITE = {
    "domain": "alfaapanels.com",
    "brand": "Alfa Panels",
    "niche": "aluminum composite panels building materials cladding facades",
    "description": (
        "Alfa Panels manufactures and supplies high-quality aluminum composite panels (ACP) "
        "used in building facades, cladding, signage, and interior design."
    ),
    "target_keywords": [
        "aluminum composite panels",
        "ACP cladding",
        "building facade panels",
        "aluminium cladding",
        "composite cladding panels",
        "exterior wall panels",
        "ACP sheet",
        "architectural cladding",
    ],
    "competitors": ["alucobond.com", "reynobond.com", "alpolic.com", "alucoil.com"],
    "pages": {
        "home": "https://alfaapanels.com",
        "products": "https://alfaapanels.com/products",
        "contact": "https://alfaapanels.com/contact",
    },
}

LOG_FILE = Path("backlink_log.json")
REPORTS_DIR = Path("daily_reports")

# ── Backlink tracking ─────────────────────────────────────────────────────────

def load_log() -> dict:
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            return json.load(f)
    return {"opportunities": [], "completed": [], "daily_runs": []}


def save_log(log: dict) -> None:
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def already_logged(log: dict, url: str) -> bool:
    all_urls = [e.get("url", "") for e in log["opportunities"] + log["completed"]]
    return url in all_urls


# ── Claude tools ──────────────────────────────────────────────────────────────

@beta_tool
def log_backlink_opportunity(
    url: str,
    opportunity_type: str,
    relevance_score: int,
    action_required: str,
    anchor_text_suggestion: str,
    notes: str,
) -> str:
    """Record a discovered backlink opportunity.

    Args:
        url: URL of the page / site where a backlink can be obtained.
        opportunity_type: One of: directory, forum, qa_site, guest_post, resource_page,
            broken_link, brand_mention, social_bookmark, comment, niche_citation.
        relevance_score: Relevance to alfaapanels.com niche, 1-10.
        action_required: Short description of what needs to be done.
        anchor_text_suggestion: Suggested anchor text for the backlink.
        notes: Any extra notes (contact info, submission guidelines, etc.).
    """
    log = load_log()
    today = str(date.today())
    entry = {
        "date_found": today,
        "url": url,
        "type": opportunity_type,
        "relevance_score": relevance_score,
        "action_required": action_required,
        "anchor_text_suggestion": anchor_text_suggestion,
        "notes": notes,
        "status": "pending",
    }
    if not already_logged(log, url):
        log["opportunities"].append(entry)
        save_log(log)
        return f"✓ Logged: {url} [{opportunity_type}] score={relevance_score}"
    return f"⚠ Already in log: {url}"


@beta_tool
def score_link_prospect(
    page_url: str,
    page_title: str,
    page_content_snippet: str,
) -> str:
    """Score a potential link-building prospect for alfaapanels.com.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
    """
    score = 0
    reasons = []
    niche_words = SITE["niche"].split()
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for word in niche_words if word in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append(f"High niche relevance ({relevance} keyword hits) +40")
    elif relevance >= 1:
        score += 20
        reasons.append(f"Moderate relevance ({relevance} keyword hits) +20")
    else:
        reasons.append("Low relevance +0")
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "directory"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide/directory page +30")
    if any(s in page_url for s in [".edu", ".gov", ".org"]):
        score += 30
        reasons.append("High-authority domain (.edu/.gov/.org) +30")
    else:
        score += 10
        reasons.append("Standard domain +10")
    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 [{priority}]\n" + "\n".join(f"  - {r}" for r in reasons)


@beta_tool
def generate_outreach_email(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    link_type: str,
    target_page_url: str,
) -> str:
    """Generate a personalized outreach email for alfaapanels.com.

    Args:
        prospect_name: Name of the website owner / editor (use 'Team' if unknown).
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        link_type: One of: guest_post, broken_link, resource, mention.
        target_page_url: The alfaapanels.com URL to promote.
    """
    brand = SITE["brand"]
    domain = SITE["domain"]
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your article on {their_page_topic} at {prospect_site} and noticed a broken link "
            f"that might be frustrating your readers.\n\n"
            f"I have a detailed resource on {their_page_topic} at {target_page_url} that would be a "
            f"perfect replacement and add value to your page.\n\n"
            f"Would you be open to updating that link?\n\n"
            f"Best regards,\n[Your Name]\n{brand} – {domain}"
        ),
        "guest_post": (
            f"Subject: Guest Post Pitch for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following {prospect_site}'s content on {their_page_topic} and I think your audience "
            f"would love an in-depth piece on aluminum composite panels and modern facade solutions.\n\n"
            f"I'm from {brand} ({domain}) and I'd love to contribute a high-quality, original article. "
            f"No self-promotion — just genuinely useful content for your readers.\n\n"
            f"Would you be open to a collaboration?\n\n"
            f"Best,\n[Your Name]\n{brand}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is really well done! I think your readers would "
            f"also benefit from our guide at {target_page_url} — it covers {their_page_topic} from a "
            f"manufacturer's perspective with specs, installation tips, and case studies.\n\n"
            f"Would you consider adding it to your list?\n\n"
            f"Best,\n[Your Name]\n{brand} – {domain}"
        ),
        "mention": (
            f"Subject: {brand} mention – would you add a link?\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {brand} in your article about {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {target_page_url}? It would help your readers "
            f"find the product information quickly.\n\n"
            f"Thanks so much,\n[Your Name]\n{brand} – {domain}"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def get_daily_targets() -> str:
    """Return today's focused backlink-building targets for alfaapanels.com."""
    today = date.today()
    # Rotate targets by day-of-week so each run covers different channels
    weekly_rotation = {
        0: "business_directories",    # Monday
        1: "qa_and_forums",           # Tuesday
        2: "resource_pages",          # Wednesday
        3: "guest_post_prospects",    # Thursday
        4: "broken_link_building",    # Friday
        5: "brand_mentions",          # Saturday
        6: "niche_citations",         # Sunday
    }
    day_focus = weekly_rotation[today.weekday()]
    log = load_log()
    pending = len([e for e in log["opportunities"] if e["status"] == "pending"])
    completed = len(log["completed"])
    return (
        f"Today ({today}, {today.strftime('%A')}) focus: {day_focus}\n"
        f"Pending opportunities in log: {pending}\n"
        f"Completed backlinks: {completed}\n\n"
        f"Target: find 5–10 NEW {day_focus} opportunities for alfaapanels.com today."
    )


# ── Main agent runner ─────────────────────────────────────────────────────────

def run_daily_backlink_builder() -> None:
    today = str(date.today())
    print(f"\n{'='*60}")
    print(f"  Daily Backlink Builder – alfaapanels.com – {today}")
    print(f"{'='*60}\n")

    REPORTS_DIR.mkdir(exist_ok=True)
    client = anthropic.Anthropic()

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            get_daily_targets,
            log_backlink_opportunity,
            score_link_prospect,
            generate_outreach_email,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO specialist building high-quality backlinks for alfaapanels.com every day.

Site details:
- Domain: {SITE['domain']}
- Brand: {SITE['brand']}
- Description: {SITE['description']}
- Target keywords: {', '.join(SITE['target_keywords'])}
- Competitors: {', '.join(SITE['competitors'])}

TODAY'S MISSION — follow these steps in order:

STEP 1 – Get today's targets
Call get_daily_targets() to see what channel to focus on today and how many opportunities are already logged.

STEP 2 – Research & discover opportunities
Based on today's focus channel, use web_search and web_fetch to find REAL, specific websites, directories, forums, Q&A threads, and resource pages where a backlink to alfaapanels.com would be:
  a) Relevant (building materials, construction, architecture, facades, cladding, aluminum panels)
  b) Achievable (you can submit, comment, register, or pitch)
  c) Valuable (genuine audience, not spam)

Search strategies by channel:
- business_directories: Search for "building materials directory submit site" OR "construction company directory free listing" OR "aluminum panel manufacturers directory"
- qa_and_forums: Search for unanswered questions about "aluminum composite panels", "ACP cladding", "facade cladding options" on Quora, Reddit, forums
- resource_pages: Search for intitle:"resources" OR intitle:"useful links" construction facade cladding architecture
- guest_post_prospects: Search for "write for us" OR "guest post" construction architecture building materials
- broken_link_building: Search for resource pages on cladding/facade topics; check for dead links
- brand_mentions: Search for "Alfa Panels" -site:alfaapanels.com to find unlinked mentions
- niche_citations: Search for niche-specific local or industry citations for panel manufacturers

STEP 3 – Score and log opportunities
For each promising opportunity (aim for 5–10 today):
  a) Call score_link_prospect() to evaluate it
  b) If score >= 40 (MEDIUM or HIGH), call log_backlink_opportunity() to record it
  c) If it needs outreach, call generate_outreach_email() and include the email in your notes

STEP 4 – Final summary
Write a clear markdown summary of:
  1. What you found today (list each opportunity with URL, type, score, and action needed)
  2. Top 3 highest-priority opportunities with step-by-step instructions to get the link
  3. Any outreach emails drafted
  4. Running total of logged opportunities

Be specific — real URLs, real anchor text suggestions, real action steps. No vague advice.
""",
        }],
    )

    report_sections = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_sections.append(block.text)

    # Save daily report
    report_path = REPORTS_DIR / f"backlinks_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report – alfaapanels.com – {today}\n\n")
        f.write("\n\n".join(report_sections))
    print(f"\n✓ Report saved: {report_path}")

    # Record run in log
    log = load_log()
    log["daily_runs"].append({
        "date": today,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "report": str(report_path),
        "opportunities_found": len([e for e in log["opportunities"] if e["date_found"] == today]),
    })
    save_log(log)
    print(f"✓ Log updated: {LOG_FILE}")


if __name__ == "__main__":
    run_daily_backlink_builder()
