"""
Daily backlink builder for alfaapanels.com.
Runs a rotating strategy each day of the week to systematically build
relevant backlinks across directories, Q&A sites, forums, resource pages,
and competitor gap opportunities.
"""

import json
import os
from datetime import datetime, date

import anthropic
from anthropic import beta_tool

# ── Site configuration ──────────────────────────────────────────────────────
SITE_CONFIG = {
    "domain": "alfaapanels.com",
    "brand_name": "Alfa Panels",
    "niche": "solar panels renewable energy solar installation photovoltaic",
    "keywords": [
        "solar panels",
        "solar energy",
        "solar installation",
        "photovoltaic panels",
        "residential solar",
        "commercial solar",
        "solar power system",
        "renewable energy solutions",
    ],
    "competitors": [
        "sunpower.com",
        "lgelectronics.com",
        "canadiansolar.com",
        "jinko-solar.com",
        "qcells.us",
    ],
    "target_locations": ["UAE", "Middle East", "Gulf"],
}

TRACKING_FILE = "backlink_tracking.json"

# ── Day-of-week rotating strategy ───────────────────────────────────────────
DAILY_STRATEGIES = {
    0: {  # Monday
        "name": "Business Directory Submissions",
        "description": "Submit alfaapanels.com to high-authority business and solar energy directories.",
        "focus": "directories",
        "search_queries": [
            "solar energy company directory submit site",
            "renewable energy business directory listing",
            "solar panel installation company directory",
            "green energy business listings UAE",
        ],
    },
    1: {  # Tuesday
        "name": "Q&A Platform Opportunities",
        "description": "Find and answer solar panel questions on Quora, Reddit, and niche forums.",
        "focus": "qa_platforms",
        "search_queries": [
            "site:quora.com solar panels installation questions unanswered",
            "site:reddit.com/r/solar questions solar panels",
            "site:reddit.com/r/renewable questions solar energy",
            "questions about solar panels cost installation",
        ],
    },
    2: {  # Wednesday
        "name": "Solar Energy Forum Participation",
        "description": "Find active solar and renewable energy forums for brand presence and backlinks.",
        "focus": "forums",
        "search_queries": [
            "solar energy forum community intitle:forum",
            "renewable energy discussion board register",
            "photovoltaic panels forum intitle:discussion",
            "solar installation professionals community",
        ],
    },
    3: {  # Thursday
        "name": "Resource Page Link Building",
        "description": "Find resource pages about solar energy that should link to alfaapanels.com.",
        "focus": "resource_pages",
        "search_queries": [
            'intitle:"resources" "solar panels" OR "solar energy" OR "renewable energy"',
            'inurl:resources "solar installation" -alfaapanels.com',
            '"useful links" OR "helpful resources" solar panels',
            '"recommended suppliers" solar energy renewable',
        ],
    },
    4: {  # Friday
        "name": "Guest Post & Blog Outreach",
        "description": "Find solar and energy blogs accepting guest posts or missing coverage.",
        "focus": "guest_posts",
        "search_queries": [
            '"write for us" solar energy renewable panels',
            '"guest post" OR "contribute" solar panels blog',
            '"submit article" renewable energy solar',
            "solar energy blog accepting contributions",
        ],
    },
    5: {  # Saturday
        "name": "Broken Link Building",
        "description": "Find broken links on solar and renewable energy pages to pitch replacements.",
        "focus": "broken_links",
        "search_queries": [
            "solar panels installation guide resources links",
            "renewable energy buying guide recommended sites",
            "photovoltaic systems comparison page",
            "solar power resources educational page",
        ],
    },
    6: {  # Sunday
        "name": "Competitor Backlink Gap Analysis",
        "description": "Find sites linking to competitors that should also link to alfaapanels.com.",
        "focus": "competitor_gaps",
        "search_queries": [
            f"link:{SITE_CONFIG['competitors'][0]} solar panels",
            f"link:{SITE_CONFIG['competitors'][1]} solar energy",
            "solar panel supplier directory UAE Gulf",
            "best solar energy companies Middle East list",
        ],
    },
}


# ── Tracking helpers ─────────────────────────────────────────────────────────

