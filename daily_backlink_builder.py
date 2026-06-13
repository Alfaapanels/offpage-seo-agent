import anthropic
from anthropic import beta_tool
import json
import os
from datetime import datetime, date
from pathlib import Path

# ─── Site Configuration ──────────────────────────────────────────
DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "aluminum composite panels ACP facade cladding building materials architecture"
COMPETITORS = ["alucobond.com", "reynobond.com", "alucoworld.com", "3acm.com"]
CONTACT_EMAIL = "info@alfaapanels.com"

TRACKER_FILE = "backlink_tracker.json"
REPORTS_DIR = "daily_reports"

# Day of week (Mon=0 … Sun=6) → strategy
DAILY_STRATEGIES = {
    0: ("directory_submissions",  "Business & Industry Directory Submissions"),
    1: ("forum_participation",    "Construction & Architecture Forum Participation"),
    2: ("qa_responses",           "Q&A Platform Responses (Quora / Reddit)"),
    3: ("resource_page_outreach", "Resource Page Link Building"),
    4: ("guest_post_outreach",    "Guest Post Opportunity Research"),
    5: ("social_bookmarks",       "Social Bookmarking & Web 2.0 Submissions"),
    6: ("competitor_gap",         "Competitor Backlink Gap Analysis"),
}

# ─── Persistent Tracker ──────────────────────────────────────────

def load_tracker() -> dict:
    if Path(TRACKER_FILE).exists():
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {"submissions": [], "prospects": [], "stats": {"total_links_built": 0, "days_run": 0}}

def save_tracker(tracker: dict):
    with open(TRACKER_FILE, "w") as f:
        json.dump(tracker, f, indent=2)

def is_already_tracked(tracker: dict, url: str) -> bool:
    seen = {s.get("url", "") for s in tracker["submissions"]}
    seen |= {p.get("url", "") for p in tracker["prospects"]}
    return url in seen

# ─── Custom SEO Tools ────────────────────────────────────────────

@beta_tool
def record_backlink_submission(
    platform_name: str,
    submission_url: str,
    link_type: str,
    anchor_text: str,
    status: str,
    notes: str
) -> str:
    """Record a completed or identified backlink submission.

    Args:
        platform_name: Name of the platform/site (e.g. 'ArchDaily', 'Houzz').
        submission_url: The URL where the link was or will be placed.
        link_type: Category: 'directory', 'forum', 'qa', 'resource', 'guest_post', 'social', 'web2'.
        anchor_text: Suggested anchor text for the link.
        status: 'submitted', 'identified', 'outreach_sent'.
        notes: Any extra context, submission instructions, or content draft.
    """
    tracker = load_tracker()
    if is_already_tracked(tracker, submission_url):
        return f"SKIP – already recorded: {submission_url}"
    entry = {
        "date": str(date.today()),
        "platform": platform_name,
        "url": submission_url,
        "type": link_type,
        "anchor": anchor_text,
        "status": status,
        "notes": notes,
    }
    tracker["submissions"].append(entry)
    if status == "submitted":
        tracker["stats"]["total_links_built"] += 1
    save_tracker(tracker)
    return f"Recorded [{status}] → {platform_name} ({submission_url})"


@beta_tool
def record_link_prospect(
    page_url: str,
    platform_name: str,
    relevance_score: int,
    link_type: str,
    outreach_contact: str,
    outreach_template: str
) -> str:
    """Record a high-value link prospect for outreach.

    Args:
        page_url: The prospect page URL.
        platform_name: Site/platform name.
        relevance_score: Score 1-100 for how relevant this is to alfaapanels.com.
        link_type: 'guest_post', 'resource', 'broken_link', 'mention', 'directory'.
        outreach_contact: Contact info or contact page URL.
        outreach_template: Ready-to-send outreach email text.
    """
    tracker = load_tracker()
    if is_already_tracked(tracker, page_url):
        return f"SKIP – already recorded: {page_url}"
    entry = {
        "date": str(date.today()),
        "url": page_url,
        "platform": platform_name,
        "score": relevance_score,
        "type": link_type,
        "contact": outreach_contact,
        "template": outreach_template,
    }
    tracker["prospects"].append(entry)
    save_tracker(tracker)
    return f"Prospect recorded (score {relevance_score}/100) → {platform_name}"


