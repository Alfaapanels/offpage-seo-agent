#!/usr/bin/env python3
"""
Daily Backlink Builder for alfaapanels.com
Rotates through 7 link-building strategies, one per day.
Tracks every action so nothing is targeted twice.
"""

import anthropic
import json
import os
import datetime
from pathlib import Path
from anthropic import beta_tool

# ============================================================
# Configuration
# ============================================================
DOMAIN = "alfaapanels.com"
BRAND = "Alfa Panels"
NICHE = "aluminium composite panels, ACP sheets, facade cladding, signage panels, building cladding materials India"
COMPETITORS = ["vivaacp.com", "eurobond.in", "alucobond.com", "reynobond.com", "alucolux.com"]
CONTACT_EMAIL = "info@alfaapanels.com"

# Strategy rotation by day of week
DAILY_STRATEGIES = {
    0: "directory_submission",       # Monday
    1: "qa_platform_engagement",     # Tuesday
    2: "resource_page_outreach",     # Wednesday
    3: "competitor_gap_analysis",    # Thursday
    4: "brand_mention_recovery",     # Friday
    5: "forum_community_building",   # Saturday
    6: "social_profile_building",    # Sunday
}

LOG_FILE = "backlink_log.json"
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

client = anthropic.Anthropic()


# ============================================================
# Log helpers
# ============================================================

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return {"submissions": [], "runs": []}


def save_log(log_data):
    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=2)


# ============================================================
# Custom Tools
# ============================================================

@beta_tool
def track_backlink_action(action_type: str, target_url: str, details: str, status: str) -> str:
    """Record a backlink building action to prevent duplicate targeting.

    Args:
        action_type: 'directory', 'qa_answer', 'outreach', 'resource', 'forum', 'social', 'brand_mention'.
        target_url: The URL where the action was taken or will be taken.
        details: Description of exactly what was done or what needs to be done.
        status: 'completed', 'pending_manual', or 'failed'.
    """
    log = load_log()
    today = datetime.date.today().isoformat()

    entry = {
        "date": today,
        "type": action_type,
        "url": target_url,
        "details": details,
        "status": status,
    }
    log["submissions"].append(entry)
    save_log(log)

    total = len(log["submissions"])
    return f"[TRACKED] {action_type} | {target_url} | {status} | Total logged: {total}"


@beta_tool
def check_if_already_targeted(url: str) -> str:
    """Check whether a URL has already been processed to avoid duplicate work.

    Args:
        url: The URL to check against the backlink log.
    """
    log = load_log()
    for entry in log.get("submissions", []):
        if entry.get("url", "").rstrip("/") == url.rstrip("/"):
            return (
                f"ALREADY_TARGETED on {entry['date']} via {entry['type']} "
                f"(status: {entry['status']}). SKIP this URL."
            )
    return f"FRESH_OPPORTUNITY: {url} has not been targeted yet. Proceed."


@beta_tool
def score_link_prospect(page_url: str, page_title: str, page_content_snippet: str, your_niche: str) -> str:
    """Score a potential link-building prospect on relevance and authority.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short content snippet from the page.
        your_niche: The niche/topic of alfaapanels.com.
    """
    score = 0
    reasons = []

    niche_phrases = [p.strip() for p in your_niche.lower().split(",")]
    content_lower = (page_url + " " + page_title + " " + page_content_snippet).lower()

    matched = sum(1 for phrase in niche_phrases if phrase in content_lower)
    if matched >= 2:
        score += 40
        reasons.append(f"High niche relevance: {matched} phrases matched (+40)")
    elif matched == 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low relevance — consider skipping (0)")

    high_value_keywords = ["resource", "guide", "directory", "supplier", "manufacturer", "list", "best", "top", "review"]
    if any(kw in page_url.lower() or kw in page_title.lower() for kw in high_value_keywords):
        score += 30
        reasons.append("High-value page type: resource/directory/guide (+30)")

    if any(tld in page_url for tld in [".edu", ".gov", ".org"]):
        score += 30
        reasons.append("Authority TLD (.edu/.gov/.org) (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")

    india_signals = [".in", "india", "mumbai", "delhi", "gujarat", "chennai", "bangalore", "pune", "hyderabad"]
    if any(sig in page_url.lower() or sig in content_lower for sig in india_signals):
        score += 10
        reasons.append("India geo-relevance bonus (+10)")

    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM PRIORITY" if score >= 40 else "LOW PRIORITY"
    lines = [f"Prospect Score: {score}/100 — {priority}", f"URL: {page_url}", "Reasons:"]
    lines += [f"  • {r}" for r in reasons]
    return "\n".join(lines)