def load_tracking() -> dict:
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE) as f:
            return json.load(f)
    return {"submitted": [], "targeted": [], "history": []}


def save_tracking(data: dict) -> None:
    with open(TRACKING_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Custom tools ─────────────────────────────────────────────────────────────

@beta_tool
def track_backlink_opportunity(url: str, link_type: str, priority: str, notes: str) -> str:
    """Record a backlink opportunity found during research.

    Args:
        url: URL of the opportunity.
        link_type: Type: 'directory', 'forum', 'qa', 'resource_page', 'guest_post', 'broken_link'.
        priority: 'high', 'medium', or 'low'.
        notes: Brief notes about the opportunity and how to pursue it.
    """
    data = load_tracking()
    entry = {
        "url": url,
        "type": link_type,
        "priority": priority,
        "notes": notes,
        "date_found": date.today().isoformat(),
        "status": "identified",
    }
    if url not in [t["url"] for t in data["targeted"]]:
        data["targeted"].append(entry)
        save_tracking(data)
        return f"Tracked NEW opportunity [{priority.upper()}]: {url}\nType: {link_type}\nNotes: {notes}"
    return f"Already tracked: {url}"


@beta_tool
def mark_backlink_submitted(url: str, submission_details: str) -> str:
    """Mark a backlink as submitted/actioned for today.

    Args:
        url: URL where the backlink was submitted or outreach was sent.
        submission_details: Details of the action taken (e.g. submitted profile, posted answer, sent email).
    """
    data = load_tracking()
    entry = {
        "url": url,
        "details": submission_details,
        "date": date.today().isoformat(),
    }
    data["submitted"].append(entry)
    for t in data["targeted"]:
        if t["url"] == url:
            t["status"] = "actioned"
    save_tracking(data)
    return f"Marked as actioned: {url}\nDetails: {submission_details}"


@beta_tool
def get_previously_targeted_urls() -> str:
    """Return all URLs already targeted so we avoid duplicating effort."""
    data = load_tracking()
    if not data["targeted"]:
        return "No URLs targeted yet — this is a fresh start."
    lines = [f"- [{t['status']}] {t['url']} ({t['type']})" for t in data["targeted"]]
    return "Previously targeted URLs:\n" + "\n".join(lines)


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
        reasons.append("High relevance to niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "directory", "forum"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/directory/forum page (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 [{priority}]\n" + "\n".join(reasons)


@beta_tool
def generate_outreach_message(
    prospect_name: str,
    their_site: str,
    their_page_topic: str,
    link_type: str,
    your_content_url: str,
) -> str:
    """Generate a ready-to-send outreach message for a specific backlink type.

    Args:
        prospect_name: Name or website editor.
        their_site: Their website name or domain.
        their_page_topic: The topic of the page where you want a link.
        link_type: 'directory', 'guest_post', 'resource', 'broken_link', 'mention'.
        your_content_url: The alfaapanels.com URL to be linked.
    """
    brand = SITE_CONFIG["brand_name"]
    domain = SITE_CONFIG["domain"]
    templates = {
        "directory": (
            f"Subject: Listing Request — {brand} Solar Panels\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'd like to add {brand} ({domain}) to your {their_page_topic} directory.\n\n"
            f"We provide premium solar panel installation and renewable energy solutions. "
            f"Our listing details:\n"
            f"  Name: {brand}\n"
            f"  URL: https://{domain}\n"
            f"  Category: Solar Energy / Renewable Energy\n"
            f"  Description: Alfa Panels offers professional solar panel installation, "
            f"photovoltaic systems, and renewable energy solutions for residential and commercial clients.\n\n"
            f"Could you add our listing?\n\nBest regards,\n[Your Name]\n{brand}"
        ),
        "guest_post": (
            f"Subject: Guest Post Pitch — Solar Energy Topics for {their_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following {their_site} and love your coverage of {their_page_topic}.\n\n"
            f"I write for {brand} ({domain}) and would love to contribute a guest post. "
            f"Here are 3 topic ideas:\n"
            f"  1. How to Choose the Right Solar Panels for Your Home in 2026\n"
            f"  2. Solar ROI: What to Expect in the First 5 Years\n"
            f"  3. Common Solar Installation Mistakes and How to Avoid Them\n\n"
            f"Would any of these interest your readers?\n\nBest,\n[Your Name]\n{brand}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your page on {their_page_topic} is a great resource. "
            f"I thought your readers might find value in: {your_content_url}\n\n"
            f"It covers [specific angle] and complements your existing links well.\n\n"
            f"Would you consider adding it?\n\nBest,\n[Your Name]\n{brand}"
        ),
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I noticed a broken link on your {their_page_topic} page on {their_site}.\n\n"
            f"I have a comprehensive resource at {your_content_url} that would be a perfect replacement.\n\n"
            f"Would you consider updating the link?\n\nBest,\n[Your Name]\n{brand}"
        ),
        "mention": (
            f"Subject: Thank you for mentioning {brand}!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {brand} in your article about {their_page_topic}!\n\n"
            f"Would you be open to turning that into a direct link to {your_content_url}? "
            f"It would help your readers find us more easily.\n\nThanks,\n[Your Name]\n{brand}"
        ),
    }
    return templates.get(link_type, templates["resource"])


# ── Main daily runner ────────────────────────────────────────────────────────

def run_daily_backlink_builder():
    today = date.today()
    weekday = today.weekday()  # 0=Monday … 6=Sunday
    strategy = DAILY_STRATEGIES[weekday]

    print(f"\n{'=' * 65}")
    print(f"  Daily Backlink Builder — {SITE_CONFIG['domain']}")
    print(f"  Date   : {today.isoformat()}")
    print(f"  Strategy: {strategy['name']}")
    print(f"{'=' * 65}\n")

    config = SITE_CONFIG
    client = anthropic.Anthropic()

    prompt = f"""You are an expert off-page SEO specialist executing today's backlink building session for {config['domain']}.

SITE DETAILS:
- Domain: {config['domain']}
- Brand: {config['brand_name']}
- Niche: {config['niche']}
- Target keywords: {', '.join(config['keywords'])}
- Target locations: {', '.join(config['target_locations'])}
- Competitors: {', '.join(config['competitors'])}

TODAY'S STRATEGY: {strategy['name']}
{strategy['description']}

SEARCH QUERIES TO USE:
{chr(10).join(f"  {i+1}. {q}" for i, q in enumerate(strategy['search_queries']))}

INSTRUCTIONS:
1. First, call get_previously_targeted_urls() to see what's already been done so you don't repeat it.
2. Execute each search query using web_search to find REAL, specific URLs.
3. For each promising result, fetch the page with web_fetch to verify it's still live and relevant.
4. Score each prospect with score_link_prospect() — only pursue HIGH or MEDIUM scores.
5. For the top 5 prospects:
   a. Track them with track_backlink_opportunity()
   b. Generate a ready-to-use outreach message with generate_outreach_message()
   c. If it's a directory or Q&A platform where you can submit/answer directly, describe EXACTLY how to do it (step-by-step URL, form fields, category to choose).
6. Mark any completed submissions with mark_backlink_submitted().
7. End with a structured DAILY REPORT including:
   - Opportunities found today (count and list)
   - Top 3 with full outreach messages
   - Step-by-step action instructions for each
   - Cumulative progress note

Focus on ACTIONABLE, REAL results. Every URL you mention must be a real, live page.
Prioritize relevance to solar panels, renewable energy, and the Middle East/UAE market."""

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            track_backlink_opportunity,
            mark_backlink_submitted,
            get_previously_targeted_urls,
            score_link_prospect,
            generate_outreach_message,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{"role": "user", "content": prompt}],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    # Save dated report
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_filename = os.path.join(report_dir, f"backlinks_{today.isoformat()}.md")
    with open(report_filename, "w") as f:
        f.write(f"# Daily Backlink Report — {config['domain']}\n")
        f.write(f"**Date:** {today.isoformat()}  \n")
        f.write(f"**Strategy:** {strategy['name']}  \n\n")
        f.write("---\n\n")
        f.write("\n\n".join(full_report))

    print(f"\nReport saved: {report_filename}")
    return report_filename


if __name__ == "__main__":
    run_daily_backlink_builder()