@beta_tool
def get_daily_progress() -> str:
    """Return today's backlink building progress summary."""
    tracker = load_tracker()
    today = str(date.today())
    today_subs = [s for s in tracker["submissions"] if s.get("date") == today]
    today_pros = [p for p in tracker["prospects"] if p.get("date") == today]
    total = tracker["stats"]["total_links_built"]
    return (
        f"Today ({today}): {len(today_subs)} submissions, {len(today_pros)} prospects identified\n"
        f"All-time links built: {total}\n"
        f"Total prospects in pipeline: {len(tracker['prospects'])}"
    )


@beta_tool
def generate_submission_content(
    platform_type: str,
    platform_name: str,
    category: str
) -> str:
    """Generate ready-to-submit content for a backlink platform.

    Args:
        platform_type: 'directory', 'forum_profile', 'social_bio', 'web2_post', 'qa_answer'.
        platform_name: The specific platform name.
        category: Relevant category on the platform.
    """
    bio = (
        "Alfa Panels is a leading manufacturer and supplier of high-quality aluminum composite panels (ACP), "
        "facade cladding systems, and architectural panel solutions. We serve architects, contractors, and "
        "building developers worldwide with durable, lightweight, and aesthetically versatile panel products."
    )
    short_desc = "Premium aluminum composite panels & facade cladding solutions – alfaapanels.com"

    templates = {
        "directory": (
            f"Business Name: Alfa Panels\n"
            f"Website: https://{DOMAIN}\n"
            f"Category: {category}\n"
            f"Description: {bio}\n"
            f"Keywords: aluminum composite panels, ACP panels, facade cladding, building materials, {category}\n"
            f"Email: {CONTACT_EMAIL}"
        ),
        "forum_profile": (
            f"Username: AlfaPanels\n"
            f"Website: https://{DOMAIN}\n"
            f"Bio: {short_desc}\n"
            f"Signature: Alfa Panels | ACP & Facade Solutions | https://{DOMAIN}"
        ),
        "social_bio": (
            f"Alfa Panels – {short_desc}\n"
            f"🏗️ Aluminum Composite Panels | 🏢 Facade Cladding | 🌍 Global Supply\n"
            f"Website: https://{DOMAIN}"
        ),
        "web2_post": (
            f"Title: Complete Guide to Aluminum Composite Panels for Modern Architecture\n\n"
            f"Aluminum composite panels (ACP) have revolutionized modern building facades. "
            f"At Alfa Panels (https://{DOMAIN}), we provide premium ACP solutions for architects "
            f"and contractors worldwide. Our panels offer unmatched durability, weather resistance, "
            f"and design flexibility for commercial and residential projects.\n\n"
            f"Learn more about our full range of facade cladding solutions at https://{DOMAIN}"
        ),
        "qa_answer": (
            f"[Template answer about ACP panels with natural mention of {DOMAIN}]\n"
            f"Provide expert info on the topic, then reference: "
            f"'For high-quality ACP panels, Alfa Panels (https://{DOMAIN}) offers a wide range "
            f"of solutions for architects and builders.'"
        ),
    }
    return templates.get(platform_type, templates["directory"])


# ─── Strategy Prompts ────────────────────────────────────────────