@beta_tool
def generate_outreach_email(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    link_type: str,
    value_proposition: str,
) -> str:
    """Generate a ready-to-send outreach email for link building.

    Args:
        prospect_name: Contact name or 'Team' if unknown.
        prospect_site: Their website name or domain.
        their_page_topic: Topic of the page where we want a link.
        link_type: 'broken_link', 'guest_post', 'resource_addition', or 'brand_mention'.
        value_proposition: What specific value alfaapanels.com offers their audience.
    """
    templates = {
        "broken_link": f"""Subject: Broken link on your {their_page_topic} page

Hi {prospect_name},

I was reading your page on {their_page_topic} at {prospect_site} and noticed a broken link that could frustrate your visitors.

We run Alfa Panels (alfaapanels.com) — India's specialist in {value_proposition}. We have a detailed resource that would make an excellent replacement and genuinely help your readers.

Happy to share the exact broken link location and our suggested URL. Would that be useful?

Best regards,
Team Alfa Panels
info@alfaapanels.com | alfaapanels.com""",

        "guest_post": f"""Subject: Guest article idea for {prospect_site}

Hi {prospect_name},

I've been following your content on {their_page_topic} at {prospect_site} — great work.

I'm from Alfa Panels (alfaapanels.com), specialists in {value_proposition} across India. I'd love to contribute a practical, expert article tailored for your audience — no fluff, just actionable guidance they can't find elsewhere.

Can I send over three topic ideas for your consideration?

Best regards,
Team Alfa Panels
info@alfaapanels.com | alfaapanels.com""",

        "resource_addition": f"""Subject: Resource suggestion for your {their_page_topic} page

Hi {prospect_name},

Your curated resource page on {their_page_topic} at {prospect_site} is exactly the kind of thing architects and contractors bookmark — really well done.

I wanted to suggest Alfa Panels (alfaapanels.com) as an addition. We cover {value_proposition} in depth, including technical specs, installation guides, and real project galleries. It fills a gap I noticed on your list.

Would you be open to taking a look?

Best regards,
Team Alfa Panels
info@alfaapanels.com | alfaapanels.com""",

        "brand_mention": f"""Subject: Thanks for mentioning Alfa Panels!

Hi {prospect_name},

I came across your article on {their_page_topic} at {prospect_site} — thank you for mentioning Alfa Panels! We really appreciate it.

Quick ask: would you consider turning the mention into a direct link to https://alfaapanels.com? It would make it easier for your readers to find us without having to search.

Thanks again — and let me know if we can return the favour.

Team Alfa Panels
info@alfaapanels.com | alfaapanels.com""",
    }
    return templates.get(link_type, templates["resource_addition"])


@beta_tool
def craft_qa_answer(question: str, platform: str, question_url: str, topic_angle: str) -> str:
    """Produce a structured template for answering a Q&A question with a natural alfaapanels.com mention.

    Args:
        question: The question text.
        platform: Platform name (Quora, Reddit, IndiaMART Forum, etc.).
        question_url: Direct URL to the question.
        topic_angle: The specific ACP/panel angle to lead with in the answer.
    """
    return f"""PLATFORM: {platform}
URL: {question_url}
QUESTION: {question}
ANGLE: {topic_angle}

ANSWER FRAMEWORK:
1. Open with direct, confident answer (2-3 sentences addressing "{question}" head-on)
2. Elaborate with technical detail specific to {topic_angle} — thickness, grades, brands, installation tips
3. Mention cost ranges or quality considerations relevant to the Indian market
4. Natural mention: "If you need detailed specs or pricing, Alfa Panels (alfaapanels.com) is a solid starting point — they specialise in ACP sheets and composite cladding across India."
5. Close with a pro tip or common mistake to avoid

POSTING INSTRUCTION: Write a complete, expert answer (300-500 words) before posting.
Do not post a stub or pure promotional reply — it will be downvoted/removed.
Track submission with track_backlink_action once posted."""


@beta_tool
def identify_link_gap(competitor_domain: str, linking_page_url: str, linking_page_topic: str) -> str:
    """Analyse a competitor backlink gap and produce a targeting action plan.

    Args:
        competitor_domain: The competitor that already has this backlink.
        linking_page_url: The URL of the page linking to the competitor.
        linking_page_topic: Topic/subject of that linking page.
    """
    return f"""LINK GAP OPPORTUNITY
====================
Competitor: {competitor_domain}
Linking source: {linking_page_url}
Topic: {linking_page_topic}

ACTION PLAN for alfaapanels.com:
1. Fetch {linking_page_url} to understand why they linked to {competitor_domain}
2. Identify what content/page on {competitor_domain} earned the link
3. Create a better or complementary resource on alfaapanels.com covering "{linking_page_topic}"
4. Reach out to {linking_page_url} positioning Alfa Panels as the India-market specialist
5. Use generate_outreach_email with link_type='resource_addition'

PRIORITY: HIGH — competitor already validated this source accepts industry links
CONTENT ANGLE: Indian market focus, local project examples, Hindi/regional language option"""


