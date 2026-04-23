"""
Daily Backlink Builder for alfaapanels.com
Runs every day to find and build relevant backlinks.
"""

import anthropic
import json
import os
from datetime import date, datetime
from anthropic import beta_tool

# ── Site config ──────────────────────────────────────────────────────────────
TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "SMM panel social media marketing services buy followers likes views"
COMPETITORS = [
    "smmking.com",
    "peakerr.com",
    "justanotherpanel.com",
    "smmhut.com",
    "crescitaly.com",
]
ACTIVITY_LOG = "backlink_activity_log.json"

client = anthropic.Anthropic()


# ── Persistence helpers ───────────────────────────────────────────────────────

def load_activity_log() -> dict:
    if os.path.exists(ACTIVITY_LOG):
        with open(ACTIVITY_LOG) as f:
            return json.load(f)
    return {"processed_urls": [], "activities": []}


def save_activity_log(log: dict) -> None:
    with open(ACTIVITY_LOG, "w") as f:
        json.dump(log, f, indent=2, default=str)


# ── Agent tools ───────────────────────────────────────────────────────────────

@beta_tool
def track_backlink_activity(
    url: str,
    action_type: str,
    status: str,
    notes: str,
) -> str:
    """Record a backlink building activity to the persistent log.

    Args:
        url: The target URL where the backlink was or will be placed.
        action_type: One of: directory_submission, outreach_sent, forum_post,
                     guest_post_pitch, resource_page_outreach, broken_link_outreach,
                     brand_mention_outreach, social_bookmark, qa_answer.
        status: One of: pending, submitted, live, rejected, follow_up_needed.
        notes: Brief description of the action taken and any contact details.
    """
    log = load_activity_log()
    entry = {
        "date": date.today().isoformat(),
        "url": url,
        "action_type": action_type,
        "status": status,
        "notes": notes,
    }
    log["activities"].append(entry)
    if url not in log["processed_urls"]:
        log["processed_urls"].append(url)
    save_activity_log(log)
    return f"Logged: [{action_type}] {url} → {status}"


@beta_tool
def check_if_already_processed(url: str) -> str:
    """Check whether a URL has already been targeted for backlink building.

    Args:
        url: The URL to check against the activity log.
    """
    log = load_activity_log()
    if url in log["processed_urls"]:
        matches = [a for a in log["activities"] if a["url"] == url]
        last = matches[-1]
        return f"ALREADY PROCESSED on {last['date']} — action: {last['action_type']}, status: {last['status']}"
    return "NOT YET PROCESSED — safe to target"


@beta_tool
def get_todays_activity_summary() -> str:
    """Return a summary of all backlink activities logged today."""
    log = load_activity_log()
    today = date.today().isoformat()
    todays = [a for a in log["activities"] if a["date"] == today]
    if not todays:
        return "No activities logged yet today."
    lines = [f"Today's backlink activities ({today}) — {len(todays)} total:"]
    for a in todays:
        lines.append(f"  [{a['action_type']}] {a['url']} → {a['status']}")
    return "\n".join(lines)


