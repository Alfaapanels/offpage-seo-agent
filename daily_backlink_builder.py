#!/usr/bin/env python3
"""
Daily Backlink Builder for alfaapanels.com
Finds and documents relevant backlink opportunities every day.

Usage:
  python daily_backlink_builder.py           # Run once immediately
  python daily_backlink_builder.py --once    # Same as above
  python daily_backlink_builder.py --schedule  # Run now + schedule daily at 09:00
"""

import anthropic
from anthropic import beta_tool
import json
import os
import sys
import schedule
import time
from datetime import datetime, date

client = anthropic.Anthropic()

# ──────────────────────────────────────────────────────────────
# Site Configuration
# ──────────────────────────────────────────────────────────────
SITE_CONFIG = {
    "domain": "alfaapanels.com",
    "brand_name": "Alfa Panels",
    "niche": "solar panels insulated panels SIP panels building materials construction energy efficiency",
    "target_keywords": [
        "solar panels",
        "insulated panels",
        "SIP panels",
        "structural insulated panels",
        "building materials",
        "construction panels",
        "energy efficient building",
        "roof panels",
        "wall panels",
        "alfaapanels",
    ],
    "competitors": [
        "canadiansolar.com",
        "jinko-solar.com",
        "longi.com",
        "sipsystems.co.uk",
        "kingspanpanels.com",
    ],
    "content_urls": [
        "https://alfaapanels.com",
        "https://alfaapanels.com/products",
        "https://alfaapanels.com/solar-panels",
        "https://alfaapanels.com/insulated-panels",
    ],
    "description": (
        "Alfa Panels supplies high-quality solar panels and insulated building panels "
        "for residential and commercial construction. Products include SIP panels, "
        "solar modules, roofing panels, and wall panels designed for energy efficiency."
    ),
}

TRACKER_FILE = "backlink_tracker.json"
REPORTS_DIR = "reports"


# ──────────────────────────────────────────────────────────────
# Tracker helpers
# ──────────────────────────────────────────────────────────────

def load_tracker() -> dict:
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {
        "contacted_sites": [],
        "submitted_directories": [],
        "opportunities": [],
        "total_opportunities_found": 0,
        "days_run": 0,
        "last_run": None,
    }


def save_tracker(tracker: dict):
    with open(TRACKER_FILE, "w") as f:
        json.dump(tracker, f, indent=2, default=str)


# ──────────────────────────────────────────────────────────────
# Agent Tools
# ──────────────────────────────────────────────────────────────

@beta_tool
def track_backlink_opportunity(
    site_url: str,
    opportunity_type: str,
    priority: str,
    action_required: str,
    notes: str,
) -> str:
    """Log a new backlink opportunity so it can be actioned.

    Args:
        site_url: Full URL of the page or site offering the opportunity.
        opportunity_type: One of: 'directory', 'guest_post', 'broken_link',
            'resource_page', 'unlinked_mention', 'qa_answer', 'forum_post',
            'link_gap', 'social_profile'.
        priority: 'high', 'medium', or 'low'.
        action_required: Exact next step to turn this into a live backlink.
        notes: Relevance, DA estimate, or other useful context.
    """
    tracker = load_tracker()
    entry = {
        "date": str(date.today()),
        "site_url": site_url,
        "type": opportunity_type,
        "priority": priority,
        "action": action_required,
        "notes": notes,
        "status": "identified",
    }
    tracker["opportunities"].append(entry)
    tracker["total_opportunities_found"] += 1
    save_tracker(tracker)
    return f"Tracked [{priority.upper()}] {opportunity_type}: {site_url}"


@beta_tool
def generate_directory_submission(
    directory_name: str,
    directory_url: str,
    submit_url: str,
    category: str,
) -> str:
    """Prepare a complete directory submission for alfaapanels.com.

    Args:
        directory_name: Human-readable name of the directory.
        directory_url: Homepage of the directory.
        submit_url: Direct URL to the submission form.
        category: Best-fit category for alfaapanels.com.
    """
    tracker = load_tracker()
    if directory_url in tracker["submitted_directories"]:
        return f"SKIPPED (already tracked): {directory_url}"

    tracker["submitted_directories"].append(directory_url)
    save_tracker(tracker)

    return f"""
DIRECTORY SUBMISSION
====================
Directory : {directory_name}
Homepage  : {directory_url}
Submit at : {submit_url}
Category  : {category}

Fields to fill in:
  Title       : Alfa Panels – Solar & Insulated Building Panels
  URL         : https://alfaapanels.com
  Description : Alfa Panels supplies premium solar panels and insulated building
                panels (SIP) for residential and commercial construction.
                Energy-efficient, durable roofing and wall panel solutions.
  Keywords    : solar panels, SIP panels, insulated panels, building materials,
                structural insulated panels, construction panels
  Category    : {category}

Status: READY TO SUBMIT
"""