# ============================================================
# Daily runner
# ============================================================

def run_daily_backlink_builder():
    today = datetime.date.today()
    strategy = DAILY_STRATEGIES[today.weekday()]
    date_str = today.isoformat()

    print(f"\n{'='*60}")
    print(f"  Daily Backlink Builder — {date_str}")
    print(f"  Domain : {DOMAIN}")
    print(f"  Strategy: {strategy.replace('_', ' ').title()}")
    print(f"{'='*60}\n")

    strategy_prompts = {
        "directory_submission": f"""
TODAY'S FOCUS: Directory Submissions

Find the 10 most relevant online directories for {DOMAIN} and action them.

Search targets:
- Indian B2B directories: IndiaMART, TradeIndia, ExportersIndia, IndiaBizInfo, Yellow Pages India
- Construction/building materials directories
- ACP and cladding supplier directories
- Global B2B: Alibaba Suppliers, GlobalSpec, ThomasNet
- Regional: Just Dial, Sulekha, Quikr Business

For each directory found:
1. Call check_if_already_targeted with the directory URL
2. Search the directory for "alfaapanels" to see if already listed
3. Score it with score_link_prospect
4. Call track_backlink_action:
   - status='pending_manual' with the exact signup/submission URL in details
   - OR status='completed' if alfaapanels is already listed
5. Note exact fields the directory requires (business name, address, category, description)

Prioritise directories with DA > 40 and clear niche relevance. Reject generic low-quality link farms.""",

        "qa_platform_engagement": f"""
TODAY'S FOCUS: Q&A Platform Engagement

Find unanswered or under-answered questions about our niche on Quora, Reddit, and industry forums.

Search queries to run:
- site:quora.com "aluminium composite panels" OR "ACP sheets" India
- site:reddit.com "ACP panels" OR "aluminium cladding" architect
- "aluminium composite panel" forum question 2024 OR 2025
- "ACP sheet price India" forum
- "facade cladding material" question site:archello.com OR site:archdaily.com

For each question:
1. call check_if_already_targeted
2. Assess whether alfaapanels.com can add genuine expert value
3. Call craft_qa_answer to build a structured answer template
4. Call track_backlink_action with status='pending_manual' and the full answer template in details

Target: 6 high-quality questions. Skip anything older than 2 years or with spam-heavy comment sections.""",

        "resource_page_outreach": f"""
TODAY'S FOCUS: Resource Page Outreach

Find "best of" lists, curated directories, and resource pages that should include alfaapanels.com.

Search queries:
- "best ACP sheet suppliers India" list
- "aluminium composite panel manufacturers" India directory
- "facade cladding materials" resource architects guide
- "building materials suppliers" India comprehensive list
- "signage panel suppliers" India

For each resource page:
1. Fetch the page and confirm it links to industry suppliers
2. Call check_if_already_targeted
3. Score with score_link_prospect
4. Generate outreach email with generate_outreach_email (link_type='resource_addition')
5. Call track_backlink_action with status='pending_manual', including the full email in details

Target: 5 pages with clear inclusion criteria. Note the editor email if discoverable.""",

        "competitor_gap_analysis": f"""
TODAY'S FOCUS: Competitor Backlink Gap Analysis

For each competitor — {', '.join(COMPETITORS)} — find sites linking to them that do not link to {DOMAIN}.

For each competitor, search:
- "{competitor}" review OR mentioned site:*.in
- "{competitor}" aluminium panels recommended
- "{competitor}" ACP sheets supplier listed
- intitle:"aluminium composite" {competitor}

For each linking page discovered:
1. Verify the link to competitor exists (use web_fetch to confirm)
2. Call check_if_already_targeted
3. Call identify_link_gap to build the action plan
4. Score with score_link_prospect
5. Generate outreach with generate_outreach_email
6. Call track_backlink_action

Target: 4 validated link gap opportunities with full action plans.""",

        "brand_mention_recovery": f"""
TODAY'S FOCUS: Brand Mention Recovery

Find all web mentions of Alfa Panels and alfaapanels.com that are NOT linked.

Search queries:
- "Alfa Panels" -site:{DOMAIN} building materials
- "alfaapanels" -site:{DOMAIN}
- "alfaapanels.com" -site:{DOMAIN}
- "Alpha Panels India" ACP cladding (common misspelling)

For each mention:
1. Fetch the page to confirm the mention exists
2. Check if it contains an <a href> link to alfaapanels.com
3. Call check_if_already_targeted
4. If unlinked: call generate_outreach_email with link_type='brand_mention'
5. If already linked: call track_backlink_action with status='completed'
6. If unlinked: call track_backlink_action with status='pending_manual' + full email in details

Target: Find every brand mention from the past 90 days.""",

        "forum_community_building": f"""
TODAY'S FOCUS: Forum & Community Participation

Identify professional communities where Alfa Panels can build authority with helpful posts.

Search for:
- "aluminium composite panel" site:archello.com OR site:archdaily.com forum
- Indian architecture and construction Facebook groups
- LinkedIn groups: "Building Materials India", "Architects India", "Interior Designers India"
- "ACP panels" site:indiamart.com/messages OR forum

For each community found:
1. Call check_if_already_targeted
2. Score with score_link_prospect
3. Identify a specific thread or topic where expertise can be shared
4. Call track_backlink_action with status='pending_manual', include:
   - The community URL
   - Specific thread/topic to engage with
   - Key talking points for the post
   - Whether the platform allows profile links

Target: 5 communities with active recent discussions.""",

        "social_profile_building": f"""
TODAY'S FOCUS: Social Profile & Citation Building

Identify platforms where alfaapanels.com is absent or has an incomplete profile.

Check these platforms:
- Google Business Profile (search "Alfa Panels" on Google Maps)
- ArchDaily company listing
- Houzz professional profile (India)
- LinkedIn company page
- Pinterest business account
- YouTube channel
- IndiaMART company showcase page
- TradeIndia premium listing
- JustDial business page
- Alibaba supplier profile

For each platform:
1. Search for existing alfaapanels.com presence
2. Call check_if_already_targeted
3. Score the citation opportunity with score_link_prospect
4. Call track_backlink_action with:
   - status='completed' if profile exists and is optimised
   - status='pending_manual' if absent or incomplete, with setup URL and required NAP data

NAP data to use:
Brand: Alfa Panels
Website: https://alfaapanels.com
Email: {CONTACT_EMAIL}
Category: Aluminium Composite Panel Supplier / Building Materials

Target: Full audit of 10 citation sources.""",
    }

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            track_backlink_action,
            check_if_already_targeted,
            score_link_prospect,
            generate_outreach_email,
            craft_qa_answer,
            identify_link_gap,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[
            {
                "role": "user",
                "content": f"""You are an expert off-page SEO strategist executing a daily backlink-building session for {DOMAIN}.

SITE PROFILE:
  Domain     : {DOMAIN}
  Brand      : {BRAND}
  Niche      : {NICHE}
  Market     : India (primary), South & Southeast Asia
  Contact    : {CONTACT_EMAIL}
  Competitors: {', '.join(COMPETITORS)}
  Date       : {date_str}

TODAY'S MISSION:
{strategy_prompts[strategy]}

RULES (follow strictly):
1. ALWAYS call check_if_already_targeted before processing any URL.
2. ALWAYS call track_backlink_action after processing each opportunity.
3. Never fabricate URLs — use web_search then web_fetch to verify.
4. Quality over quantity: 5 relevant prospects beat 20 off-topic ones.
5. Prioritise Indian-market sources; geo-relevance boosts rankings.
6. All outreach emails must be ready-to-send — personalised, not generic.

FINISH WITH a structured DAILY SUMMARY:
- Strategy executed
- Number of opportunities found and logged
- Top 3 action items (manual tasks the team should complete today)
- Any high-priority items discovered outside today's strategy focus""",
            }
        ],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_path = REPORTS_DIR / f"report_{date_str}_{strategy}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report: {DOMAIN}\n\n")
        f.write(f"**Date:** {date_str}  \n")
        f.write(f"**Strategy:** {strategy.replace('_', ' ').title()}  \n\n")
        f.write("---\n\n")
        f.write("\n\n".join(full_report))

    print(f"\nReport saved: {report_path}")

    log = load_log()
    log.setdefault("runs", []).append({
        "date": date_str,
        "strategy": strategy,
        "report": str(report_path),
    })
    save_log(log)

    return str(report_path)


if __name__ == "__main__":
    run_daily_backlink_builder()