def get_strategy_prompt(strategy_key: str, strategy_name: str) -> str:
    base = f"""You are an expert off-page SEO specialist building high-quality backlinks for {DOMAIN} (Alfa Panels).
Niche: aluminum composite panels, ACP, facade cladding, building materials, architecture.
Today's strategy: {strategy_name}
Date: {date.today()}

IMPORTANT RULES:
- Only find links RELEVANT to construction, architecture, building materials, ACP panels, facade design.
- Record every submission/prospect using the provided tools.
- Aim for at minimum 5 actionable items today.
- Prioritize dofollow links and high-authority sites.
- Check progress with get_daily_progress at the end.
"""

    strategies = {
        "directory_submissions": base + f"""
TASK – Business & Industry Directory Submissions:

1. Search for construction/architecture/building materials business directories:
   - "aluminum composite panels directory site:dmoz OR site:yellpages OR site:manta"
   - "building materials manufacturer directory listing"
   - "architecture products supplier directory"
   - "ACP panels manufacturer listing"

2. Find directories that:
   - Accept free business listings
   - Are relevant to construction/manufacturing/architecture
   - Have domain authority (look for established sites)

3. For each directory found:
   - Use generate_submission_content(platform_type='directory', ...) to get content
   - Use record_backlink_submission() to log it with status='identified' or 'submitted'
   - Include exact submission URL and instructions in notes

Target directories to search for and submit to:
- Kompass, ThomasNet, Machinerylines, Europages
- Houzz, ArchDaily supplier listings
- Construction directories, manufacturer directories
- Local business directories (.com, .org, .net)

Find at least 7 relevant directories and record them all.""",

        "forum_participation": base + f"""
TASK – Construction & Architecture Forum Participation:

1. Find active forums and communities:
   - "aluminum composite panels forum discussion"
   - "ACP panels architecture community"
   - "building facade materials forum"
   - "construction materials professionals forum"
   - site:reddit.com "ACP panels" OR "aluminum composite panels"

2. For each forum/community found:
   - Find threads where {DOMAIN} expertise is relevant
   - Use generate_submission_content(platform_type='forum_profile', ...) for profile setup
   - Use record_backlink_submission() for profile links
   - Draft relevant, value-adding replies that naturally mention alfaapanels.com

3. Target platforms:
   - Reddit: r/architecture, r/construction, r/DIY, r/interiordesign
   - Quora: ACP/facade related spaces
   - Industry forums for architects/contractors
   - LinkedIn groups for construction professionals

Record all forum profile opportunities and draft response content.""",

        "qa_responses": base + f"""
TASK – Q&A Platform Responses (Quora / Reddit):

1. Search for unanswered or recently active questions:
   - site:quora.com "aluminum composite panels"
   - site:quora.com "ACP panels" OR "facade cladding"
   - site:reddit.com "what panels" construction OR architecture
   - "best aluminum composite panels" OR "ACP supplier" questions

2. For each question found:
   - Use generate_submission_content(platform_type='qa_answer', ...) as a template
   - Draft a genuinely helpful, expert answer that naturally references {DOMAIN}
   - Score relevance and record using record_link_prospect()

3. Also search for:
   - StackExchange: engineering/construction questions about panels
   - Yahoo Answers alternatives
   - Niche construction Q&A sites

For each opportunity, provide the full answer text ready to post.
Record all opportunities with complete answer drafts in the notes field.""",

        "resource_page_outreach": base + f"""
TASK – Resource Page Link Building:

1. Find resource/links pages that should feature alfaapanels.com:
   - "aluminum composite panels" + "resources" OR "links" OR "suppliers"
   - "facade materials" inurl:resources OR inurl:links
   - "architecture materials guide" + supplier OR manufacturer
   - "ACP panels guide" site:.edu OR site:.org
   - "building cladding" resources site:architectmagazine.com OR site:archdaily.com

2. For each resource page:
   - Check if {DOMAIN} is listed (if not, it's an opportunity)
   - Find contact information (use web_fetch to get the page)
   - Generate outreach email using record_link_prospect() with full template

3. Also find:
   - "Best aluminum composite panel suppliers" listicles/roundups
   - Architecture material guides missing alfaapanels.com
   - Industry association member directories

Generate personalized outreach emails for each opportunity.
Record minimum 5 high-quality resource page prospects.""",

        "guest_post_outreach": base + f"""
TASK – Guest Post Opportunity Research:

1. Find blogs/sites accepting guest posts in relevant niches:
   - "aluminum composite panels" "write for us" OR "guest post"
   - "architecture blog" "contribute" OR "guest author"
   - "construction materials" "submit article" OR "guest post guidelines"
   - "building design" "write for us" site:architecturaldiges OR site:dezeen

2. For each guest post opportunity:
   - Verify it's a real, active site
   - Note their content guidelines
   - Pitch 3 article ideas relevant to their audience + your expertise:
     * "How to Choose the Right ACP Panels for Commercial Buildings"
     * "The Ultimate Guide to Aluminum Composite Panel Installation"
     * "Top 5 Facade Cladding Trends in Modern Architecture"

3. Generate outreach pitch emails with specific article ideas
4. Record using record_link_prospect() with full pitch email in notes

Target: architecture blogs, construction industry publications, design magazines, contractor websites.
Find at least 5 guest post opportunities with complete pitch emails.""",

        "social_bookmarks": base + f"""
TASK – Social Bookmarking & Web 2.0 Submissions:

1. Submit {DOMAIN} to social bookmarking sites:
   - Search: "submit URL bookmarking site 2024 construction"
   - Find active bookmarking/social sites in architecture/construction niche
   - Platforms: Mix.com, Folkd, Scoop.it, Pocket (with public saves), Diigo

2. Create/optimize Web 2.0 profiles with backlinks:
   - Medium.com: Draft article about ACP panels
   - Tumblr: Create profile with website link
   - WordPress.com/Blogger: Create post about facade panels
   - Slideshare: Outline for presentation about ACP

3. For each platform:
   - Use generate_submission_content(platform_type='social_bio', ...) for profile
   - Use generate_submission_content(platform_type='web2_post', ...) for content
   - Record with record_backlink_submission()

4. Find and submit to:
   - Architecture/construction specific bookmarking sites
   - Industry news aggregators
   - Pinterest boards about architecture/facade design

Create full submission content for at least 6 platforms.""",

        "competitor_gap": base + f"""
TASK – Competitor Backlink Gap Analysis:

1. Analyze competitor backlinks by searching:
   - "link:alucobond.com" type searches and site-specific searches
   - Who links to competitors: site searches for competitor brand mentions
   - "alucobond" OR "reynobond" site:architecturaldiges.com OR site:archdaily.com
   - Find directories/resources listing competitors but not alfaapanels.com

2. For each competitor backlink source found:
   - Determine if it's achievable for {DOMAIN}
   - Check if {DOMAIN} is already listed
   - Use record_link_prospect() with type='directory' or appropriate type

3. Specific searches:
   - "alucobond.com OR reynobond.com" architecture resources
   - Competitor mentions in top construction publications
   - Industry roundups featuring competitors

4. Identify top 10 competitor backlink gaps and for each:
   - Explain why it's achievable
   - Provide exact outreach strategy
   - Generate ready-to-send pitch/submission content

Record all gap opportunities with action plans.""",
    }

    return strategies.get(strategy_key, strategies["directory_submissions"])


