#!/usr/bin/env python3
"""Daily backlink builder for alfaapanels.com — run this script every day."""

import json
from datetime import date
from pathlib import Path

import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()

DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
TRACKING_FILE = "backlink_tracking.json"
REPORTS_DIR = Path("daily_reports")


def load_tracking() -> dict:
    if Path(TRACKING_FILE).exists():
        with open(TRACKING_FILE) as f:
            return json.load(f)
    return {"submitted": [], "contacted": [], "pending": []}


def save_tracking(data: dict) -> None:
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f, indent=2)


@beta_tool
def score_link_prospect(
    page_url: str,
    page_title: str,
    page_content_snippet: str,
    niche: str,
) -> str:
    """Score a potential link building prospect on relevance and authority.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
        niche: Space-separated keywords describing the niche.
    """
    score = 0
    reasons = []
    niche_words = niche.lower().split()
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for word in niche_words if word in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low relevance (+0)")
    high_value = ["resource", "guide", "tools", "blog", "list", "best", "directory", "submit", "add"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("High-value page type (+30)")
    if any(s in page_url for s in [".edu", ".gov", ".org"]):
        score += 30
        reasons.append("High-authority domain (.edu/.gov/.org) (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 [{priority}]\nURL: {page_url}\n" + "\n".join(f"  {r}" for r in reasons)


@beta_tool
def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    topic: str,
    link_type: str,
    target_url: str,
) -> str:
    """Generate outreach email or submission content for a backlink opportunity.

    Args:
        prospect_name: Contact name or generic 'Editor'/'Team'.
        prospect_site: Their website name or URL.
        topic: The relevant topic or page subject.
        link_type: One of: guest_post, broken_link, resource, directory, forum, qa.
        target_url: The alfaapanels.com URL to link to.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I noticed a broken link on your {topic} page at {prospect_site}.\n"
            f"Our page at {target_url} covers this topic well and would serve as a great replacement.\n\n"
            f"Hope this helps your readers!\n\nBest,\n[Your Name] — {BRAND_NAME}"
        ),
        "guest_post": (
            f"Subject: Guest Post Idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I really enjoy your content on {topic} at {prospect_site}.\n"
            f"I represent {BRAND_NAME} ({DOMAIN}) and would love to contribute a guest article on this topic.\n\n"
            f"Would you be open to a collaboration?\n\nBest,\n[Your Name] — {BRAND_NAME}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your {topic} resource page is excellent! We created {target_url} which your readers might find valuable.\n\n"
            f"Would it be worth adding? Best,\n[Your Name] — {BRAND_NAME}"
        ),
        "directory": (
            f"Directory Submission — {BRAND_NAME}\n"
            f"Site URL: https://{DOMAIN}\n"
            f"Category: {topic}\n"
            f"Listing URL: {target_url}\n"
            f"Business Name: {BRAND_NAME}\n"
            f"Description: [Write a 150-word description of {BRAND_NAME}'s products/services here]"
        ),
        "forum": (
            f"Forum Participation Plan\n"
            f"Platform: {prospect_site}\n"
            f"Topic/Thread: {topic}\n"
            f"Strategy: Provide a genuinely helpful answer. Reference {BRAND_NAME} only when directly relevant.\n"
            f"Link to: {target_url} only if it adds real value to the discussion."
        ),
        "qa": (
            f"Q&A Response Draft\n"
            f"Platform: {prospect_site}\n"
            f"Question: {topic}\n"
            f"Response: [Provide a comprehensive, helpful answer]\n"
            f"Closing: For more information on this topic, see {target_url}"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def record_opportunity(
    url: str,
    opportunity_type: str,
    priority: str,
    action: str,
) -> str:
    """Record a new backlink opportunity in the tracking system.

    Args:
        url: The URL of the opportunity.
        opportunity_type: One of: directory, forum, qa, guest_post, resource, broken_link.
        priority: One of: high, medium, low.
        action: Brief description of the action to take (e.g., 'Submit listing', 'Answer question').
    """
    tracking = load_tracking()
    today = date.today().isoformat()
    entry = {
        "url": url,
        "type": opportunity_type,
        "priority": priority,
        "action": action,
        "date": today,
    }
    all_tracked_urls = {t["url"] for cat in tracking.values() for t in cat}
    if url in all_tracked_urls:
        return f"Already tracked: {url}"
    tracking["pending"].append(entry)
    save_tracking(tracking)
    return f"Recorded [{priority.upper()}] {opportunity_type}: {url} — {action}"


@beta_tool
def get_tracked_urls() -> str:
    """Get previously tracked URLs to avoid researching duplicates.

    Returns a summary of already-found opportunities.
    """
    tracking = load_tracking()
    all_entries = [e for cat in tracking.values() for e in cat]
    if not all_entries:
        return "No URLs tracked yet — this is the first run!"
    recent = sorted(all_entries, key=lambda x: x.get("date", ""), reverse=True)[:100]
    url_list = "\n".join(f"  [{e['type']}] {e['url']}" for e in recent)
    return f"Already tracked {len(all_entries)} total opportunities. Recent 100:\n{url_list}"


def run_daily() -> None:
    today = date.today().isoformat()
    REPORTS_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Daily Backlink Builder — {DOMAIN}")
    print(f"Date: {today}")
    print("=" * 60)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        tools=[
            score_link_prospect,
            generate_outreach_template,
            record_opportunity,
            get_tracked_urls,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO specialist. Your mission today is to
find and document RELEVANT, high-quality backlink opportunities for {DOMAIN} (brand: {BRAND_NAME}).

Today's date: {today}

Work through these steps systematically:

## STEP 1 — Understand the site
Search for "{BRAND_NAME}" and fetch https://{DOMAIN} to learn:
- Products and services offered
- Target audience and industry
- Key pages that deserve backlinks
- Main keywords/niche

## STEP 2 — Check what's already tracked
Call get_tracked_urls now to avoid researching duplicate URLs.

## STEP 3 — Find 15+ NEW backlink opportunities today

### A. Business Directories (5+ new entries)
Search: "[niche] business directory" OR "[niche] add listing" OR "[niche] submit site"
Look for: industry associations, niche portals, local/regional directories, professional registries
Score each with score_link_prospect.

### B. Q&A Opportunities (3+ new)
Search: site:quora.com "[niche topic]"
Search: site:reddit.com "[niche] [product type]"
Find recent unanswered or under-answered questions where {BRAND_NAME} could help.

### C. Resource & Link Pages (3+ new)
Search: "[niche] resources" OR "[niche] tools" intitle:resources -site:{DOMAIN}
Search: "best [niche] companies" OR "[niche] suppliers list"
Find pages that list companies/resources in the niche.

### D. Forum Communities (2+ new)
Search: "[niche] forum" OR "[niche] community" OR "[niche] discussion board"
Find active communities where participation adds genuine value.

### E. Guest Post Opportunities (2+ new)
Search: "[niche] write for us" OR "[niche] guest post" OR "[niche] contribute article"
Look for relevant blogs actively accepting contributors.

## STEP 4 — Process each opportunity
For every opportunity found:
1. Use score_link_prospect to evaluate quality
2. Use generate_outreach_template for HIGH priority ones
3. Use record_opportunity to log every find

## STEP 5 — Compile the Daily Action Plan
Write a clear, prioritized plan:

### DO TODAY (High Priority — 3-5 items)
Specific URLs with exact instructions for immediate action.

### THIS WEEK (Medium Priority — 5-8 items)
Opportunities to pursue over the next few days.

### BACKLOG (Low Priority)
Remaining opportunities for future consideration.

Be thorough. Use real URLs. Every item must be immediately actionable.""",
        }],
    )

    report_parts = []
    for message in runner:
        for block in message.content:
            if block.type == "text" and block.text:
                print(block.text)
                report_parts.append(block.text)

    report_path = REPORTS_DIR / f"backlinks_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report — {DOMAIN}\n\n**Date:** {today}\n\n")
        f.write("\n\n".join(report_parts))

    tracking = load_tracking()
    total = sum(len(v) for v in tracking.values())
    print(f"\n{'='*60}")
    print(f"Report saved: {report_path}")
    print(
        f"Tracking: {total} total | "
        f"{len(tracking['submitted'])} submitted | "
        f"{len(tracking['pending'])} pending | "
        f"{len(tracking['contacted'])} contacted"
    )
    print("=" * 60)


if __name__ == "__main__":
    run_daily()