@beta_tool
def generate_qa_answer(
    platform: str,
    question_url: str,
    question_text: str,
    draft_answer: str,
) -> str:
    """Draft a helpful Q&A answer that naturally references alfaapanels.com.

    Args:
        platform: Platform name (e.g. Quora, Reddit r/solar, StackExchange).
        question_url: URL of the question thread.
        question_text: The exact question being answered.
        draft_answer: A thorough, helpful answer that mentions alfaapanels.com
            naturally where relevant.
    """
    return f"""
Q&A BACKLINK OPPORTUNITY
========================
Platform     : {platform}
Question URL : {question_url}
Question     : {question_text}

--- DRAFT ANSWER ---
{draft_answer}
--------------------

Action: Post the answer above on {platform}. Ensure it adds genuine value.
Link placement should feel natural, not promotional.
"""


@beta_tool
def generate_guest_post_pitch(
    site_url: str,
    site_niche: str,
    contact_page: str,
    da_estimate: str,
    pitch_topics: str,
) -> str:
    """Create a personalised guest-post pitch email for a target site.

    Args:
        site_url: URL of the site accepting guest contributions.
        site_niche: The site's main topic area.
        contact_page: URL of their contact / write-for-us page.
        da_estimate: Estimated domain authority: 'high (50+)', 'medium (30-50)',
            or 'low (<30)'.
        pitch_topics: 2–3 specific article ideas relevant to their audience.
    """
    tracker = load_tracker()
    if site_url not in tracker["contacted_sites"]:
        tracker["contacted_sites"].append(site_url)
        save_tracker(tracker)

    return f"""
GUEST POST PITCH
================
Target site   : {site_url}
Niche         : {site_niche}
Contact page  : {contact_page}
Est. DA       : {da_estimate}

Proposed article ideas:
{pitch_topics}

--- EMAIL TEMPLATE ---
Subject: Guest Post Pitch – Expert Content on [Topic] for Your Readers

Hi [Editor Name],

I'm writing from Alfa Panels (alfaapanels.com), a company specialising in solar
panels and insulated building panels (SIPs).

I've been enjoying your content on {site_niche} and would love to contribute
a high-quality, original article. Here are a few ideas tailored for your audience:

{pitch_topics}

Each piece would be thoroughly researched, include original data where possible,
and bring genuine value to your readers. In return I'd appreciate a single
contextual link back to alfaapanels.com.

Would any of these interest you? Happy to share writing samples or adjust topics.

Best regards,
[Your Name]
Alfa Panels | alfaapanels.com
----------------------
"""


@beta_tool
def generate_link_gap_strategy(
    competitor_domain: str,
    linking_page_url: str,
    linking_page_topic: str,
    linking_page_contact: str,
) -> str:
    """Build an outreach strategy for a competitor backlink gap.

    Args:
        competitor_domain: The competitor that has the backlink.
        linking_page_url: URL of the page linking to the competitor.
        linking_page_topic: Topic of that linking page.
        linking_page_contact: Contact info or contact-page URL for that site.
    """
    return f"""
LINK GAP STRATEGY
=================
Competitor        : {competitor_domain}
Linking page      : {linking_page_url}
Topic             : {linking_page_topic}
Contact           : {linking_page_contact}

3-step action plan:
1. RESEARCH  – Find exactly which page on {competitor_domain} earned this link.
               Understand why {linking_page_topic} editors found it valuable.
2. CREATE    – Publish a more comprehensive resource on alfaapanels.com covering
               the same topic with more depth, data, or visuals.
3. OUTREACH  – Email {linking_page_contact}:
               "Hi [Name], I noticed you linked to {competitor_domain} in your
               article about {linking_page_topic}. We've just published an even
               more detailed guide at alfaapanels.com that your readers would
               find valuable – would you consider adding it as an additional
               resource?"
"""


@beta_tool
def generate_broken_link_outreach(
    linking_page_url: str,
    broken_url: str,
    replacement_url: str,
    webmaster_contact: str,
) -> str:
    """Generate a broken-link replacement outreach for alfaapanels.com.

    Args:
        linking_page_url: Page that contains the broken link.
        broken_url: The specific broken URL on that page.
        replacement_url: The alfaapanels.com page that should replace it.
        webmaster_contact: Email or contact-page URL for the webmaster.
    """
    return f"""
BROKEN LINK OUTREACH
====================
Linking page    : {linking_page_url}
Broken link     : {broken_url}
Replacement     : {replacement_url}
Contact         : {webmaster_contact}

--- EMAIL TEMPLATE ---
Subject: Broken link found on your page

Hi [Name],

I was reading your article at {linking_page_url} and noticed a broken link
pointing to: {broken_url}

I have a resource at {replacement_url} that covers the same topic and would
serve as a great replacement for your readers.

Would you be open to updating the link? Let me know if you need anything else
from our end.

Best,
[Your Name]
Alfa Panels | alfaapanels.com
----------------------
"""