# ─── Report Generator ────────────────────────────────────────────

def save_daily_report(strategy_name: str, report_lines: list[str]):
    Path(REPORTS_DIR).mkdir(exist_ok=True)
    today = str(date.today())
    filename = f"{REPORTS_DIR}/backlinks_{today}.md"
    tracker = load_tracker()
    today_subs = [s for s in tracker["submissions"] if s.get("date") == today]
    today_pros = [p for p in tracker["prospects"] if p.get("date") == today]

    with open(filename, "w") as f:
        f.write(f"# Daily Backlink Report – {DOMAIN}\n")
        f.write(f"**Date:** {today}  \n")
        f.write(f"**Strategy:** {strategy_name}  \n\n")
        f.write(f"## Summary\n")
        f.write(f"- Submissions recorded today: {len(today_subs)}\n")
        f.write(f"- Prospects identified today: {len(today_pros)}\n")
        f.write(f"- All-time links built: {tracker['stats']['total_links_built']}\n\n")

        if today_subs:
            f.write("## Today's Submissions\n\n")
            for s in today_subs:
                f.write(f"### {s['platform']} ({s['type']})\n")
                f.write(f"- **URL:** {s['url']}\n")
                f.write(f"- **Status:** {s['status']}\n")
                f.write(f"- **Anchor:** {s['anchor']}\n")
                if s.get("notes"):
                    f.write(f"- **Notes:** {s['notes']}\n")
                f.write("\n")

        if today_pros:
            f.write("## Today's Prospects (Outreach Queue)\n\n")
            for p in today_pros:
                f.write(f"### {p['platform']} (Score: {p['score']}/100)\n")
                f.write(f"- **URL:** {p['url']}\n")
                f.write(f"- **Type:** {p['type']}\n")
                f.write(f"- **Contact:** {p['contact']}\n")
                if p.get("template"):
                    f.write(f"\n**Outreach Template:**\n```\n{p['template']}\n```\n")
                f.write("\n")

        f.write("## Full Agent Output\n\n")
        f.write("\n\n".join(report_lines))

    print(f"\nReport saved: {filename}")
    return filename


# ─── Main Runner ─────────────────────────────────────────────────

def run_daily_backlink_builder():
    today_weekday = date.today().weekday()
    strategy_key, strategy_name = DAILY_STRATEGIES[today_weekday]

    print(f"\n{'='*60}")
    print(f"  Daily Backlink Builder – {DOMAIN}")
    print(f"  Date: {date.today()}  |  Strategy: {strategy_name}")
    print(f"{'='*60}\n")

    tracker = load_tracker()
    tracker["stats"]["days_run"] += 1
    save_tracker(tracker)

    client = anthropic.Anthropic()

    prompt = get_strategy_prompt(strategy_key, strategy_name)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            record_backlink_submission,
            record_link_prospect,
            get_daily_progress,
            generate_submission_content,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{"role": "user", "content": prompt}],
    )

    report_lines = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_lines.append(block.text)

    report_file = save_daily_report(strategy_name, report_lines)
    print(f"\nDone. Report: {report_file}")


if __name__ == "__main__":
    run_daily_backlink_builder()