@beta_tool
def score_link_prospect(
    page_url: str,
    page_title: str,
    page_content_snippet: str,
    your_niche: str,
) -> str:
    """Score a potential link building prospect (0–100).

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
    relevance = sum(1 for w in niche_words if w in content_lower)
    if relevance >= 4:
        score += 40
        reasons.append("High relevance to SMM niche (+40)")
    elif relevance >= 2:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "top", "review", "directory"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/list page — high link value (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High-authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 [{priority}]\nURL: {page_url}\n" + "\n".join(reasons)


@beta_tool
def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    link_type: str,
    your_content_url: str,
) -> str:
    """Generate a personalized outreach email for a backlink opportunity.

    Args:
        prospect_name: Name of the website owner or editor (use 'there' if unknown).
        prospect_site: Their website or blog name.
        their_page_topic: Topic of the specific page where you want a link.
        link_type: One of: guest_post, broken_link, resource, mention, directory.
        your_content_url: URL of your content or page to be linked.
    """
    base = f"https://{TARGET_DOMAIN}"
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your {their_page_topic} article on {prospect_site} and noticed a broken link "
            f"that might be frustrating your readers.\n\n"
            f"I've published a comprehensive, up-to-date guide at {your_content_url} that covers the same "
            f"topic — it could be a great replacement.\n\n"
            f"Would you consider swapping it out? Happy to send more details.\n\nBest,\n[Your Name]\n{base}"
        ),
        "guest_post": (
            f"Subject: Guest Post Pitch — {their_page_topic} for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'm a contributor at {BRAND_NAME} ({base}) and a regular reader of {prospect_site}. "
            f"Your content on {their_page_topic} is excellent.\n\n"
            f"I'd love to write an original, in-depth piece for your audience. A few topic ideas:\n"
            f"  1. How to choose the right SMM panel for your business\n"
            f"  2. The 2025 guide to growing social media accounts safely\n"
            f"  3. SMM panels vs organic growth — pros and cons\n\n"
            f"All content is 100% original and includes actionable takeaways. Interested?\n\nBest,\n[Your Name]\n{base}"
        ),
        "resource": (
            f"Subject: Quick resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource list on {their_page_topic} is one of the best I've found — great curation!\n\n"
            f"I thought {your_content_url} might be a useful addition for your readers. It covers "
            f"[brief value prop] and gets updated regularly.\n\n"
            f"No worries if it's not a fit — thanks for the great content either way!\n\nBest,\n[Your Name]\n{base}"
        ),
        "mention": (
            f"Subject: You mentioned {BRAND_NAME} — thank you!\n\n"
            f"Hi {prospect_name},\n\n"
            f"I just came across your article on {their_page_topic} at {prospect_site} — thank you for "
            f"mentioning {BRAND_NAME}!\n\n"
            f"Would you be open to linking directly to {your_content_url}? It would make it much easier "
            f"for your readers to find us. Happy to return the favor.\n\nThanks,\n[Your Name]\n{base}"
        ),
        "directory": (
            f"Submission details for {prospect_site} ({their_page_topic} directory):\n\n"
            f"Site Name: {BRAND_NAME}\n"
            f"URL: {base}\n"
            f"Category: SMM Panel / Social Media Marketing Services\n"
            f"Description: {BRAND_NAME} is a reliable SMM panel offering affordable social media "
            f"marketing services including followers, likes, views, and engagement for all major platforms. "
            f"Instant delivery, 24/7 support, and competitive pricing.\n"
            f"Keywords: SMM panel, buy followers, social media marketing, buy likes, buy views\n"
            f"Contact: support@{TARGET_DOMAIN}"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(
    competitor_domain: str,
    linking_page_topic: str,
) -> str:
    """Assess a competitor backlink as a gap opportunity for alfaapanels.com.

    Args:
        competitor_domain: The competitor's domain that has this backlink.
        linking_page_topic: Topic or description of the page linking to the competitor.
    """
    return (
        f"LINK GAP DETECTED\n"
        f"Competitor with backlink: {competitor_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Action plan:\n"
        f"1. Identify the exact content on {competitor_domain} that earned this link\n"
        f"2. Create equal or better content on {TARGET_DOMAIN}\n"
        f"3. Reach out to the linking page offering {TARGET_DOMAIN} as an additional/replacement resource\n"
        f"4. Track outreach with track_backlink_activity"
    )


# ── Main daily runner ─────────────────────────────────────────────────────────

def run_daily_backlink_builder() -> None:
    today = date.today().isoformat()
    print(f"\n{'=' * 60}")
    print(f"  DAILY BACKLINK BUILDER — {TARGET_DOMAIN}")
    print(f"  Date: {today}")
    print(f"{'=' * 60}\n")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            track_backlink_activity,
            check_if_already_processed,
            get_todays_activity_summary,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO specialist executing today's backlink building session for {TARGET_DOMAIN} ({BRAND_NAME}).

Today's date: {today}
Niche: SMM panels, social media marketing services, buy followers/likes/views
Competitors: {', '.join(COMPETITORS)}

Your job is to find and act on REAL, relevant backlink opportunities today. Work through ALL six tasks below. For every URL you find, use check_if_already_processed before acting on it to avoid duplicate work. Use track_backlink_activity to log every action you take.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 1 — BRAND MENTION AUDIT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Search: "Alfa Panels" OR "alfaapanels" -site:{TARGET_DOMAIN}
- Find at least 3 unlinked brand mentions
- For each: categorize sentiment, generate a mention outreach email, and log it

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 2 — COMPETITOR BACKLINK GAP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For each competitor, web-search for sites linking to them in the SMM niche:
  site:smmking.com OR site:peakerr.com "SMM panel" resource OR review OR list
- Find at least 3 sites that link to competitors but likely not to you
- For each: use identify_link_gap_opportunity, score the prospect, and log it

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 3 — RESOURCE PAGE & DIRECTORY OPPORTUNITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Search for:
  - "best SMM panels" list OR resource site:blog OR site:wordpress.com
  - "SMM panel" intitle:directory OR intitle:list 2024 OR 2025
  - "social media marketing tools" resource page
- Find at least 5 resource pages or directories accepting submissions
- For each: score the prospect, generate the right outreach template, and log it

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 4 — GUEST POST OPPORTUNITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Search for:
  - "write for us" social media marketing OR digital marketing
  - "guest post" SMM OR "social media panel"
  - "contribute" digital marketing blog
- Find at least 3 blogs accepting guest posts relevant to {TARGET_DOMAIN}
- For each: score the prospect, generate a guest post pitch, and log it

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 5 — Q&A & COMMUNITY LINKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Search Quora and Reddit for questions about SMM panels:
  - site:quora.com "best SMM panel" OR "what is SMM panel"
  - site:reddit.com "SMM panel recommendation" OR "buy followers safe"
- Find at least 3 unanswered or partially answered questions
- For each: draft a helpful, non-spammy answer that naturally references {TARGET_DOMAIN} and log it

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 6 — DAILY REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Call get_todays_activity_summary, then write a concise daily report with:
  - Total opportunities found today
  - Top 3 HIGH-priority opportunities with exact URLs and next steps
  - Outreach templates ready to send
  - Any follow-up items from previous days
  - Tomorrow's recommended focus area

Be thorough and action-oriented. Prioritize quality over quantity."""
        }],
    )

    report_blocks = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_blocks.append(block.text)

    report_path = f"daily_report_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report — {TARGET_DOMAIN}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(report_blocks))

    print(f"\nReport saved: {report_path}")
    print("Activity log updated:", ACTIVITY_LOG)


if __name__ == "__main__":
    run_daily_backlink_builder()
