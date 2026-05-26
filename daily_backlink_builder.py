"""
Daily backlink builder for alfaapanels.com.

Run directly: python daily_backlink_builder.py
Schedule via cron: see setup_cron.sh
"""

import os
import json
from datetime import datetime
from anthropic import beta_tool
import anthropic

from config import SITE_CONFIG, DAILY_STRATEGIES
from link_tracker import (
    load_tracker,
    save_tracker,
    get_already_submitted,
    get_summary,
    record_submission,
)

client = anthropic.Anthropic()

cfg = SITE_CONFIG


# ── Tools ─────────────────────────────────────────────────────────────────────

@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a potential backlink.

    Args:
        url: Target URL (alfaapanels.com).
        backlink_url: The URL that will link to you.
        anchor_text: Anchor text to use in the link.
    """
    signals = []
    generic = {"click here", "website", "here", "link", "read more"}
    if anchor_text.lower() in generic:
        signals.append("Warning: Generic anchor text — low value")
    else:
        signals.append(f"Good: Descriptive anchor '{anchor_text}'")
    spam_words = ["spam", "casino", "viagra", "porn", "xxx"]
    if any(w in backlink_url.lower() for w in spam_words):
        signals.append("TOXIC — skip this link")
    else:
        signals.append("Domain looks clean")
    authority = any(s in backlink_url for s in [".edu", ".gov"])
    if authority:
        signals.append("High-authority domain (.edu/.gov) — prioritise")
    return "\n".join(signals)


@beta_tool
def score_link_prospect(
    page_url: str,
    page_title: str,
    page_content_snippet: str,
    your_niche: str,
) -> str:
    """Score a link-building prospect 0-100.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
        your_niche: Your site's niche keywords.
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
        reasons.append("Low relevance (+0)")
    high_value = ["resource", "guide", "tools", "blog", "list", "best", "directory", "supplier"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("Resource/guide/directory page (+30)")
    if any(s in page_url for s in [".edu", ".gov", ".org"]):
        score += 30
        reasons.append("Authority domain (.edu/.gov/.org) (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 [{priority}]\nURL: {page_url}\n" + "\n".join(reasons)


@beta_tool
def generate_outreach_email(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    link_type: str,
    your_content_url: str,
) -> str:
    """Generate a personalised outreach email for backlink acquisition.

    Args:
        prospect_name: Name of the site owner / editor.
        prospect_site: Their website name or domain.
        their_page_topic: Topic of the page where you want a link.
        link_type: One of: guest_post | broken_link | resource | mention | directory.
        your_content_url: URL on alfaapanels.com to be linked.
    """
    brand = cfg["brand_name"]
    domain = cfg["domain"]
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your page on {their_page_topic} at {prospect_site} and noticed a broken link.\n\n"
            f"I have a detailed resource at {your_content_url} that would be an excellent replacement for your readers.\n\n"
            f"Would you be open to updating that link?\n\n"
            f"Best regards,\n[Your Name]\n{brand} — {domain}"
        ),
        "guest_post": (
            f"Subject: Guest post idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following {prospect_site}'s content on {their_page_topic} — great work.\n\n"
            f"I'm a contributor at {brand} ({domain}) and would love to write a practical guide for your audience on the same topic. "
            f"I'd naturally reference {your_content_url} as a supporting resource.\n\n"
            f"Would you be open to a guest post collaboration?\n\n"
            f"Best,\n[Your Name]"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is genuinely useful. "
            f"I created {your_content_url} which covers building panels in depth and might add value for your readers.\n\n"
            f"Would you consider adding it?\n\n"
            f"Best,\n[Your Name]\n{brand}"
        ),
        "mention": (
            f"Subject: {brand} mention on {prospect_site} — quick request\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {brand} in your article about {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {your_content_url} so your readers can find us easily?\n\n"
            f"Thanks,\n[Your Name]\n{brand}"
        ),
        "directory": (
            f"Subject: Listing request — {brand}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'd like to submit {brand} ({domain}) for inclusion in your {their_page_topic} directory.\n\n"
            f"We manufacture high-quality sandwich and insulation panels for construction projects worldwide. "
            f"Our resource page is {your_content_url}.\n\n"
            f"Please let me know what information you need.\n\n"
            f"Best,\n[Your Name]\n{brand}"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def log_backlink_opportunity(
    target_url: str,
    link_type: str,
    prospect_domain: str,
    priority: str,
    notes: str,
) -> str:
    """Log a discovered backlink opportunity to the tracker file.

    Args:
        target_url: URL on alfaapanels.com being linked to.
        link_type: Category: directory | forum | qa | guest_post | resource | broken_link | mention.
        prospect_domain: Domain offering the backlink.
        priority: HIGH | MEDIUM | LOW.
        notes: Any extra context (anchor text, page topic, etc.).
    """
    tracker_file = cfg["tracker_file"]
    data = load_tracker(tracker_file)
    entry = {
        "target_url": target_url,
        "type": link_type,
        "prospect": prospect_domain,
        "priority": priority,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "notes": notes,
    }
    data.setdefault("opportunities", []).append(entry)
    data["total_opportunities"] = len(data.get("submitted", [])) + len(data["opportunities"])
    save_tracker(tracker_file, data)
    return f"Logged: [{priority}] {link_type} opportunity at {prospect_domain}"


@beta_tool
def get_previous_submissions(days: int = 7) -> str:
    """Retrieve recently submitted/logged links to avoid duplication.

    Args:
        days: How many past days to include (default 7).
    """
    return get_summary(cfg["tracker_file"])


# ── Daily runner ───────────────────────────────────────────────────────────────

def run_daily_build(force_strategy: str | None = None) -> str:
    """Run today's backlink building session and return the report."""
    today = datetime.now()
    weekday = today.weekday()
    strategy = DAILY_STRATEGIES[weekday]
    strategy_name = force_strategy or strategy["name"]

    os.makedirs(cfg["reports_dir"], exist_ok=True)
    report_path = os.path.join(
        cfg["reports_dir"],
        f"{today.strftime('%Y-%m-%d')}_{strategy_name.replace(' ', '_')}.md",
    )

    print(f"\n{'='*60}")
    print(f"  Alfa Panels — Daily Backlink Builder")
    print(f"  Date : {today.strftime('%Y-%m-%d')}")
    print(f"  Focus: {strategy_name}")
    print(f"{'='*60}\n")

    already_done = get_already_submitted(cfg["tracker_file"])
    already_summary = get_summary(cfg["tracker_file"])

    keywords_str = ", ".join(cfg["target_keywords"])
    competitors_str = ", ".join(cfg["competitors"])
    already_str = "\n".join(already_done[-30:]) if already_done else "None yet — this is the first run."

    prompt = f"""You are an expert off-page SEO specialist working for Alfa Panels (alfaapanels.com).

COMPANY OVERVIEW
- Domain: {cfg['domain']}
- Brand: {cfg['brand_name']}
- Product niche: {cfg['niche']}
- Target keywords: {keywords_str}
- Target audience: {cfg['target_audience']}
- Unique selling points: {', '.join(cfg['unique_selling_points'])}
- Competitors: {competitors_str}

TODAY'S STRATEGY: {strategy_name}
Goal: {strategy['goal']}

TASK DETAILS
{strategy['focus']}

ALREADY SUBMITTED/LOGGED (do NOT revisit these):
{already_str}

PREVIOUS TOTALS
{already_summary}

INSTRUCTIONS
1. Use web_search to find real, live prospects matching today's strategy.
2. Use score_link_prospect to evaluate each one (skip LOW scores).
3. Use analyze_backlink_quality to verify quality.
4. Use generate_outreach_email for each MEDIUM/HIGH prospect.
5. Use log_backlink_opportunity to record every opportunity found.
6. At the end produce a structured Markdown report with:
   - Executive Summary (what was found today)
   - Opportunities table (URL | Type | Priority | Notes)
   - Top 5 outreach emails ready to send
   - Tomorrow's recommended focus
   - Running 30-day action plan progress

Be thorough — find REAL sites, not hypothetical ones.
"""

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            score_link_prospect,
            generate_outreach_email,
            log_backlink_opportunity,
            get_previous_submissions,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{"role": "user", "content": prompt}],
    )

    report_sections = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_sections.append(block.text)

    full_report = "\n\n".join(report_sections)

    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report — {today.strftime('%Y-%m-%d')}\n")
        f.write(f"**Strategy:** {strategy_name}  \n")
        f.write(f"**Goal:** {strategy['goal']}  \n\n")
        f.write("---\n\n")
        f.write(full_report)

    print(f"\nReport saved → {report_path}")
    return report_path


if __name__ == "__main__":
    import sys
    force = sys.argv[1] if len(sys.argv) > 1 else None
    run_daily_build(force_strategy=force)