# ──────────────────────────────────────────────────────────────
# Daily runner
# ──────────────────────────────────────────────────────────────

def run_daily_backlink_builder():
    today = str(date.today())
    print(f"\n{'=' * 60}")
    print(f"  DAILY BACKLINK BUILDER  –  alfaapanels.com")
    print(f"  Date: {today}")
    print(f"{'=' * 60}\n")

    os.makedirs(REPORTS_DIR, exist_ok=True)

    tracker = load_tracker()
    tracker["days_run"] += 1
    tracker["last_run"] = today
    save_tracker(tracker)

    config = SITE_CONFIG
    already_contacted = tracker.get("contacted_sites", [])
    already_submitted = tracker.get("submitted_directories", [])

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            track_backlink_opportunity,
            generate_directory_submission,
            generate_qa_answer,
            generate_guest_post_pitch,
            generate_link_gap_strategy,
            generate_broken_link_outreach,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are a specialist link-builder working daily for alfaapanels.com.

Site details
------------
Domain      : {config['domain']}
Brand       : {config['brand_name']}
Niche       : {config['niche']}
Keywords    : {', '.join(config['target_keywords'])}
Competitors : {', '.join(config['competitors'])}
Description : {config['description']}

Already contacted (skip): {', '.join(already_contacted[-30:]) or 'None yet'}
Already submitted dirs   : {', '.join(already_submitted[-20:]) or 'None yet'}

Today's date: {today}

════════════════════════════════════════
DAILY TASKS – complete all 6 tasks below
════════════════════════════════════════

TASK 1 – Web Directory Submissions (find 5 real directories)
Search: "submit site" OR "add your website" (solar panels OR "building materials"
        OR "construction" OR "insulated panels") directory
- Find niche-relevant and general high-DA directories that accept free listings.
- Use generate_directory_submission for each one found.
- Use track_backlink_opportunity with type='directory' after each submission.

TASK 2 – Q&A Platform Opportunities (find 4 real threads)
Search on Quora, Reddit (r/solar, r/DIY, r/homeimprovement, r/construction),
engineering forums, and green-building communities for recent questions about:
  • Installing solar panels
  • SIP / insulated panel construction
  • Energy-efficient homes or buildings
  • Choosing building materials
- Write a genuinely helpful, detailed answer for each.
- Mention alfaapanels.com naturally where relevant.
- Use generate_qa_answer then track_backlink_opportunity (type='qa_answer').

TASK 3 – Guest Post Prospects (find 3 real sites)
Search: "write for us" OR "guest post guidelines" (solar OR "building materials"
        OR construction OR "energy efficiency" OR "home improvement")
- Prioritise sites with DA 30+ that cover relevant topics.
- Use generate_guest_post_pitch then track_backlink_opportunity (type='guest_post').

TASK 4 – Competitor Backlink Gaps (find 3 real opportunities)
Search for pages that link to: {config['competitors'][0]}, {config['competitors'][1]}
Use web_fetch to examine those pages and identify link gap opportunities.
- Use generate_link_gap_strategy then track_backlink_opportunity (type='link_gap').

TASK 5 – Broken Link Building (find 2 real broken links)
Search: site:{config['competitors'][0]} OR site:{config['competitors'][1]}
Find resource pages in the niche, then check for broken outbound links.
- Use generate_broken_link_outreach then track_backlink_opportunity (type='broken_link').

TASK 6 – Daily Summary
Write a clear markdown summary containing:
  • Total opportunities found today with counts by type
  • Top 3 priority actions ranked by impact
  • Quick-win actions (can be done in < 30 min)
  • Longer-term actions (content to create)
  • Any trends or insights from today's research

Use REAL URLs from actual web searches – not placeholder examples.
""",
        }],
    )

    report_sections = [
        f"# Daily Backlink Report – alfaapanels.com\n**Date:** {today}\n",
    ]

    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_sections.append(block.text)

    report_path = os.path.join(REPORTS_DIR, f"{today}.md")
    with open(report_path, "w") as f:
        f.write("\n\n".join(report_sections))

    final_tracker = load_tracker()
    print(f"\n{'─' * 60}")
    print(f"Report saved : {report_path}")
    print(f"Opportunities found today + prior : {final_tracker['total_opportunities_found']}")
    print(f"Total days run                    : {final_tracker['days_run']}")
    print(f"{'─' * 60}\n")


# ──────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────

def schedule_daily():
    """Run immediately, then every day at 09:00."""
    print("Daily backlink builder scheduled for 09:00 every day.")
    print("Running first session now…\n")
    run_daily_backlink_builder()
    schedule.every().day.at("09:00").do(run_daily_backlink_builder)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    if "--schedule" in sys.argv:
        schedule_daily()
    else:
        run_daily_backlink_builder()
